# Experiments

Thesis research harness for the GCN-Leiden architecture: baselines, single-run
CLIs, sweep drivers, and cloud-sharding deploy. Everything here depends on the
`gcn_leiden` library; the library never imports this package. Run all commands
from the **repository root**.

```
experiments/
├── baselines/    louvain, leiden, deepwalk (native), dgi, dmon
├── harness/      results.py (shared CSV schema), telemetry.py (RAM/VRAM),
│                 sweep.py (shared run-loop for every sweep driver)
├── runners/      gcn.py, baseline.py — one run -> one CSV row
├── sweeps/       full.py, recal.py, validate.py — grids of runner commands
├── analysis/     load tidy CSVs -> LaTeX tables + multi-panel figures
├── deploy/       launch_shards.sh — one GCE instance per dataset shard
└── fetch_results.sh   rsync results back from the GCS bucket
```

## Single runs

```bash
# Proposed method (and its Louvain ablation)
uv run python -m experiments.runners.gcn --dataset cora --prior leiden
uv run python -m experiments.runners.gcn --dataset cora --prior louvain

# Baselines (same unified results CSV)
uv run python -m experiments.runners.baseline --method leiden --dataset cora                  # canonical, resolution 1.0
uv run python -m experiments.runners.baseline --method leiden --dataset cora --resolution 0.3 # prior-alone ablation
uv run python -m experiments.runners.baseline --method dgi --dataset cora
uv run python -m experiments.runners.baseline --method dmon --dataset cora
uv run python -m experiments.runners.baseline --method deepwalk --dataset cora
```

Every run appends to `results/runs.csv` with one shared schema
(method-specific hyperparameters in the `config` column); GCN runs also dump
per-epoch history to `results/history/` for the convergence study.

## Sweeps

Each sweep runs every configuration for ONE dataset (one cloud shard) and
writes into its own **batch** directory, `results/<batch>/runs_<dataset>.csv`
(plus `history_<dataset>/`); merging shards = concatenation. `--batch`
defaults to the launch timestamp, so a new sweep never touches earlier
results; pass the same name to group several sweeps.

```bash
uv run python -m experiments.sweeps.full --dataset cora                  # full method x seed sweep
uv run python -m experiments.sweeps.full --dataset amap --dry-run        # show planned runs + output dir
uv run python -m experiments.sweeps.full --dataset cora --batch rerun-v2 # named batch
uv run python -m experiments.sweeps.recal --dataset sbm_1000_5           # beta x gamma prior sweep
uv run python -m experiments.sweeps.validate --dataset cora              # dispersion-gated filter check
```

```
results/
├── runs.csv, history/          ad-hoc single runs (tracked in git)
├── runs_*.csv, history/...     pre-batch cloud results (batch "unbatched")
└── <batch>/                    one sweep or one cloud launch
    └── <shard>/                cloud only: one prefix per instance
        ├── runs_<dataset>.csv
        └── history_<dataset>/
```

Nothing overwrites: run CSVs are append-only, a rerun's history is written
as `..._seed<N>-2.csv`, cloud shards upload to their own prefix with
`--no-clobber`, and fetching never replaces local files.

**Adding an experiment:** drop a new module in `experiments/sweeps/` that
builds a list of runner commands (use `gcn_command` / `baseline_command` from
`experiments.harness.sweep`) and hands them to `run_sweep`. The argument
plumbing, dry-run printing, sequential execution, and failure reporting are all
provided by `experiments/harness/sweep.py`.

## Cloud sharding

One instance per dataset (dense memory scales with n², so the dataset
determines machine size); all methods x seeds run inside, each instance writes
`results/runs_<dataset>.csv`.

```bash
PROJECT=my-project BUCKET=gs://my-bucket REPO=https://github.com/<user>/gcn-leiden.git \
  ./experiments/deploy/launch_shards.sh           # all shards, BATCH=<timestamp>
BATCH=sbm-fix PROJECT=... BUCKET=... REPO=... \
  ./experiments/deploy/launch_shards.sh sbm       # named batch

# when the shards finish, pull their CSVs back down (no-clobber rsync):
BUCKET=gs://my-bucket ./experiments/fetch_results.sh
```

Each shard uploads to `$BUCKET/results/<BATCH>/<shard>/`. The launcher
refuses, before creating any instance, a shard whose prefix already exists.

## Analysis (tables + figures)

Install the reporting deps once (`uv sync --extra analysis`), then turn the
CSVs into the results section with a few calls. Seeds are aggregated
automatically (mean ± std); figures are multi-panel (faceted), so you get a
handful of artifacts, not one image per dataset.

```python
from experiments.analysis import (load_runs, load_history, latex_table,
                                   convergence_figure, scalability_figure,
                                   recal_figure)

runs = load_runs()                                   # results/**/runs*.csv, every batch
sbm = load_runs(batches="sbm-fix")                   # only one batch (and its shards)
print(latex_table(runs, metric="nmi", caption="NMI", label="tab:nmi"))
convergence_figure(load_history(), savepath="fig_convergence.pdf")  # loss + grad-norm
scalability_figure(runs, savepath="fig_scaling.pdf")                # RAM/VRAM/runtime vs n

recal = load_runs(pattern="runs_recal_*.csv", exclude=())           # unpacks beta/gamma
recal_figure(recal, savepath="fig_recal.pdf")
```

`load_runs` unpacks the packed `config` column into real columns (so `beta`,
`resolution`, etc. are filterable/plottable) and adds `n_nodes` and `batch`
(`load_history` adds `batch` too, and skips recal/validate histories by
default). `latex_table`
bold-faces the best method per dataset.

## Experiment matrix (thesis Objetivo 3-4)

| Method                  | 9 empirical datasets¹ | SBM (quality) | SBM scaling → 500k² |
|-------------------------|:---------------------:|:-------------:|:-------------------:|
| Louvain                 | **ready**             | **ready**     | CPU reference       |
| Leiden                  | **ready**             | **ready**     | CPU reference       |
| DeepWalk                | **ready**             | **ready**     | —                   |
| DGI                     | **ready**             | **ready**     | yes (VRAM)          |
| DMoN                    | **ready**             | **ready**     | yes (VRAM)          |
| GCN-Louvain (Wang 2025) | **ready**             | **ready**     | yes                 |
| GCN-Leiden (thesis)     | **ready**             | **ready**     | yes                 |

¹ cora, citeseer, pubmed, cocs, cophysics, amac, amap, film, wikics.
² Pending: runs on Google Cloud; requires the sparse-loss refactor
  (tr(PᵀBP) = tr(PᵀAP) − ‖dᵀP‖²/2m avoids materializing B), deliberately
  deferred. The dense pipeline is the validated reference behavior.
