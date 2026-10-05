"""Price download, caching and return construction."""

import numpy as np
import pandas as pd
import yfinance as yf

from .config import DATA_FILE, END, START, TICKERS, TRADING_DAYS


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
