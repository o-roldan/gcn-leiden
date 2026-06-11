"""Baseline runners. Each returns (metrics dict, k, config string).

Protocol notes (thesis experimental design):
  * Classical heuristics report their full partition (no size filter --
    the filter belongs to the proposed architecture, not to them).
  * Deep baselines that need a cluster count receive the ground-truth k,
    mirroring the protocol of Wang et al. (2025) and the deep-clustering
    literature; this favors the baselines, making our comparisons
    conservative.
"""

from gcn_leiden.baselines.classical import run_classical
from gcn_leiden.baselines.deepwalk import run_deepwalk
from gcn_leiden.baselines.dgi import run_dgi
from gcn_leiden.baselines.dmon import run_dmon

RUNNERS = {
    "louvain": run_classical,
    "leiden": run_classical,
    "deepwalk": run_deepwalk,
    "dgi": run_dgi,
    "dmon": run_dmon,
}
