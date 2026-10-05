import numpy as np
import pandas as pd
import pytest

from ivoverlay.backtest import backtest, inverse_vol_weights, rebalance_dates


def test_inverse_vol_weights_sum_to_one_and_scale_with_inverse_vol(returns):
    w = inverse_vol_weights(np.log1p(returns))
    assert w.sum() == pytest.approx(1.0)
    vol = np.log1p(returns).std()
    assert w["EQ"] / w["FX"] == pytest.approx(vol["FX"] / vol["EQ"])
    assert w.idxmax() == "FX"  # lowest-vol asset gets the largest weight


def test_rebalance_dates_are_last_trading_day_of_quarter(returns):
    dates = rebalance_dates(returns.index, 3)
    assert set(dates.month) == {3, 6, 9, 12}
    for d in dates:
        same_month = returns.index[(returns.index.year == d.year) & (returns.index.month == d.month)]
        assert d == same_month.max()


def test_fixed_weights_match_explicit_holdings_simulation(returns):
    """Between rebalances the book must behave like buy-and-hold units."""
    w0 = np.array([0.6, 0.3, 0.1])
    res = backtest(returns, every_months=12, fixed=tuple(w0), cost_bps=0.0, min_train=1)

    prices = (1 + returns).cumprod()
    value, units = None, None
    wealth = []
    for d in returns.index:
        if units is not None:
            value = float(units @ prices.loc[d].to_numpy())
            wealth.append((d, value))
        if d in set(res.targets.index):
            value = 1.0 if value is None else value
            units = w0 * value / prices.loc[d].to_numpy()
    expected = pd.Series(dict(wealth))
    simulated = np.exp(res.ret.cumsum())
    np.testing.assert_allclose(simulated.to_numpy(), expected.loc[simulated.index].to_numpy(), rtol=1e-10)


def test_costs_equal_bps_times_traded_notional(returns):
    free = backtest(returns, fixed=(0.6, 0.3, 0.1), cost_bps=0.0)
    costly = backtest(returns, fixed=(0.6, 0.3, 0.1), cost_bps=25.0)
    drag = (free.ret - costly.ret)[lambda s: s.abs() > 1e-15]
    assert set(drag.index) <= set(costly.targets.index)  # costs only on rebalance days

    held = free.held.shift(1).loc[drag.index]  # drifted weights just before trading...
    rets = returns.loc[drag.index]
    drifted = held * (1 + rets)
    drifted = drifted.div(drifted.sum(axis=1), axis=0)  # ...after that day's move
    traded = (free.targets.loc[drag.index] - drifted).abs().sum(axis=1)
    expected = -np.log1p(-25e-4 * traded)  # log(1+r) − log((1+r)(1−c))
    np.testing.assert_allclose(drag.to_numpy(), expected.to_numpy(), rtol=1e-9)


def test_no_look_ahead(returns):
    """Changing returns after a cut-off must not change anything up to the cut-off."""
    cut = pd.Timestamp("2020-06-30")
    shocked = returns.copy()
    after = shocked.index > cut
    shocked.loc[after] = shocked.loc[after] * 5.0 + 0.01

    base = backtest(returns, vol_target=0.10)
    alt = backtest(shocked, vol_target=0.10)
    pd.testing.assert_frame_equal(base.targets.loc[:cut], alt.targets.loc[:cut])
    pd.testing.assert_series_equal(base.ret.loc[:cut], alt.ret.loc[:cut])
    assert not base.targets.loc[cut:].iloc[1:].equals(alt.targets.loc[cut:].iloc[1:])


def test_vol_target_hits_target_ex_ante_and_respects_leverage_cap(returns):
    res = backtest(returns, vol_target=0.10, max_leverage=3.0)
    log_r = np.log1p(returns)
    for d, w in res.targets.iterrows():
        i = returns.index.get_loc(d)
        cov = log_r.iloc[max(0, i - 251) : i + 1].cov().to_numpy()
        ex_ante = np.sqrt(w.to_numpy() @ cov @ w.to_numpy() * 252)
        if w.sum() < 3.0 - 1e-12:
            assert ex_ante == pytest.approx(0.10)
    assert (res.leverage <= 3.0 + 1e-12).all()

    capped = backtest(returns * 0.01, vol_target=0.10, max_leverage=3.0)  # tiny vol -> cap binds
    np.testing.assert_allclose(capped.leverage.to_numpy(), 3.0)


def test_raises_without_enough_history(returns):
    with pytest.raises(ValueError):
        backtest(returns.iloc[:100])
