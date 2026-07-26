"""Aggregate-over-seeds tables: the main comparison artifact.

A method x dataset grid of ``mean ± std`` for one metric. ``summary_table``
returns a readable pivot; ``latex_table`` emits a booktabs table with the best
entry per dataset in bold.
"""

import pandas as pd

# Metrics where a smaller value is better (so "best" = column min).
LOWER_IS_BETTER = {"dbi", "peak_dbi", "ram_peak_mb", "vram_peak_mb", "runtime_s"}


def summary_table(runs, metric="nmi", index="method", columns="dataset"):
    """Pivot of ``mean ± std`` strings over seeds (for quick inspection)."""
    grouped = runs.groupby([index, columns])[metric].agg(["mean", "std"])
    cells = grouped.apply(_format_cell, axis=1)
    return cells.unstack(columns)


def latex_table(runs, metric="nmi", index="method", columns="dataset",
                caption=None, label=None):
    """booktabs LaTeX table; best value per column is bold-faced."""
    means = runs.groupby([index, columns])[metric].mean().unstack(columns)
    stds = runs.groupby([index, columns])[metric].std().unstack(columns)
    best = (means.idxmin() if metric in LOWER_IS_BETTER else means.idxmax())

    def cell(i, c):
        mean = means.loc[i, c]
        if pd.isna(mean):
            return ""
        std = stds.loc[i, c]
        text = f"{mean:.3f}" + (f" $\\pm$ {std:.3f}" if pd.notna(std) else "")
        return rf"\textbf{{{text}}}" if best[c] == i else text

    table = pd.DataFrame(
        {c: {i: cell(i, c) for i in means.index} for c in means.columns})
    body = table.to_latex(
        escape=False, column_format="l" + "r" * len(table.columns))
    if caption is None and label is None:
        return body
    parts = ["\\begin{table}[t]", "\\centering"]
    if caption:
        parts.append(f"\\caption{{{caption}}}")
    if label:
        parts.append(f"\\label{{{label}}}")
    parts += [body.rstrip(), "\\end{table}"]
    return "\n".join(parts)


def _format_cell(row):
    if pd.isna(row["std"]):
        return f"{row['mean']:.3f}"
    return f"{row['mean']:.3f} ± {row['std']:.3f}"
