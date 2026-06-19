# GCN-Leiden

One-layer GCN community detection guided by a structural prior, optimizing
Soft Modularity (Q'). Thesis implementation based on the architecture of
Wang et al. (2025), substituting the Louvain prior with **Leiden** (Traag et
al. 2019) and quantifying RAM/VRAM scalability.

The architecture has four phases: (1) a structural prior pre-detects
communities and a dynamic size filter fixes the cluster count *k*; (2) a
single graph convolution encodes nodes; (3) community centroids and a
temperature softmax yield a soft affiliation matrix P; (4) training maximizes
soft modularity over P.

## Install

```bash
uv add gcn-leiden            # or: pip install gcn-leiden
# editable, from a clone:
uv pip install -e .
```

The `gcn_leiden` package is the architecture and nothing else. Datasets are
retrieved from the internet (PyTorch Geometric) or generated locally (SBM) —
no pre-processed local files.

## Library layout

```
gcn_leiden/
├── datasets.py   PyG auto-downloaded benchmarks + SBM generator
├── prior.py      structural pre-detection (Louvain / Leiden) + size filter
├── model.py      one-layer GCN encoder + soft affiliation operator
├── loss.py       soft modularity objective
├── metrics.py    NMI, ARI, Q, DBI
└── trainer.py    training loop, early stopping, checkpoint restore
```

## Reuse example

```python
import networkx as nx
import numpy as np
import torch

from gcn_leiden import (
    load_dataset, build_prior, CommunityAffiliation,
    communities_to_index, train, TrainConfig,
)

data = load_dataset("cora")                     # or "sbm_5000_10"
graph = nx.from_numpy_array(data.adj)

prior = build_prior(graph, method="leiden")     # phase 1: prior + size filter
model = CommunityAffiliation(data.num_features, 512, k=prior.k)

feat = torch.from_numpy(data.feat)
edge_index = torch.from_numpy(np.array(np.nonzero(data.adj)))
adj = torch.from_numpy(data.adj)
idx = communities_to_index(prior.communities)

result = train(model, feat, edge_index, adj, graph, data.label, idx,
               TrainConfig(epochs=300))
print(result.best)   # {'nmi': ..., 'ari': ..., 'q': ..., 'dbi': ...}
```

`build_prior` accepts `method="louvain"` for the original Wang prior, plus
`resolution`, `beta` (size-filter coefficient), `objective`, and
`filter_variant`. See the docstrings in `gcn_leiden/prior.py`,
`gcn_leiden/model.py`, and `gcn_leiden/trainer.py`.

## Thesis experiments

The baseline comparisons (DGI, DMoN, DeepWalk, classical heuristics), sweep
drivers, and cloud-sharding tooling used to validate the architecture live in
the separate top-level [`experiments/`](experiments/README.md) package. They
depend on this library; the library never depends on them, so reusers can
ignore that directory entirely.

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
