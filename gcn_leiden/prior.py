"""Structural prior: community pre-detection and dynamic size filter.

Phase 1 of the architecture (Wang et al. 2025): a modularity heuristic
produces an initial partition; communities whose size does not reach the
dynamic threshold T = mean + beta * std are discarded; the survivors
define k and anchor the latent centroids.

The Leiden prior (Traag et al. 2019, via leidenalg) defaults to the
resolution-scaled modularity objective (RBConfiguration) so that the
Leiden-vs-Louvain ablation changes only the algorithm, not the objective.
CPM is available behind the `objective` flag for exploration.
"""

from dataclasses import dataclass

import igraph as ig
import leidenalg
import networkx as nx
import numpy as np

_LEIDEN_OBJECTIVES = {
    "modularity": leidenalg.RBConfigurationVertexPartition,
    "cpm": leidenalg.CPMVertexPartition,
}


@dataclass
class StructuralPrior:
    communities: list       # list[set[int]] surviving communities
    threshold: float        # dynamic size threshold T
    initial_count: int      # communities before filtering (K_0)

    @property
    def k(self):
        return len(self.communities)


def detect_communities(graph, method="louvain", resolution=0.3, seed=123,
                       objective="modularity"):
    """Run the structural pre-detection heuristic."""
    if method == "louvain":
        if objective != "modularity":
            raise ValueError("Louvain only optimizes modularity.")
        return nx.community.louvain_communities(
            graph, resolution=resolution, threshold=1e-09, seed=seed)
    if method == "leiden":
        return _leiden_communities(graph, resolution, seed, objective)
    raise ValueError(f"Unknown prior method: {method}")


def _leiden_communities(graph, resolution, seed, objective):
    if objective not in _LEIDEN_OBJECTIVES:
        raise ValueError(f"Unknown Leiden objective: {objective}. "
                         f"Available: {sorted(_LEIDEN_OBJECTIVES)}")
    # Build the igraph from the edge list with an explicit vertex count so
    # node ids are preserved and isolated nodes are kept.
    igraph_graph = ig.Graph(n=graph.number_of_nodes(),
                            edges=list(graph.edges()))
    partition = leidenalg.find_partition(
        igraph_graph, _LEIDEN_OBJECTIVES[objective],
        resolution_parameter=resolution, seed=seed)
    return [set(community) for community in partition]


def filter_by_size(communities, beta=0.5, variant="wang", cv_threshold=0.25):
    """Apply the dynamic size filter T = mean + beta * std (Wang et al. Eq. 6).

    Variants:
      * "wang" .......... strict comparison len(c) > T, replicating Wang's
                          published code (the paper text prints >=; the
                          discrepancy is documented in the thesis).
      * "recalibrado" ... the thesis' dispersion-gated filter: when the size
                          distribution is near-uniform (coefficient of
                          variation below cv_threshold) there are no noise
                          micro-communities to purge and the filter
                          deactivates; otherwise it applies the paper's
                          len(c) >= T. Real networks sit at CV >~ 1 and SBM
                          partitions at ~1e-2, so cv_threshold is uncritical.
    """
    sizes = np.array([len(c) for c in communities], dtype=np.float64)
    threshold = sizes.mean() + beta * sizes.std()
    if variant == "wang":
        return [c for c in communities if len(c) > threshold], threshold
    if variant == "recalibrado":
        if sizes.std() / sizes.mean() < cv_threshold:
            return list(communities), threshold
        return [c for c in communities if len(c) >= threshold], threshold
    raise ValueError(f"Unknown filter variant: {variant}")


def build_prior(graph, method="louvain", resolution=0.3, beta=0.5, seed=123,
                objective="modularity", filter_variant="wang"):
    initial = detect_communities(graph, method, resolution, seed, objective)
    selected, threshold = filter_by_size(initial, beta, filter_variant)
    if not selected:
        raise RuntimeError(
            f"Size filter (beta={beta}) discarded every community; "
            "lower beta or inspect the partition.")
    return StructuralPrior(communities=selected, threshold=threshold,
                           initial_count=len(initial))
