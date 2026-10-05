# Inverse-volatility books and a volatility-targeted futures overlay

[![CI](https://github.com/lwang-genomics/inverse-vol-futures-overlay/actions/workflows/ci.yml/badge.svg)](https://github.com/lwang-genomics/inverse-vol-futures-overlay/actions/workflows/ci.yml)
![Python 3.12](https://img.shields.io/badge/python-3.12-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

A walk-forward study of a long-only **inverse-volatility** portfolio of equities, the US dollar and gold
(ES / DX / GC futures, 2001–2026), compared with a Treasury-based alternative and a fixed 60/30/10 portfolio.
Each book is then scaled to a **10% volatility target** with a futures overlay, using only past data.

The emphasis is on **what survives robustness testing**: realistic implementation, ex-ante risk matching,
sub-periods, block-bootstrap confidence intervals and asset-dependence checks. Several "obvious" conclusions
did not survive them.

📄 **Full report (22 pages):** [`report/inverse_vol_futures_overlay.pdf`](report/inverse_vol_futures_overlay.pdf)

---

## Findings

| | Robust? | Evidence |
|---|---|---|
| Inverse-vol books cut drawdowns sharply | **Yes** | Max drawdown −11% (dollar book) and −19% (Treasury book), vs −34% for 60/30/10 and −57% for equities. Both lost less than 60/30/10 in every stress episode tested. |
| The dollar book has the best risk-adjusted return | **Suggestive, not established** | Highest full-sample Sharpe (0.87 vs 0.67 / 0.60), but the bootstrap 95% intervals of the differences include zero, and the Treasury book led in 2001–2012. |
| At equal risk, the dollar book compounds fastest | Yes, *with ≈2× leverage* | Scaled ex ante to 10% volatility: 9.8% a year vs 6.9% (Treasury book), 6.0% (60/30/10) and 5.0% (equities). |
| The edge depends on gold | **Yes, a key dependency** | Without gold, both inverse-vol books have a Sharpe ratio of ≈0.35. |
| Which defensive asset is better depends on the regime | Yes | Treasuries hedged the deflationary crashes (2002, 2008, 2020); the dollar hedged the 2022 inflation shock, when the stock–bond correlation turned positive. |
| Rebalancing frequency matters | **No** | Monthly to annual moves Sharpe by at most ≈0.06. At quarterly rebalancing, costs are ≈2 bp a year. |
| S&P 500 beats a world-equity sleeve | **Only in 2012–2026** | Significant in that era (t ≈ 2.6), but on 2000–2026 the difference is insignificant, and inside the inverse-vol book the two give the same Sharpe (0.87 vs 0.86). |

<p align="center">
  <img src="figures/fig14_trad_growth.png" width="90%"><br>
  <em>a, unlevered books. b, the same books scaled ex ante to a 10% volatility target (futures overlay, leverage ≤ 3×).</em>
</p>

### Same risk, no hindsight: books scaled to a 10% volatility target (futures, 2001-10 → 2026-10)

| | Inv-vol USD (ES/DX/GC) | Inv-vol Trad (ES/ZN/GC) | Fixed 60/30/10 | ES only |
|---|---:|---:|---:|---:|
| Annual return | **9.83%** | 6.94% | 5.96% | 4.98% |
| Annual volatility | 11.25% | 10.98% | 11.51% | 11.50% |
| Max drawdown | **−22.8%** | −30.1% | −27.0% | −28.4% |
| Sharpe | **0.87** | 0.63 | 0.52 | 0.43 |
| Average / max leverage | 1.96× / 2.92× | 1.84× / 3.00× | 1.09× / 2.75× | 0.67× / 1.58× |

### How robust is the ranking?

<p align="center">
  <img src="figures/fig20_rolling_sharpe.png" width="70%"><br>
  <em>Rolling 3-year Sharpe ratio: leadership changes hands several times.</em>
</p>

Sharpe differences, moving-block bootstrap (63-day blocks, 2,000 resamples):

| Comparison | Δ Sharpe | 95% interval | Share > 0 |
|---|---:|:---:|---:|
| Inv-vol USD vs Inv-vol Trad | 0.20 | −0.23 to 0.57 | 80% |
| Inv-vol USD vs Fixed 60/30/10 | 0.28 | −0.07 to 0.63 | 94% |

| Sharpe by sub-period | Inv-vol USD | Inv-vol Trad | Fixed 60/30/10 |
|---|---:|---:|---:|
| 2001–2012 | 0.57 | **0.83** | 0.37 |
| 2013–2021 | **0.95** | 0.56 | 0.93 |
| 2022–2026 | **1.52** | 0.53 | 0.65 |

## Method

- **Universe.** Yahoo Finance continuous futures (ES, DX index, GC, ZN), cross-checked against US ETFs
  (SPY, UUP, GLD, IEF) and UCITS equity ETFs (CSPX, VWRD/VWCE). A 2000–2026 world-equity proxy (50% SPY + 50% VGTSX)
  is validated against ACWI (weekly correlation 0.996).
- **Walk-forward.** Quarter-end rebalancing. Inverse-vol weights come from the trailing 252 days, the book is traded
  at the close, and **weights drift** between rebalances. Each trade pays **10 bp per unit traded**.
- **Volatility targeting.** At each rebalance, the target weights are scaled so that the ex-ante volatility from the
  trailing covariance equals 10%, with leverage capped at 3×. No full-sample information is used.
- **Statistics.** Futures returns are excess of cash, so their Sharpe uses rf = 0; ETF and UCITS Sharpe ratios are
  measured over 13-week T-bills. Robustness checks: sub-periods, moving-block bootstrap of Sharpe differences, stress
  episodes, drop-one-asset tests and rebalance-frequency sensitivity.

## Reproduce

Requires [uv](https://docs.astral.sh/uv/).

```bash
uv sync                  # Python 3.12 environment from uv.lock
uv run ivoverlay         # download prices, run every backtest, write results/ and figures/
uv run ivoverlay-report  # compile report/inverse_vol_futures_overlay.pdf (Typst, via the typst package)
uv run pytest            # unit tests on synthetic data (no network)
```

Prices are downloaded on first run and cached in `data/` (not committed; Yahoo's terms do not allow
redistribution). Yahoo occasionally revises history, so a fresh download can move the last digits of some
results. The committed `results/` match the committed report.

## Code

```
src/ivoverlay/
  config.py     instruments, parameters, analysis periods
  data.py       download, cache, return construction, T-bill rate
  backtest.py   walk-forward engine: inverse-vol / fixed weights, drift, costs, vol targeting
  metrics.py    performance metrics, drawdowns, rolling Sharpe
  stats.py      moving-block bootstrap of Sharpe differences
  study.py      the full study, one method per report section
  plots.py      figures (styling from viz_style.py)
  report.py     PDF build
tests/          engine tests, including an explicit no-look-ahead test
report/         Typst source and compiled PDF
```

The tests check the engine against independent calculations:

- agreement with an explicit buy-and-hold holdings simulation;
- costs equal to bp × traded notional, charged only on rebalance days;
- ex-ante volatility equal to the target, with the leverage cap respected;
- **no look-ahead**: changing every return after a cut-off date leaves all weights and returns before it unchanged.

## Limitations

- Yahoo continuous futures are not back-adjusted, and futures roll costs are not modelled. DX is the spot
  index, with no carry.
- The volatility-targeted books assume frictionless leverage up to 3×. Margin, financing basis and liquidity are
  ignored.
- The sample covers only the final leg of the 2000–02 dot-com crash.
- There are no taxes. Results are in USD; a EUR-based investor would face additional currency effects.

## Follow-up

Part III of [trend-following-replication](https://github.com/lwang-genomics/trend-following-replication) rebuilds
the inverse-vol Treasury book with the same rules on back-adjusted futures (roll yield included, 1991–2024). It adds
a trend-following overlay, following Dao et al. (2016) on trend convexity. At equal 10% volatility the overlay raises
the Sharpe ratio from 0.66 to 0.99 and reduces the maximum drawdown from −28% to −21%. Its protection covers bear
markets that unfold over months, such as 2022, rather than crashes lasting a few weeks.

## Context

This started as a practical question: how to run a long-only multi-asset portfolio and scale it to a target
volatility with a futures overlay, and which parts of the usual backtest story actually hold up. It is research
code, **not investment advice**.

Implemented with AI-assisted coding (Claude Code). Research questions, design decisions, robustness checks
and interpretation are my own; all results are reproducible from the code.

**Author:** Liangxi Wang, computational scientist (Genomics PhD). Independent project, not affiliated with any
employer. Licence: MIT.
