"""Figures for the report. Styling comes from viz_style (slide-ready theme on import)."""

from .viz_style import *  # noqa: I001  (must load first: sets the theme)

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.dates import DateFormatter, YearLocator
from matplotlib.ticker import MultipleLocator, PercentFormatter

from .config import DISPLAY_LOG_TARGET, FIG_DIR, PORT_LABELS, PORTS, ROOT
from .metrics import drawdown

PORT_COLORS = dict(zip(PORTS, list(DALE_METHOD_COLORS.values())[:3]))
PORT_LSTYLES = dict(zip(PORTS, list(DALE_METHOD_LSTYLES.values())[:3]))
PORT_LW = {"iv_usd": DALE_LINE_EMPH, "iv_trad": DALE_LINE_WIDTH, "fixed_trad": DALE_LINE_WIDTH}

# Okabe-Ito: blue equity, green dollar, orange gold, mauve Treasury
EQUITY_C, USD_C, GOLD_C, BOND_C = (DALE_OKABE_ITO[i] for i in (4, 2, 0, 6))
ASSET_COLORS = {
    "ES": EQUITY_C, "SPY": EQUITY_C, "DX": USD_C, "UUP": USD_C,
    "GC": GOLD_C, "GLD": GOLD_C, "ZN": BOND_C, "IEF": BOND_C,
}
SLEEVE_COLORS = {"CSPX": DALE_2GROUP_LIST[0], "VWRD": DALE_2GROUP_LIST[1]}
SLEEVE_LSTYLES = {"CSPX": "solid", "VWRD": "dashed"}
SLEEVE_LABELS = {"CSPX": "S&P 500 (CSPX)", "VWRD": "All-World (VWRD)"}
BOOK_TICKS = ["Inv-vol\nUSD", "Inv-vol\nTrad", "Fixed\n60/30/10"]

# Colours/styles keyed by display label, for comparison plots that include a grey benchmark
LABEL_COLORS = {PORT_LABELS[k]: PORT_COLORS[k] for k in PORTS} | {"ES only": DALE_NONSIG, "SPY only": DALE_NONSIG}
LABEL_LSTYLES = {PORT_LABELS[k]: PORT_LSTYLES[k] for k in PORTS}
LABEL_LW = {PORT_LABELS[k]: PORT_LW[k] for k in PORTS}


# ------------------------------------------------------------------ helpers


def style_dates(ax, idx: pd.DatetimeIndex, rotate: bool = True) -> None:
    years = (idx[-1] - idx[0]).days / 365.25
    ax.xaxis.set_major_locator(YearLocator(base=2 if years > 12 else 1))
    ax.xaxis.set_major_formatter(DateFormatter("%Y"))
    ax.set_xlim(idx[0], idx[-1])
    if rotate:
        ax.tick_params(axis="x", labelrotation=45)
        for label in ax.get_xticklabels():
            label.set_horizontalalignment("right")


def panel_label(ax, letter: str) -> None:
    ax.text(-0.12, 1.12, letter, transform=ax.transAxes, fontsize=16, fontweight="bold", va="top")


def legend_top(ax, ncol: int, **kw) -> None:
    ax.legend(ncol=ncol, loc="lower left", bbox_to_anchor=(0.0, 1.0), borderaxespad=0.2, **kw)


def fig_legend(fig, ax, ncol: int) -> None:
    """Shared legend centred above side-by-side panels (keeps panel labels clear)."""
    fig.legend(*ax.get_legend_handles_labels(), ncol=ncol, loc="lower center",
               bbox_to_anchor=(0.5, 0.96), borderaxespad=0.2)


def finish(fig, name: str, wide: bool = True, size: tuple[float, float] | None = None) -> None:
    """Save with the style file's slide sizes; `size` (in) overrides them for a specific figure."""
    FIG_DIR.mkdir(exist_ok=True)
    path = FIG_DIR / name
    if size is not None:
        save_slide_wide(path, fig, width=size[0], height=size[1])
    else:
        (save_slide_wide if wide else save_slide)(path, fig)
    plt.close(fig)
    print(f"Saved {path.relative_to(ROOT)}")


def scaled_cum(lr: pd.Series) -> pd.Series:
    """Cumulative log return rescaled to a 10% average annual endpoint (path shape only)."""
    cum = lr.cumsum()
    years = (cum.index[-1] - cum.index[0]).days / 365.25
    return cum * (years * DISPLAY_LOG_TARGET / cum.iloc[-1])


def sleeve_bars(ax, values: dict[str, list[float]], colors: dict[str, str], labels: dict[str, str],
                hatched: str) -> None:
    x = np.arange(len(PORTS))
    for i, (key, vals) in enumerate(values.items()):
        ax.bar(x + (i - 0.5) * 0.35, vals, width=0.35, color=colors[key], hatch="//" if key == hatched else None,
               edgecolor="#4D4D4D", linewidth=0.7, label=labels[key])
    ax.set_xticks(x, BOOK_TICKS)
    ax.axhline(0.0, color="black", linewidth=0.8)


# ------------------------------------------------------------------ generic figures


def assets_cum(lr: pd.DataFrame, name: str) -> None:
    fig, ax = plt.subplots()
    cum = lr.cumsum()
    for c in cum.columns:
        ax.plot(cum.index, cum[c], color=ASSET_COLORS[c], linewidth=DALE_LINE_WIDTH, label=c)
    ax.axhline(0.0, color=DALE_NONSIG, linewidth=0.8)
    ax.set_ylabel("Cumulative log return")
    legend_top(ax, ncol=len(cum.columns))
    style_dates(ax, cum.index)
    finish(fig, name)


def scaled_path(lr: pd.Series, name: str, label: str) -> None:
    cum = scaled_cum(lr)
    fig, ax = plt.subplots()
    ax.plot(cum.index, cum, color=PORT_COLORS["iv_usd"], linewidth=DALE_LINE_EMPH, label=label)
    ax.set_ylabel("Scaled cumulative log return")
    legend_top(ax, ncol=1)
    style_dates(ax, cum.index)
    finish(fig, name)


def drawdowns(series: dict[str, pd.Series], name: str, colors: dict, lstyles: dict | None = None) -> None:
    fig, ax = plt.subplots()
    for k, lr in series.items():
        dd = drawdown(lr)
        ax.plot(dd.index, dd, color=colors[k], linewidth=DALE_LINE_WIDTH,
                linestyle=(lstyles or {}).get(k, "solid"), label=k)
        if len(series) == 1:
            ax.fill_between(dd.index, dd, 0.0, color=colors[k], alpha=0.3, linewidth=0)
    ax.yaxis.set_major_formatter(PercentFormatter(1.0))
    ax.set_ylabel("Drawdown")
    legend_top(ax, ncol=len(series))
    style_dates(ax, next(iter(series.values())).index)
    finish(fig, name)


def weights(held: dict[str, pd.DataFrame], name: str) -> None:
    fig, axes = plt.subplots(len(held), 1, sharex=True)
    axes = np.atleast_1d(axes)
    for ax, (title, h), letter in zip(axes, held.items(), "abc"):
        ax.stackplot(h.index, h.T.values, colors=[ASSET_COLORS[c] for c in h.columns],
                     labels=h.columns, alpha=0.85, linewidth=0)
        ax.set_ylim(0, 1)
        ax.set_ylabel("Weight")
        ax.legend(ncol=3, loc="lower left", bbox_to_anchor=(0.30, 1.0), borderaxespad=0.2)
        ax.text(0.0, 1.04, title, transform=ax.transAxes, fontsize=DALE_FONT_ANNOT, va="bottom")
        if len(held) > 1:
            panel_label(ax, letter)
    style_dates(axes[-1], next(iter(held.values())).index)
    finish(fig, name)


def yearly(lr: pd.Series, name: str) -> None:
    yr = np.exp(lr.groupby(lr.index.year).sum()) - 1.0
    fig, ax = plt.subplots()
    colors = [DALE_2GROUP_LIST[0] if v >= 0 else DALE_2GROUP_LIST[1] for v in yr]
    ax.bar(yr.index.astype(str), yr.values, color=colors, width=DALE_BAR_WIDTH)
    ax.axhline(0.0, color="black", linewidth=0.8)
    ax.set_ylabel("Calendar-year return")
    ax.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    ax.tick_params(axis="x", labelrotation=90)
    finish(fig, name)


# ------------------------------------------------------------------ section-specific figures


def rolling_corr(panels: dict[str, tuple[str, dict[str, pd.Series]]], name: str) -> None:
    """panels: letter -> (title, {pair label: rolling correlation}); same pair role -> same style."""
    pair_style = [(DALE_REGLINE, "solid"), (GOLD_C, "dashed"), (DALE_SIG, "dotted")]
    fig, axes = plt.subplots(len(panels), 1, sharex=True)
    for ax, (letter, (title, pairs)) in zip(axes, panels.items()):
        for (label, rc), (color, ls) in zip(pairs.items(), pair_style):
            ax.plot(rc.index, rc, color=color, linestyle=ls, linewidth=DALE_LINE_WIDTH, label=label)
        ax.axhline(0.0, color=DALE_NONSIG, linewidth=0.8)
        ax.set_ylim(-1, 1)
        ax.set_ylabel("Correlation")
        ax.legend(ncol=3, loc="lower left", bbox_to_anchor=(0.42, 1.0), borderaxespad=0.2)
        ax.text(0.0, 1.04, title, transform=ax.transAxes, fontsize=DALE_FONT_ANNOT, va="bottom")
        panel_label(ax, letter)
    first = next(iter(next(iter(panels.values()))[1].values())).dropna()
    style_dates(axes[-1], first.index)
    finish(fig, name)


def corr_regimes(regime: pd.DataFrame, name: str) -> None:
    fig, ax = plt.subplots()
    im = ax.imshow(regime.values, cmap=dale_div_cmap(), vmin=-0.6, vmax=0.6, aspect="auto")
    for (r, c), v in np.ndenumerate(regime.values):
        ax.text(c, r, f"{v:+.2f}".replace("-", "−"), ha="center", va="center", fontsize=DALE_FONT_ANNOT)
    ax.set_xticks(range(regime.shape[1]), regime.columns)
    ax.set_yticks(range(regime.shape[0]), regime.index)
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    fig.colorbar(im, ax=ax, label="Daily correlation", shrink=0.8)
    finish(fig, name)


def compare_fut_etf(fut: pd.Series, etf: pd.Series, name: str) -> None:
    fig, ax = plt.subplots()
    for lr, color, ls, label in [(fut, PORT_COLORS["iv_usd"], "solid", "Futures ES/DX/GC"),
                                 (etf, PORT_COLORS["iv_trad"], "dashed", "ETF SPY/UUP/GLD")]:
        cum = scaled_cum(lr)
        ax.plot(cum.index, cum, color=color, linestyle=ls, linewidth=DALE_LINE_EMPH, label=label)
    ax.set_ylabel("Scaled cumulative log return")
    legend_top(ax, ncol=2)
    style_dates(ax, fut.index)
    finish(fig, name)


def growth_unlevered_vs_target(unlevered: dict[str, pd.Series], targeted: dict[str, pd.Series], name: str) -> None:
    """Side-by-side panels on a shared y-axis: a, unlevered books; b, books scaled to the vol target."""
    fig, axes = plt.subplots(1, 2, sharey=True)
    for ax, letter, panel, title in zip(axes, "ab", (unlevered, targeted), ("Unlevered", "10% volatility target")):
        for k, lr in panel.items():
            cum = lr.cumsum()
            ax.plot(cum.index, cum, color=LABEL_COLORS[k], linestyle=LABEL_LSTYLES.get(k, "solid"),
                    linewidth=LABEL_LW.get(k, DALE_LINE_WIDTH), label=k, zorder=1 if k == "ES only" else 2)
        style_dates(ax, cum.index)
        ax.xaxis.set_major_locator(YearLocator(base=5))
        ax.text(0.0, 1.02, title, transform=ax.transAxes, fontsize=DALE_FONT_ANNOT, va="bottom")
        panel_label(ax, letter)
    axes[0].set_ylabel("Cumulative log return")
    axes[1].tick_params(axis="y", labelleft=False)
    fig_legend(fig, axes[0], ncol=4)
    fig.subplots_adjust(wspace=0.08)
    finish(fig, name, size=(12.0, 4.5))


def yearly_books(yr: pd.DataFrame, name: str) -> None:
    fig, ax = plt.subplots()
    x = np.arange(len(yr))
    bw = DALE_BAR_WIDTH / 3
    for j, k in enumerate(PORTS):
        ax.bar(x + (j - 1) * bw, yr[PORT_LABELS[k]], width=bw, color=PORT_COLORS[k], label=PORT_LABELS[k])
    ax.scatter(x, yr["ES only"], marker="_", s=120, color="black", linewidths=1.6, label="ES only", zorder=3)
    ax.axhline(0.0, color="black", linewidth=0.8)
    ax.set_xticks(x, yr.index.astype(str), rotation=90)
    ax.set_xlim(-0.6, len(x) - 0.4)
    ax.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    ax.set_ylabel("Calendar-year return")
    legend_top(ax, ncol=4)
    finish(fig, name)


def rolling_sharpes(roll: dict[str, pd.Series], name: str) -> None:
    """roll: book key -> rolling Sharpe series."""
    fig, ax = plt.subplots()
    for k, s in roll.items():
        ax.plot(s.index, s, color=PORT_COLORS[k], linestyle=PORT_LSTYLES[k], linewidth=PORT_LW[k],
                label=PORT_LABELS[k])
    ax.axhline(0.0, color="black", linewidth=0.8)
    ax.set_ylabel("Rolling 3-year Sharpe")
    legend_top(ax, ncol=3)
    style_dates(ax, s.index)
    finish(fig, name)


def rebalance_frequency(sharpe: dict[str, list[float]], turnover: dict[str, list[float]], name: str) -> None:
    """sharpe/turnover: book key -> values for M, Q, 6M, A."""
    fig, axes = plt.subplots(1, 2)
    x = np.arange(4)
    for ax, values, ylabel, letter in zip(axes, (sharpe, turnover), ("Sharpe", "Turnover per year"), "ab"):
        for i, k in enumerate(PORTS):
            ax.bar(x + (i - 1) * 0.25, values[k], width=0.25, color=PORT_COLORS[k], label=PORT_LABELS[k])
        ax.set_xticks(x, ["M", "Q", "6M", "A"])
        ax.set_xlabel("Rebalance frequency")
        ax.set_ylabel(ylabel)
        panel_label(ax, letter)
    axes[1].yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    axes[0].set_ylim(0, None)
    fig_legend(fig, axes[0], ncol=3)
    fig.subplots_adjust(wspace=0.35)
    finish(fig, name)


def sleeves_standalone(sl_lr: pd.DataFrame, rel: pd.Series, name: str) -> None:
    fig, axes = plt.subplots(2, 1, sharex=True)
    for c in ["SPY", "CSPX", "VWRD"]:
        axes[0].plot(sl_lr.index, sl_lr[c].cumsum(), color=SLEEVE_COLORS.get(c, DALE_NONSIG),
                     linestyle=SLEEVE_LSTYLES.get(c, "solid"),
                     linewidth=DALE_LINE_EMPH if c != "SPY" else DALE_LINE_WIDTH,
                     label=SLEEVE_LABELS.get(c, "SPY (US-listed)"), zorder=1 if c == "SPY" else 2)
    axes[0].set_ylabel("Cum. log return")
    axes[0].legend(ncol=3, loc="lower left", bbox_to_anchor=(0.0, 1.0), borderaxespad=0.2)
    _relative_panel(axes[1], rel, "1y log return,\nVWRD − CSPX")
    panel_label(axes[0], "a")
    panel_label(axes[1], "b")
    style_dates(axes[1], sl_lr.index)
    finish(fig, name)


def sleeves_in_books(sharpe: dict[str, list[float]], max_dd: dict[str, list[float]], name: str) -> None:
    """sharpe/max_dd: sleeve ('CSPX'/'VWRD') -> values per book."""
    fig, axes = plt.subplots(1, 2)
    for ax, values, ylabel, letter in zip(axes, (sharpe, max_dd), ("Sharpe (excess of T-bills)", "Max drawdown"), "ab"):
        sleeve_bars(ax, values, SLEEVE_COLORS, SLEEVE_LABELS, hatched="VWRD")
        ax.set_ylabel(ylabel)
        panel_label(ax, letter)
    axes[1].yaxis.set_major_locator(MultipleLocator(0.05))
    axes[1].yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    fig_legend(fig, axes[0], ncol=2)
    fig.subplots_adjust(wspace=0.35)
    finish(fig, name)


def world_vs_sp500(eq_lr: pd.DataFrame, rel3: pd.Series, name: str) -> None:
    fig, axes = plt.subplots(2, 1, sharex=True)
    for c, color, ls, label in (("S&P 500", SLEEVE_COLORS["CSPX"], "solid", "S&P 500 (SPY)"),
                                ("World", SLEEVE_COLORS["VWRD"], "dashed", "World proxy (50% SPY + 50% VGTSX)")):
        axes[0].plot(eq_lr.index, eq_lr[c].cumsum(), color=color, linestyle=ls, linewidth=DALE_LINE_EMPH, label=label)
    axes[0].set_ylabel("Cum. log return")
    axes[0].legend(ncol=2, loc="lower left", bbox_to_anchor=(0.0, 1.0), borderaxespad=0.2)
    _relative_panel(axes[1], rel3, "3y log return p.a.,\nWorld − S&P")
    panel_label(axes[0], "a")
    panel_label(axes[1], "b")
    style_dates(axes[1], eq_lr.index)
    finish(fig, name)


def world_sleeve_in_books(sharpe_by_era: dict[str, dict[str, list[float]]], name: str) -> None:
    """sharpe_by_era: era -> sleeve ('S&P 500'/'World') -> Sharpe per book."""
    colors = {"S&P 500": SLEEVE_COLORS["CSPX"], "World": SLEEVE_COLORS["VWRD"]}
    labels = {"S&P 500": "S&P 500 sleeve", "World": "World sleeve"}
    fig, axes = plt.subplots(1, 2, sharey=True)
    for ax, (era, values), letter in zip(axes, sharpe_by_era.items(), "ab"):
        sleeve_bars(ax, values, colors, labels, hatched="World")
        ax.text(0.0, 1.02, era, transform=ax.transAxes, fontsize=DALE_FONT_ANNOT, va="bottom")
        panel_label(ax, letter)
    axes[0].set_ylabel("Sharpe")
    fig_legend(fig, axes[0], ncol=2)
    fig.subplots_adjust(wspace=0.15)
    finish(fig, name)


def _relative_panel(ax, rel: pd.Series, ylabel: str) -> None:
    ax.plot(rel.index, rel, color=DALE_REGLINE, linewidth=DALE_LINE_WIDTH)
    ax.fill_between(rel.index, rel, 0.0, color=DALE_REGLINE, alpha=0.2, linewidth=0)
    ax.axhline(0.0, color="black", linewidth=0.8)
    ax.set_ylabel(ylabel)
