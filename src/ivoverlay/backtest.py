"""Walk-forward portfolio backtests with drifting weights, costs and volatility targeting."""

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .config import (
    COST_BPS,
    LOOKBACK_DAYS,
    MAIN_FREQ,
    MAX_LEVERAGE,
    MIN_TRAIN_DAYS,
    TRAD_WEIGHTS,
    TRADING_DAYS,
)


@dataclass(frozen=True)
class BacktestResult:
    ret: pd.Series  # daily log returns after costs, from the day after the first rebalance
    held: pd.DataFrame  # end-of-day (drifting) weights
    targets: pd.DataFrame  # target weights set at each rebalance date
    turnover_pa: float  # average sum of |Δw| traded per year

    @property
    def leverage(self) -> pd.Series:
        """Gross notional exposure at each rebalance (1.0 for a fully invested long-only book)."""
        return self.targets.sum(axis=1)


def inverse_vol_weights(log_returns: pd.DataFrame) -> pd.Series:
    """w_i ∝ 1/σ_i, normalised to sum to one."""
    inv = 1.0 / log_returns.std()
    return inv / inv.sum()


def rebalance_dates(index: pd.DatetimeIndex, every_months: int) -> pd.DatetimeIndex:
    """Last trading day of every `every_months`-th month (Mar/Jun/Sep/Dec for 3)."""
    last = pd.Series(index, index=index).groupby(index.to_period("M")).last()
    return pd.DatetimeIndex([d for p, d in last.items() if p.month % every_months == 0])


def backtest(
    rets: pd.DataFrame,
    every_months: int = MAIN_FREQ,
    fixed: tuple[float, ...] | None = None,
    cost_bps: float = COST_BPS,
    vol_target: float | None = None,
    lookback: int = LOOKBACK_DAYS,
    min_train: int = MIN_TRAIN_DAYS,
    max_leverage: float = MAX_LEVERAGE,
) -> BacktestResult:
    """Drifting-weight walk-forward backtest on daily simple returns.

    At the close of each rebalance date, target weights are set (inverse-vol on
    the trailing `lookback` days of log returns, or `fixed`) and the book is
    traded to target at that close, paying `cost_bps` per unit of traded
    notional (sum |target − drifted weight|). Between rebalances holdings drift
    with prices. With `vol_target`, target weights are scaled so the ex-ante
    portfolio volatility (trailing covariance) hits the target, capped at
    `max_leverage`; this is meaningful for futures, whose returns are already
    excess of cash. Only data up to each rebalance close is used.
    """
    log_r = np.log1p(rets)
    idx = rets.index
    targets: dict[int, np.ndarray] = {}
    for d in rebalance_dates(idx, every_months):
        i = idx.get_loc(d)
        train = log_r.iloc[max(0, i - lookback + 1) : i + 1]
        if len(train) < min_train:
            continue
        w = np.asarray(fixed, dtype=float) if fixed is not None else inverse_vol_weights(train).to_numpy()
        if vol_target is not None:
            ex_ante = float(np.sqrt(w @ train.cov().to_numpy() @ w * TRADING_DAYS))
            w = w * min(max_leverage, vol_target / ex_ante)
        targets[i] = w
    if not targets:
        raise ValueError("no rebalance date has enough training history")

    R = rets.to_numpy()
    port = np.full(len(idx), np.nan)
    held = np.full(R.shape, np.nan)
    turnover = {}
    w = None
    for i in range(len(idx)):
        if w is not None:
            r_p = float(w @ R[i])
            w = w * (1.0 + R[i]) / (1.0 + r_p)
            port[i] = r_p
        if i in targets:
            tgt = targets[i]
            if w is not None:
                traded = float(np.abs(tgt - w).sum())
                port[i] = (1.0 + port[i]) * (1.0 - cost_bps / 1e4 * traded) - 1.0
                turnover[idx[i]] = traded
            w = tgt.copy()
        if w is not None:
            held[i] = w

    first = min(targets)
    ret = np.log1p(pd.Series(port, index=idx).iloc[first + 1 :])
    order = sorted(targets)
    return BacktestResult(
        ret=ret,
        held=pd.DataFrame(held, index=idx, columns=rets.columns).iloc[first:],
        targets=pd.DataFrame([targets[i] for i in order], index=idx[order], columns=rets.columns),
        turnover_pa=sum(turnover.values()) / (len(ret) / TRADING_DAYS),
    )


def walk_forward_constant_mix(log_returns: pd.DataFrame, min_train: int = MIN_TRAIN_DAYS) -> pd.Series:
    """Reference shortcut: prior-calendar-year inverse-vol, held for the next
    month as a constant mix of log returns (implicit daily rebalancing, no costs)."""
    parts = []
    for month in log_returns.index.to_period("M").unique():
        apply_start = month.to_timestamp()
        train = log_returns.loc[apply_start - pd.DateOffset(years=1) : apply_start - pd.Timedelta(days=1)]
        if len(train) < min_train:
            continue
        w = inverse_vol_weights(train)
        month_rets = log_returns[log_returns.index.to_period("M") == month]
        parts.append(month_rets.mul(w, axis=1).sum(axis=1))
    return pd.concat(parts).sort_index()


def run_three(
    rets_usd: pd.DataFrame,
    rets_trad: pd.DataFrame,
    every_months: int = MAIN_FREQ,
    vol_target: float | None = None,
) -> dict[str, BacktestResult]:
    """The three books compared throughout: inverse-vol on the dollar basket,
    inverse-vol on the Treasury basket, and fixed 60/30/10 on the Treasury basket."""
    return {
        "iv_usd": backtest(rets_usd, every_months, vol_target=vol_target),
        "iv_trad": backtest(rets_trad, every_months, vol_target=vol_target),
        "fixed_trad": backtest(rets_trad, every_months, fixed=TRAD_WEIGHTS, vol_target=vol_target),
    }
