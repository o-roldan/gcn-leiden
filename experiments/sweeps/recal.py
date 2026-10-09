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

Results land in results/<batch>/runs_recal_<dataset>.csv; histories are
split per configuration so grid points do not overwrite each other.

Examples:
    python -m experiments.sweeps.recal --dataset film --dry-run
    python -m experiments.sweeps.recal --dataset sbm_1000_5 --seeds 0,1
"""

import argparse

from experiments.harness.sweep import (
    add_common_sweep_args,
    batch_dir,
    gcn_command,
    parse_seeds,
    run_sweep,
)

BETAS = (-0.5, 0.0, 0.25, 0.5)
PRIORS = ("louvain", "leiden")
SBM_CPM_GAMMA = 0.0275  # midpoint of the generator's p_in=0.05, p_out=0.005


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
    seeds = parse_seeds(args.seeds)
    out = batch_dir(args)
    results = args.results or str(out / f"runs_recal_{args.dataset}.csv")

    commands = []
    for prior, objective, gamma, beta in grid_for(args.dataset):
        tag = f"{objective}_g{gamma}_b{beta}"
        history = out / f"history_recal_{args.dataset}" / tag
        for seed in seeds:
            commands.append(gcn_command(
                "--dataset", args.dataset, "--results", results,
                "--prior", prior, "--prior-objective", objective,
                "--resolution", gamma, "--beta", beta,
                "--seed", seed, "--device", args.device,
                "--eval-every", args.eval_every,
                "--history-dir", history))
    return commands


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    add_common_sweep_args(parser)
    args = parser.parse_args()
    run_sweep(f"recal {args.dataset}", build_commands(args),
              dry_run=args.dry_run, output=batch_dir(args))


if __name__ == "__main__":
    main()
