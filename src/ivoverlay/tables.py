"""Formatted result tables (consumed by report/report.typ) and their writers."""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from .metrics import series_metrics

METRIC_ROWS = [
    ("avg_annual_return", "Avg annual return", "pct"),
    ("avg_annual_vol", "Avg annual vol", "pct"),
    ("skewness", "Skewness", "num"),
    ("kurtosis", "Kurtosis (excess)", "num"),
    ("downside_vol", "Downside vol", "pct"),
    ("max_drawdown", "Max drawdown", "pct"),
    ("sharpe", "Sharpe", "num"),
    ("sortino", "Sortino", "num"),
    ("calmar", "Calmar", "num"),
]
SHORT_ROWS = ["avg_annual_return", "avg_annual_vol", "max_drawdown", "sharpe", "sortino", "calmar"]

Table = dict[str, list]


def fmt(x: float | None, kind: str) -> str:
    """'pct' -> 4.97%, 'num' -> 0.87; typographic minus; dash for missing."""
    if x is None or not np.isfinite(x):
        return "–"
    s = f"{x:.2%}" if kind == "pct" else f"{x:.2f}"
    return s.replace("-", "−")


def metrics_table(
    series: dict[str, pd.Series],
    turnover: dict[str, float] | None = None,
    rows: list[str] | None = None,
    rf: pd.Series | None = None,
    excess: set[str] | None = None,
) -> Table:
    """{label: log-return series} -> {"header": [...], "rows": [[...], ...]}.

    Columns named in `excess` (funded, total-return series) get Sharpe/Sortino
    over `rf`; with `rf` given and `excess` omitted, every column does.
    """
    excess = set(series) if excess is None and rf is not None else (excess or set())
    m = {k: series_metrics(v, rf if k in excess else None) for k, v in series.items()}
    keys = rows or [r[0] for r in METRIC_ROWS]
    out = [[label] + [fmt(m[c][key], kind) for c in series] for key, label, kind in METRIC_ROWS if key in keys]
    if turnover is not None:
        out.append(["Turnover / yr"] + [fmt(turnover.get(c, np.nan), "pct") for c in series])
    return {"header": ["Metric", *series.keys()], "rows": out}


def write_results(facts: dict, tables: dict[str, Table], res_dir: Path, preamble: str) -> None:
    """results.json for the report, metrics.md for quick reading on GitHub."""
    res_dir.mkdir(exist_ok=True)
    with open(res_dir / "results.json", "w", encoding="utf-8") as f:
        json.dump({"facts": facts, "tables": tables}, f, indent=1, default=float)
    md = ["# Performance tables", "", preamble, ""]
    for name, t in tables.items():
        md += [
            f"## {name}",
            "",
            "| " + " | ".join(h.replace("\n", " · ") for h in t["header"]) + " |",
            "| --- |" + " ---: |" * (len(t["header"]) - 1),
        ]
        md += ["| " + " | ".join(r) + " |" for r in t["rows"]] + [""]
    (res_dir / "metrics.md").write_text("\n".join(md), encoding="utf-8")
