"""Classical heuristic baselines: Louvain and Leiden, full partition.

No size filter is applied: these baselines answer (a) how the canonical
heuristic performs (resolution=1.0) and (b) what the GCN adds over the
raw prior partition (resolution=0.3, Wang's prior setting).
"""

import numpy as np

from gcn_leiden.metrics import evaluate_partition
from gcn_leiden.prior import detect_communities
from gcn_leiden.results import config_string


def run_classical(method, data, graph, seed=123, resolution=1.0,
                  objective="modularity", **_):
    communities = detect_communities(
        graph, method=method, resolution=resolution, seed=seed,
        objective=objective)

    pred = np.empty(data.num_nodes, dtype=np.int64)
    for community_id, community in enumerate(communities):
        pred[list(community)] = community_id

    metrics = evaluate_partition(pred, data.label, graph)
    config = config_string(resolution=resolution, objective=objective)
    return metrics, len(communities), config
