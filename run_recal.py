#!/usr/bin/env python
"""Recalibration sweep for the prior stage (Objetivo 2): one dataset per shard.

Explores the size-filter coefficient beta (T = mean + beta * std) and the
prior resolution gamma, holding the rest of the Wang architecture fixed.
Arms per dataset family:

  * real networks ........ modularity prior at gamma=0.3 (Wang) x beta grid;
                           film additionally runs gamma=1.0 (its Leiden prior
                           collapses to k=1 at 0.3).
  * sbm_* ................ modularity prior at gamma=1.0 x beta grid (at 0.3
                           the partition is a single community, so no beta
                           can pass the strict size filter), plus a
                           Leiden-only CPM arm at gamma=(p_in+p_out)/2
                           (Traag et al. 2019: intra-density > gamma >
                           inter-density; generator defaults 0.05/0.005).

Results land in results/runs_recal_<dataset>.csv; histories are split per
configuration so grid points do not overwrite each other.

Examples:
    python run_recal.py --dataset film --dry-run
    python run_recal.py --dataset sbm_1000_5 --seeds 0,1
"""

import argparse
import subprocess
import sys
import time

PYTHON = sys.executable

BETAS = (-0.5, 0.0, 0.25, 0.5)
PRIORS = ("louvain", "leiden")
SBM_CPM_GAMMA = 0.0275  # midpoint of the generator's p_in=0.05, p_out=0.005


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--seeds", default="0,1,2,3,4",
                        help="comma-separated seeds")
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--eval-every", type=int, default=2)
    parser.add_argument("--results", default=None,
                        help="default: results/runs_recal_<dataset>.csv")
    parser.add_argument("--dry-run", action="store_true",
                        help="print the planned commands without running")
    return parser.parse_args()


def grid_for(dataset):
    """Yield (prior, objective, gamma, beta) arms for one dataset."""
    if dataset.startswith("sbm"):
        gammas = (1.0,)
    elif dataset == "film":
        gammas = (0.3, 1.0)
    else:
        gammas = (0.3,)
    for gamma in gammas:
        for prior in PRIORS:
            for beta in BETAS:
                yield prior, "modularity", gamma, beta
    if dataset.startswith("sbm"):
        for beta in BETAS:
            yield "leiden", "cpm", SBM_CPM_GAMMA, beta


def build_commands(args):
    seeds = [int(s) for s in args.seeds.split(",")]
    results = args.results or f"results/runs_recal_{args.dataset}.csv"

    commands = []
    for prior, objective, gamma, beta in grid_for(args.dataset):
        tag = f"{objective}_g{gamma}_b{beta}"
        history = f"results/history_recal_{args.dataset}/{tag}"
        for seed in seeds:
            commands.append([
                PYTHON, "run_experiment.py",
                "--dataset", args.dataset, "--results", results,
                "--prior", prior, "--prior-objective", objective,
                "--resolution", str(gamma), "--beta", str(beta),
                "--seed", str(seed), "--device", args.device,
                "--eval-every", str(args.eval_every),
                "--history-dir", history])
    return commands


def main():
    args = parse_args()
    commands = build_commands(args)
    print(f"[recal {args.dataset}] {len(commands)} runs planned")

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
