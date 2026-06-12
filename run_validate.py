#!/usr/bin/env python
"""Validation sweep for the dispersion-gated filter (filtro recalibrado).

Two claims to verify, one dataset per shard invocation:

  * sbm_* ........ with variant=recalibrado the CV gate deactivates the
                   filter, the gamma=1.0 modularity prior keeps every
                   planted block, and the previously-impossible runs now
                   execute (expected NMI ~= 1 given the prior is exact).
  * real nets .... no-regression control: the CV gate never fires
                   (CV >~ 1) and >= coincides with > away from ties, so
                   results must match the Wang-variant runs exactly.

Results land in results/runs_validate_<dataset>.csv.

Examples:
    python run_validate.py --dataset sbm_5000_10 --dry-run
    python run_validate.py --dataset cora --seeds 0,1
"""

import argparse
import subprocess
import sys
import time

PYTHON = sys.executable
PRIORS = ("louvain", "leiden")


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--seeds", default="0,1,2,3,4",
                        help="comma-separated seeds")
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--eval-every", type=int, default=2)
    parser.add_argument("--results", default=None,
                        help="default: results/runs_validate_<dataset>.csv")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def build_commands(args):
    seeds = [int(s) for s in args.seeds.split(",")]
    results = args.results or f"results/runs_validate_{args.dataset}.csv"
    gamma = "1.0" if args.dataset.startswith("sbm") else "0.3"

    commands = []
    for prior in PRIORS:
        history = (f"results/history_validate_{args.dataset}/"
                   f"recalibrado_g{gamma}_{prior}")
        for seed in seeds:
            commands.append([
                PYTHON, "run_experiment.py",
                "--dataset", args.dataset, "--results", results,
                "--prior", prior, "--resolution", gamma,
                "--beta", "0.5", "--filter-variant", "recalibrado",
                "--seed", str(seed), "--device", args.device,
                "--eval-every", str(args.eval_every),
                "--history-dir", history])
    return commands


def main():
    args = parse_args()
    commands = build_commands(args)
    print(f"[validate {args.dataset}] {len(commands)} runs planned")

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
