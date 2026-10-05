"""Performance metrics on daily log returns."""

import numpy as np
import pandas as pd

from .config import TRADING_DAYS


def drawdown(log_returns: pd.Series) -> pd.Series:
    wealth = np.exp(log_returns.cumsum())
    return wealth / wealth.cummax() - 1.0


def sharpe(log_returns) -> float:
    """Annualised Sharpe ratio with rf = 0 (use on excess returns)."""
    return float(np.expm1(log_returns.mean() * TRADING_DAYS) / (log_returns.std() * np.sqrt(TRADING_DAYS)))


def series_metrics(log_returns: pd.Series, rf: pd.Series | None = None) -> dict[str, float]:
    """Performance metrics from daily log returns.

    Sharpe and Sortino use returns in excess of `rf` (daily log T-bill return)
    when given; otherwise rf = 0, which is correct for futures excess returns.
    """
    ann_ret = float(np.exp(log_returns.mean() * TRADING_DAYS) - 1.0)
    ann_vol = float(log_returns.std(ddof=1) * np.sqrt(TRADING_DAYS))
    downside_vol = float(np.sqrt((log_returns.clip(upper=0.0) ** 2).mean()) * np.sqrt(TRADING_DAYS))
    max_dd = float(drawdown(log_returns).min())
    ex = log_returns if rf is None else log_returns - rf.reindex(log_returns.index).ffill().fillna(0.0)
    ann_ex = float(np.exp(ex.mean() * TRADING_DAYS) - 1.0)
    vol_ex = float(ex.std(ddof=1) * np.sqrt(TRADING_DAYS))
    down_ex = float(np.sqrt((ex.clip(upper=0.0) ** 2).mean()) * np.sqrt(TRADING_DAYS))
    return {
        "avg_annual_return": ann_ret,
        "avg_annual_vol": ann_vol,
        "skewness": float(log_returns.skew()),
        "kurtosis": float(log_returns.kurt()),
        "downside_vol": downside_vol,
        "max_drawdown": max_dd,
        "sharpe": ann_ex / vol_ex if vol_ex > 0 else float("nan"),
        "sortino": ann_ex / down_ex if down_ex > 0 else float("nan"),
        "calmar": ann_ret / abs(max_dd) if max_dd < 0 else float("nan"),
    }


def period_return(log_returns: pd.Series, start: str, end: str) -> float:
    """Simple return from the close of `start` to the close of `end`."""
    w = log_returns.loc[pd.Timestamp(start) + pd.Timedelta(days=1) : end]
    return float(np.exp(w.sum()) - 1.0) if len(w) else float("nan")


def rolling_sharpe(log_returns: pd.Series, window: int) -> pd.Series:
    mean = log_returns.rolling(window).mean()
    std = log_returns.rolling(window).std()
    return (np.expm1(mean * TRADING_DAYS) / (std * np.sqrt(TRADING_DAYS))).dropna()


def common(series: dict[str, pd.Series]) -> dict[str, pd.Series]:
    """Restrict every series to the dates they all share."""
    idx = None
    for s in series.values():
        idx = s.index if idx is None else idx.intersection(s.index)
    return {k: v.loc[idx] for k, v in series.items()}


def span(s: pd.Series | pd.DataFrame) -> str:
    return f"{s.index.min():%Y-%m-%d} → {s.index.max():%Y-%m-%d}"
