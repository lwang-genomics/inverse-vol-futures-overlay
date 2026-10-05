import numpy as np
import pandas as pd
import pytest

from ivoverlay.metrics import drawdown, period_return, series_metrics
from ivoverlay.stats import bootstrap_sharpe_diff


def test_drawdown_on_known_path():
    lr = pd.Series(np.log([1.10, 0.5, 1.2, 2.0]), index=pd.bdate_range("2020-01-01", periods=4))
    # wealth 1.1, 0.55, 0.66, 1.32 -> peaks 1.1, 1.1, 1.1, 1.32
    np.testing.assert_allclose(drawdown(lr).to_numpy(), [0.0, -0.5, -0.4, 0.0])
    assert series_metrics(lr)["max_drawdown"] == pytest.approx(-0.5)


def test_annual_return_and_vol_annualisation():
    rng = np.random.default_rng(0)
    lr = pd.Series(rng.normal(0.0003, 0.01, 252 * 40), index=pd.bdate_range("1980-01-01", periods=252 * 40))
    m = series_metrics(lr)
    assert m["avg_annual_return"] == pytest.approx(np.expm1(lr.mean() * 252))
    assert m["avg_annual_vol"] == pytest.approx(lr.std() * np.sqrt(252))


def test_sharpe_is_measured_over_the_risk_free_rate():
    idx = pd.bdate_range("2020-01-01", periods=1000)
    rng = np.random.default_rng(1)
    excess = pd.Series(rng.normal(0.0002, 0.005, len(idx)), index=idx)
    rf = pd.Series(0.0001, index=idx)
    with_rf = series_metrics(excess + rf, rf)["sharpe"]
    assert with_rf == pytest.approx(series_metrics(excess)["sharpe"])
    assert series_metrics(excess + rf)["sharpe"] > with_rf  # ignoring rf flatters the funded series


def test_period_return_runs_close_to_close():
    lr = pd.Series(np.log([1.0, 1.1, 1.2, 0.9]), index=pd.to_datetime(["2020-01-01", "2020-01-02", "2020-01-03",
                                                                      "2020-01-06"]))
    assert period_return(lr, "2020-01-01", "2020-01-03") == pytest.approx(1.1 * 1.2 - 1)


def test_bootstrap_of_identical_series_is_degenerate_and_reproducible():
    rng = np.random.default_rng(2)
    a = pd.Series(rng.normal(0.0003, 0.01, 2000), index=pd.bdate_range("2010-01-01", periods=2000))
    same = bootstrap_sharpe_diff(a, a, n_boot=200)
    assert same["diff"] == same["lo"] == same["hi"] == 0.0

    b = a + rng.normal(0, 0.002, len(a))
    assert bootstrap_sharpe_diff(a, b, n_boot=200, seed=7) == bootstrap_sharpe_diff(a, b, n_boot=200, seed=7)


def test_bootstrap_detects_a_large_true_difference():
    rng = np.random.default_rng(3)
    idx = pd.bdate_range("2000-01-01", periods=252 * 20)
    noise = rng.normal(0, 0.01, len(idx))
    good = pd.Series(noise + 0.001, index=idx)  # Sharpe ≈ 1.6
    bad = pd.Series(noise - 0.0005, index=idx)
    res = bootstrap_sharpe_diff(good, bad, n_boot=300)
    assert res["lo"] > 0 and res["p_pos"] == 1.0
