#!/usr/bin/env python
"""Run one baseline: method x dataset x seed.

Examples:
    python run_baseline.py --method louvain --dataset cora                  # canonical (resolution 1.0)
    python run_baseline.py --method leiden --dataset cora --resolution 0.3  # prior-alone ablation
    python run_baseline.py --method dgi --dataset cora --epochs 300
    python run_baseline.py --method dmon --dataset amap

Appends one row to the same unified results CSV as run_experiment.py.
"""

import argparse
import time

import networkx as nx

from gcn_leiden.baselines import RUNNERS
from gcn_leiden.datasets import load_dataset
from gcn_leiden.results import append_result
from gcn_leiden.telemetry import peak_ram_mb, peak_vram_mb


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--method", required=True, choices=sorted(RUNNERS))
    parser.add_argument("--dataset", default="cora")
    parser.add_argument("--seed", type=int, default=24)
    parser.add_argument("--epochs", type=int, default=None,
                        help="training epochs for deep baselines "
                             "(deepwalk default 5, dgi/dmon default 300)")
    parser.add_argument("--resolution", type=float, default=1.0,
                        help="resolution for classical baselines "
                             "(1.0 canonical, 0.3 = prior-alone ablation)")
    parser.add_argument("--objective", default="modularity",
                        choices=["modularity", "cpm"],
                        help="quality function for the leiden baseline")
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--results", default="results/runs.csv")
    return parser.parse_args()


_DEFAULT_EPOCHS = {"deepwalk": 5, "dgi": 300, "dmon": 300}


def main():
    args = parse_args()
    epochs = args.epochs or _DEFAULT_EPOCHS.get(args.method)

    data = load_dataset(args.dataset)
    graph = nx.from_numpy_array(data.adj)
    print(f"[{args.method} | {args.dataset}] n={data.num_nodes} "
          f"F={data.num_features}")

    start = time.perf_counter()
    metrics, k, config = RUNNERS[args.method](
        args.method, data, graph, seed=args.seed, epochs=epochs,
        resolution=args.resolution, objective=args.objective,
        device=args.device)
    runtime = time.perf_counter() - start

    print(" ".join(f"{key}={val:.4f}" for key, val in sorted(metrics.items())))
    print(f"k={k} runtime={runtime:.1f}s ram={peak_ram_mb():.0f}MB")

    append_result(
        args.results, method=args.method, dataset=args.dataset,
        seed=args.seed, k=k, epochs=epochs or "",
        runtime_s=round(runtime, 2),
        nmi=metrics["nmi"], ari=metrics["ari"], q=metrics["q"],
        dbi=metrics.get("dbi", float("nan")),
        ram_peak_mb=round(peak_ram_mb(), 1),
        vram_peak_mb=round(peak_vram_mb(), 1), config=config)
    print(f"appended -> {args.results}")


if __name__ == "__main__":
    main()
