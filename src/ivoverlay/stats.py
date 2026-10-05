"""Resampling statistics for comparing strategies."""

import numpy as np
import pandas as pd

from .config import BOOT_BLOCK, BOOT_N, TRADING_DAYS
from .metrics import sharpe


def bootstrap_sharpe_diff(
    a: pd.Series,
    b: pd.Series,
    block: int = BOOT_BLOCK,
    n_boot: int = BOOT_N,
    seed: int = 0,
) -> dict[str, float]:
    """Moving-block bootstrap of Sharpe(a) − Sharpe(b) on aligned daily log returns.

    Both series are resampled with the same block indices, so their correlation
    and the autocorrelation within each block are preserved.
    Returns the point estimate, a 95% percentile interval and the share of
    resamples in which `a` has the higher Sharpe ratio.
    """
    idx = a.index.intersection(b.index)
    A, B = a.loc[idx].to_numpy(), b.loc[idx].to_numpy()
    n = len(A)
    rng = np.random.default_rng(seed)
    starts = rng.integers(0, n - block, size=(n_boot, n // block + 1))
    ii = (starts[:, :, None] + np.arange(block)).reshape(n_boot, -1)[:, :n]

    def sr(x: np.ndarray) -> np.ndarray:
        return np.expm1(x.mean(axis=1) * TRADING_DAYS) / (x.std(axis=1, ddof=1) * np.sqrt(TRADING_DAYS))

    d = sr(A[ii]) - sr(B[ii])
    lo, hi = np.percentile(d, [2.5, 97.5])
    return {
        "diff": sharpe(pd.Series(A)) - sharpe(pd.Series(B)),
        "lo": float(lo),
        "hi": float(hi),
        "p_pos": float((d > 0).mean()),
    }
