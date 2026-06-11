"""DGI baseline: PyG DeepGraphInfomax with a one-layer GCN encoder.

Standard setting of Velickovic et al. (2019): hidden 512, feature-shuffle
corruption, sigmoid-mean readout. Embeddings are clustered with k-means
using the ground-truth k (see baselines/__init__.py).
"""

import math

import numpy as np
import torch
from sklearn.cluster import KMeans
from torch import nn
from torch_geometric.nn import DeepGraphInfomax, GCNConv

from gcn_leiden.metrics import evaluate_partition
from gcn_leiden.results import config_string

_DEFAULTS = {"hidden": 512, "lr": 1e-3, "patience": 20}


class _Encoder(nn.Module):
    def __init__(self, in_channels, hidden_channels):
        super().__init__()
        self.conv = GCNConv(in_channels, hidden_channels)
        self.activation = nn.PReLU(hidden_channels)

    def forward(self, x, edge_index):
        return self.activation(self.conv(x, edge_index))


def _corruption(x, edge_index):
    return x[torch.randperm(x.size(0))], edge_index


def _summary(z, *args, **kwargs):
    return torch.sigmoid(z.mean(dim=0))


def run_dgi(method, data, graph, seed=24, epochs=300, device="cpu", **_):
    del method
    torch.manual_seed(seed)
    np.random.seed(seed)
    device = torch.device(device)

    feat = torch.from_numpy(data.feat).to(device)
    edge_index = torch.from_numpy(np.array(np.nonzero(data.adj))).to(device)

    model = DeepGraphInfomax(
        hidden_channels=_DEFAULTS["hidden"],
        encoder=_Encoder(data.num_features, _DEFAULTS["hidden"]),
        summary=_summary, corruption=_corruption).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=_DEFAULTS["lr"])

    best_loss, stale = math.inf, 0
    model.train()
    for _epoch in range(epochs):
        optimizer.zero_grad()
        pos_z, neg_z, summary = model(feat, edge_index)
        loss = model.loss(pos_z, neg_z, summary)
        loss.backward()
        optimizer.step()
        if loss.item() < best_loss:
            best_loss, stale = loss.item(), 0
        else:
            stale += 1
        if stale >= _DEFAULTS["patience"]:
            break

    model.eval()
    with torch.no_grad():
        embeddings = model.encoder(feat, edge_index).cpu().numpy()

    k = int(np.unique(data.label).size)
    pred = KMeans(n_clusters=k, n_init=10,
                  random_state=seed).fit_predict(embeddings)
    metrics = evaluate_partition(pred, data.label, graph,
                                 embeddings=embeddings)
    config = config_string(epochs=epochs, k_source="ground_truth",
                           **_DEFAULTS)
    return metrics, k, config
