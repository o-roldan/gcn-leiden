#!/usr/bin/env python
"""Run one GCN experiment: dataset x prior x seed.

Examples:
    python run_experiment.py --dataset cora --prior leiden
    python run_experiment.py --dataset sbm_5000_10 --prior louvain --seed 7

Appends one row to the unified results CSV and dumps the training history
(loss + metrics per evaluation) for the convergence study.
"""

import argparse
import csv
from pathlib import Path

import networkx as nx
import numpy as np
import torch

from gcn_leiden.datasets import load_dataset
from gcn_leiden.model import CommunityAffiliation, communities_to_index
from gcn_leiden.prior import build_prior
from gcn_leiden.results import append_result, config_string
from gcn_leiden.telemetry import peak_ram_mb, peak_vram_mb
from gcn_leiden.trainer import TrainConfig, train


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", default="cora",
                        help="dataset name or sbm spec (e.g. sbm_5000_10)")
    parser.add_argument("--prior", default="louvain",
                        choices=["louvain", "leiden"])
    parser.add_argument("--prior-objective", default="modularity",
                        choices=["modularity", "cpm"],
                        help="Leiden quality function (modularity keeps the "
                             "Louvain ablation single-variable)")
    parser.add_argument("--resolution", type=float, default=0.3)
    parser.add_argument("--beta", type=float, default=0.5,
                        help="deviation coefficient of the size filter T")
    parser.add_argument("--filter-variant", default="wang",
                        choices=["wang", "recalibrado"],
                        help="wang: strict > of the official code; "
                             "recalibrado: dispersion-gated >= (thesis)")
    parser.add_argument("--prior-seed", type=int, default=123)
    parser.add_argument("--hidden", type=int, default=512)
    parser.add_argument("--temperature", type=float, default=30.0)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--weight-decay", type=float, default=5e-3)
    parser.add_argument("--loss-scale", type=float, default=1e-3)
    parser.add_argument("--epochs", type=int, default=300)
    parser.add_argument("--eval-every", type=int, default=2)
    parser.add_argument("--patience", type=int, default=200)
    parser.add_argument("--seed", type=int, default=24)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--results", default="results/runs.csv")
    parser.add_argument("--history-dir", default="results/history",
                        help="where to dump per-run training history")
    return parser.parse_args()


def main():
    args = parse_args()
    method = f"gcn-{args.prior}"

    data = load_dataset(args.dataset)
    graph = nx.from_numpy_array(data.adj)
    prior = build_prior(graph, method=args.prior, resolution=args.resolution,
                        beta=args.beta, seed=args.prior_seed,
                        objective=args.prior_objective,
                        filter_variant=args.filter_variant)
    print(f"[{method} | {args.dataset}] n={data.num_nodes} "
          f"F={data.num_features} | prior: {prior.initial_count} -> "
          f"k={prior.k} (T={prior.threshold:.1f})")

    np.random.seed(args.seed)
    torch.manual_seed(args.seed)

    feat = torch.from_numpy(data.feat)
    edge_index = torch.from_numpy(np.array(np.nonzero(data.adj)))
    adj = torch.from_numpy(data.adj)
    community_index = communities_to_index(prior.communities)

    model = CommunityAffiliation(
        data.num_features, args.hidden, k=prior.k,
        temperature=args.temperature)
    cfg = TrainConfig(epochs=args.epochs, lr=args.lr,
                      weight_decay=args.weight_decay,
                      loss_scale=args.loss_scale, eval_every=args.eval_every,
                      patience=args.patience, device=args.device)
    result = train(model, feat, edge_index, adj, graph, data.label,
                   community_index, cfg)

    print(f"best (min-loss checkpoint): {_fmt(result.best)}")
    print(f"peak (over training):       {_fmt(result.peak)}")
    print(f"epochs={result.epochs_ran} runtime={result.runtime_s:.1f}s "
          f"ram={peak_ram_mb():.0f}MB")

    config = config_string(
        prior_objective=args.prior_objective, resolution=args.resolution,
        beta=args.beta, filter_variant=args.filter_variant,
        prior_seed=args.prior_seed, hidden=args.hidden,
        temperature=args.temperature, lr=args.lr,
        weight_decay=args.weight_decay, loss_scale=args.loss_scale,
        k0=prior.initial_count, threshold=round(prior.threshold, 2))
    append_result(
        args.results, method=method, dataset=args.dataset, seed=args.seed,
        k=prior.k, epochs=result.epochs_ran,
        runtime_s=round(result.runtime_s, 2),
        nmi=result.best["nmi"], ari=result.best["ari"], q=result.best["q"],
        dbi=result.best.get("dbi", float("nan")),
        peak_nmi=result.peak["nmi"], peak_ari=result.peak["ari"],
        peak_q=result.peak["q"], peak_dbi=result.peak.get("dbi",
                                                          float("nan")),
        ram_peak_mb=round(peak_ram_mb(), 1),
        vram_peak_mb=round(peak_vram_mb(), 1), config=config)
    print(f"appended -> {args.results}")

    _dump_history(Path(args.history_dir), method, args, result.history)


def _fmt(values):
    return " ".join(f"{key}={val:.4f}" for key, val in sorted(values.items()))


def _dump_history(history_dir, method, args, history):
    if not history:
        return
    history_dir.mkdir(parents=True, exist_ok=True)
    path = history_dir / f"{method}_{args.dataset}_seed{args.seed}.csv"
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(history[0].keys()))
        writer.writeheader()
        writer.writerows(history)
    print(f"history  -> {path}")


if __name__ == "__main__":
    main()
