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


def soft_modularity_loss_sparse(p, adj, degrees, two_m):
    """Same -Q' without materializing B (sparse path).

    Uses tr(P^T B P) = tr(P^T A P) - ||P^T d||^2 / 2m with A a sparse
    adjacency without self-loops: memory O(E + n k) instead of O(n^2).
    Equal to soft_modularity_loss up to floating-point summation order.
    """
    if two_m == 0:
        return torch.zeros((), device=p.device)
    pd = p.t() @ degrees
    return -((p * torch.sparse.mm(adj, p)).sum() - (pd * pd).sum() / two_m) / two_m
