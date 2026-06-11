"""DMoN baseline: GCN encoder + DMoNPooling (Tsitsulin et al. 2023).

The pooling layer optimizes a relaxed modularity with a collapse
regularizer; cluster assignments come directly from its soft assignment
matrix (no downstream k-means). k is the ground-truth number of classes
(see baselines/__init__.py). Dense, like the rest of the pipeline.
"""

import numpy as np
import torch
import torch.nn.functional as F
from torch import nn
from torch_geometric.nn import DMoNPooling, GCNConv

from gcn_leiden.metrics import evaluate_partition
from gcn_leiden.results import config_string

_DEFAULTS = {"hidden": 512, "lr": 1e-3}


class _DMoN(nn.Module):
    def __init__(self, in_channels, hidden_channels, k):
        super().__init__()
        self.conv = GCNConv(in_channels, hidden_channels)
        self.pool = DMoNPooling([hidden_channels], k)

    def forward(self, x, edge_index, adj):
        h = F.selu(self.conv(x, edge_index))
        s, _, _, spectral_loss, ortho_loss, cluster_loss = self.pool(
            h.unsqueeze(0), adj.unsqueeze(0))
        return s.squeeze(0), h, spectral_loss + ortho_loss + cluster_loss


def run_dmon(method, data, graph, seed=24, epochs=300, device="cpu", **_):
    del method
    torch.manual_seed(seed)
    np.random.seed(seed)
    device = torch.device(device)

    feat = torch.from_numpy(data.feat).to(device)
    edge_index = torch.from_numpy(np.array(np.nonzero(data.adj))).to(device)
    adj = torch.from_numpy(data.adj).to(device)
    k = int(np.unique(data.label).size)

    model = _DMoN(data.num_features, _DEFAULTS["hidden"], k).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=_DEFAULTS["lr"])

    model.train()
    for _epoch in range(epochs):
        optimizer.zero_grad()
        _, _, loss = model(feat, edge_index, adj)
        loss.backward()
        optimizer.step()

    model.eval()
    with torch.no_grad():
        assignments, embeddings, _ = model(feat, edge_index, adj)
    pred = assignments.argmax(dim=1).cpu().numpy()
    embeddings = embeddings.cpu().numpy()

    metrics = evaluate_partition(pred, data.label, graph,
                                 embeddings=embeddings)
    config = config_string(epochs=epochs, k_source="ground_truth",
                           **_DEFAULTS)
    return metrics, k, config
