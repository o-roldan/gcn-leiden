"""Partition quality metrics, matching the thesis evaluation set:

    NMI  -- agreement with the reference partition (information-theoretic)
    ARI  -- agreement with the reference partition (chance-adjusted pairs)
    Q    -- Newman modularity of the predicted partition (no reference)
    DBI  -- Davies-Bouldin index of the latent embeddings (no reference)
"""

from collections import defaultdict

import networkx as nx
import numpy as np
from sklearn import metrics as sk_metrics


def nmi(pred, true):
    return sk_metrics.normalized_mutual_info_score(true, pred)


def ari(pred, true):
    return sk_metrics.adjusted_rand_score(true, pred)


def modularity(graph, pred):
    """Newman modularity Q of the predicted partition on the graph."""
    communities = defaultdict(list)
    for node, label in enumerate(np.asarray(pred)):
        communities[int(label)].append(node)
    return nx.community.modularity(graph, list(communities.values()))


def davies_bouldin(embeddings, pred):
    if np.unique(pred).size < 2:
        return float("nan")
    return sk_metrics.davies_bouldin_score(embeddings, pred)


def evaluate_partition(pred, true, graph, embeddings=None):
    """All partition metrics as a dict. Inputs are never mutated."""
    pred = np.asarray(pred).copy()
    true = np.asarray(true)
    results = {
        "nmi": nmi(pred, true),
        "ari": ari(pred, true),
        "q": modularity(graph, pred),
    }
    if embeddings is not None:
        results["dbi"] = davies_bouldin(embeddings, pred)
    return results
