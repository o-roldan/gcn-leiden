#!/usr/bin/env python
"""Full sweep: run every method x seed for ONE dataset (one cloud shard).

Results land in results/runs_<dataset>.csv; merging shards = concatenation.

Examples:
    python -m experiments.sweeps.full --dataset cora                  # full sweep, 5 seeds
    python -m experiments.sweeps.full --dataset cora --seeds 24       # single seed
    python -m experiments.sweeps.full --dataset amap --dry-run        # show planned runs
"""

import argparse

from experiments.harness.sweep import (
    add_common_sweep_args,
    baseline_command,
    gcn_command,
    parse_seeds,
    run_sweep,
)

# Classical heuristics run at the canonical resolution and at the
# prior-alone ablation resolution (see baselines/classical.py).
CLASSICAL_RESOLUTIONS = (1.0, 0.3)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    add_common_sweep_args(parser)
    parser.add_argument("--methods",
                        default="louvain,leiden,deepwalk,dgi,dmon,"
                                "gcn-louvain,gcn-leiden",
                        help="comma-separated subset to run")
    return parser.parse_args()


def build_commands(args):
    seeds = parse_seeds(args.seeds)
    methods = args.methods.split(",")
    results = args.results or f"results/runs_{args.dataset}.csv"
    common = ["--dataset", args.dataset, "--results", results]

    commands = []
    for seed in seeds:
        for method in methods:
            if method in ("gcn-louvain", "gcn-leiden"):
                commands.append(gcn_command(
                    *common, "--prior", method.removeprefix("gcn-"),
                    "--seed", seed, "--device", args.device,
                    "--eval-every", args.eval_every,
                    "--history-dir", f"results/history_{args.dataset}"))
            elif method in ("louvain", "leiden"):
                for resolution in CLASSICAL_RESOLUTIONS:
                    commands.append(baseline_command(
                        *common, "--method", method, "--seed", seed,
                        "--resolution", resolution))
            else:
                commands.append(baseline_command(
                    *common, "--method", method, "--seed", seed,
                    "--device", args.device))
    return commands


def main():
    args = parse_args()
    run_sweep(args.dataset, build_commands(args), dry_run=args.dry_run)


if __name__ == "__main__":
    main()
