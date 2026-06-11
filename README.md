# GCN-Leiden

One-layer GCN community detection guided by a structural prior, optimizing
Soft Modularity (Q'). Thesis implementation based on the architecture of
Wang et al. (2025), substituting the Louvain prior with Leiden and
quantifying RAM/VRAM scalability.

## Structure

```
gcn_leiden/            core package
├── datasets.py        PyG auto-downloaded benchmarks + SBM generator
├── prior.py           structural pre-detection (Louvain / Leiden) + size filter
├── model.py           one-layer GCN encoder + soft affiliation operator
├── loss.py            soft modularity objective
├── metrics.py         NMI, ARI, Q, DBI (thesis evaluation set)
├── trainer.py         training loop, early stopping, checkpoint restore
├── telemetry.py       peak RAM / VRAM instrumentation
├── results.py         unified results schema (one CSV for all methods)
└── baselines/         louvain, leiden, deepwalk (native), dgi, dmon
run_experiment.py      CLI: GCN run = dataset x prior x seed -> CSV row + history
run_baseline.py        CLI: baseline run = method x dataset x seed -> CSV row
```

## Usage

```bash
# Proposed method (and its Louvain ablation)
uv run python run_experiment.py --dataset cora --prior leiden
uv run python run_experiment.py --dataset cora --prior louvain

# Baselines (same unified results CSV)
uv run python run_baseline.py --method leiden --dataset cora                  # canonical, resolution 1.0
uv run python run_baseline.py --method leiden --dataset cora --resolution 0.3 # prior-alone ablation
uv run python run_baseline.py --method dgi --dataset cora
uv run python run_baseline.py --method dmon --dataset cora
uv run python run_baseline.py --method deepwalk --dataset cora
```

Every dataset is retrieved from the internet (PyTorch Geometric) or
generated locally (SBM) — no pre-processed local files. All runs append to
`results/runs.csv` with one shared schema (method-specific hyperparameters
in the `config` column); GCN runs also dump per-epoch history to
`results/history/` for the convergence study.

**Cloud sharding:** one instance per dataset (dense memory scales with n²,
so the dataset determines machine size); all methods x seeds run inside,
each instance writes `results/runs_<dataset>.csv`; merge = concatenation.

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
  (tr(PᵀBP) = tr(PᵀAP) − ‖dᵀP‖²/2m avoids materializing B), which is
  deliberately deferred.

## Roadmap

1. Sweep driver for methods x datasets x seeds (gcloud, per-dataset shards).
2. Sparse loss path for the 500k-node study (on explicit request only —
   the dense pipeline is the validated reference behavior).

## Citation

Base architecture:

```bibtex
@article{Wang2025,
  author  = {Wang, Hong and Zhang, Yinglong and Zhao, Zhangqi and
             Cai, Zhicong and Xia, Xuewen and Xu, Xing},
  title   = {Simple yet effective heuristic community detection with
             graph convolution network},
  journal = {Scientific Reports},
  volume  = {15},
  number  = {1},
  pages   = {39249},
  year    = {2025},
  doi     = {10.1038/s41598-025-22860-z}
}
```
