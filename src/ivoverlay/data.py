"""Price download, caching and return construction."""

import io
import time
import urllib.request

import numpy as np
import pandas as pd
import yfinance as yf

from .config import BACKADJ, DATA_FILE, END, FUTURES_COMMIT, FUTURES_URL, SPLICE_END, START, TICKERS, TRADING_DAYS

FUTURES_DIR = DATA_FILE.parent / "futures"


def load_prices(refresh: bool = False) -> pd.DataFrame:
    """Daily adjusted closes for every label in TICKERS, cached in data/prices.csv.

    An existing cache is reused; labels missing from it are downloaded up to the
    cache's last date and merged in, so earlier results stay reproducible.
    """
    if DATA_FILE.exists() and not refresh:
        px = pd.read_csv(DATA_FILE, index_col=0, parse_dates=True)
        missing = [k for k in TICKERS if k not in px]
        if not missing:
            return px[list(TICKERS)]
        end = f"{px.index.max() + pd.Timedelta(days=1):%Y-%m-%d}"
        extra = download_close([TICKERS[k] for k in missing], end=end)
        px = px.join(extra.rename(columns={TICKERS[k]: k for k in missing}), how="outer")[list(TICKERS)]
        px.to_csv(DATA_FILE)
        return px
    close = download_close(list(TICKERS.values()), end=END)
    px = close.rename(columns={v: k for k, v in TICKERS.items()})[list(TICKERS)]
    DATA_FILE.parent.mkdir(exist_ok=True)
    px.to_csv(DATA_FILE)
    return px


def download_close(symbols: list[str], end: str) -> pd.DataFrame:
    close = yf.download(symbols, start=START, end=end, auto_adjust=True, progress=False)["Close"]
    if isinstance(close, pd.Series):
        close = close.to_frame(symbols[0])
    for _ in range(3):  # Yahoo occasionally drops a symbol; retry those one by one
        missing = [s for s in symbols if s not in close or close[s].isna().all()]
        for s in missing:
            one = yf.download(s, start=START, end=end, auto_adjust=True, progress=False)["Close"]
            close[s] = one.squeeze()
    if close.index.tz is not None:
        close.index = close.index.tz_localize(None)
    return close


def basket_returns(px: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """Daily simple returns; forward-fill within the basket, drop leading gaps."""
    p = px[cols].dropna(how="all").ffill().dropna()
    return p.pct_change().dropna()


def tbill_log_returns(px: pd.DataFrame) -> pd.Series:
    """Daily log return of holding 13-week T-bills, from the ^IRX yield (% p.a.)."""
    return np.log1p(px["TBILL"].ffill() / 100.0 / TRADING_DAYS).dropna()


# ------------------------------------------------------------------ back-adjusted futures


def _fetch(path: str, retries: int = 3) -> bytes:
    """One pysystemtrade data file at the pinned commit, cached under data/futures/."""
    local = FUTURES_DIR / path.replace("/", "_")
    if not local.exists():
        FUTURES_DIR.mkdir(parents=True, exist_ok=True)
        for attempt in range(retries):
            try:
                with urllib.request.urlopen(FUTURES_URL.format(FUTURES_COMMIT, path), timeout=60) as r:
                    local.write_bytes(r.read())
                break
            except OSError:
                if attempt == retries - 1:
                    raise
                time.sleep(2 * (attempt + 1))
    return local.read_bytes()


def _last_per_day(raw: bytes, column: str) -> pd.Series:
    x = pd.read_csv(io.BytesIO(raw), parse_dates=["DATETIME"]).set_index("DATETIME")[column].astype(float).dropna()
    d = x.groupby(x.index.normalize()).last()
    return d[d.index.dayofweek < 5]


def backadjusted_returns(instrument: str) -> pd.Series:
    """Daily excess return of the futures contract held: back-adjusted price change over the contract's actual price.

    Back-adjustment shifts history at each roll, so price changes are those of the contract held (no roll gap) and
    roll yield is included; the actual price (PRICE in the multiple-prices file) turns them into percentages.
    """
    adj = _last_per_day(_fetch(f"adjusted_prices_csv/{instrument}.csv"), "price")
    actual = _last_per_day(_fetch(f"multiple_prices_csv/{instrument}.csv"), "PRICE")
    both = pd.concat([adj, actual], axis=1, keys=["adj", "px"]).dropna()
    return (both["adj"].diff() / both["px"].shift(1)).dropna()


def splice_levels(fut: pd.Series, etf_excess: pd.Series, index: pd.DatetimeIndex, splice_end: str) -> pd.Series:
    """Excess-return price index on `index`: futures returns up to `splice_end`, ETF excess returns after.

    The futures index is compounded on its own calendar and sampled on `index` (last value on or before each
    date), so returns over days one market did not trade are not lost.
    """
    level = (1.0 + fut.loc[:splice_end]).cumprod()
    head = level.reindex(index.union(level.index)).ffill().reindex(index).loc[:splice_end]
    tail = (1.0 + etf_excess.reindex(index).fillna(0.0).loc[index > pd.Timestamp(splice_end)]).cumprod()
    return pd.concat([head, head.dropna().iloc[-1] * tail])


def with_backadjusted_futures(px: pd.DataFrame) -> pd.DataFrame:
    """Replace the Yahoo futures columns by back-adjusted excess-return indices spliced with ETF excess returns.

    Each new column starts where its Yahoo series starts, so the study windows do not change. The Yahoo
    originals are kept as `<label>_yahoo` for the roll-bias check.
    """
    out = px.copy()
    rf = (px["TBILL"].ffill() / 100.0 / TRADING_DAYS).reindex(px.index).ffill()
    for label, (instrument, etf) in BACKADJ.items():
        etf_excess = px[etf].pct_change() - rf
        new = splice_levels(backadjusted_returns(instrument), etf_excess, px.index, SPLICE_END)
        new[new.index < px[label].first_valid_index()] = np.nan
        out[f"{label}_yahoo"] = px[label]
        out[label] = new
    return out
