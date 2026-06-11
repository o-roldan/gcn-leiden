"""Dataset loading: every dataset is internet-retrievable or generated.

Benchmark graphs come from PyTorch Geometric (auto-downloaded on first
use); synthetic graphs are Stochastic Block Models generated locally.
No pre-processed local files are required.
"""

import re
import warnings
from dataclasses import dataclass

import networkx as nx
import numpy as np
from torch_geometric.datasets import Actor, Amazon, Coauthor, Planetoid, WikiCS
from torch_geometric.utils import remove_self_loops, to_undirected

_PYG_LOADERS = {
    "cora":      lambda root: Planetoid(root, name="Cora"),
    "citeseer":  lambda root: Planetoid(root, name="CiteSeer"),
    "pubmed":    lambda root: Planetoid(root, name="PubMed"),
    "cocs":      lambda root: Coauthor(root, name="CS"),
    "cophysics": lambda root: Coauthor(root, name="Physics"),
    "amac":      lambda root: Amazon(root, name="Computers"),
    "amap":      lambda root: Amazon(root, name="Photo"),
    "film":      lambda root: Actor(root + "/film"),
    "wikics":    lambda root: WikiCS(root + "/wikics", is_undirected=True),
}

_SBM_DEFAULTS = {"n": 1000, "k": 5, "p_in": 0.05, "p_out": 0.005,
                 "feat_dim": 64, "noise": 1.0}


@dataclass
class GraphData:
    """An attributed graph: features, ground-truth labels, dense adjacency."""
    feat: np.ndarray    # (n, F) float32
    label: np.ndarray   # (n,)   int64
    adj: np.ndarray     # (n, n) float32, symmetric 0/1, no self-loops

    @property
    def num_nodes(self):
        return self.adj.shape[0]

    @property
    def num_features(self):
        return self.feat.shape[1]


def available_datasets():
    return sorted(_PYG_LOADERS) + ["sbm[_n_k[_pin_pout]]"]


def load_dataset(name, root="datasets_pyg"):
    """Load a benchmark dataset by name, or generate an SBM graph.

    SBM names: "sbm" (defaults), "sbm_5000_10", "sbm_5000_10_0.05_0.005".
    """
    name = name.lower()
    if name.startswith("sbm"):
        return generate_sbm(**_parse_sbm_name(name))
    if name in _PYG_LOADERS:
        return _from_pyg(_PYG_LOADERS[name](root)[0])
    raise ValueError(
        f"Unknown dataset '{name}'. Available: {available_datasets()}")


def generate_sbm(n=None, k=None, p_in=None, p_out=None,
                 feat_dim=None, noise=None, seed=123):
    """SBM graph with Gaussian-mixture node features.

    Each community draws a random center in R^feat_dim and its nodes get
    center + N(0, noise^2), so attributes carry the planted signal as in
    the attributed benchmark datasets.
    """
    cfg = dict(_SBM_DEFAULTS)
    overrides = {"n": n, "k": k, "p_in": p_in, "p_out": p_out,
                 "feat_dim": feat_dim, "noise": noise}
    cfg.update({key: val for key, val in overrides.items() if val is not None})

    rng = np.random.default_rng(seed)
    sizes = [cfg["n"] // cfg["k"]] * cfg["k"]
    sizes[0] += cfg["n"] - sum(sizes)

    probs = np.full((cfg["k"], cfg["k"]), cfg["p_out"])
    np.fill_diagonal(probs, cfg["p_in"])
    graph = nx.stochastic_block_model(sizes, probs.tolist(), seed=seed)
    _warn_if_dense_unfriendly(cfg["n"])
    adj = nx.to_numpy_array(graph, dtype=np.float32)

    label = np.concatenate(
        [np.full(s, c, dtype=np.int64) for c, s in enumerate(sizes)])
    centers = rng.normal(0.0, 3.0, size=(cfg["k"], cfg["feat_dim"]))
    feat = (centers[label]
            + rng.normal(0.0, cfg["noise"], size=(cfg["n"], cfg["feat_dim"]))
            ).astype(np.float32)
    return GraphData(feat=feat, label=label, adj=adj)


def _from_pyg(data):
    edge_index = to_undirected(data.edge_index)
    edge_index, _ = remove_self_loops(edge_index)
    n = data.num_nodes

    _warn_if_dense_unfriendly(n)
    adj = np.zeros((n, n), dtype=np.float32)
    src, dst = edge_index.numpy()
    adj[src, dst] = 1.0
    adj[dst, src] = 1.0

    return GraphData(feat=data.x.numpy().astype(np.float32),
                     label=data.y.numpy().astype(np.int64),
                     adj=adj)


def _warn_if_dense_unfriendly(n):
    """The pipeline is dense: adjacency and modularity matrices are n x n."""
    gib = n * n * 4 / 2**30
    if gib > 2.0:
        warnings.warn(
            f"{n} nodes -> each dense n x n matrix takes ~{gib:.1f} GiB; "
            "the pipeline allocates several. Use the sparse path (pending) "
            "before running graphs of this size.")


def _parse_sbm_name(name):
    match = re.fullmatch(r"sbm(?:_(\d+)_(\d+)(?:_([\d.]+)_([\d.]+))?)?", name)
    if match is None:
        raise ValueError(f"Unrecognized SBM dataset name: {name}")
    n, k, p_in, p_out = match.groups()
    return {"n": int(n) if n else None,
            "k": int(k) if k else None,
            "p_in": float(p_in) if p_in else None,
            "p_out": float(p_out) if p_out else None}
