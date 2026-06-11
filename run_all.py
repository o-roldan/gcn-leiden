#!/usr/bin/env python
"""Sweep driver: run every method x seed for ONE dataset (one cloud shard).

Each run executes in its own subprocess so the peak-RAM telemetry of one
method cannot contaminate another's. Results land in
results/runs_<dataset>.csv; merging shards = concatenating CSVs.

Examples:
    python run_all.py --dataset cora                  # full sweep, 5 seeds
    python run_all.py --dataset cora --seeds 24       # single seed
    python run_all.py --dataset amap --dry-run        # show planned runs
"""

import argparse
import subprocess
import sys
import time

PYTHON = sys.executable

# Classical heuristics run at the canonical resolution and at the
# prior-alone ablation resolution (see baselines/classical.py).
CLASSICAL_RESOLUTIONS = (1.0, 0.3)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--seeds", default="0,1,2,3,4",
                        help="comma-separated seeds")
    parser.add_argument("--methods",
                        default="louvain,leiden,deepwalk,dgi,dmon,"
                                "gcn-louvain,gcn-leiden",
                        help="comma-separated subset to run")
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--eval-every", type=int, default=2,
                        help="evaluation cadence for GCN runs (raise to 10 "
                             "on large datasets to cut metric overhead)")
    parser.add_argument("--results", default=None,
                        help="default: results/runs_<dataset>.csv")
    parser.add_argument("--dry-run", action="store_true",
                        help="print the planned commands without running")
    return parser.parse_args()


def build_commands(args):
    seeds = [int(s) for s in args.seeds.split(",")]
    methods = args.methods.split(",")
    results = args.results or f"results/runs_{args.dataset}.csv"
    common = ["--dataset", args.dataset, "--results", results]

    commands = []
    for seed in seeds:
        for method in methods:
            if method in ("gcn-louvain", "gcn-leiden"):
                commands.append([
                    PYTHON, "run_experiment.py", *common,
                    "--prior", method.removeprefix("gcn-"),
                    "--seed", str(seed), "--device", args.device,
                    "--eval-every", str(args.eval_every),
                    "--history-dir", f"results/history_{args.dataset}"])
            elif method in ("louvain", "leiden"):
                for resolution in CLASSICAL_RESOLUTIONS:
                    commands.append([
                        PYTHON, "run_baseline.py", *common,
                        "--method", method, "--seed", str(seed),
                        "--resolution", str(resolution)])
            else:
                commands.append([
                    PYTHON, "run_baseline.py", *common,
                    "--method", method, "--seed", str(seed),
                    "--device", args.device])
    return commands


def main():
    args = parse_args()
    commands = build_commands(args)
    print(f"[{args.dataset}] {len(commands)} runs planned")

    if args.dry_run:
        for command in commands:
            print("  " + " ".join(command[1:]))
        return

    failures = []
    start = time.perf_counter()
    for index, command in enumerate(commands, 1):
        label = " ".join(command[2:])
        print(f"--- [{index}/{len(commands)}] {label}")
        completed = subprocess.run(command)
        if completed.returncode != 0:
            failures.append(label)
            print(f"    FAILED (exit {completed.returncode}) — continuing")

    elapsed = time.perf_counter() - start
    print(f"\ndone: {len(commands) - len(failures)}/{len(commands)} runs ok "
          f"in {elapsed/60:.1f} min")
    if failures:
        print("failed runs:")
        for label in failures:
            print(f"  {label}")
        sys.exit(1)


if __name__ == "__main__":
    main()
