"""Model: one-layer GCN encoder + soft community affiliation operator.

Phases 2-3 of the architecture (Wang et al. 2025): a single graph
convolution produces L2-normalized embeddings; community centroids are
the means of member embeddings; a temperature softmax over node-centroid
similarities yields the soft affiliation matrix P.

This module reproduces the reference implementation of Wang et al.
(github.com/wuanghoong/Less-is-More) operation by operation, including
its parameter-initialization sequence, so that runs with the same seed
match the reference results. Do not reorder or "optimize" these
operations without re-validating against the reference runs.
"""

import torch
from torch import nn
from torch_geometric.nn import GCNConv
from torch_geometric.nn.inits import reset, uniform


class OneLayerGCN(nn.Module):
    """Single graph convolution with PReLU activation."""

    def __init__(self, in_channels, hidden_channels):
        super().__init__()
        self.conv = GCNConv(in_channels, hidden_channels)
        self.activation = nn.PReLU(hidden_channels)

    def forward(self, x, edge_index):
        return self.activation(self.conv(x, edge_index))


class CommunityAffiliation(nn.Module):
    """Soft node-community affiliation guided by a structural prior.

    forward() returns:
        z   (n, d)  L2-normalized node embeddings
        mu  (k, d)  community centroids (means over prior communities)
        p   (n, k)  soft affiliation matrix, rows on the simplex
    """

    def __init__(self, in_channels, hidden_channels, k, temperature=30.0):
        super().__init__()
        self.encoder = OneLayerGCN(in_channels, hidden_channels)
        # The two attributes below are NOT used by the method. They replicate
        # the DGI-wrapper leftovers of the reference implementation
        # (discriminator weight + random centroid init) in the exact original
        # order, because they consume RNG draws: removing them changes the
        # encoder initialization under a fixed seed and therefore the results.
        self.weight = nn.Parameter(
            torch.Tensor(hidden_channels, hidden_channels))
        reset(self.encoder)
        uniform(hidden_channels, self.weight)
        self.init = torch.rand(k, hidden_channels)
        self.temperature = temperature

    def forward(self, x, edge_index, community_index):
        z = self.encoder(x, edge_index)
        # Row-wise L2 normalization written exactly as in the reference
        # implementation (dense diagonal product) to preserve parity.
        z = torch.diag(1. / torch.norm(z, p=2, dim=1)) @ z
        mu = torch.stack([torch.mean(z.index_select(0, idx), dim=0)
                          for idx in community_index])
        similarity = z @ mu.t()
        p = torch.softmax(self.temperature * similarity, dim=1)
        return z, mu, p


def communities_to_index(communities, device=None):
    """Convert prior communities (iterables of node ids) to index tensors.

    Preserves the iteration order of each community (as the reference
    implementation does) so floating-point summation order is identical.
    """
    return [torch.tensor(list(c), dtype=torch.long, device=device)
            for c in communities]
