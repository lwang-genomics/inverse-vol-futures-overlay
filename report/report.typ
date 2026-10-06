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

// Figure set used in this PDF: "report/" = figures sized for the page (default); "" = the slide versions
// shown in the README (the previous layout of this report).
#let figset = "report/"
#let fig(path, caption, label: none) = [#figure(image("../figures/" + figset + path, width: 100%), caption: caption) #label]

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
  #v(0.5em)
  #text(size: 10pt, fill: luma(110))[Liangxi Wang · data through #F.end_date · October 2026 \
    #link("https://github.com/lwang-genomics/inverse-vol-futures-overlay")[github.com/lwang-genomics/inverse-vol-futures-overlay]]
]
#v(0.8em)
#block(inset: (x: 1.2em), [
  #text(weight: "bold")[Abstract.] A walk-forward study of long-only inverse-volatility portfolios built from
  back-adjusted futures (S&P 500, the US dollar or 10-year Treasuries, and gold) and from their ETF proxies,
  October 2001 to October 2026. Weights come from the trailing year and are reset quarterly, trades pay 10 bp, and
  a futures overlay can scale each book to 10% ex-ante volatility. The robust finding is the drawdown profile: the
  inverse-vol books lost less than a fixed 60/30/10 portfolio and than equities in every stress episode. Which
  defensive asset is better depends on the period: Treasuries over the full sample (Sharpe 0.75 vs 0.68 for the
  dollar book), the dollar since 2022, and no difference is statistically significant. Using unadjusted
  front-month futures, as is common with free data, would have reversed this ranking. The ETF version tracks the
  futures book closely, rebalancing frequency is a second-order choice, and the S&P 500 sleeve's lead over an
  All-World sleeve belongs to the period after 2012.
])
#v(0.2em)
#figure(image("../figures/" + figset + "fig14_trad_growth.png", width: 84%),
  caption: [Inverse-vol books and a fixed 60/30/10 portfolio, unlevered (a) and scaled to 10% ex-ante volatility (b). Grey: S&P 500 futures alone.])
#figure(image("../figures/" + figset + "fig15_trad_drawdown.png", width: 84%),
  caption: [Drawdowns of the same unlevered books: the inverse-vol books lost less in every stress episode.])
#pagebreak()
#outline(depth: 2, indent: auto)

// ---------------------------------------------------------------- 1
= Key results

The study runs a long-only inverse-volatility rule on three futures sleeves (equity ES, US dollar DX, gold GC)
and asks four questions: can it be replicated with ETFs (SPY, UUP, GLD); how does it compare with a traditional
basket holding 10-year Treasuries instead of the dollar (ES / ZN / GC), run with the same rule and as a fixed
60/30/10 allocation; how do the correlations behind each basket evolve; and, for a European investor, which
UCITS equity sleeve works better, an S&P 500 ETF (CSPX) or the FTSE All-World ETF (VWRD, the same fund as VWCE)?

- *The robust finding is the drawdown profile.* Both inverse-vol books lost less than 60/30/10 and equities in
  every stress episode. Their worst drawdowns were −13% (dollar book) and −17% (Treasury book), against −34% for
  60/30/10 and −58% for equities.
- *Performance.* Inverse-vol on ES / ZN / GC has the best full-sample Sharpe ratio (0.75, 4.6% a year at 6.2%
  volatility), ahead of the dollar book (0.68) and 60/30/10 (0.62). Scaled to the same 10% volatility, the Treasury
  and dollar books compound at 7.9% and 7.5% a year (about 1.8× leverage), against 6.1% for 60/30/10.
- *The ranking depends on the period.* Treasuries led in 2001–2012 (Sharpe 1.04 vs 0.35), the dollar in
  2022–2026 (1.09 vs 0.27), when bonds fell with equities. Every block-bootstrap 95% interval for the Sharpe
  differences includes zero.
- *Data matter.* On Yahoo's unadjusted front-month futures the dollar book looked best (0.87 vs 0.63). Unadjusted
  series miss each future's carry: they overstate gold by about 2% a year and erase most of the Treasury future's
  return (@sec-datacheck).
- *Implementation.* The ETF version tracks the futures book closely (weekly correlation 0.90; Sharpe 0.84 over
  T-bills). Quarterly rebalancing cuts turnover by a third relative to monthly, and Sharpe moves by at most 0.04.
- *Equity sleeve.* On 2012–2026 the S&P 500 sleeve beat the All-World sleeve on its own and inside every
  portfolio. A 2000–2026 test with a world-equity proxy shows the lead belongs to one era: the world sleeve led in
  2000–2011, and inside the inverse-vol book the two are indistinguishable over the full period (Sharpe 0.68 vs
  0.66).

// ---------------------------------------------------------------- 2
= Data and universe

== Futures basket

Futures returns must not count a roll's price gap as a return, and they must include carry. They are built from
daily *back-adjusted* futures from the open-source pysystemtrade project, pinned to one commit: the change of the
back-adjusted price over the actual price of the contract held. These free data end on 28 March 2024; from then on
each leg continues with the excess return over T-bills of a total-return ETF on the same asset (SPY, UUP, GLD,
IEF). On 2008–2024 those ETF excess returns track the futures with weekly correlations of 0.89–0.98 and annual
return gaps of 0.4–1.3% (largest for UUP, whose fees make the splice slightly conservative for the dollar book).
The futures histories start where Yahoo's do (August–September 2000), so the study windows are unchanged.

#text(size: 9pt, table(
  columns: 3, stroke: none, inset: (x: 5pt, y: 3pt),
  table.hline(stroke: 0.8pt),
  table.header([*Label*], [*Futures (to March 2024)*], [*ETF excess return (after)*]),
  table.hline(stroke: 0.5pt),
  [ES], [E-mini S&P 500], [SPY],
  [DX], [ICE US Dollar Index futures (carry included)], [UUP],
  [GC], [COMEX gold], [GLD],
  [ZN], [CBOT 10-year T-note (traditional basket)], [IEF],
  table.hline(stroke: 0.8pt),
))

Within each basket, series are forward-filled and rows with remaining gaps are dropped. Futures returns are
_excess_ returns (no collateral yield), which holds for every futures portfolio here alike. ETF and other prices
are daily adjusted closes from Yahoo Finance from 2000-01-01.

== Unadjusted vs back-adjusted futures <sec-datacheck>

#let DC = F.data_check
#let gap(c) = DC.at(c).ret_adj - DC.at(c).ret_yahoo
#let sp(x) = {
  let v = str(calc.round(calc.abs(x) * 100, digits: 1))
  (if x < 0 { "−" } else { "+" }) + (if v.contains(".") { v } else { v + ".0" }) + "%"
}
#let wp(book, c) = str(int(calc.round(DC.at(book).weights.at(c) * 100))) + "%"

Free continuous futures, such as Yahoo's, splice the front contract to the next at each expiry without
adjustment, so every roll's price gap is counted as a return. @tbl-datacheck compares them with the back-adjusted
series over #DC.period. Volatilities are the same, but returns are not, and the ranking of the two books
reverses. The difference is not noise: it is the carry of each leg.

#mtable(T.data_check, [Yahoo's unadjusted front-month futures vs back-adjusted futures, #DC.period (before the ETF splice). Unlevered books, same rules. Futures returns are excess of cash.], size: 8.5pt) <tbl-datacheck>

*Why the gap is the carry.* A future trades away from spot by its cost of carry and converges to spot as it
approaches expiry; the holder earns that convergence. Rolling into the next contract restores the gap, and an
unadjusted series books the jump as a return, which cancels the convergence. The unadjusted series therefore
tracks the spot price, while the back-adjusted series gives the futures' excess return:
$ r_"adjusted" - r_"unadjusted" approx "carry" = y - r_f, $
where $y$ is what the asset yields (coupon, dividend, foreign interest rate or gold lease rate) and $r_f$ is the
financing rate. Its sign differs across the four legs (annual return gaps, adjusted minus Yahoo):

- *Gold (GC), #sp(gap("GC")).* Gold yields almost nothing, so its carry is about minus the financing rate. The gap
  is a little larger than the average T-bill rate (#pct(DC.tbill)), because gold forwards are priced off bank
  funding rates, which sit above T-bills. Yahoo overstates gold.
- *10-year Treasury (ZN), #sp(gap("ZN")).* The bond's yield exceeds the short-term financing rate and it rolls
  down an upward-sloping curve, so carry is positive and the next contract trades lower. Each quarterly roll shows
  up as a loss, and Yahoo's series earns almost nothing.
- *Dollar index (DX), #sp(gap("DX")).* Carry is the US interest rate minus the rates of the currency
  basket (57% euro). Its sign changed several times over the sample, so the net gap is small.
- *S&P 500 (ES), #sp(gap("ES")).* Dividends roughly offset the financing rate.

*Why the books move in opposite directions.* Both books hold ES and GC; they differ in the defensive asset, to
which inverse-vol weighting gives about half the book. Weighting each leg's gap by the book's average weights
predicts the change in the book's return:

- *Dollar book* (DX #wp("iv_usd", "DX"), GC #wp("iv_usd", "GC"), ES #wp("iv_usd", "ES")): predicted
  #sp(DC.iv_usd.ret_gap_from_legs) a year, observed #sp(DC.iv_usd.ret_gap). Sharpe
  #num(DC.iv_usd.sr_yahoo) → #num(DC.iv_usd.sr_adj).
- *Treasury book* (ZN #wp("iv_trad", "ZN"), GC #wp("iv_trad", "GC"), ES #wp("iv_trad", "ES")): predicted
  #sp(DC.iv_trad.ret_gap_from_legs) a year, observed #sp(DC.iv_trad.ret_gap). Sharpe
  #num(DC.iv_trad.sr_yahoo) → #num(DC.iv_trad.sr_adj).

The two errors in Yahoo's data favour the same book. Gold, which the dollar book depends on more
(@sec-robust), is overstated, and the Treasury future's carry is removed. The same bias affects any unadjusted
continuous series: assets with positive carry (bonds, high-yielding currencies held long) look worse than they
are, and assets that cost money to hold (gold, commodities in contango) look better.


== ETF proxy basket

#text(size: 9pt, table(
  columns: 3, stroke: none, inset: (x: 5pt, y: 3pt),
  table.hline(stroke: 0.8pt),
  table.header([*ETF*], [*Maps to*], [*Notes*]),
  table.hline(stroke: 0.5pt),
  [SPY], [ES], [S&P 500 ETF; weekly corr with ES #F.fut_etf_corr.at("ES–SPY")],
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

Gold and equities earned similar excess returns (about 8% a year), gold with less volatility. The dollar future
lost slightly (−0.7% a year), because holding it paid the interest-rate differential for much of the period, and
the 10-year note future gains steadily until 2020, then gives much of that back in the 2022 rate shock.

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

#fig("fig05_rolling_corr.png")[52-week rolling pairwise correlations of weekly log returns (the futures settle at different times of day, which dilutes daily correlations). *a*, assets of the Inv-vol USD basket. *b*, assets of the traditional basket. ES–GC appears in both panels.]

#fig("fig06_corr_regimes.png")[Weekly correlation by regime for every asset pair in the two baskets (blue = diversifying, red = moving together).]

The two baskets diversify in different ways:

- *Dollar basket.* The defensive pair DX–GC is persistently and strongly negative: about
  #F.roll_corr_mean.at("DX–GC") on average, and between −0.33 and −0.56 in every regime. Dollar and gold offset
  each other, which is why the book's volatility (≈6%) sits far below that of any sleeve. ES–DX changed sign: it
  was slightly positive in 2001–07 and negative (−0.23 to −0.37) in every regime since, the dollar acting as a
  safe haven.
- *Traditional basket.* ES–ZN was the classic hedge, between −0.18 and −0.45 in every regime up to 2021. In 2022 it
  flipped positive (+0.15 in the regime, +#F.roll_corr_last.at("ES–ZN") on the latest 1-year window). ZN–GC is
  _positive_ in every regime (+0.09 to +0.39): bonds and gold both respond to real yields, so they hedge each
  other poorly.
- Today all three traditional pairs are positive (+#F.roll_corr_last.at("ES–ZN") to
  +#F.roll_corr_last.at("ZN–GC")), so the traditional basket is at a low point of internal diversification, while
  the dollar basket still has two negative pairs.

== Calendar-year returns

#fig("fig07_fut_yearly_returns.png")[Calendar-year simple returns of the Inv-vol USD futures portfolio, $exp(sum_"year" r_t) - 1$. Teal = positive, salmon = negative. 2026 is year-to-date.]

== Performance table (futures full sample)

#mtable(T.fut, [Futures full-sample metrics on the walk-forward window (quarterly rebalancing, 10 bp costs). Futures returns are excess of cash, so Sharpe uses $r_f = 0$.])

// ---------------------------------------------------------------- 5
= Insights (futures)

+ *Risk-adjusted performance is the story.* Absolute return (≈4.1% a year) trails ES and GC, but volatility
  (6.0%) and max drawdown (−13%) are far better, and Sharpe, Sortino and Calmar lead the table.
+ *Inverse-vol concentrates in DX.* Low dollar volatility mechanically pulls about half of the weight, so the
  dollar's carry matters: with a spot dollar index (no carry) the book's Sharpe would look higher (@sec-datacheck).
+ *Diversification is real but regime-dependent.* The dollar–gold offset is the stable ingredient; the
  equity–dollar and equity–bond correlations are not (@sec-corr).
+ *Implementation costs are small.* Quarterly rebalancing trades about 24% of the book a year, so costs come
  to only ≈2.4 bp a year (@sec-rebal).

// ---------------------------------------------------------------- 6
= ETF replication (SPY / UUP / GLD)

== Mapping and sample

UUP's history shortens the ETF experiment: walk-forward OOS runs #F.etf_period. On overlapping weekly
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

Overlap portfolio correlation (weekly) ≈ #F.overlap_corr, annualized tracking error ≈ #pct(F.overlap_te).

== Metrics including ETF and overlap

#mtable(T.etf, [Inv-vol USD metrics: full futures sample, full ETF sample, and both on the common overlap. ETF Sharpe and Sortino are over 13-week T-bills; futures returns are already excess returns.])

// ---------------------------------------------------------------- 7
= Insights (replication)

+ SPY / UUP / GLD is a practical proxy for the research basket in a US cash brokerage account.
+ The weights rhyme: UUP plays the same low-vol role as DX (≈52% average weight).
+ Tracking is close but not perfect (≈2.3% annual tracking error on weekly returns). The gap reflects fees,
  futures financing vs T-bill yields, and the different maturity of IEF and the 10-year note.
+ On a like-for-like excess-return basis the two are about equal: Sharpe 0.84 for the ETF book over T-bills and
  0.81 for the futures book on the same window. The ETFs' expense ratios (UUP and GLD are the expensive sleeves)
  are offset by the futures' financing, which costs a little more than T-bills, so ETFs are a fair way to implement
  the strategy.

// ---------------------------------------------------------------- 8
= Comparison with a traditional portfolio

== Growth, unlevered and at equal risk

#fig("fig14_trad_growth.png")[Futures portfolios on their common window (#F.trad_fut_period). *a*, unlevered cumulative log returns. *b*, the same books scaled ex ante to a 10% volatility target at every rebalance (@sec-vt). Grey = ES alone.]

Unlevered (panel a), the fixed 60/30/10 portfolio ends highest of the three diversified books, but it carries
about twice the risk of the inverse-vol books. Scaled to the same risk (panel b), the inverse-vol books end ahead of
60/30/10 and of equities alone. The path matters: Inv-vol Trad led clearly until 2021, and the dollar book closed
most of the gap only in the 2022 bond sell-off.

== Drawdowns and calendar years

#fig("fig15_trad_drawdown.png")[Ongoing drawdown of the three futures portfolios and ES alone (grey).]

#fig("fig16_trad_yearly.png")[Calendar-year returns of the three futures portfolios; black ticks = ES alone. 2026 is year-to-date.]

Counting negative calendar years: Inv-vol USD #F.trad_yearly_neg.at("Inv-vol USD"), Inv-vol Trad
#F.trad_yearly_neg.at("Inv-vol Trad"), Fixed 60/30/10 #F.trad_yearly_neg.at("Fixed 60/30/10"), ES alone
#F.trad_yearly_neg.at("ES only"). Inv-vol Trad's negative years are small, except 2022 (−12%).

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
equal risk, Inv-vol Trad returns 7.9% a year and Inv-vol USD 7.5%, against 6.1% for 60/30/10 and 4.7% for
equities alone. The dollar book has the shallowest drawdown (−20%, against −28% to −31% for the others). The price
is leverage: about 1.8× on average and up to 3×, which brings margin, liquidity and model risk that a backtest does
not capture. 60/30/10 barely needs leverage (≈1.1×), so its absolute-return advantage disappears once risk is
equalised.

== How robust is the ranking? <sec-robust>

#mtable(T.subperiods, [Sharpe ratio (max drawdown in brackets) by sub-period, unlevered futures books.])

#fig("fig20_rolling_sharpe.png")[Rolling 3-year Sharpe ratio of the three unlevered futures books.]

The ranking is not stable over time. In 2001–2012, Inv-vol Trad had by far the best Sharpe (1.04 vs 0.35 for
Inv-vol USD), helped by Treasuries rallying in 2002 and 2008. In 2013–2021, 60/30/10 led (1.07, against 0.89 and
0.74). In 2022–2026, Inv-vol USD pulled clearly ahead (1.09 vs 0.27–0.43). Leadership in the rolling 3-year
Sharpe changes hands several times.

#mtable(T.bootstrap, [Moving-block bootstrap (63-day blocks, 2,000 resamples) of full-sample Sharpe differences between the unlevered futures books.])

Sampling noise is large relative to the differences. None of the 95% intervals excludes zero. Inv-vol Trad has
the higher Sharpe in 82% of resamples against 60/30/10 and in 70% against Inv-vol USD. The data lean towards the
Treasury book over the full sample, but they do not establish a winner.

The dollar book leans on gold. Over the sample, gold futures had a Sharpe of
#calc.round(F.gc_sharpe, digits: 2) during a long bull market. The same inverse-vol rule without gold has a
Sharpe of only #calc.round(F.no_gold_sharpe.at("Inv-vol ES/DX"), digits: 2) for ES / DX, but
#calc.round(F.no_gold_sharpe.at("Inv-vol ES/ZN"), digits: 2) for ES / ZN: Treasuries diversify equities on their
own, the dollar much less so.


== Insights (traditional comparison)

+ *Drawdown control is the robust finding.* Both inverse-vol books lost less than 60/30/10 and equities in every
  stress episode, and their worst drawdowns (−13% and −17%) are a fraction of 60/30/10's −34%. This holds
  across sub-periods.
+ *Neither defensive asset wins conclusively.* Over the full futures sample the Treasury book has the higher
  Sharpe (0.75 vs 0.68; 60/30/10 0.62); on the shorter ETF window (2008–2026), which is dominated by 2022–2026, the
  dollar book does (0.84 vs 0.68 over T-bills). The bootstrap intervals include zero.
+ *At equal risk both inverse-vol books beat 60/30/10, with ≈1.8× leverage.* 60/30/10's higher unlevered return
  reflects higher risk, not a better mix.
+ *The defensive asset decides which regime you are protected in.* Treasuries hedged the deflationary sell-offs
  (2002, 2008); the dollar hedged the 2022 inflation shock (Inv-vol USD +1.8% vs Inv-vol Trad −12.4% for the
  year). Neither hedge worked in every regime.
+ *Gold matters most for the dollar book.* Without gold its Sharpe falls to ≈0.32; the Treasury book keeps 0.60.
  Any forward-looking use of the dollar version is partly a bet that gold keeps diversifying the way it did in
  2001–2026.

// ---------------------------------------------------------------- 9
= Rebalancing frequency <sec-rebal>

#fig("fig17_rebalance_frequency.png")[Effect of rebalance frequency (M = monthly, Q = quarterly, 6M = semi-annual, A = annual) on futures portfolios over a common window. *a*, Sharpe. *b*, annual turnover (sum of |Δw|).]

#mtable(T.rebal, left-cols: 2, [Rebalance-frequency sensitivity, futures, common window #F.rebal_period, 10 bp per unit traded. \*Constant mix = monthly weights from the prior calendar year applied to daily log returns (implicit daily rebalancing, no costs).], size: 8.5pt)

+ *Frequency barely matters.* Across monthly to annual schedules, Sharpe moves by at most ≈0.06 and max drawdown
  by at most ≈3 pp for every portfolio. These differences are smaller than the estimation noise of a 25-year
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
has a Sharpe of 0.68 with the S&P 500 and 0.66 with the world sleeve. The block-bootstrap difference is
#num(F.world_boot.iv_usd.diff), with a 95% interval of
[#num(F.world_boot.iv_usd.lo), #num(F.world_boot.iv_usd.hi)]. The
return cost of the world sleeve in that book was ≈0.2 pp a year (4.10% vs 3.92%).

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

A walk-forward inverse-volatility mix of equities, a defensive asset and gold is much smoother than any single
sleeve. Over 2001–2026 the worst drawdowns were −13% (dollar) and −17% (Treasuries), against −34% for a fixed
60/30/10 portfolio and −58% for equities. Both inverse-vol books also beat 60/30/10 on return per unit of risk, and
when all books were scaled ex ante to the same 10% volatility.

Which defensive asset is better is not settled. Over the full sample the Treasury book has the higher Sharpe; it
led by a wide margin in 2001–2012, and the dollar book led in 2022–2026. The differences are within bootstrap
noise, and the dollar book depends heavily on gold's long bull market. The safer reading is that inverse-vol
weighting on these assets reliably cuts drawdowns, and that the choice of defensive asset is a view on whether
the next crisis is deflationary (Treasuries) or inflationary (the dollar). The data treatment matters as much
as that view: on unadjusted front-month futures, the dollar book would have looked best.

The ETF implementation tracks the futures book closely, with about the same excess return. The rebalancing schedule is a second-order choice; quarterly is a practical default. Among
UCITS equity sleeves, the S&P 500 won the 2012–2026 backtest, but inside the inverse-vol book the difference is
small. A 2000–2026 test with a world-equity proxy shows that the S&P 500's lead is specific to that era. The
world sleeve led in 2000–2011, and over the full period the two sleeves give the same Sharpe inside the
inverse-vol book. Choosing between CSPX and VWCE is therefore a view on continued US leadership, not something
the backtest settles.

Caveats: futures are back-adjusted only to March 2024 and continue with ETF excess returns after that; roll
transaction costs are not modelled;
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
