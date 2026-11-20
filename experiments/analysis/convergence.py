"""Convergence of the soft-modularity optimisation: Leiden vs Louvain prior.

Answers the thesis question "does a higher-quality prior accelerate the
optimisation of Q'?" from the stored training histories (one row per
evaluation: every 2 epochs on cora/citeseer/amap/film, 5 on amac/wikics and
10 on pubmed/cocs, as set per shard in experiments/deploy/launch_shards.sh).
Q'_0 is the first evaluated value, not epoch 0. Since ``loss = -alpha * Q'`` with alpha = 1e-3,
Q' is recovered as ``-loss / alpha``.

Two speed measures, which must agree before drawing a conclusion:

  * relative -- epochs until a run covers ``frac`` of its *own* gain
    (``Q'_0 + frac * (Q'_max - Q'_0)``);
  * fixed target -- epochs until a run reaches the *same* Q' bar for both
    priors: ``frac * min(mean Q'_max Louvain, mean Q'_max Leiden)`` per
    dataset. Every run reaches it for frac <= 0.95; at frac = 0.99 one Cora
    run (gcn-louvain, seed 3) falls short and its pair is dropped (n = 34).

Runs are paired by seed (the seed fixes weight initialisation) and compared
with a Wilcoxon signed-rank test; zero differences (frequent, because of the
coarse 2/5/10-epoch evaluation grid) are dropped by the test and reported
separately. The five seeds of a dataset share the same prior, so they are not
independent replicates of the prior's effect.

It also reports the NMI-vs-Q' misalignment: the epoch of peak NMI against the
epoch of maximum Q', and the NMI lost by continuing to maximise Q'.

Usage::

    python -m experiments.analysis.convergence [results_dir]
"""

import sys

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

from experiments.analysis.load import load_history

LOSS_SCALE = 1e-3                     # alpha in L = -alpha * Q'
PRIORS = ("gcn-louvain", "gcn-leiden")
# Actor (film) is excluded by default: the Leiden prior collapses to k=1 there,
# so Q' is identically 0 and no convergence is defined.
DATASETS = ("cora", "citeseer", "pubmed", "cocs", "amac", "amap", "wikics")


def load_prior_histories(results_dir="results", seeds=range(5),
                         datasets=DATASETS):
    """Histories of both GCN variants for the given seeds, with a Q' column."""
    hist = load_history(results_dir)
    hist = hist[hist.method.isin(PRIORS) & hist.seed.isin(list(seeds))
                & hist.dataset.isin(datasets)].copy()
    hist["q_soft"] = -hist["loss"] / LOSS_SCALE
    return hist.sort_values(["dataset", "method", "seed", "epoch"])


def run_summary(hist, fracs=(0.5, 0.9, 0.95, 0.99)):
    """One row per run: Q' levels, relative convergence epochs, NMI timing."""
    rows = []
    for (dataset, method, seed), run in hist.groupby(
            ["dataset", "method", "seed"]):
        q, epochs, nmi = run.q_soft.to_numpy(), run.epoch.to_numpy(), \
            run.nmi.to_numpy()
        q0, qmax = q[0], q.max()
        row = dict(dataset=dataset, method=method, seed=seed,
                   last_epoch=epochs[-1], q0=q0, qmax=qmax,
                   ep_qmax=epochs[q.argmax()], nmi_peak=nmi.max(),
                   ep_nmi_peak=epochs[nmi.argmax()],
                   nmi_at_qmax=nmi[q.argmax()])
        for frac in fracs:
            row[f"t{round(frac * 100)}"] = _first_epoch(
                q, epochs, q0 + frac * (qmax - q0))
        rows.append(row)
    return pd.DataFrame(rows)


def fixed_target_epochs(hist, summary, frac=0.95):
    """Epochs each run needs to reach a Q' bar shared by both priors."""
    rows = []
    for dataset, runs in summary.groupby("dataset"):
        target = frac * runs.groupby("method").qmax.mean().min()
        for (method, seed), run in hist[hist.dataset == dataset].groupby(
                ["method", "seed"]):
            rows.append(dict(dataset=dataset, method=method, seed=seed,
                             target=target, epochs=_first_epoch(
                                 run.q_soft.to_numpy(),
                                 run.epoch.to_numpy(), target)))
    return pd.DataFrame(rows)


def paired_comparison(frame, value):
    """Leiden minus Louvain per seed-pair: counts and Wilcoxon p-value."""
    wide = frame.pivot_table(index=["dataset", "seed"], columns="method",
                             values=value).dropna()
    diff = wide["gcn-leiden"] - wide["gcn-louvain"]
    pvalue = (wilcoxon(wide["gcn-leiden"], wide["gcn-louvain"]).pvalue
              if (diff != 0).any() else 1.0)
    return dict(n=len(diff), leiden_lower=int((diff < 0).sum()),
                leiden_higher=int((diff > 0).sum()),
                ties=int((diff == 0).sum()), median_diff=float(diff.median()),
                pvalue=float(pvalue))


def latex_fixed_target_table(fixed):
    """Rows ``Red & Q' objetivo & Louvain & Leiden`` (mean ± std epochs)."""
    names = {"cora": "Cora", "citeseer": "CiteSeer", "pubmed": "PubMed",
             "cocs": "Coauthor CS", "amac": "Amazon Computers",
             "amap": "Amazon Photo", "wikics": "WikiCS"}
    lines = []
    for dataset in DATASETS:
        runs = fixed[fixed.dataset == dataset]
        if runs.empty:
            continue
        cells = [f"{runs.target.iloc[0]:.3f}"]
        for method in PRIORS:
            ep = runs[runs.method == method].epochs
            cells.append(f"{ep.mean():.1f}{{\\scriptsize$\\pm${ep.std():.1f}}}")
        lines.append(f"{names[dataset]} & " + " & ".join(cells) + r" \\")
    return "\n".join(lines)


def report(results_dir="results"):
    hist = load_prior_histories(results_dir)
    summary = run_summary(hist)
    print(f"runs: {len(summary)}")
    for frac in (0.9, 0.95, 0.99):
        fixed = fixed_target_epochs(hist, summary, frac)
        print(f"fixed target {frac:.2f}:",
              paired_comparison(fixed, "epochs"))
    table = latex_fixed_target_table(fixed_target_epochs(hist, summary, 0.95))
    for value in ("t95", "q0", "qmax"):
        print(f"{value}:", paired_comparison(summary, value))
    early = (summary.ep_nmi_peak < summary.ep_qmax).sum()
    print(f"NMI peaks before max Q' in {early}/{len(summary)} runs")
    loss = (summary.nmi_peak - summary.nmi_at_qmax).groupby(
        summary.dataset).mean().round(3)
    print("mean NMI lost from peak to max-Q' epoch:", loss.to_dict())
    late = summary.groupby("dataset").ep_qmax.mean().round(1)
    print("mean epoch of max Q':", late.to_dict())
    print("\nLaTeX rows (95% fixed target):\n" + table)
    return summary


def _first_epoch(q, epochs, level):
    reached = q >= level
    return float(epochs[np.argmax(reached)]) if reached.any() else np.nan


if __name__ == "__main__":
    report(sys.argv[1] if len(sys.argv) > 1 else "results")
