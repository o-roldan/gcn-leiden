"""GCN-Leiden: one-layer GCN community detection with a structural prior.

Thesis implementation based on Wang et al. (2025), substituting the
Louvain prior with Leiden. Modules:

    datasets  -- internet-retrievable dataset loaders (PyG) + SBM generator
    prior     -- structural pre-detection (Louvain/Leiden) and size filter
    model     -- one-layer GCN encoder + soft community affiliation
    loss      -- soft modularity objective
    metrics   -- partition quality metrics (NMI, ACC, F1, ARI, Q, DBI)
    trainer   -- training loop with early stopping

Typical use::

    from gcn_leiden import (load_dataset, build_prior,
                            CommunityAffiliation, communities_to_index,
                            train, TrainConfig)

    data = load_dataset("cora")
    graph = nx.from_numpy_array(data.adj)
    prior = build_prior(graph, method="leiden")
    model = CommunityAffiliation(data.num_features, 512, k=prior.k)
    ...

The thesis experiment harness (baselines, sweeps, telemetry) lives in the
separate top-level ``experiments`` package and is not imported here.
"""

from .datasets import (
    GraphData,
    available_datasets,
    generate_sbm,
    load_dataset,
)
from .loss import modularity_matrix, soft_modularity_loss
from .metrics import evaluate_partition
from .model import (
    CommunityAffiliation,
    OneLayerGCN,
    communities_to_index,
)
from .prior import (
    StructuralPrior,
    build_prior,
    detect_communities,
    filter_by_size,
)
from .trainer import TrainConfig, TrainResult, train

__all__ = [
    # datasets
    "load_dataset",
    "available_datasets",
    "generate_sbm",
    "GraphData",
    # prior
    "build_prior",
    "detect_communities",
    "filter_by_size",
    "StructuralPrior",
    # model
    "CommunityAffiliation",
    "OneLayerGCN",
    "communities_to_index",
    # loss
    "modularity_matrix",
    "soft_modularity_loss",
    # trainer
    "train",
    "TrainConfig",
    "TrainResult",
    # metrics
    "evaluate_partition",
]
