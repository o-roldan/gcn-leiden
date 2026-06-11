"""GCN-Leiden: one-layer GCN community detection with a structural prior.

Thesis implementation based on Wang et al. (2025), substituting the
Louvain prior with Leiden. Modules:

    datasets  -- internet-retrievable dataset loaders (PyG) + SBM generator
    prior     -- structural pre-detection (Louvain/Leiden) and size filter
    model     -- one-layer GCN encoder + soft community affiliation
    loss      -- soft modularity objective
    metrics   -- partition quality metrics (NMI, ACC, F1, ARI, Q, DBI)
    trainer   -- training loop with early stopping
"""
