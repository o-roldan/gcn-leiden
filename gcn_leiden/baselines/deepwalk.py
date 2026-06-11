"""DeepWalk baseline: uniform random walks + skip-gram, native torch.

Implemented without pyg-lib/torch-cluster (no macOS wheels for this torch
version): walks are sampled with numpy over the adjacency lists and the
skip-gram objective with negative sampling is optimized in plain torch.
Embeddings are clustered with k-means using the ground-truth k
(protocol of Wang et al. 2025; see baselines/__init__.py).
"""

import numpy as np
import torch
import torch.nn.functional as F
from sklearn.cluster import KMeans
from torch import nn

from gcn_leiden.metrics import evaluate_partition
from gcn_leiden.results import config_string

_DEFAULTS = {"embedding_dim": 128, "walk_length": 80, "context_size": 10,
             "walks_per_node": 10, "lr": 0.01, "batch_size": 8192}


def run_deepwalk(method, data, graph, seed=24, epochs=5, device="cpu", **_):
    del method
    rng = np.random.default_rng(seed)
    torch.manual_seed(seed)
    np.random.seed(seed)
    device = torch.device(device)

    indptr, indices = _adjacency_csr(data.adj)

    n = data.num_nodes
    dim = _DEFAULTS["embedding_dim"]
    center_emb = nn.Embedding(n, dim, sparse=True).to(device)
    context_emb = nn.Embedding(n, dim, sparse=True).to(device)
    optimizer = torch.optim.SparseAdam(
        list(center_emb.parameters()) + list(context_emb.parameters()),
        lr=_DEFAULTS["lr"])

    for _epoch in range(epochs):
        walks = _sample_walks(indptr, indices, rng, _DEFAULTS["walk_length"],
                              _DEFAULTS["walks_per_node"])
        centers, contexts = _skipgram_pairs(walks, _DEFAULTS["context_size"])
        order = rng.permutation(len(centers))
        for start in range(0, len(order), _DEFAULTS["batch_size"]):
            batch = order[start:start + _DEFAULTS["batch_size"]]
            center = torch.from_numpy(centers[batch]).to(device)
            context = torch.from_numpy(contexts[batch]).to(device)
            negative = torch.randint(n, (len(batch),), device=device)

            optimizer.zero_grad()
            z = center_emb(center)
            pos_score = (z * context_emb(context)).sum(dim=1)
            neg_score = (z * context_emb(negative)).sum(dim=1)
            loss = (F.binary_cross_entropy_with_logits(
                        pos_score, torch.ones_like(pos_score))
                    + F.binary_cross_entropy_with_logits(
                        neg_score, torch.zeros_like(neg_score)))
            loss.backward()
            optimizer.step()

    embeddings = center_emb.weight.detach().cpu().numpy()
    k = int(np.unique(data.label).size)
    pred = KMeans(n_clusters=k, n_init=10,
                  random_state=seed).fit_predict(embeddings)
    metrics = evaluate_partition(pred, data.label, graph,
                                 embeddings=embeddings)
    config = config_string(epochs=epochs, k_source="ground_truth",
                           implementation="native", **_DEFAULTS)
    return metrics, k, config


def _adjacency_csr(adj):
    """CSR neighbor lists from the dense 0/1 adjacency."""
    src, dst = np.nonzero(adj)            # row-major: src is sorted
    degrees = np.bincount(src, minlength=adj.shape[0])
    indptr = np.concatenate(([0], np.cumsum(degrees)))
    return indptr.astype(np.int64), dst.astype(np.int64)


def _sample_walks(indptr, indices, rng, walk_length, walks_per_node):
    """Uniform random walks from every node, fully vectorized.

    Dead ends (isolated nodes) repeat in place.
    """
    n = len(indptr) - 1
    degrees = np.diff(indptr)
    starts = np.tile(np.arange(n), walks_per_node)
    walks = np.empty((len(starts), walk_length), dtype=np.int64)
    walks[:, 0] = starts
    for step in range(1, walk_length):
        current = walks[:, step - 1]
        deg = degrees[current]
        offsets = (rng.random(len(current))
                   * np.maximum(deg, 1)).astype(np.int64)
        positions = np.minimum(indptr[current] + offsets, len(indices) - 1)
        walks[:, step] = np.where(deg > 0, indices[positions], current)
    return walks


def _skipgram_pairs(walks, context_size):
    """All (center, context) pairs within the sliding window, both sides."""
    centers, contexts = [], []
    for offset in range(1, context_size + 1):
        centers.append(walks[:, :-offset].ravel())
        contexts.append(walks[:, offset:].ravel())
        centers.append(walks[:, offset:].ravel())
        contexts.append(walks[:, :-offset].ravel())
    return np.concatenate(centers), np.concatenate(contexts)
