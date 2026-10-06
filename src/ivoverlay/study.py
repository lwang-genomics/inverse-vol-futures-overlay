"""End-to-end study: backtests, robustness checks, figures and result tables.

Run:  uv run ivoverlay             (uses the cached prices in data/ when present)
      uv run ivoverlay --refresh   (re-download from Yahoo Finance)
"""

import argparse
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from . import plots
from .backtest import BacktestResult, backtest, run_three, walk_forward_constant_mix
from .config import (
    COST_BPS,
    EQUITY_ERAS,
    ETF_TRAD,
    ETF_USD,
    FREQS,
    FUT_TRAD,
    FUT_USD,
    MAIN_FREQ,
    PORT_LABELS,
    PORTS,
    REGIMES,
    RES_DIR,
    ROLL_CORR_WINDOW,
    ROLL_SHARPE_WINDOW,
    SPLICE_END,
    STRESS_PERIODS,
    SUBPERIODS,
    TRADING_DAYS,
    VOL_TARGET,
    WORLD_US_WEIGHT,
)
from .data import basket_returns, load_prices, tbill_log_returns, with_backadjusted_futures
from .metrics import common, period_return, rolling_sharpe, series_metrics, span
from .stats import bootstrap_sharpe_diff
from .tables import METRIC_ROWS, SHORT_ROWS, fmt, metrics_table, write_results

LAB = PORT_LABELS


def weekly(log_returns: pd.DataFrame | pd.Series):
    """Weekly log returns (Friday weeks), for correlations between series that close at different times."""
    return log_returns.resample("W-FRI").sum(min_count=1).dropna(how="all")


@dataclass
class Study:
    px: pd.DataFrame
    facts: dict = field(default_factory=dict)
    tables: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.rf = tbill_log_returns(self.px)
        self.facts |= {"end_date": f"{self.px.index.max():%Y-%m-%d}", "cost_bps": COST_BPS}
        self.fut4 = basket_returns(self.px, ["ES", "DX", "GC", "ZN"])
        self.lr4 = np.log1p(self.fut4)
        self.fut: dict[str, BacktestResult] = run_three(self.fut4[FUT_USD], self.fut4[FUT_TRAD])
        self.fut_iv = self.fut["iv_usd"].ret
        self.fut_lr = self.lr4.loc[self.fut_iv.index]

    def run(self) -> None:
        self.data_check()
        self.futures()
        self.correlations()
        self.etf_replication()
        self.traditional()
        self.robustness()
        self.rebalancing()
        self.ucits_sleeves()
        self.world_equities()

    # ------------------------------------------------------------ data: unadjusted vs back-adjusted futures

    def data_check(self) -> None:
        """Bias of Yahoo's unadjusted front-month series: per leg and on the two inverse-vol books.

        Compared on the common window of the back-adjusted data (no ETF splice), October 2001 to SPLICE_END.
        """
        px = self.px
        legs = ["ES", "DX", "GC", "ZN"]
        raw = basket_returns(px, [f"{c}_yahoo" for c in legs]).set_axis(legs, axis=1)
        adj = self.fut4[legs]
        idx = raw.index.intersection(adj.index)
        idx = idx[(idx >= self.fut_iv.index[0]) & (idx <= pd.Timestamp(SPLICE_END))]
        raw, adj = raw.loc[idx], adj.loc[idx]
        rows, out = [], {}
        for c in legs:
            m_raw, m_adj = series_metrics(np.log1p(raw[c])), series_metrics(np.log1p(adj[c]))
            out[c] = {"ret_yahoo": m_raw["avg_annual_return"], "ret_adj": m_adj["avg_annual_return"],
                      "sr_yahoo": m_raw["sharpe"], "sr_adj": m_adj["sharpe"]}
            rows.append([c, fmt(m_raw["avg_annual_return"], "pct"), fmt(m_adj["avg_annual_return"], "pct"),
                         fmt(m_raw["avg_annual_vol"], "pct"), fmt(m_adj["avg_annual_vol"], "pct"),
                         fmt(m_raw["sharpe"], "num"), fmt(m_adj["sharpe"], "num")])
        books_raw = run_three(raw[FUT_USD], raw[FUT_TRAD])
        books_adj = run_three(adj[FUT_USD], adj[FUT_TRAD])
        for k in ("iv_usd", "iv_trad", "fixed_trad"):
            a, b = series_metrics(books_raw[k].ret), series_metrics(books_adj[k].ret)
            out[k] = {"sr_yahoo": a["sharpe"], "sr_adj": b["sharpe"]}
            rows.append([LAB[k], fmt(a["avg_annual_return"], "pct"), fmt(b["avg_annual_return"], "pct"),
                         fmt(a["avg_annual_vol"], "pct"), fmt(b["avg_annual_vol"], "pct"),
                         fmt(a["sharpe"], "num"), fmt(b["sharpe"], "num")])
        self.facts["data_check"] = out | {"period": span(raw)}
        self.tables["data_check"] = {
            "header": ["Series", "Return, Yahoo", "Return, adjusted", "Vol, Yahoo", "Vol, adjusted",
                       "Sharpe, Yahoo", "Sharpe, adjusted"],
            "rows": rows,
        }

    # ------------------------------------------------------------ core futures book

    def futures(self) -> None:
        fut, f = self.fut, self.facts
        f["fut_period"] = span(self.fut_iv)
        f["fut_n_rebal"] = len(fut["iv_usd"].targets)
        f["fut_mean_w"] = {k: fut[k].targets.mean().round(2).to_dict() for k in ("iv_usd", "iv_trad")}
        series = {c: self.fut_lr[c] for c in FUT_USD} | {"Inv-vol USD": self.fut_iv}
        self.tables["fut"] = metrics_table(series, {"Inv-vol USD": fut["iv_usd"].turnover_pa})

        plots.assets_cum(self.fut_lr[["ES", "DX", "GC", "ZN"]], "fig01_fut_assets_cum_log.png")
        plots.scaled_path(self.fut_iv, "fig02_fut_portfolio_cum_log.png", "Inv-vol USD (ES/DX/GC)")
        plots.drawdowns({"Inv-vol USD": self.fut_iv}, "fig03_fut_portfolio_drawdown.png",
                        {"Inv-vol USD": plots.PORT_COLORS["iv_usd"]})
        plots.weights({"Inv-vol USD (ES/DX/GC)": fut["iv_usd"].held, "Inv-vol Trad (ES/ZN/GC)": fut["iv_trad"].held},
                      "fig04_fut_weights.png")
        plots.yearly(self.fut_iv, "fig07_fut_yearly_returns.png")

    def correlations(self) -> None:
        # Weekly returns: the futures settle at different times of day, which dilutes daily correlations
        lr4, start = weekly(self.lr4), self.fut_iv.index[0]
        panels = {
            "a": ("Inv-vol USD basket (ES / DX / GC)", [("ES", "DX"), ("ES", "GC"), ("DX", "GC")]),
            "b": ("Traditional basket (ES / ZN / GC)", [("ES", "ZN"), ("ES", "GC"), ("ZN", "GC")]),
        }
        roll = {
            letter: (title, {f"{a}–{b}": lr4[a].rolling(ROLL_CORR_WINDOW).corr(lr4[b]).loc[start:] for a, b in pairs})
            for letter, (title, pairs) in panels.items()
        }
        plots.rolling_corr(roll, "fig05_rolling_corr.png")
        flat = {k: v for _, pairs in roll.values() for k, v in pairs.items()}

        regime_pairs = [("ES", "DX"), ("ES", "ZN"), ("ES", "GC"), ("DX", "GC"), ("ZN", "GC")]
        regime = pd.DataFrame(
            {name: [lr4.loc[s:e, a].corr(lr4.loc[s:e, b]) for a, b in regime_pairs]
             for name, (s, e) in REGIMES.items()},
            index=[f"{a}–{b}" for a, b in regime_pairs],
        )
        plots.corr_regimes(regime, "fig06_corr_regimes.png")
        self.facts["regime_corr"] = regime.round(2).to_dict()
        self.facts["roll_corr_last"] = {k: round(float(v.dropna().iloc[-1]), 2) for k, v in flat.items()}
        self.facts["roll_corr_mean"] = {k: round(float(v.mean()), 2) for k, v in flat.items()}

    # ------------------------------------------------------------ ETF implementation

    def etf_replication(self) -> None:
        px, f = self.px, self.facts
        etf4 = basket_returns(px, ["SPY", "UUP", "GLD", "IEF"])
        etf = run_three(etf4[ETF_USD], basket_returns(px, ETF_TRAD))  # IEF/GLD start before UUP
        etf_iv = etf["iv_usd"].ret
        self.etf, self.etf4 = etf, etf4
        f["etf_period"] = span(etf_iv)
        f["etf_mean_w"] = {k: etf[k].targets.mean().round(2).to_dict() for k in ("iv_usd", "iv_trad")}
        wk = weekly(np.log1p(px[["ES", "SPY", "DX", "UUP", "GC", "GLD", "ZN", "IEF"]].dropna().pct_change()).dropna())
        f["fut_etf_corr"] = {
            f"{a}–{b}": round(float(wk[a].corr(wk[b])), 2)
            for a, b in [("ES", "SPY"), ("DX", "UUP"), ("GC", "GLD"), ("ZN", "IEF")]
        }

        plots.assets_cum(np.log1p(etf4).loc[etf_iv.index][["SPY", "UUP", "GLD", "IEF"]], "fig08_etf_assets_cum_log.png")
        plots.scaled_path(etf_iv, "fig09_etf_portfolio_cum_log.png", "Inv-vol USD (SPY/UUP/GLD)")
        plots.drawdowns({"Inv-vol USD ETF": etf_iv}, "fig10_etf_portfolio_drawdown.png",
                        {"Inv-vol USD ETF": plots.PORT_COLORS["iv_usd"]})
        plots.weights({"Inv-vol USD (SPY/UUP/GLD)": etf["iv_usd"].held,
                       "Inv-vol Trad (SPY/IEF/GLD)": etf["iv_trad"].held.loc[etf_iv.index[0] :]},
                      "fig11_etf_weights.png")
        plots.yearly(etf_iv, "fig12_etf_yearly_returns.png")

        ov = common({"futures": self.fut_iv, "etf": etf_iv})
        f["overlap_period"] = span(ov["futures"])
        ovw = weekly(pd.DataFrame(ov))
        f["overlap_corr"] = round(float(ovw["futures"].corr(ovw["etf"])), 3)
        f["overlap_te"] = float((ovw["futures"] - ovw["etf"]).std() * np.sqrt(52))
        plots.compare_fut_etf(ov["futures"], ov["etf"], "fig13_compare_fut_etf.png")

        rf = self.rf
        self.tables["etf"] = metrics_table(
            {"Fut full": self.fut_iv, "ETF full": etf_iv, "Fut overlap": ov["futures"], "ETF overlap": ov["etf"]},
            rows=SHORT_ROWS, rf=rf, excess={"ETF full", "ETF overlap"},
        )
        f["etf_sharpe"] = {
            "etf_rf0": series_metrics(etf_iv)["sharpe"],
            "etf_excess": series_metrics(etf_iv, rf)["sharpe"],
            "fut_overlap": series_metrics(ov["futures"])["sharpe"],
            "etf_overlap_excess": series_metrics(ov["etf"], rf)["sharpe"],
            "tbill_overlap": float(np.expm1(rf.reindex(ov["etf"].index).ffill().mean() * TRADING_DAYS)),
        }

    # ------------------------------------------------------------ traditional comparison + vol targeting

    def traditional(self) -> None:
        fut, etf, f = self.fut, self.etf, self.facts
        self.fut_cmp = common({LAB[k]: fut[k].ret for k in PORTS} | {"ES only": self.fut_lr["ES"]})
        self.tables["trad_fut"] = metrics_table(self.fut_cmp, {LAB[k]: fut[k].turnover_pa for k in PORTS})
        etf_cmp = common({LAB[k]: etf[k].ret for k in PORTS} | {"SPY only": np.log1p(self.etf4["SPY"])})
        self.tables["trad_etf"] = metrics_table(etf_cmp, {LAB[k]: etf[k].turnover_pa for k in PORTS}, rf=self.rf)
        f["trad_etf_period"] = span(next(iter(etf_cmp.values())))
        f["trad_fut_period"] = span(next(iter(self.fut_cmp.values())))
        f["trad_fut_metrics"] = {k: series_metrics(v) for k, v in self.fut_cmp.items()}
        f["trad_etf_metrics"] = {k: series_metrics(v, self.rf) for k, v in etf_cmp.items()}

        # Same risk, no hindsight: scale each book to VOL_TARGET at every rebalance from trailing covariance
        vt = run_three(self.fut4[FUT_USD], self.fut4[FUT_TRAD], vol_target=VOL_TARGET)
        vt["es"] = backtest(self.fut4[["ES"]], fixed=(1.0,), vol_target=VOL_TARGET)
        key = {LAB[k]: k for k in PORTS} | {"ES only": "es"}
        vt_cmp = common({label: vt[k].ret for label, k in key.items()})
        lev = {label: vt[k].leverage for label, k in key.items()}
        t = metrics_table(vt_cmp, {label: vt[k].turnover_pa for label, k in key.items()}, rows=SHORT_ROWS)
        t["rows"].append(["Avg leverage"] + [f"{lev[k].mean():.2f}×" for k in vt_cmp])
        t["rows"].append(["Max leverage"] + [f"{lev[k].max():.2f}×" for k in vt_cmp])
        self.tables["voltarget"] = t
        f["vt_metrics"] = {k: series_metrics(v) for k, v in vt_cmp.items()}
        f["vt_lev_mean"] = {k: float(v.mean()) for k, v in lev.items()}

        plots.growth_unlevered_vs_target(self.fut_cmp, vt_cmp, "fig14_trad_growth.png")
        plots.drawdowns(self.fut_cmp, "fig15_trad_drawdown.png", plots.LABEL_COLORS, plots.LABEL_LSTYLES)

        yr = pd.DataFrame({k: np.exp(v.groupby(v.index.year).sum()) - 1.0 for k, v in self.fut_cmp.items()})
        plots.yearly_books(yr, "fig16_trad_yearly.png")
        f["trad_yearly_neg"] = {k: int((yr[k] < 0).sum()) for k in yr}
        f["trad_yearly_worst"] = {k: [int(yr[k].idxmin()), float(yr[k].min())] for k in yr}
        f["trad_yearly_2022"] = {k: float(yr.loc[2022, k]) for k in yr}

        self.tables["stress"] = {
            "header": ["Episode (futures)", *self.fut_cmp.keys()],
            "rows": [[name] + [fmt(period_return(v, s, e), "pct") for v in self.fut_cmp.values()]
                     for name, (s, e) in STRESS_PERIODS.items()],
        }

    def robustness(self) -> None:
        fut, f = self.fut, self.facts
        rows = []
        for name, (s, e) in SUBPERIODS.items():
            ms = {k: series_metrics(lr.loc[s:e]) for k, lr in self.fut_cmp.items()}
            rows.append([name] + [f"{fmt(m['sharpe'], 'num')} ({fmt(m['max_drawdown'], 'pct')})" for m in ms.values()])
        self.tables["subperiods"] = {"header": ["Period", *self.fut_cmp.keys()], "rows": rows}
        f["subperiod_sharpe"] = {
            name: {k: series_metrics(lr.loc[s:e])["sharpe"] for k, lr in self.fut_cmp.items()}
            for name, (s, e) in SUBPERIODS.items()
        }

        boot = {
            f"{LAB[a]} − {LAB[b]}": bootstrap_sharpe_diff(fut[a].ret, fut[b].ret)
            for a, b in [("iv_usd", "iv_trad"), ("iv_usd", "fixed_trad"), ("iv_trad", "fixed_trad")]
        }
        self.tables["bootstrap"] = {
            "header": ["Sharpe difference (futures)", "Point\nestimate", "95%\ninterval", "Share of\nresamples > 0"],
            "rows": [[k, fmt(v["diff"], "num"), f"[{fmt(v['lo'], 'num')}, {fmt(v['hi'], 'num')}]", f"{v['p_pos']:.0%}"]
                     for k, v in boot.items()],
        }
        f["bootstrap"] = boot

        no_gold = {"Inv-vol ES/DX": ["ES", "DX"], "Inv-vol ES/ZN": ["ES", "ZN"]}
        f["no_gold_sharpe"] = {k: series_metrics(backtest(self.fut4[c]).ret)["sharpe"] for k, c in no_gold.items()}
        f["gc_sharpe"] = series_metrics(self.fut_lr["GC"])["sharpe"]

        plots.rolling_sharpes({k: rolling_sharpe(fut[k].ret, ROLL_SHARPE_WINDOW) for k in PORTS},
                              "fig20_rolling_sharpe.png")

    def rebalancing(self) -> None:
        runs = {name: run_three(self.fut4[FUT_USD], self.fut4[FUT_TRAD], m) for name, m in FREQS.items()}
        const_mix = walk_forward_constant_mix(self.lr4[FUT_USD])
        start = max(r[k].ret.index[0] for r in runs.values() for k in PORTS)

        def row(k: str, name: str, m: dict, turnover: str, cost: str) -> list[str]:
            return [LAB[k], name, fmt(m["avg_annual_return"], "pct"), fmt(m["avg_annual_vol"], "pct"),
                    fmt(m["max_drawdown"], "pct"), fmt(m["sharpe"], "num"), turnover, cost]

        rows, sharpe, turnover = [], {k: [] for k in PORTS}, {k: [] for k in PORTS}
        for k in PORTS:
            for name, r in runs.items():
                m = series_metrics(r[k].ret.loc[start:])
                sharpe[k].append(m["sharpe"])
                turnover[k].append(r[k].turnover_pa)
                rows.append(row(k, name, m, fmt(r[k].turnover_pa, "pct"), f"{r[k].turnover_pa * COST_BPS:.1f} bp"))
            if k == "iv_usd":
                rows.append(row(k, "Constant mix*", series_metrics(const_mix.loc[start:]), "–", "0 bp"))
        self.tables["rebal"] = {
            "header": ["Portfolio", "Rebalance", "Ann.\nreturn", "Ann.\nvol", "Max DD", "Sharpe", "Turnover\n/ yr",
                       "Cost\n/ yr"],
            "rows": rows,
        }
        self.facts["rebal_period"] = f"{start:%Y-%m-%d} → {self.fut_iv.index[-1]:%Y-%m-%d}"
        self.facts["rebal_sharpe"] = {f"{k}|{n}": round(v, 3) for k in PORTS for n, v in zip(FREQS, sharpe[k])}
        plots.rebalance_frequency(sharpe, turnover, "fig17_rebalance_frequency.png")

    # ------------------------------------------------------------ equity sleeve: S&P 500 vs world

    def ucits_sleeves(self) -> None:
        px, rf, f = self.px, self.rf, self.facts
        sl_lr = np.log1p(basket_returns(px, ["CSPX", "VWRD", "SPY"]))
        self.tables["sleeve"] = metrics_table({c: sl_lr[c] for c in ("CSPX", "VWRD", "SPY")}, rf=rf)
        f["sleeve_period"] = span(sl_lr)
        f["sleeve_metrics"] = {c: series_metrics(sl_lr[c], rf) for c in sl_lr}
        wk = np.log1p(px[["CSPX", "VWRD", "SPY"]].dropna().resample("W-FRI").last().pct_change().dropna())
        f["sleeve_weekly_corr"] = round(float(wk["CSPX"].corr(wk["VWRD"])), 3)
        f["sleeve_daily_corr"] = round(float(sl_lr["CSPX"].corr(sl_lr["VWRD"])), 3)
        f["cspx_spy_te"] = float((wk["CSPX"] - wk["SPY"]).std() * np.sqrt(52))
        chk = np.log1p(px[["VWRD", "VWRA"]].dropna().pct_change().dropna())
        f["vwrd_vwra"] = {
            "period": span(chk),
            "corr": round(float(chk["VWRD"].corr(chk["VWRA"])), 3),
            "te": float((chk["VWRD"] - chk["VWRA"]).std() * np.sqrt(TRADING_DAYS)),
            "ret_vwrd": series_metrics(chk["VWRD"])["avg_annual_return"],
            "ret_vwra": series_metrics(chk["VWRA"])["avg_annual_return"],
        }
        rel = (sl_lr["VWRD"] - sl_lr["CSPX"]).rolling(TRADING_DAYS).sum()
        plots.sleeves_standalone(sl_lr, rel, "fig18_sleeves_standalone.png")
        f["sleeve_rel_share_positive"] = float((rel.dropna() > 0).mean())

        runs = {eq: run_three(basket_returns(px, [eq, "UUP", "GLD"]), basket_returns(px, [eq, "IEF", "GLD"]))
                for eq in ("CSPX", "VWRD")}
        series = common({f"{k}|{eq}": runs[eq][k].ret for eq in runs for k in PORTS})
        f["sleeve_port_period"] = span(next(iter(series.values())))
        sm = {key: series_metrics(v, rf) for key, v in series.items()}
        self.tables["sleeve_ports"] = {
            "header": ["Metric"] + [f"{LAB[k]}\n{eq}" for k in PORTS for eq in ("CSPX", "VWRD")],
            "rows": [[label] + [fmt(sm[f"{k}|{eq}"][key], kind) for k in PORTS for eq in ("CSPX", "VWRD")]
                     for key, label, kind in METRIC_ROWS if key in SHORT_ROWS],
        }
        f["sleeve_port_metrics"] = sm
        f["sleeve_port_mean_w"] = {
            f"{k}|{eq}": runs[eq][k].targets.mean().round(2).to_dict() for eq in runs for k in ("iv_usd", "iv_trad")
        }
        plots.sleeves_in_books({eq: [sm[f"{k}|{eq}"]["sharpe"] for k in PORTS] for eq in ("CSPX", "VWRD")},
                               {eq: [sm[f"{k}|{eq}"]["max_drawdown"] for k in PORTS] for eq in ("CSPX", "VWRD")},
                               "fig19_sleeves_in_portfolios.png")

    def world_equities(self) -> None:
        px, rf, f = self.px, self.rf, self.facts
        eq = basket_returns(px, ["SPY", "VGTSX"])
        world = WORLD_US_WEIGHT * eq["SPY"] + (1 - WORLD_US_WEIGHT) * eq["VGTSX"]
        eq_lr = pd.DataFrame({"S&P 500": np.log1p(eq["SPY"]), "World": np.log1p(world)})
        f["world_period"] = span(eq_lr)

        wk_world = (1 + world).resample("W-FRI").prod() - 1
        wk_px = px[["ACWI", "VWRD"]].resample("W-FRI").last().pct_change()
        f["world_check"] = {}
        for ref in ("ACWI", "VWRD"):
            x = pd.concat([wk_world, wk_px[ref]], axis=1, keys=["proxy", ref]).dropna()
            d = np.log1p(x["proxy"]) - np.log1p(x[ref])
            f["world_check"][ref] = {"period": span(x), "corr": float(x.corr().iloc[0, 1]),
                                     "gap": float(d.mean() * 52), "te": float(d.std() * np.sqrt(52))}

        rows = []
        f["world_eras"] = {}
        for era, (s, e) in {"2000–2026": ("2000-01-01", "2100-01-01"), **EQUITY_ERAS}.items():
            w = eq_lr.loc[s:e]
            m = {c: series_metrics(w[c], rf) for c in w}
            gap_wk = (w["S&P 500"] - w["World"]).resample("W-FRI").sum()
            tstat = float(gap_wk.mean() / gap_wk.std() * np.sqrt(len(gap_wk)))
            f["world_eras"][era] = m | {"tstat": tstat}
            rows.append([era] + [fmt(m[c][k], kind) for k, kind in
                                 (("avg_annual_return", "pct"), ("sharpe", "num"), ("max_drawdown", "pct"))
                                 for c in ("S&P 500", "World")] + [f"{tstat:+.2f}".replace("-", "−")])
        self.tables["world_eras"] = {
            "header": ["Period", "Return\nS&P", "Return\nWorld", "Sharpe\nS&P", "Sharpe\nWorld",
                       "Max DD\nS&P", "Max DD\nWorld", "t-stat\nS&P − World"],
            "rows": rows,
        }
        rel3 = (eq_lr["World"] - eq_lr["S&P 500"]).rolling(ROLL_SHARPE_WINDOW).sum() / 3
        plots.world_vs_sp500(eq_lr, rel3, "fig21_world_vs_sp500_long.png")
        f["world_rel3_share_positive"] = float((rel3.dropna() > 0).mean())

        # Inside the futures books: equity sleeve as excess return over T-bills, same footing as ES
        base = basket_returns(px, ["SPY", "VGTSX", "DX", "GC", "ZN"])
        rfx = np.expm1(rf).reindex(base.index).ffill().fillna(0.0)
        sleeves = {
            "S&P 500": (1 + base["SPY"]) / (1 + rfx) - 1,
            "World": (1 + WORLD_US_WEIGHT * base["SPY"] + (1 - WORLD_US_WEIGHT) * base["VGTSX"]) / (1 + rfx) - 1,
        }
        runs = {}
        for name, eqx in sleeves.items():
            r = base[["DX", "GC", "ZN"]].assign(EQ=eqx)
            runs[name] = run_three(r[["EQ", "DX", "GC"]], r[["EQ", "ZN", "GC"]])
        series = common({f"{k}|{n}": runs[n][k].ret for n in runs for k in PORTS})
        f["world_port_period"] = span(next(iter(series.values())))
        rows = []
        f["world_ports"] = {}
        for era, (s, e) in {"Full": ("2000-01-01", "2100-01-01"), **EQUITY_ERAS}.items():
            for k in PORTS:
                m = {n: series_metrics(series[f"{k}|{n}"].loc[s:e]) for n in sleeves}
                f["world_ports"][f"{era}|{k}"] = m
                rows.append([era if k == PORTS[0] else "", LAB[k]]
                            + [fmt(m[n]["avg_annual_return"], "pct") for n in sleeves]
                            + [fmt(m[n]["sharpe"], "num") for n in sleeves]
                            + [fmt(m[n]["max_drawdown"], "pct") for n in sleeves])
        self.tables["world_ports"] = {
            "header": ["Period", "Portfolio", "Return\nS&P", "Return\nWorld", "Sharpe\nS&P", "Sharpe\nWorld",
                       "Max DD\nS&P", "Max DD\nWorld"],
            "rows": rows,
        }
        f["world_boot"] = {k: bootstrap_sharpe_diff(series[f"{k}|S&P 500"], series[f"{k}|World"]) for k in PORTS}
        plots.world_sleeve_in_books(
            {era: {n: [f["world_ports"][f"{era}|{k}"][n]["sharpe"] for k in PORTS] for n in sleeves}
             for era in EQUITY_ERAS},
            "fig22_world_sleeve_in_portfolios.png",
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--refresh", action="store_true", help="re-download prices from Yahoo Finance")
    args = parser.parse_args()

    study = Study(with_backadjusted_futures(load_prices(refresh=args.refresh)))
    study.run()
    preamble = (f"Data through {study.facts['end_date']}; rebalancing every {MAIN_FREQ} months, "
                f"{COST_BPS:g} bp per unit traded. Futures Sharpe uses rf = 0 (excess returns); "
                "ETF/UCITS Sharpe is over 13-week T-bills.")
    write_results(study.facts, study.tables, RES_DIR, preamble)
    print(f"Saved {RES_DIR.name}/results.json and {RES_DIR.name}/metrics.md")


if __name__ == "__main__":
    main()
