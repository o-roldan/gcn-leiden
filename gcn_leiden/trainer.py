"""Training loop: early stopping on the loss, best-checkpoint restore.

Tracks two views of quality:
  * best  -- metrics of the checkpoint with minimum loss (deployable model)
  * peak  -- per-metric maxima over training (comparable to the reporting
             convention of Wang et al. 2025)
"""

import copy
import math
import time
from dataclasses import dataclass, field

import torch

from . import metrics
from .loss import modularity_matrix, soft_modularity_loss


@dataclass
class TrainConfig:
    epochs: int = 300
    lr: float = 1e-3
    weight_decay: float = 5e-3
    loss_scale: float = 1e-3      # alpha in L = -alpha * Q'
    eval_every: int = 2
    patience: int = 200
    device: str = "cpu"


@dataclass
class TrainResult:
    best: dict                    # metrics at the min-loss checkpoint
    peak: dict                    # per-metric extrema over training
    history: list = field(repr=False)
    epochs_ran: int = 0
    runtime_s: float = 0.0


_HIGHER_IS_BETTER = ("nmi", "ari", "q")


def train(model, feat, edge_index, adj, graph, labels, community_index,
          cfg=None):
    cfg = cfg or TrainConfig()
    device = torch.device(cfg.device)
    model = model.to(device)
    feat = feat.to(device)
    edge_index = edge_index.to(device)
    adj = adj.to(device)
    community_index = [idx.to(device) for idx in community_index]

    mod = modularity_matrix(adj)
    two_m = (adj.sum() - adj.diagonal().sum()).item()
    optimizer = torch.optim.Adam(
        model.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay)

    start = time.perf_counter()
    history = []
    peak = {}
    best_state = copy.deepcopy(model.state_dict())
    min_loss = math.inf
    stale = 0
    epochs_ran = 0

    for epoch in range(1, cfg.epochs + 1):
        epochs_ran = epoch
        model.train()
        optimizer.zero_grad()
        _, _, p = model(feat, edge_index, community_index)
        loss = cfg.loss_scale * soft_modularity_loss(p, mod, two_m)
        loss.backward()
        optimizer.step()
        loss_value = loss.item()

        if epoch % cfg.eval_every == 0:
            snapshot = _evaluate(
                model, feat, edge_index, community_index, graph, labels)
            history.append({"epoch": epoch, "loss": loss_value, **snapshot})
            _update_peak(peak, snapshot)

        if loss_value < min_loss:
            min_loss = loss_value
            best_state = copy.deepcopy(model.state_dict())
            stale = 0
        else:
            stale += 1
        if stale >= cfg.patience:
            break

    model.load_state_dict(best_state)
    best = _evaluate(model, feat, edge_index, community_index, graph, labels)
    return TrainResult(best=best, peak=peak, history=history,
                       epochs_ran=epochs_ran,
                       runtime_s=time.perf_counter() - start)


def _evaluate(model, feat, edge_index, community_index, graph, labels):
    model.eval()
    with torch.no_grad():
        z, _, p = model(feat, edge_index, community_index)
    pred = p.argmax(dim=1).cpu().numpy()
    return metrics.evaluate_partition(
        pred, labels, graph, embeddings=z.cpu().numpy())


def _update_peak(peak, snapshot):
    for key in _HIGHER_IS_BETTER:
        peak[key] = max(peak.get(key, -math.inf), snapshot[key])
    if not math.isnan(snapshot.get("dbi", math.nan)):
        peak["dbi"] = min(peak.get("dbi", math.inf), snapshot["dbi"])
