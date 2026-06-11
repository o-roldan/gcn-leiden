"""Soft modularity objective (Phase 4).

L = -alpha * Q' with Q' = tr(P^T B P) / 2m, where B is the modularity
matrix of the graph without self-loops (Wang et al. 2025).
"""

import torch


def modularity_matrix(adj):
    """Dense modularity matrix B = A - d d^T / 2m (self-loops removed)."""
    adj = adj.clone()
    adj.fill_diagonal_(0)
    degrees = adj.sum(dim=0, keepdim=True)
    return adj - degrees.t() @ degrees / adj.sum()


def soft_modularity_loss(p, mod_matrix, two_m):
    """Negative soft modularity -Q'. Minimizing it maximizes Q'."""
    if two_m == 0:
        return torch.zeros((), device=p.device)
    return -(p.t() @ mod_matrix @ p).trace() / two_m
