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

Results land in results/<batch>/runs_validate_<dataset>.csv.

Examples:
    python -m experiments.sweeps.validate --dataset sbm_5000_10 --dry-run
    python -m experiments.sweeps.validate --dataset cora --seeds 0,1
"""

import argparse

from experiments.harness.sweep import (
    add_common_sweep_args,
    batch_dir,
    gcn_command,
    parse_seeds,
    run_sweep,
)

PRIORS = ("louvain", "leiden")


def build_commands(args):
    seeds = parse_seeds(args.seeds)
    out = batch_dir(args)
    results = args.results or str(out / f"runs_validate_{args.dataset}.csv")
    gamma = "1.0" if args.dataset.startswith("sbm") else "0.3"

    commands = []
    for prior in PRIORS:
        history = (out / f"history_validate_{args.dataset}"
                   / f"recalibrado_g{gamma}_{prior}")
        for seed in seeds:
            commands.append(gcn_command(
                "--dataset", args.dataset, "--results", results,
                "--prior", prior, "--resolution", gamma,
                "--beta", "0.5", "--filter-variant", "recalibrado",
                "--seed", seed, "--device", args.device,
                "--eval-every", args.eval_every,
                "--history-dir", history))
    return commands


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    add_common_sweep_args(parser)
    args = parser.parse_args()
    run_sweep(f"validate {args.dataset}", build_commands(args),
              dry_run=args.dry_run, output=batch_dir(args))


if __name__ == "__main__":
    main()
