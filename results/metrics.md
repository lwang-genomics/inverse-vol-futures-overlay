# Performance tables

Data through 2026-10-02; rebalancing every 3 months, 10 bp per unit traded. Futures Sharpe uses rf = 0 (excess returns); ETF/UCITS Sharpe is over 13-week T-bills.

## data_check

| Series | Return, Yahoo | Return, adjusted | Vol, Yahoo | Vol, adjusted | Sharpe, Yahoo | Sharpe, adjusted |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| ES | 7.46% | 7.33% | 19.36% | 18.84% | 0.39 | 0.39 |
| DX | −0.36% | −0.82% | 7.69% | 7.80% | −0.05 | −0.10 |
| GC | 9.38% | 7.06% | 17.39% | 17.28% | 0.54 | 0.41 |
| ZN | 0.08% | 2.25% | 6.19% | 6.03% | 0.01 | 0.37 |
| Inv-vol USD | 4.84% | 4.10% | 5.57% | 5.93% | 0.87 | 0.69 |
| Inv-vol Trad | 3.86% | 4.55% | 6.11% | 6.06% | 0.63 | 0.75 |
| Fixed 60/30/10 | 6.74% | 7.07% | 10.99% | 10.76% | 0.61 | 0.66 |

## fut

| Metric | ES | DX | GC | Inv-vol USD |
| --- | ---: | ---: | ---: | ---: |
| Avg annual return | 7.98% | −0.68% | 8.03% | 4.07% |
| Avg annual vol | 18.42% | 7.65% | 17.76% | 5.98% |
| Skewness | −0.11 | −0.00 | −0.48 | −0.29 |
| Kurtosis (excess) | 11.74 | 1.96 | 6.15 | 3.87 |
| Downside vol | 13.21% | 5.45% | 12.83% | 4.24% |
| Max drawdown | −57.58% | −44.15% | −45.35% | −13.02% |
| Sharpe | 0.43 | −0.09 | 0.45 | 0.68 |
| Sortino | 0.60 | −0.13 | 0.63 | 0.96 |
| Calmar | 0.14 | −0.02 | 0.18 | 0.31 |
| Turnover / yr | – | – | – | 24.52% |

## etf

| Metric | Fut full | ETF full | Fut overlap | ETF overlap |
| --- | ---: | ---: | ---: | ---: |
| Avg annual return | 4.07% | 6.45% | 5.01% | 6.45% |
| Avg annual vol | 5.98% | 5.93% | 6.21% | 5.93% |
| Max drawdown | −13.02% | −9.13% | −8.17% | −9.13% |
| Sharpe | 0.68 | 0.84 | 0.81 | 0.84 |
| Sortino | 0.96 | 1.18 | 1.14 | 1.18 |
| Calmar | 0.31 | 0.71 | 0.61 | 0.71 |

## trad_fut

| Metric | Inv-vol USD | Inv-vol Trad | Fixed 60/30/10 | ES only |
| --- | ---: | ---: | ---: | ---: |
| Avg annual return | 4.07% | 4.63% | 6.61% | 7.98% |
| Avg annual vol | 5.98% | 6.17% | 10.74% | 18.42% |
| Skewness | −0.29 | −0.13 | −0.04 | −0.11 |
| Kurtosis (excess) | 3.87 | 4.05 | 9.11 | 11.74 |
| Downside vol | 4.24% | 4.32% | 7.59% | 13.21% |
| Max drawdown | −13.02% | −16.90% | −33.89% | −57.58% |
| Sharpe | 0.68 | 0.75 | 0.62 | 0.43 |
| Sortino | 0.96 | 1.07 | 0.87 | 0.60 |
| Calmar | 0.31 | 0.27 | 0.20 | 0.14 |
| Turnover / yr | 24.52% | 21.98% | 14.60% | – |

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
| Avg annual return | 7.49% | 7.88% | 6.06% | 4.71% |
| Avg annual vol | 10.93% | 10.99% | 11.29% | 11.34% |
| Max drawdown | −19.51% | −28.19% | −29.66% | −30.68% |
| Sharpe | 0.69 | 0.72 | 0.54 | 0.42 |
| Sortino | 0.96 | 1.01 | 0.74 | 0.57 |
| Calmar | 0.38 | 0.28 | 0.20 | 0.15 |
| Turnover / yr | 79.94% | 77.66% | 58.49% | 33.56% |
| Avg leverage | 1.83× | 1.86× | 1.12× | 0.69× |
| Max leverage | 2.69× | 2.99× | 2.73× | 1.58× |

## stress

| Episode (futures) | Inv-vol USD | Inv-vol Trad | Fixed 60/30/10 | ES only |
| --- | ---: | ---: | ---: | ---: |
| 2002 dot-com bear (final leg) | −8.71% | 3.94% | −15.54% | −32.57% |
| 2007–09 GFC | −5.46% | −0.37% | −33.73% | −57.58% |
| 2018 Q4 sell-off | −1.74% | −0.84% | −9.15% | −16.96% |
| 2020 COVID crash | −6.58% | −6.25% | −20.09% | −34.56% |
| 2022 rate shock | 2.67% | −15.01% | −19.98% | −25.09% |
| 2025 tariff shock | −6.78% | −3.82% | −11.10% | −19.22% |

## subperiods

| Period | Inv-vol USD | Inv-vol Trad | Fixed 60/30/10 | ES only |
| --- | ---: | ---: | ---: | ---: |
| 2001–2012 | 0.35 (−13.02%) | 1.04 (−14.88%) | 0.43 (−33.89%) | 0.12 (−57.58%) |
| 2013–2021 | 0.89 (−7.77%) | 0.74 (−8.34%) | 1.07 (−20.21%) | 0.99 (−34.78%) |
| 2022–2026 | 1.09 (−7.37%) | 0.27 (−16.28%) | 0.43 (−20.31%) | 0.48 (−25.09%) |

## bootstrap

| Sharpe difference (futures) | Point · estimate | 95% · interval | Share of · resamples > 0 |
| --- | ---: | ---: | ---: |
| Inv-vol USD − Inv-vol Trad | −0.07 | [−0.48, 0.28] | 30% |
| Inv-vol USD − Fixed 60/30/10 | 0.07 | [−0.29, 0.40] | 64% |
| Inv-vol Trad − Fixed 60/30/10 | 0.13 | [−0.17, 0.49] | 82% |

## rebal

| Portfolio | Rebalance | Ann. · return | Ann. · vol | Max DD | Sharpe | Turnover · / yr | Cost · / yr |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Inv-vol USD | Monthly | 4.25% | 5.91% | −12.87% | 0.72 | 37.05% | 3.7 bp |
| Inv-vol USD | Quarterly | 4.06% | 5.99% | −13.02% | 0.68 | 24.52% | 2.5 bp |
| Inv-vol USD | Semi-annual | 4.03% | 6.04% | −12.67% | 0.67 | 20.85% | 2.1 bp |
| Inv-vol USD | Annual | 4.05% | 6.12% | −11.87% | 0.66 | 15.43% | 1.5 bp |
| Inv-vol USD | Constant mix* | 3.63% | 5.97% | −13.46% | 0.61 | – | 0 bp |
| Inv-vol Trad | Monthly | 4.85% | 6.10% | −16.61% | 0.80 | 31.12% | 3.1 bp |
| Inv-vol Trad | Quarterly | 4.72% | 6.17% | −16.90% | 0.77 | 21.98% | 2.2 bp |
| Inv-vol Trad | Semi-annual | 4.69% | 6.23% | −16.95% | 0.75 | 18.29% | 1.8 bp |
| Inv-vol Trad | Annual | 4.86% | 6.27% | −16.88% | 0.77 | 13.32% | 1.3 bp |
| Fixed 60/30/10 | Monthly | 6.39% | 10.84% | −34.73% | 0.59 | 23.25% | 2.3 bp |
| Fixed 60/30/10 | Quarterly | 6.48% | 10.74% | −33.89% | 0.60 | 14.60% | 1.5 bp |
| Fixed 60/30/10 | Semi-annual | 6.44% | 10.59% | −33.20% | 0.61 | 10.10% | 1.0 bp |
| Fixed 60/30/10 | Annual | 6.59% | 10.42% | −31.98% | 0.63 | 7.52% | 0.8 bp |

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
| Full | Inv-vol USD | 4.10% | 3.92% | 0.68 | 0.66 | −12.89% | −12.86% |
|  | Inv-vol Trad | 4.64% | 4.46% | 0.75 | 0.71 | −17.32% | −18.50% |
|  | Fixed 60/30/10 | 6.75% | 6.06% | 0.62 | 0.57 | −32.66% | −35.61% |
| 2000–2011 | Inv-vol USD | 2.07% | 2.72% | 0.34 | 0.45 | −12.89% | −12.86% |
|  | Inv-vol Trad | 6.59% | 7.10% | 1.03 | 1.08 | −14.77% | −16.28% |
|  | Fixed 60/30/10 | 4.75% | 5.81% | 0.39 | 0.48 | −32.66% | −35.61% |
| 2012–2026 | Inv-vol USD | 5.52% | 4.76% | 0.94 | 0.82 | −7.64% | −8.18% |
|  | Inv-vol Trad | 3.32% | 2.68% | 0.55 | 0.44 | −17.32% | −18.50% |
|  | Fixed 60/30/10 | 8.15% | 6.23% | 0.82 | 0.66 | −20.59% | −21.60% |
