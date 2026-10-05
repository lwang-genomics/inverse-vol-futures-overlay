// Inverse-volatility walk-forward backtest report.
// Build from the repository root: uv run ivoverlay && uv run ivoverlay-report
#let res = json("../results/results.json")
#let T = res.tables
#let F = res.facts
#let pct(x) = {
  let parts = str(calc.round(x * 100, digits: 2)).split(".")
  let dec = if parts.len() > 1 { parts.at(1) } else { "" }
  parts.at(0) + "." + dec + "0" * (2 - dec.len()) + "%"
}

#set document(title: "Inverse-Volatility Walk-Forward Backtest", author: "Liangxi Wang")
#set page(paper: "a4", margin: (x: 2.2cm, y: 2.2cm), numbering: "1")
#set text(font: ("Arial", "Helvetica Neue", "Helvetica"), size: 10pt)
#set par(justify: true, leading: 0.62em)
#set heading(numbering: "1.1")
#show heading.where(level: 1): it => block(above: 1.6em, below: 0.9em, text(size: 14pt, it))
#show heading.where(level: 2): it => block(above: 1.3em, below: 0.7em, text(size: 11.5pt, it))
#show figure.caption: set text(size: 9pt)
#show figure: set block(breakable: false, above: 1.2em, below: 1.2em)
#set figure(gap: 0.6em)

#let fig(path, caption, label: none) = [#figure(image("../figures/" + path, width: 100%), caption: caption) #label]

#let num(x) = {
  let neg = x < 0
  let parts = str(calc.round(calc.abs(x), digits: 2)).split(".")
  let dec = if parts.len() > 1 { parts.at(1) } else { "" }
  (if neg { "−" } else { "" }) + parts.at(0) + "." + dec + "0" * (2 - dec.len())
}

#let mtable(t, caption, size: 9pt, columns: auto, left-cols: 1) = figure(
  text(size: size)[#set par(justify: false); #table(
    columns: if columns == auto { t.header.len() } else { columns },
    align: (x, y) => if x < left-cols { left } else { right },
    stroke: none,
    inset: (x: 5pt, y: 3.2pt),
    table.hline(stroke: 0.8pt),
    table.header(..t.header.map(h => text(weight: "bold", h))),
    table.hline(stroke: 0.5pt),
    ..t.rows.flatten().map(c => [#c]),
    table.hline(stroke: 0.8pt),
  )],
  caption: caption,
  kind: table,
)

// ---------------------------------------------------------------- title
#align(center)[
  #text(size: 20pt)[Inverse-Volatility Walk-Forward Backtest] \
  #v(0.3em)
  #text(size: 12pt)[Futures basket (ES / DX / GC), ETF proxies (SPY / UUP / GLD), \
    a traditional Treasury basket, and UCITS equity sleeves] \
  #v(0.3em)
  #text(size: 10pt, fill: luma(110))[Liangxi Wang · data via Yahoo Finance (yfinance) through #F.end_date · October 2026 \
    #link("https://github.com/lwang-genomics/inverse-vol-futures-overlay")[github.com/lwang-genomics/inverse-vol-futures-overlay]]
]
#v(1em)
#outline(depth: 2, indent: auto)
#pagebreak()

// ---------------------------------------------------------------- 1
= Abstract

This note documents a walk-forward backtest of a long-only inverse-volatility portfolio on three futures
sleeves (equity ES, US dollar DX, gold GC) from October 2001 through October 2026. Weights are estimated
from the trailing year of daily returns and reset every quarter; between rebalances they drift with prices,
and every trade pays 10 bp. The note then asks four questions. Can the rule be replicated with liquid ETFs
(SPY, UUP, GLD)? How does it compare with a traditional basket that holds 10-year Treasuries instead of the
dollar (ES / ZN / GC, or SPY / IEF / GLD), run both with the same inverse-vol rule and as a fixed 60/30/10
allocation? How do the asset correlations behind each basket evolve? And, for a European implementation, which
UCITS equity sleeve works better: an S&P 500 ETF (CSPX) or the Vanguard FTSE All-World ETF (VWRD, the same fund
as VWCE)?

Over the full sample the inverse-vol USD book returns ≈5.0% a year at 5.7% volatility with a −11% worst
drawdown (Sharpe 0.87). Inverse-vol on ES / ZN / GC has a Sharpe of 0.67 and a −19% drawdown. The fixed 60/30/10
portfolio earns more in absolute terms, but at about twice the volatility, with a −34% drawdown and a Sharpe of 0.60.
Scaled ex ante to the same 10% volatility, the inverse-vol USD book still compounds fastest (9.8% vs
6.0–6.9% a year), but it needs about 2× leverage to get there.

This ranking should be read with caution. The Sharpe differences are not statistically significant: every
block-bootstrap 95% interval includes zero. Inverse-vol on Treasuries was ahead in 2001–2012, and much of the
dollar book's lead comes from 2022–2026, when bonds fell together with equities. Without gold, both inverse-vol
books have Sharpe ratios near 0.35. The robust finding is the drawdown profile: both inverse-vol books lost less
than 60/30/10 and equities in every stress episode in the sample.

The ETF version tracks the futures book closely (correlation ≈0.91); measured over T-bills, its Sharpe is
0.84. Rebalancing frequency is a second-order choice: quarterly cuts turnover by a third relative to monthly,
and Sharpe moves by less than 0.05. On the 2012–2026 sample, the S&P 500 sleeve beat the All-World sleeve on its
own and inside every portfolio. A 2000–2026 test with a world-equity proxy shows that this lead belongs to one era:
the world sleeve led in 2000–2011, and inside the inverse-vol book the two sleeves are indistinguishable over the
full period (Sharpe 0.87 vs 0.86).

// ---------------------------------------------------------------- 2
= Data and universe

== Futures basket

Daily adjusted closes are downloaded from Yahoo Finance from 2000-01-01; the futures histories begin in
August–September 2000:

#text(size: 9pt, table(
  columns: 3, stroke: none, inset: (x: 5pt, y: 3pt),
  table.hline(stroke: 0.8pt),
  table.header([*Label*], [*Yahoo symbol*], [*Role*]),
  table.hline(stroke: 0.5pt),
  [ES], [ES=F], [E-mini S&P 500 continuous futures],
  [DX], [DX-Y.NYB], [ICE US Dollar Index (spot); DX=F has no Yahoo history],
  [GC], [GC=F], [COMEX gold continuous futures],
  [ZN], [ZN=F], [CBOT 10-year T-note continuous futures (traditional basket)],
  table.hline(stroke: 0.8pt),
))

Within each basket, series are forward-filled and rows with remaining gaps are dropped. Yahoo's
continuous futures are not back-adjusted, so roll gaps leak into returns; futures returns are also
_excess_ returns (no collateral yield), which holds for every futures portfolio here alike.

== ETF proxy basket

#text(size: 9pt, table(
  columns: 3, stroke: none, inset: (x: 5pt, y: 3pt),
  table.hline(stroke: 0.8pt),
  table.header([*ETF*], [*Maps to*], [*Notes*]),
  table.hline(stroke: 0.5pt),
  [SPY], [ES], [S&P 500 ETF; daily corr with ES #F.fut_etf_corr.at("ES–SPY")],
  [UUP], [DX], [Dollar bullish ETF; available from 2007; corr #F.fut_etf_corr.at("DX–UUP")],
  [GLD], [GC], [Gold ETF; fees and tracking differ from futures; corr #F.fut_etf_corr.at("GC–GLD")],
  [IEF], [ZN], [iShares 7–10y Treasury ETF; corr #F.fut_etf_corr.at("ZN–IEF")],
  table.hline(stroke: 0.8pt),
))

ETF prices are dividend-adjusted (total return). The SPY / UUP / GLD walk-forward starts in 2008
(UUP history plus one year of lookback). The 13-week T-bill yield (^IRX) is downloaded as the risk-free rate
for ETF and UCITS Sharpe ratios.

== UCITS equity sleeves

The two European-domiciled equity ETFs are taken from their *USD-denominated London lines*, so no FX
conversion is needed and they are directly comparable with the US-listed assets:

#text(size: 9pt, table(
  columns: 3, stroke: none, inset: (x: 5pt, y: 3pt),
  table.hline(stroke: 0.8pt),
  table.header([*Ticker*], [*Fund*], [*Why this line*]),
  table.hline(stroke: 0.5pt),
  [CSPX.L], [iShares Core S&P 500 UCITS (Acc)], [Same fund as SXR8 on Xetra; history from 2010],
  [VWRD.L], [Vanguard FTSE All-World UCITS (Dist)], [Same fund as VWCE (Acc); history from 2012],
  [VWRA.L], [Vanguard FTSE All-World UCITS (Acc)], [Used only to validate VWRD as a proxy for VWCE],
  table.hline(stroke: 0.8pt),
))

VWCE and VWRA only exist since mid-2019, which is too short for a walk-forward with a one-year
lookback. On their common window (#F.vwrd_vwra.period), dividend-adjusted VWRD and accumulating VWRA have a daily
correlation of #F.vwrd_vwra.corr and annual returns of #pct(F.vwrd_vwra.ret_vwrd)
vs #pct(F.vwrd_vwra.ret_vwra). VWRD is therefore a faithful long-history
stand-in for VWCE.

For a longer test of the equity-sleeve choice (@sec-world), a world-equity proxy is built from two US-listed
funds that close at the same time: 50% SPY plus 50% Vanguard Total International Stock Index (VGTSX, including
emerging markets, from 1996). The iShares MSCI ACWI ETF (ACWI, from 2008) is used to validate it.

// ---------------------------------------------------------------- 3
= Methodology

== Inverse-volatility weights

For a training window of daily log returns, let $sigma_i$ be the sample standard deviation of sleeve $i$:
$ w_i = sigma_i^(-1) / (sum_j sigma_j^(-1)). $
The rule is long-only and fully invested.

== Walk-forward schedule and rebalancing

The backtest simulates an account that is actually traded:

- *Rebalance dates:* the last trading day of March, June, September and December (quarterly).
- *Estimation:* inverse-vol weights from the trailing 252 trading days ending on the rebalance date
  (windows with fewer than 200 days are skipped). The book is traded to target at that close.
- *Drift:* between rebalances, holdings are left alone and weights drift with prices:
  $ R_(p,t) = sum_i w_(i,t-1) R_(i,t), quad w_(i,t) = w_(i,t-1) (1 + R_(i,t)) / (1 + R_(p,t)). $
- *Costs:* each rebalance pays #F.cost_bps bp per unit traded, $c = 10 "bp" times sum_i |w_i^* - w_(i,t)|$,
  a conservative retail estimate covering spread, commission and slippage.

A common shortcut computes the portfolio return as $sum_i w_i r_(i,t)$ on _log_ returns with weights held
constant within each month. That implicitly rebalances every day at zero cost, and averaging log returns
understates the compounded return of the mix. @sec-rebal reports this constant-mix shortcut as a reference,
alongside monthly, quarterly, semi-annual and annual schedules.

== Portfolios compared

#text(size: 9pt, table(
  columns: 3, stroke: none, inset: (x: 5pt, y: 3pt),
  table.hline(stroke: 0.8pt),
  table.header([*Name*], [*Futures / ETF assets*], [*Weights*]),
  table.hline(stroke: 0.5pt),
  [Inv-vol USD], [ES/DX/GC · SPY/UUP/GLD], [inverse-vol (core strategy)],
  [Inv-vol Trad], [ES/ZN/GC · SPY/IEF/GLD], [inverse-vol, same rule with 10y Treasuries instead of the dollar],
  [Fixed 60/30/10], [ES/ZN/GC · SPY/IEF/GLD], [fixed 60% equity / 30% Treasury / 10% gold],
  table.hline(stroke: 0.8pt),
))

10-year Treasuries were chosen as the bond sleeve because they are the benchmark duration of a classic
balanced portfolio and have liquid futures (ZN) and ETF (IEF) proxies over the whole sample. All three
portfolios use the same quarterly schedule, costs and start date.

== Metrics

Annualization uses 252 trading days. For a series of daily log returns $r$:

- Average annual return: $exp(macron(r) dot 252) - 1$; average annual volatility: $s dot sqrt(252)$
- Downside volatility: $sqrt(E[min(r, 0)^2]) dot sqrt(252)$ (MAR = 0)
- Max drawdown: minimum of wealth / running peak − 1, with wealth = $exp("cumsum"(r))$
- Sharpe / Sortino: annualised excess return over the volatility / downside volatility of excess returns.
  Futures returns are already excess of cash, so they use $r_f = 0$. ETF and UCITS series are total returns,
  so they are measured over the 13-week T-bill.
- Calmar: annual return over |max drawdown|
- Kurtosis: excess (Fisher); turnover: average sum of $|Delta w|$ traded per year

Some single-portfolio path plots are linearly scaled so the terminal cumulative log return equals
$T dot ln(1.10)$. This scaling is for display only; metrics always use unscaled returns. Same-risk
comparisons (@sec-vt) use ex-ante volatility targeting, which needs no hindsight.

// ---------------------------------------------------------------- 4
= Futures results

Walk-forward OOS for futures: #F.fut_period (#F.fut_n_rebal quarterly weight updates).

== Asset cumulative log returns

#fig("fig01_fut_assets_cum_log.png")[Cumulative log returns of ES, DX, GC and ZN over the walk-forward window.]

Gold leads in raw cumulative log return. Equities are positive but much more volatile. The dollar is
roughly flat, and the 10-year note future gains steadily until 2020, then gives much of that back in the 2022 rate shock.

== Portfolio path and drawdown

#fig("fig02_fut_portfolio_cum_log.png")[Inverse-vol USD futures portfolio (quarterly, drifting weights, after costs): cumulative log returns scaled to a 10% average annual endpoint for visual comparison of path shape.]

#fig("fig03_fut_portfolio_drawdown.png")[Ongoing drawdown of the unscaled inverse-vol USD futures portfolio.]

== Weights

#fig("fig04_fut_weights.png")[Actual daily weights with quarterly rebalancing (targets reset at each quarter-end, then drift). *a*, Inv-vol USD. *b*, Inv-vol Trad.]

Mean target weights: ES #F.fut_mean_w.iv_usd.ES, DX #F.fut_mean_w.iv_usd.DX, GC #F.fut_mean_w.iv_usd.GC.
The book is structurally dollar-heavy because DX is the lowest-volatility sleeve. In the traditional
basket, ZN plays the same role (ES #F.fut_mean_w.iv_trad.ES, ZN #F.fut_mean_w.iv_trad.ZN, GC #F.fut_mean_w.iv_trad.GC),
so the two inverse-vol books differ mainly in the defensive half of their capital.

== Rolling correlations in both baskets <sec-corr>

#fig("fig05_rolling_corr.png")[252-day rolling pairwise correlations of daily log returns. *a*, assets of the Inv-vol USD basket. *b*, assets of the traditional basket. ES–GC appears in both panels.]

#fig("fig06_corr_regimes.png")[Daily correlation by regime for every asset pair in the two baskets (blue = diversifying, red = moving together).]

The two baskets diversify in different ways:

- *Dollar basket.* The defensive pair DX–GC is persistently and strongly negative: about −0.42 on average,
  and between −0.34 and −0.47 in every regime. Dollar and gold offset each other, which is why the book's
  volatility (≈5.7%) sits far below that of any sleeve. ES–DX changes sign over time. It was positive in
  2001–05, a safe-haven negative in 2008–14 and again in 2021–24, and mostly positive in 2015–17.
- *Traditional basket.* ES–ZN was the classic hedge: −0.3 to −0.6 from 2002 to 2021. In 2022 it flipped
  positive (+0.07 in the regime, +#F.roll_corr_last.at("ES–ZN") on the latest 1-year window). ZN–GC is
  _positive_ in every regime and peaks near +0.6 in 2017, 2020 and 2023. Bonds and gold both respond to
  real yields, so they hedge each other poorly.
- Today all three traditional pairs are positive (+0.2 to +0.3), so the traditional basket is at a low point of
  internal diversification, while the dollar basket still has two negative pairs.

== Calendar-year returns

#fig("fig07_fut_yearly_returns.png")[Calendar-year simple returns of the Inv-vol USD futures portfolio, $exp(sum_"year" r_t) - 1$. Teal = positive, salmon = negative. 2026 is year-to-date.]

== Performance table (futures full sample)

#mtable(T.fut, [Futures full-sample metrics on the walk-forward window (quarterly rebalancing, 10 bp costs). Futures returns are excess of cash, so Sharpe uses $r_f = 0$.])

// ---------------------------------------------------------------- 5
= Insights (futures)

+ *Risk-adjusted performance is the story.* Absolute return (≈5.0% a year) trails ES and GC, but volatility
  (5.7%) and max drawdown (−11%) are far better, and Sharpe, Sortino and Calmar lead the table.
+ *Inverse-vol concentrates in DX.* Low dollar volatility mechanically pulls about half of the weight. Results are
  sensitive to the DX proxy (DX-Y.NYB spot index, not listed DX futures, so no carry).
+ *Diversification is real but regime-dependent.* The dollar–gold offset is the stable ingredient; the
  equity–dollar and equity–bond correlations are not (@sec-corr).
+ *Implementation costs are small.* Quarterly rebalancing trades about 24% of the book a year, so costs come
  to only ≈2.4 bp a year (@sec-rebal).

// ---------------------------------------------------------------- 6
= ETF replication (SPY / UUP / GLD)

== Mapping and sample

UUP's history shortens the ETF experiment: walk-forward OOS runs #F.etf_period. On overlapping daily
log returns, correlations against the futures sleeves are ES–SPY #F.fut_etf_corr.at("ES–SPY"),
DX–UUP #F.fut_etf_corr.at("DX–UUP"), GC–GLD #F.fut_etf_corr.at("GC–GLD") and ZN–IEF #F.fut_etf_corr.at("ZN–IEF").

== ETF plots

#fig("fig08_etf_assets_cum_log.png")[Cumulative log returns of SPY, UUP, GLD and IEF (total return).]

#fig("fig09_etf_portfolio_cum_log.png")[ETF Inv-vol USD portfolio cumulative log returns (scaled to a 10% average annual endpoint for display).]

#fig("fig10_etf_portfolio_drawdown.png")[Ongoing drawdown of the ETF Inv-vol USD portfolio.]

#fig("fig11_etf_weights.png")[Actual daily ETF weights under quarterly rebalancing. *a*, SPY / UUP / GLD. *b*, SPY / IEF / GLD.]

Mean target weights: SPY #F.etf_mean_w.iv_usd.SPY / UUP #F.etf_mean_w.iv_usd.UUP / GLD #F.etf_mean_w.iv_usd.GLD.

#fig("fig12_etf_yearly_returns.png")[ETF Inv-vol USD calendar-year returns (teal = positive, salmon = negative; 2026 year-to-date).]

== Overlap comparison

#fig("fig13_compare_fut_etf.png")[Futures vs ETF Inv-vol USD cumulative log returns on the common window (each scaled to a 10% average annual endpoint).]

Overlap portfolio correlation ≈ #F.overlap_corr; annualized tracking error ≈ #pct(F.overlap_te).

== Metrics including ETF and overlap

#mtable(T.etf, [Inv-vol USD metrics: full futures sample, full ETF sample, and both on the common overlap. ETF Sharpe and Sortino are over 13-week T-bills; futures returns are already excess returns.])

// ---------------------------------------------------------------- 7
= Insights (replication)

+ SPY / UUP / GLD is a practical proxy for the research basket in a US cash brokerage account.
+ The weights rhyme: UUP plays the same low-vol role as DX (≈52% average weight).
+ Tracking is close but not perfect (≈2.5% annual TE). The gap reflects fees, futures roll vs ETF economics,
  and the fact that UUP is not pure DX spot.
+ On a like-for-like excess-return basis, the ETF book is somewhat weaker: Sharpe 0.84 vs 0.99 for the futures book
  on the same window. Its 6.5% total return includes ≈1.4% a year of T-bill yield, which leaves about 0.7 pp a
  year less excess return than futures. That gap is roughly in line with the ETFs' expense ratios (UUP and GLD are
  the expensive sleeves), and is the realistic cost of implementing the strategy with ETFs.

// ---------------------------------------------------------------- 8
= Comparison with a traditional portfolio

== Growth, unlevered and at equal risk

#fig("fig14_trad_growth.png")[Futures portfolios on their common window (#F.trad_fut_period). *a*, unlevered cumulative log returns. *b*, the same books scaled ex ante to a 10% volatility target at every rebalance (@sec-vt). Grey = ES alone.]

Unlevered (panel a), the fixed 60/30/10 portfolio ends highest of the three diversified books, but it carries
about twice the risk of the inverse-vol books. Scaled to the same risk (panel b), the order changes. Inv-vol USD
ends highest, followed by Inv-vol Trad, then 60/30/10, then equities alone. The path matters, though: Inv-vol Trad led
until about 2014 and stayed level with Inv-vol USD until 2021, and its shortfall is concentrated in the 2022 bond
sell-off.

== Drawdowns and calendar years

#fig("fig15_trad_drawdown.png")[Ongoing drawdown of the three futures portfolios and ES alone (grey).]

#fig("fig16_trad_yearly.png")[Calendar-year returns of the three futures portfolios; black ticks = ES alone. 2026 is year-to-date.]

Counting negative calendar years: Inv-vol USD #F.trad_yearly_neg.at("Inv-vol USD"), Inv-vol Trad
#F.trad_yearly_neg.at("Inv-vol Trad"), Fixed 60/30/10 #F.trad_yearly_neg.at("Fixed 60/30/10"), ES alone
#F.trad_yearly_neg.at("ES only"). Inv-vol Trad has many negative years, but they are small, except 2022 (−12%).

== Stress episodes

#mtable(T.stress, [Cumulative return during equity stress episodes (futures portfolios, peak-to-trough dates of the S&P 500).])

== Metrics

#mtable(T.trad_fut, [Traditional comparison, futures, #F.trad_fut_period. Turnover is per year at quarterly rebalancing.])

#mtable(T.trad_etf, [Traditional comparison, ETFs (SPY / UUP / GLD vs SPY / IEF / GLD), common window #F.trad_etf_period. Sharpe and Sortino over 13-week T-bills.])

== Same risk without hindsight: volatility targeting <sec-vt>

The unlevered books run at very different risk levels (≈6% vs ≈11% volatility), so their absolute returns
are not comparable. Here each futures book, and ES alone, is rescaled at every quarterly rebalance so that
its _ex-ante_ volatility hits 10%. The volatility is estimated from the trailing 252-day covariance and the new
target weights, and leverage is capped at 3×. Only past data are used, and futures make the leverage
straightforward because their returns are already excess of cash.

#mtable(T.voltarget, [Futures books scaled ex ante to 10% volatility, quarterly, 10 bp per unit traded, #F.trad_fut_period. Leverage = sum of notional weights at rebalance.])

Realised volatility comes out at ≈11–11.5%, slightly above target, because exposure is only reset quarterly. At
equal risk, Inv-vol USD returns 9.8% a year, against 6.9% for Inv-vol Trad, 6.0% for 60/30/10 and 5.0% for
equities alone. It also has the shallowest drawdown (−23%). The price is leverage: ≈2× on average and up to
2.9×, which brings margin, liquidity and model risk that a backtest does not capture. 60/30/10 barely needs
leverage (≈1.1×), so its absolute-return advantage disappears once risk is equalised.

== How robust is the ranking?

#mtable(T.subperiods, [Sharpe ratio (max drawdown in brackets) by sub-period, unlevered futures books.])

#fig("fig20_rolling_sharpe.png")[Rolling 3-year Sharpe ratio of the three unlevered futures books.]

The ranking is not stable over time. In 2001–2012, Inv-vol Trad had the best Sharpe (0.83 vs 0.57 for
Inv-vol USD), helped by Treasuries rallying in 2002 and 2008. In 2013–2021, Inv-vol USD and 60/30/10 were
roughly tied (0.95 vs 0.93). Only in 2022–2026 does Inv-vol USD pull clearly ahead (1.52 vs ≈0.5–0.65).
Leadership in the rolling 3-year Sharpe changes hands several times.

#mtable(T.bootstrap, [Moving-block bootstrap (63-day blocks, 2,000 resamples) of full-sample Sharpe differences between the unlevered futures books.])

Sampling noise is large relative to the differences. None of the 95% intervals excludes zero. Inv-vol USD has
the higher Sharpe in 94% of resamples against 60/30/10 and in 80% against Inv-vol Trad. The data are
consistent with the dollar book being better, but they do not establish it.

The result also leans on gold. Over the sample, gold futures had a Sharpe of
#calc.round(F.gc_sharpe, digits: 2) during a long bull market. The same inverse-vol rule without gold has a
Sharpe of only #calc.round(F.no_gold_sharpe.at("Inv-vol ES/DX"), digits: 2) for ES / DX and
#calc.round(F.no_gold_sharpe.at("Inv-vol ES/ZN"), digits: 2) for ES / ZN.


== Insights (traditional comparison)

+ *Drawdown control is the robust finding.* Both inverse-vol books lost less than 60/30/10 and equities in every
  stress episode, and their worst drawdowns (−11% and −19%) are a fraction of 60/30/10's −34%. This holds
  across sub-periods.
+ *Return per unit of risk favours the dollar book in this sample, but not conclusively.* Its full-sample Sharpe
  is the highest (0.87 vs 0.67 and 0.60 in futures; 0.84 vs 0.68 and 0.66 for ETFs over T-bills). The
  bootstrap intervals include zero, and the lead comes mainly from 2022–2026.
+ *At equal risk the dollar book compounds fastest, but only with ≈2× leverage.* 60/30/10's higher unlevered
  return reflects higher risk, not a better mix.
+ *The defensive asset decides which regime you are protected in.* Treasuries hedged the deflationary sell-offs
  (2002, 2008, 2020); the dollar hedged the 2022 inflation shock (Inv-vol USD +1.4% vs Inv-vol Trad −12.1% for
  the year). Neither hedge worked in every regime.
+ *Gold does much of the work in both inverse-vol books.* Without it, their Sharpe ratios fall to ≈0.35. Any
  forward-looking use of the strategy is partly a bet that gold keeps diversifying the way it did in 2001–2026.

// ---------------------------------------------------------------- 9
= Rebalancing frequency <sec-rebal>

#fig("fig17_rebalance_frequency.png")[Effect of rebalance frequency (M = monthly, Q = quarterly, 6M = semi-annual, A = annual) on futures portfolios over a common window. *a*, Sharpe. *b*, annual turnover (sum of |Δw|).]

#mtable(T.rebal, left-cols: 2, [Rebalance-frequency sensitivity, futures, common window #F.rebal_period, 10 bp per unit traded. \*Constant mix = monthly weights from the prior calendar year applied to daily log returns (implicit daily rebalancing, no costs).], size: 8.5pt)

+ *Frequency barely matters.* Across monthly to annual schedules, Sharpe moves by at most ≈0.06 and max drawdown
  by at most ≈2.5 pp for every portfolio. These differences are smaller than the estimation noise of a 25-year
  backtest.
+ *Costs are negligible at this turnover.* Quarterly rebalancing trades about 15–25% of the book a year, or
  1.5–2.5 bp a year at 10 bp per unit. Even at 50 bp per unit the drag would stay below 0.15 pp a year.
+ *Quarterly is a sensible default.* It cuts turnover by about a third relative to monthly for a loss of about 0.04
  Sharpe, keeps weights close to their inverse-vol targets (@sec-corr shows how fast correlations move),
  and is easy to operate by hand. Semi-annual is equally defensible for a taxable account where every
  sale may realise gains. Annual has the lowest turnover, but its inverse-vol targets can be up to a year stale.
+ *The constant-mix shortcut understates returns.* Averaging log returns ignores the compounding gain of a
  rebalanced mix, so it reports about 0.4–0.5 pp a year less than the drift-and-trade simulation, even after costs.

// ---------------------------------------------------------------- 10
= Equity sleeve: S&P 500 (CSPX) vs All-World (VWRD / VWCE)

== On their own

#fig("fig18_sleeves_standalone.png")[*a*, cumulative log returns (total return, USD) of CSPX, VWRD and US-listed SPY (grey) since #F.sleeve_period. *b*, trailing one-year log return of VWRD minus CSPX.]

#mtable(T.sleeve, [Equity sleeves on their own, #F.sleeve_period (daily, USD, total return; Sharpe and Sortino over 13-week T-bills).])

Over 2012–2026, the S&P 500 sleeve compounded about 2.9 pp a year faster than All-World at nearly identical
volatility and the same −34% COVID drawdown. All-World led on a trailing one-year basis only
#calc.round(F.sleeve_rel_share_positive * 100)% of the time (2017–18, early 2021, 2023, and 2025–26).
CSPX trails SPY by ≈0.3 pp a year, which reflects the fund fee and withholding tax on US dividends. Daily
volatilities differ slightly because the London close (16:30 UK) is not synchronous with the US close.

== Inside the portfolios

Each portfolio was rerun with the equity sleeve swapped (CSPX or VWRD; UUP / IEF / GLD unchanged),
quarterly rebalancing, common window #F.sleeve_port_period.

#fig("fig19_sleeves_in_portfolios.png")[Equity sleeve inside each portfolio. *a*, Sharpe over T-bills. *b*, max drawdown. Hatched = All-World (VWRD).]

#mtable(T.sleeve_ports, columns: (2.4cm,) + (1fr,) * 6, [Portfolio metrics with the S&P 500 (CSPX) vs All-World (VWRD) sleeve, #F.sleeve_port_period. Sharpe and Sortino over 13-week T-bills.], size: 7.5pt)

== Longer history: S&P 500 vs world equities, 2000–2026 <sec-world>

The UCITS comparison above covers a single decade of US leadership. To test whether the S&P 500's edge holds
across regimes, the world sleeve is replaced by the proxy described in Section 2.3, which runs back to 2000.
A constant 50% US weight is a simplification: the US share of world indices moved between roughly 45% and 65%
over the period, and 50% is the constant weight that tracks ACWI best. On weekly returns the proxy matches
ACWI with correlation #calc.round(F.world_check.ACWI.corr, digits: 3) and a return gap of
#pct(F.world_check.ACWI.gap) a year (#F.world_check.ACWI.period). Against VWRD it shows a correlation of
#calc.round(F.world_check.VWRD.corr, digits: 2) and a gap of #pct(F.world_check.VWRD.gap) a year; the lower
correlation reflects the asynchronous London close, not a level difference.

#fig("fig21_world_vs_sp500_long.png")[*a*, cumulative log total returns of the S&P 500 (SPY) and the world proxy, #F.world_period. *b*, trailing 3-year annualised log return of the world proxy minus the S&P 500.]

#mtable(T.world_eras, [S&P 500 vs world proxy on their own (USD, total return; Sharpe over 13-week T-bills). t = t-statistic of the mean weekly return difference.], size: 8.5pt)

Over the full 2000–2026 period, the S&P 500 finished ahead (8.3% vs 6.9% a year), but the difference is not
statistically significant (t = 1.38). The two eras point in opposite directions:

- *2000–2011:* the world proxy was ahead (1.3% vs 0.6% a year). On a trailing 3-year basis it led by up to
  ≈5–7% a year in 2004–2008, helped by emerging markets and a weak dollar.
- *2012–2026:* the S&P 500 led by 3.4% a year, and this is the only period where the gap is significant (t = 2.62).
  It is essentially the same result as CSPX vs VWRD above.

Overall the world proxy led on a 3-year basis #calc.round(F.world_rel3_share_positive * 100)% of the time.

To compare the sleeves inside the portfolios on the same footing as ES, each equity sleeve enters the futures
books as its total return in excess of T-bills, with DX, ZN and GC unchanged (#F.world_port_period).

#fig("fig22_world_sleeve_in_portfolios.png")[Sharpe ratio of each futures book with the S&P 500 or the world equity sleeve. *a*, 2001–2011 (the books start in October 2001). *b*, 2012–2026. Hatched = world sleeve.]

#mtable(T.world_ports, left-cols: 2, [Futures books with the S&P 500 vs world equity sleeve (equity as excess return over T-bills), by period. The books start in October 2001, so the first period covers 2001-10 to 2011.], size: 8pt)

Inside the portfolios the pattern is the same and smaller. The world sleeve gave the higher Sharpe in every
book in 2001–2011, and the S&P 500 sleeve did so in every book in 2012–2026. Over the full period, Inv-vol USD
has a Sharpe of 0.87 with the S&P 500 and 0.86 with the world sleeve. The block-bootstrap difference is
#num(F.world_boot.iv_usd.diff), with a 95% interval of
[#num(F.world_boot.iv_usd.lo), #num(F.world_boot.iv_usd.hi)]. The
return cost of the world sleeve in that book was ≈0.2 pp a year (4.94% vs 4.74%).

== Insights (equity sleeve)

+ *In 2012–2026 the S&P 500 is better everywhere, and significantly so.* CSPX beat VWRD by ≈2.6 pp a year
  (weekly t ≈ 2.4), with the same volatility and drawdown, and gave a higher Sharpe in every portfolio.
+ *That edge belongs to one era.* On the 2000–2026 record the S&P 500 is still ahead, but not significantly,
  and in 2000–2011 a world portfolio did better, both on its own and inside every book.
+ *Inverse-vol makes the choice small.* With the equity sleeve at ≈25% weight, the S&P-vs-world gap inside
  Inv-vol USD was ≈0.8 pp a year in 2012–2026 and ≈0.2 pp a year over 2001–2026, with essentially equal Sharpe.
  In the 60%-equity fixed portfolio the choice matters about three times as much.
+ *Practical choice.* The data do not identify a clear winner across regimes. CSPX is the better sleeve if
  US leadership continues, as it has since 2012. VWCE gives up that upside in exchange for not depending on it,
  and it would have been the better choice in 2000–2011. Inside the inverse-vol book the long-run difference
  is small, so this is best treated as an explicit view on US leadership, not as a result of the backtest. It
  also matters far less than the choice of defensive asset (Section 8).

// ---------------------------------------------------------------- 11
= Conclusions

A walk-forward inverse-volatility mix of equities, the US dollar and gold is much smoother than any single
sleeve. Over 2001–2026 its worst drawdown was −11%, against −34% for a fixed 60/30/10 portfolio and −57% for
equities. It also came out ahead of a Treasury-based inverse-vol basket and of 60/30/10 on return per unit of
risk, and it compounded fastest when all books were scaled ex ante to the same 10% volatility.

That ranking is suggestive rather than established. The Sharpe differences are within bootstrap noise, the
Treasury version led in 2001–2012, much of the dollar book's edge comes from the 2022 inflation shock, and both
inverse-vol books depend heavily on gold's long bull market. The safer reading is that inverse-vol weighting
on these assets reliably cuts drawdowns. Which defensive asset works best depends on whether the next crisis
is deflationary (Treasuries) or inflationary (the dollar).

The ETF implementation tracks the futures book closely but gives up about 0.7 pp a year of excess return to
fees and tracking. The rebalancing schedule is a second-order choice; quarterly is a practical default. Among
UCITS equity sleeves, the S&P 500 won the 2012–2026 backtest, but inside the inverse-vol book the difference is
small. A 2000–2026 test with a world-equity proxy shows that the S&P 500's lead is specific to that era. The
world sleeve led in 2000–2011, and over the full period the two sleeves give the same Sharpe inside the
inverse-vol book. Choosing between CSPX and VWCE is therefore a view on continued US leadership, not something
the backtest settles.

Caveats: Yahoo data limitations (DX via DX-Y.NYB, non-back-adjusted continuous futures, no futures roll costs);
futures Sharpe ratios use $r_f = 0$ because their returns are already excess of cash, while ETF and UCITS ratios
are over 13-week T-bills; the volatility-targeted books assume frictionless leverage up to 3×; the sample covers
only the final leg of the 2000–02 dot-com crash; the defensive sleeves use US-listed ETFs (a European investor would need UCITS
equivalents, for example a 7–10y Treasury UCITS ETF and a physical gold ETC, and has no direct UUP equivalent);
and there are no taxes. This is an educational backtest, not a trading recommendation.

// ---------------------------------------------------------------- 12
= Appendix: code and reproducibility

All results, tables and figures in this report are produced by the `ivoverlay` Python package in the
repository #link("https://github.com/lwang-genomics/inverse-vol-futures-overlay")[lwang-genomics/inverse-vol-futures-overlay]:

- `uv run ivoverlay` downloads the prices (cached in `data/`), runs every backtest and robustness check, and
  writes `results/results.json`, `results/metrics.md` and `figures/`. `uv run ivoverlay-report` compiles this PDF.
- `src/ivoverlay/backtest.py` holds the walk-forward engine (drifting weights, costs, ex-ante volatility
  targeting). The `stats` and `metrics` modules hold the block bootstrap and the performance metrics.
- The unit tests (`uv run pytest`) check the engine on synthetic data: weights, the quarterly calendar, agreement
  with an explicit buy-and-hold simulation, cost accounting, the volatility target and leverage cap, and the
  absence of look-ahead. That last test changes all returns after a cut-off date and asserts that no weight
  or return up to the cut-off changes.
