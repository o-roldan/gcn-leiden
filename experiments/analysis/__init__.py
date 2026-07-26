"""Results analysis: tidy loaders, LaTeX tables, and multi-panel figures.

Turns the run/history CSVs into the thesis results section with a handful of
calls. Requires the optional `analysis` dependencies::

    uv pip install -e '.[analysis]'

Typical use::

    from experiments.analysis import load_runs, load_history, latex_table, \
        convergence_figure, scalability_figure

    runs = load_runs()                                    # main sweep
    print(latex_table(runs, metric="nmi", caption="...", label="tab:nmi"))
    convergence_figure(load_history(), savepath="fig_convergence.pdf")
    scalability_figure(runs, savepath="fig_scaling.pdf")

    recal = load_runs(pattern="runs_recal_*.csv", exclude=())
    recal_figure(recal, savepath="fig_recal.pdf")
"""

from experiments.analysis.figures import (
    comparison_barplot,
    convergence_figure,
    recal_figure,
    scalability_figure,
)
from experiments.analysis.load import (
    add_node_counts,
    load_history,
    load_runs,
    node_count,
    parse_config,
)
from experiments.analysis.tables import latex_table, summary_table

__all__ = [
    # load
    "load_runs",
    "load_history",
    "parse_config",
    "add_node_counts",
    "node_count",
    # tables
    "summary_table",
    "latex_table",
    # figures
    "convergence_figure",
    "scalability_figure",
    "recal_figure",
    "comparison_barplot",
]
