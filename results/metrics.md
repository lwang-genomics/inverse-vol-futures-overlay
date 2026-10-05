# Performance tables

Data through 2026-10-02; rebalancing every 3 months, 10 bp per unit traded. Futures Sharpe uses rf = 0 (excess returns); ETF/UCITS Sharpe is over 13-week T-bills.

## fut

| Metric | ES | DX | GC | Inv-vol USD |
| --- | ---: | ---: | ---: | ---: |
| Avg annual return | 8.33% | −0.43% | 11.16% | 4.97% |
| Avg annual vol | 19.03% | 7.58% | 18.03% | 5.70% |
| Skewness | −0.30 | −0.04 | −0.49 | −0.46 |
| Kurtosis (excess) | 13.25 | 1.80 | 6.16 | 5.25 |
| Downside vol | 13.74% | 5.39% | 12.94% | 4.05% |
| Max drawdown | −57.11% | −40.68% | −44.36% | −11.24% |
| Sharpe | 0.44 | −0.06 | 0.62 | 0.87 |
| Sortino | 0.61 | −0.08 | 0.86 | 1.23 |
| Calmar | 0.15 | −0.01 | 0.25 | 0.44 |
| Turnover / yr | – | – | – | 24.45% |

## etf

| Metric | Fut full | ETF full | Fut overlap | ETF overlap |
| --- | ---: | ---: | ---: | ---: |
| Avg annual return | 4.97% | 6.45% | 5.76% | 6.46% |
| Avg annual vol | 5.70% | 5.93% | 5.81% | 5.92% |
| Max drawdown | −11.24% | −9.13% | −8.51% | −9.13% |
| Sharpe | 0.87 | 0.84 | 0.99 | 0.84 |
| Sortino | 1.23 | 1.18 | 1.40 | 1.18 |
| Calmar | 0.44 | 0.71 | 0.68 | 0.71 |

## trad_fut

| Metric | Inv-vol USD | Inv-vol Trad | Fixed 60/30/10 | ES only |
| --- | ---: | ---: | ---: | ---: |
| Avg annual return | 4.97% | 4.17% | 6.53% | 8.33% |
| Avg annual vol | 5.70% | 6.19% | 10.98% | 19.03% |
| Skewness | −0.46 | −0.30 | −0.27 | −0.30 |
| Kurtosis (excess) | 5.25 | 4.02 | 9.40 | 13.25 |
| Downside vol | 4.05% | 4.40% | 7.85% | 13.74% |
| Max drawdown | −11.24% | −18.93% | −34.42% | −57.11% |
| Sharpe | 0.87 | 0.67 | 0.60 | 0.44 |
| Sortino | 1.23 | 0.95 | 0.83 | 0.61 |
| Calmar | 0.44 | 0.22 | 0.19 | 0.15 |
| Turnover / yr | 24.45% | 22.27% | 15.01% | – |

## trad_etf

| Metric | Inv-vol USD | Inv-vol Trad | Fixed 60/30/10 | SPY only |
| --- | ---: | ---: | ---: | ---: |
| Avg annual return | 6.45% | 6.18% | 8.96% | 11.29% |
| Avg annual vol | 5.93% | 6.91% | 11.35% | 19.74% |
| Skewness | −0.55 | −0.07 | −0.16 | −0.29 |
| Kurtosis (excess) | 10.35 | 4.76 | 10.55 | 14.18 |
| Downside vol | 4.19% | 4.79% | 8.04% | 14.22% |
| Max drawdown | −9.13% | −18.32% | −31.65% | −51.87% |
| Sharpe | 0.84 | 0.68 | 0.66 | 0.49 |
| Sortino | 1.18 | 0.97 | 0.92 | 0.68 |
| Calmar | 0.71 | 0.34 | 0.28 | 0.22 |
| Turnover / yr | 25.02% | 23.31% | 15.05% | – |

## voltarget

| Metric | Inv-vol USD | Inv-vol Trad | Fixed 60/30/10 | ES only |
| --- | ---: | ---: | ---: | ---: |
| Avg annual return | 9.83% | 6.94% | 5.96% | 4.98% |
| Avg annual vol | 11.25% | 10.98% | 11.51% | 11.50% |
| Max drawdown | −22.76% | −30.11% | −26.98% | −28.44% |
| Sharpe | 0.87 | 0.63 | 0.52 | 0.43 |
| Sortino | 1.22 | 0.87 | 0.71 | 0.59 |
| Calmar | 0.43 | 0.23 | 0.22 | 0.18 |
| Turnover / yr | 87.66% | 74.67% | 57.97% | 32.46% |
| Avg leverage | 1.96× | 1.84× | 1.09× | 0.67× |
| Max leverage | 2.92× | 3.00× | 2.75× | 1.58× |

## stress

| Episode (futures) | Inv-vol USD | Inv-vol Trad | Fixed 60/30/10 | ES only |
| --- | ---: | ---: | ---: | ---: |
| 2002 dot-com bear (final leg) | −7.22% | 2.24% | −16.25% | −32.28% |
| 2007–09 GFC | −2.46% | −2.45% | −34.24% | −57.11% |
| 2018 Q4 sell-off | −1.65% | −0.78% | −10.91% | −20.19% |
| 2020 COVID crash | −5.83% | −4.65% | −19.47% | −34.45% |
| 2022 rate shock | 1.95% | −15.06% | −19.90% | −25.02% |
| 2025 tariff shock | −6.21% | −2.73% | −10.51% | −18.54% |

## subperiods

| Period | Inv-vol USD | Inv-vol Trad | Fixed 60/30/10 | ES only |
| --- | ---: | ---: | ---: | ---: |
| 2001–2012 | 0.57 (−11.24%) | 0.83 (−16.15%) | 0.37 (−34.42%) | 0.13 (−57.11%) |
| 2013–2021 | 0.95 (−8.51%) | 0.56 (−7.64%) | 0.93 (−19.47%) | 0.86 (−34.45%) |
| 2022–2026 | 1.52 (−6.46%) | 0.53 (−16.18%) | 0.65 (−20.12%) | 0.63 (−25.02%) |

## bootstrap

| Sharpe difference (futures) | Point · estimate | 95% · interval | Share of · resamples > 0 |
| --- | ---: | ---: | ---: |
| Inv-vol USD − Inv-vol Trad | 0.20 | [−0.23, 0.57] | 80% |
| Inv-vol USD − Fixed 60/30/10 | 0.28 | [−0.07, 0.63] | 94% |
| Inv-vol Trad − Fixed 60/30/10 | 0.08 | [−0.23, 0.45] | 72% |

## rebal

| Portfolio | Rebalance | Ann. · return | Ann. · vol | Max DD | Sharpe | Turnover · / yr | Cost · / yr |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Inv-vol USD | Monthly | 5.11% | 5.62% | −11.21% | 0.91 | 36.60% | 3.7 bp |
| Inv-vol USD | Quarterly | 4.95% | 5.71% | −11.24% | 0.87 | 24.45% | 2.4 bp |
| Inv-vol USD | Semi-annual | 4.96% | 5.79% | −10.90% | 0.86 | 20.90% | 2.1 bp |
| Inv-vol USD | Annual | 5.01% | 5.90% | −10.07% | 0.85 | 16.40% | 1.6 bp |
| Inv-vol USD | Constant mix* | 4.51% | 5.69% | −11.77% | 0.79 | – | 0 bp |
| Inv-vol Trad | Monthly | 4.37% | 6.12% | −18.40% | 0.71 | 30.94% | 3.1 bp |
| Inv-vol Trad | Quarterly | 4.28% | 6.19% | −18.93% | 0.69 | 22.27% | 2.2 bp |
| Inv-vol Trad | Semi-annual | 4.31% | 6.27% | −18.93% | 0.69 | 18.81% | 1.9 bp |
| Inv-vol Trad | Annual | 4.52% | 6.35% | −18.67% | 0.71 | 14.74% | 1.5 bp |
| Fixed 60/30/10 | Monthly | 6.30% | 11.09% | −35.19% | 0.57 | 23.71% | 2.4 bp |
| Fixed 60/30/10 | Quarterly | 6.41% | 10.98% | −34.42% | 0.58 | 15.01% | 1.5 bp |
| Fixed 60/30/10 | Semi-annual | 6.36% | 10.84% | −33.83% | 0.59 | 10.49% | 1.0 bp |
| Fixed 60/30/10 | Annual | 6.52% | 10.70% | −32.84% | 0.61 | 7.86% | 0.8 bp |

## sleeve

| Metric | CSPX | VWRD | SPY |
| --- | ---: | ---: | ---: |
| Avg annual return | 14.39% | 11.49% | 14.71% |
| Avg annual vol | 15.24% | 14.97% | 16.47% |
| Skewness | −0.55 | −0.62 | −0.58 |
| Kurtosis (excess) | 8.27 | 9.50 | 15.36 |
| Downside vol | 10.90% | 10.78% | 11.81% |
| Max drawdown | −33.90% | −33.83% | −33.72% |
| Sharpe | 0.82 | 0.64 | 0.78 |
| Sortino | 1.14 | 0.89 | 1.08 |
| Calmar | 0.42 | 0.34 | 0.44 |

## sleeve_ports

| Metric | Inv-vol USD · CSPX | Inv-vol USD · VWRD | Inv-vol Trad · CSPX | Inv-vol Trad · VWRD | Fixed 60/30/10 · CSPX | Fixed 60/30/10 · VWRD |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Avg annual return | 7.47% | 6.64% | 5.61% | 4.82% | 9.55% | 7.64% |
| Avg annual vol | 5.20% | 5.14% | 6.61% | 6.70% | 9.43% | 9.35% |
| Max drawdown | −7.83% | −8.44% | −17.37% | −18.66% | −20.32% | −21.36% |
| Sharpe | 1.07 | 0.92 | 0.56 | 0.44 | 0.80 | 0.61 |
| Sortino | 1.49 | 1.27 | 0.79 | 0.61 | 1.12 | 0.85 |
| Calmar | 0.95 | 0.79 | 0.32 | 0.26 | 0.47 | 0.36 |

## world_eras

| Period | Return · S&P | Return · World | Sharpe · S&P | Sharpe · World | Max DD · S&P | Max DD · World | t-stat · S&P − World |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2000–2026 | 8.33% | 6.91% | 0.33 | 0.27 | −55.19% | −58.06% | +1.38 |
| 2000–2011 | 0.57% | 1.30% | −0.08 | −0.04 | −55.19% | −58.06% | −0.45 |
| 2012–2026 | 15.09% | 11.70% | 0.80 | 0.64 | −33.72% | −33.62% | +2.62 |

## world_ports

| Period | Portfolio | Return · S&P | Return · World | Sharpe · S&P | Sharpe · World | Max DD · S&P | Max DD · World |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Full | Inv-vol USD | 4.94% | 4.74% | 0.87 | 0.86 | −11.39% | −11.53% |
|  | Inv-vol Trad | 4.13% | 3.94% | 0.67 | 0.62 | −18.72% | −19.87% |
|  | Fixed 60/30/10 | 6.56% | 5.86% | 0.60 | 0.55 | −33.62% | −36.53% |
| 2000–2011 | Inv-vol USD | 3.22% | 3.86% | 0.52 | 0.63 | −11.39% | −11.53% |
|  | Inv-vol Trad | 5.28% | 5.81% | 0.81 | 0.86 | −16.28% | −17.78% |
|  | Fixed 60/30/10 | 4.03% | 5.09% | 0.33 | 0.42 | −33.62% | −36.53% |
| 2012–2026 | Inv-vol USD | 6.16% | 5.37% | 1.15 | 1.05 | −8.79% | −9.29% |
|  | Inv-vol Trad | 3.33% | 2.65% | 0.56 | 0.44 | −18.72% | −19.87% |
|  | Fixed 60/30/10 | 8.36% | 6.40% | 0.84 | 0.68 | −20.50% | −21.67% |
