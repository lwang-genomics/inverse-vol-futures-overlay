# Inverse-volatility books and a volatility-targeted futures overlay

[![CI](https://github.com/lwang-genomics/inverse-vol-futures-overlay/actions/workflows/ci.yml/badge.svg)](https://github.com/lwang-genomics/inverse-vol-futures-overlay/actions/workflows/ci.yml)
![Python 3.12](https://img.shields.io/badge/python-3.12-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

A walk-forward study of long-only **inverse-volatility** portfolios of equities, the US dollar or Treasuries, and
gold (futures and ETFs, 2001–2026), scaled to a **10% volatility target** with a futures overlay. The focus is on
which conclusions survive robustness testing.

📄 **Full report (PDF):** [`report/inverse_vol_futures_overlay.pdf`](report/inverse_vol_futures_overlay.pdf)

| Claim | Robust? | Evidence |
|---|---|---|
| Inverse-vol books cut drawdowns | **Yes** | −11% (dollar book) and −19% (Treasury book) vs −34% for 60/30/10 and −57% for equities; less loss in every stress episode. |
| The dollar book has the best risk-adjusted return | **Suggestive** | Highest Sharpe (0.87 vs 0.67 / 0.60), but every bootstrap 95% interval of the differences includes zero. |
| At equal risk the dollar book compounds fastest | Yes, *with ≈2× leverage* | At 10% volatility: 9.8% a year vs 6.9% (Treasury book), 6.0% (60/30/10), 5.0% (equities). |
| The edge depends on gold | **Yes** | Without gold, both inverse-vol books have a Sharpe ratio of ≈0.35. |
| Rebalancing frequency matters | **No** | Monthly to annual moves Sharpe by at most ≈0.06. |
| S&P 500 beats a world-equity sleeve | **Only in 2012–2026** | On 2000–2026 the two give the same Sharpe inside the book (0.87 vs 0.86). |

---

## Growth and drawdowns

<table>
<tr>
<td width="50%"><img src="figures/fig14_trad_growth.png"></td>
<td width="50%"><img src="figures/fig15_trad_drawdown.png"></td>
</tr>
<tr>
<td><sub>Unlevered books (a) and the same books scaled ex ante to 10% volatility (b). Grey: S&P 500 futures alone.</sub></td>
<td><sub>Drawdowns of the unlevered books: the inverse-vol books lost less in every stress episode.</sub></td>
</tr>
</table>

| At 10% volatility (2001–2026) | Inv-vol USD | Inv-vol Treasury | Fixed 60/30/10 | ES only |
|---|---:|---:|---:|---:|
| Annual return | **9.8%** | 6.9% | 6.0% | 5.0% |
| Max drawdown | **−22.8%** | −30.1% | −27.0% | −28.4% |
| Sharpe | **0.87** | 0.63 | 0.52 | 0.43 |
| Average leverage | 1.96× | 1.84× | 1.09× | 0.67× |

## Why it works, and when it doesn't

<table>
<tr>
<td width="50%"><img src="figures/fig04_fut_weights.png"></td>
<td width="50%"><img src="figures/fig05_rolling_corr.png"></td>
</tr>
<tr>
<td><sub>Actual weights: the low-volatility defensive asset takes about half the book.</sub></td>
<td><sub>Rolling correlations: the stock–bond hedge turned positive in 2022; dollar and gold stay negative.</sub></td>
</tr>
<tr>
<td><img src="figures/fig20_rolling_sharpe.png"></td>
<td><img src="figures/fig13_compare_fut_etf.png"></td>
</tr>
<tr>
<td><sub>Rolling 3-year Sharpe: the lead changes hands; Treasuries led in 2001–2012, the dollar since 2022.</sub></td>
<td><sub>The ETF version (SPY / UUP / GLD) tracks the futures book closely (correlation 0.91).</sub></td>
</tr>
</table>

## Which equity sleeve: S&P 500 or All-World?

<table>
<tr>
<td width="50%"><img src="figures/fig21_world_vs_sp500_long.png"></td>
<td width="50%"><img src="figures/fig22_world_sleeve_in_portfolios.png"></td>
</tr>
<tr>
<td><sub>S&P 500 vs a world-equity proxy since 2000: the world sleeve led until 2011, the S&P 500 since.</sub></td>
<td><sub>Sharpe inside each book, by era: the S&P 500's lead belongs to 2012–2026.</sub></td>
</tr>
</table>

**Follow-up:** Part III of [trend-following-replication](https://github.com/lwang-genomics/trend-following-replication)
adds a trend-following overlay to the Treasury book (back-adjusted futures, 1991–2024). At equal 10% volatility it
raises the Sharpe ratio from 0.66 to 0.99 and cuts the maximum drawdown from −28% to −21%.

---

## Reproduce

```bash
uv sync                  # Python 3.12 environment from uv.lock
uv run ivoverlay         # download prices, run every backtest, write results/ and figures/
uv run ivoverlay-report  # compile the PDF report
uv run pytest            # unit tests on synthetic data (no network)
```

<details>
<summary><b>Method</b></summary>

- **Universe.** Yahoo Finance continuous futures (ES, DX index, GC, ZN), cross-checked against US ETFs (SPY, UUP,
  GLD, IEF) and UCITS equity ETFs (CSPX, VWRD/VWCE). A 2000–2026 world-equity proxy (50% SPY + 50% VGTSX) is validated
  against ACWI (weekly correlation 0.996).
- **Walk-forward.** Quarter-end rebalancing to inverse-vol weights from the trailing 252 days; weights drift between
  rebalances; each trade pays 10 bp per unit traded.
- **Volatility targeting.** At each rebalance the weights are scaled so that the ex-ante volatility from the trailing
  covariance is 10%, with leverage capped at 3×. No full-sample information is used.
- **Statistics.** Futures Sharpe ratios use rf = 0 (excess returns); ETF and UCITS ones are over 13-week T-bills.
  Robustness: sub-periods, moving-block bootstrap of Sharpe differences, stress episodes, drop-one-asset tests and
  rebalance-frequency sensitivity.

</details>

<details>
<summary><b>Robustness details</b></summary>

| Sharpe difference (moving-block bootstrap) | Δ Sharpe | 95% interval | Share > 0 |
|---|---:|:---:|---:|
| Inv-vol USD vs Inv-vol Treasury | 0.20 | −0.23 to 0.57 | 80% |
| Inv-vol USD vs Fixed 60/30/10 | 0.28 | −0.07 to 0.63 | 94% |

| Sharpe by sub-period | Inv-vol USD | Inv-vol Treasury | Fixed 60/30/10 |
|---|---:|---:|---:|
| 2001–2012 | 0.57 | **0.83** | 0.37 |
| 2013–2021 | **0.95** | 0.56 | 0.93 |
| 2022–2026 | **1.52** | 0.53 | 0.65 |

</details>

<details>
<summary><b>Code and tests</b></summary>

```
src/ivoverlay/
  config.py     instruments, parameters, analysis periods
  data.py       download, cache, return construction, T-bill rate
  backtest.py   walk-forward engine: inverse-vol / fixed weights, drift, costs, vol targeting
  metrics.py    performance metrics, drawdowns, rolling Sharpe
  stats.py      moving-block bootstrap of Sharpe differences
  study.py      the full study, one method per report section
  plots.py      figures: slide versions in figures/, report versions in figures/report/
  report.py     PDF build
```

The tests check the engine against an explicit buy-and-hold holdings simulation, the cost accounting, the
volatility target and leverage cap, and that there is **no look-ahead** (changing every return after a cut-off date
leaves all weights and returns before it unchanged). Prices are cached in `data/` and not committed (Yahoo's terms).

</details>

<details>
<summary><b>Limitations</b></summary>

- Yahoo continuous futures are not back-adjusted and roll costs are not modelled (the follow-up above rebuilds the
  Treasury book on back-adjusted futures). DX is the spot index, with no carry.
- Leverage up to 3× is assumed frictionless: margin, financing and liquidity are ignored.
- The sample covers only the final leg of the 2000–02 dot-com crash. No taxes; results are in USD.

</details>

---

Started as a practical question: how to run a long-only multi-asset portfolio and scale it to a target volatility
with a futures overlay, and which parts of the usual backtest story hold up. By Liangxi Wang, computational
scientist (Genomics PhD); independent, not affiliated with any employer. Implemented with AI-assisted coding (Claude
Code); research questions, design decisions, robustness checks and interpretation are my own. Research code, **not
investment advice**. MIT licence.
