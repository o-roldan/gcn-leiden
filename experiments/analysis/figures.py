"""Multi-panel seaborn figures — one image each, never one-per-dataset.

Every figure aggregates seeds automatically (seaborn's ``errorbar="sd"`` draws
the mean line/bar with a std band), and uses faceting (``col``/``row``) so a
whole sweep lands in a single figure. Pass ``savepath`` to write a PDF/PNG.
"""

import seaborn as sns

from experiments.analysis.load import add_node_counts

sns.set_theme(style="whitegrid", context="paper")


def convergence_figure(history, datasets=None, quantities=("loss", "grad_norm"),
                       hue="method", savepath=None):
    """Loss and gradient-norm vs epoch, faceted by dataset (rows = quantity).

    The gradient-norm row is drawn on a log scale (norms span orders of
    magnitude). ``grad_norm`` is skipped automatically for runs logged before
    it was tracked.
    """
    quantities = [q for q in quantities if q in history.columns]
    data = history if datasets is None else \
        history[history["dataset"].isin(datasets)]
    long = data.melt(
        id_vars=["epoch", "method", "dataset", "seed"],
        value_vars=quantities, var_name="quantity", value_name="value")
    grid = sns.relplot(
        data=long, x="epoch", y="value", hue=hue, row="quantity",
        col="dataset", kind="line", errorbar="sd",
        facet_kws={"sharey": False, "margin_titles": True},
        height=2.4, aspect=1.3)
    for (quantity, _dataset), ax in getattr(grid, "axes_dict", {}).items():
        if quantity == "grad_norm":
            ax.set_yscale("log")
    return _finish(grid, savepath)


def scalability_figure(runs, resources=("ram_peak_mb", "vram_peak_mb",
                                        "runtime_s"),
                       sbm_only=True, hue="method", savepath=None):
    """Resource use vs graph size (n), faceted by resource, log x-axis.

    Defaults to the SBM size sweep (controlled n); set ``sbm_only=False`` to
    include the empirical datasets via their known node counts.
    """
    data = add_node_counts(runs)
    if sbm_only:
        data = data[data["dataset"].astype(str).str.startswith("sbm")]
    resources = [r for r in resources if r in data.columns]
    long = data.melt(
        id_vars=["method", "dataset", "seed", "n_nodes"],
        value_vars=resources, var_name="resource", value_name="value"
    ).dropna(subset=["value", "n_nodes"])
    grid = sns.relplot(
        data=long, x="n_nodes", y="value", hue=hue, col="resource",
        kind="line", marker="o", errorbar="sd",
        facet_kws={"sharey": False}, height=3.0, aspect=1.2)
    for ax in grid.axes.flat:
        ax.set_xscale("log")
    return _finish(grid, savepath)


def recal_figure(recal_runs, metric="nmi", x="beta", hue="method",
                 col="dataset", col_wrap=3, savepath=None):
    """Metric vs a swept hyperparameter (default beta), faceted by dataset.

    Requires the swept columns to exist — load the recal runs with
    ``load_runs(pattern="runs_recal_*.csv", exclude=())`` so ``parse_config``
    has unpacked ``beta``/``resolution`` from the config string.
    """
    if x not in recal_runs.columns:
        raise KeyError(
            f"column {x!r} not found; load recal runs so parse_config unpacks "
            "it from the config string")
    style = ("resolution" if recal_runs.get("resolution") is not None
             and recal_runs["resolution"].nunique() > 1 else None)
    grid = sns.relplot(
        data=recal_runs, x=x, y=metric, hue=hue, style=style, col=col,
        col_wrap=col_wrap, kind="line", marker="o", errorbar="sd",
        facet_kws={"sharey": False}, height=3.0, aspect=1.2)
    return _finish(grid, savepath)


def comparison_barplot(runs, metric="nmi", x="dataset", hue="method",
                       savepath=None):
    """Single grouped bar chart of one metric (seeds -> mean + std bars).

    A visual alternative to ``tables.latex_table``; prefer the table for the
    thesis main text and use this for talks.
    """
    grid = sns.catplot(
        data=runs, x=x, y=metric, hue=hue, kind="bar", errorbar="sd",
        height=4.0, aspect=2.2)
    grid.set_xticklabels(rotation=45, ha="right")
    return _finish(grid, savepath)


def _finish(grid, savepath):
    if savepath:
        grid.figure.savefig(savepath, bbox_inches="tight", dpi=200)
    return grid
