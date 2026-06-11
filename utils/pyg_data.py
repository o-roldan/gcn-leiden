"""PyG-based dataset adapter.

Drop-in replacement for utils.load_data.load_data that retrieves every
dataset from the internet (PyTorch Geometric auto-download) or generates
it locally (SBM), instead of reading pre-processed local .npy files.

Supported dataset names:
    cora, citeseer, pubmed      -> Planetoid (citation)
    cocs, cophysics             -> Coauthor CS / Physics (co-authorship)
    amac, amap                  -> Amazon Computers / Photo (co-purchase)
    film                        -> Actor co-occurrence
    wikics                      -> WikiCS
    sbm[_n_k[_pin_pout]]        -> generated Stochastic Block Model, e.g.
                                   "sbm" (defaults), "sbm_5000_10",
                                   "sbm_5000_10_0.05_0.005"

Returns the same Data(feature, label, adj) triple the training script
expects: feature as torch.float32 (or numpy), label as 1-D numpy int,
adj as dense symmetric 0/1 numpy array without self-loops.
"""

import re
import warnings

import networkx as nx
import numpy as np
import torch
from torch_geometric.datasets import Actor, Amazon, Coauthor, Planetoid, WikiCS
from torch_geometric.utils import remove_self_loops, to_undirected

from utils.data_processor import numpy_to_torch
from utils.load_data import Data

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

# SBM defaults: k communities of equal size, intra/inter edge probabilities
_SBM_DEFAULTS = {"n": 1000, "k": 5, "p_in": 0.05, "p_out": 0.005,
                 "feat_dim": 64, "noise": 1.0}


def _pyg_to_arrays(data):
    """Convert a PyG data object to (feat, label, adj) numpy arrays."""
    edge_index = to_undirected(data.edge_index)
    edge_index, _ = remove_self_loops(edge_index)
    n = data.num_nodes

    _warn_if_large(n)
    adj = np.zeros((n, n), dtype=np.float32)
    src, dst = edge_index.numpy()
    adj[src, dst] = 1.0
    adj[dst, src] = 1.0

    feat = data.x.numpy().astype(np.float32)
    label = data.y.numpy().astype(np.int64)
    return feat, label, adj


def _warn_if_large(n):
    """The training pipeline is dense: adj and the modularity matrix are
    n x n. Warn when that footprint stops being laptop-friendly."""
    gib = n * n * 4 / 2**30
    if gib > 2.0:
        warnings.warn(
            f"{n} nodes -> each dense n x n matrix takes ~{gib:.1f} GiB; "
            "the pipeline allocates several. Consider the sparse path "
            "before running graphs of this size.")


def generate_sbm(n=None, k=None, p_in=None, p_out=None,
                 feat_dim=None, noise=None, seed=123):
    """Generate an SBM graph with Gaussian-mixture node features.

    Each community draws a random center in R^feat_dim and its nodes get
    center + N(0, noise^2) so that attributes carry the planted signal,
    mirroring the attributed-graph setting of the benchmark datasets.
    """
    cfg = dict(_SBM_DEFAULTS)
    for key, val in zip(("n", "k", "p_in", "p_out", "feat_dim", "noise"),
                        (n, k, p_in, p_out, feat_dim, noise)):
        if val is not None:
            cfg[key] = val

    rng = np.random.default_rng(seed)
    sizes = [cfg["n"] // cfg["k"]] * cfg["k"]
    sizes[0] += cfg["n"] - sum(sizes)  # absorb the remainder

    graph = nx.stochastic_block_model(
        sizes, _block_probs(cfg["k"], cfg["p_in"], cfg["p_out"]), seed=seed)
    _warn_if_large(cfg["n"])
    adj = nx.to_numpy_array(graph, dtype=np.float32)

    label = np.concatenate(
        [np.full(s, c, dtype=np.int64) for c, s in enumerate(sizes)])
    centers = rng.normal(0.0, 3.0, size=(cfg["k"], cfg["feat_dim"]))
    feat = (centers[label]
            + rng.normal(0.0, cfg["noise"], size=(cfg["n"], cfg["feat_dim"]))
            ).astype(np.float32)
    return feat, label, adj


def _block_probs(k, p_in, p_out):
    probs = np.full((k, k), p_out)
    np.fill_diagonal(probs, p_in)
    return probs.tolist()


def _parse_sbm_name(name):
    """Parse 'sbm', 'sbm_5000_10' or 'sbm_5000_10_0.05_0.005'."""
    match = re.fullmatch(
        r"sbm(?:_(\d+)_(\d+)(?:_([\d.]+)_([\d.]+))?)?", name)
    if match is None:
        raise ValueError(f"Unrecognized SBM dataset name: {name}")
    n, k, p_in, p_out = match.groups()
    return {"n": int(n) if n else None,
            "k": int(k) if k else None,
            "p_in": float(p_in) if p_in else None,
            "p_out": float(p_out) if p_out else None}


def load_data(dataset_path, dataset_name,
              feature_type="tensor", adj_type="npy", label_type="npy",
              adj_loop=False, adj_norm=False, adj_symmetric=True, t=None):
    """Same signature and return contract as utils.load_data.load_data."""
    if adj_loop or adj_norm or t is not None:
        raise NotImplementedError(
            "adj_loop/adj_norm/t are not supported by the PyG adapter; "
            "the training script applies its own normalization.")

    name = dataset_name.lower()
    if name.startswith("sbm"):
        feat, label, adj = generate_sbm(**_parse_sbm_name(name))
    elif name in _PYG_LOADERS:
        root = dataset_path + "datasets_pyg"
        feat, label, adj = _pyg_to_arrays(_PYG_LOADERS[name](root)[0])
    else:
        raise ValueError(
            f"Unknown dataset '{dataset_name}'. Available: "
            f"{sorted(_PYG_LOADERS)} or sbm[_n_k[_pin_pout]].")

    if feature_type == "tensor":
        feat = numpy_to_torch(feat)
    if adj_type == "tensor":
        adj = numpy_to_torch(adj)
    if label_type == "tensor":
        label = numpy_to_torch(label)
    return Data(feat, label, adj)
