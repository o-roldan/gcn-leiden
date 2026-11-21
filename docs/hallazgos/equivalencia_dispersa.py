"""Full-path check (data loading, graph, prior, edge order, loss per epoch).

Compares the dense path with the sparse path end to end.
Usage: python equivalencia_dispersa.py <dataset> [objective resolution variant]
Defaults: modularity 0.3 wang (thesis config for real graphs). For SBM use,
e.g., `sbm_1000_5 cpm 0.0275 recalibrado`.
"""
import sys, numpy as np, torch, networkx as nx
from gcn_leiden.datasets import load_dataset, to_networkx
from gcn_leiden.model import CommunityAffiliation, communities_to_index
from gcn_leiden.prior import build_prior
from gcn_leiden.loss import modularity_matrix, soft_modularity_loss, soft_modularity_loss_sparse
torch.set_num_threads(4)
ds = sys.argv[1]
objective, resolution, variant = (sys.argv[2:5] if len(sys.argv) > 4
                                  else ("modularity", "0.3", "wang"))
resolution = float(resolution)
dd = load_dataset(ds); gd = nx.from_numpy_array(dd.adj)
sd = load_dataset(ds, dense=False); gs = to_networkx(sd)
pd_ = build_prior(gd, method="leiden", resolution=resolution, beta=0.5, seed=123,
                  objective=objective, filter_variant=variant)
ps = build_prior(gs, method="leiden", resolution=resolution, beta=0.5, seed=123,
                  objective=objective, filter_variant=variant)
ei_d = np.array(np.nonzero(dd.adj)); ei_s = sd.edge_index
print(f"{ds}: aristas dirigidas densa={ei_d.shape[1]} dispersa={ei_s.shape[1]}  mismo edge_index (orden incluido): {np.array_equal(ei_d, ei_s)}")
print(f"  prior: K0 {pd_.initial_count} vs {ps.initial_count}; anclas {pd_.k} vs {ps.k}; "
      f"mismas anclas: {[frozenset(c) for c in pd_.communities] == [frozenset(c) for c in ps.communities]}; "
      f"mismo orden interno: {[list(c) for c in pd_.communities] == [list(c) for c in ps.communities]}")
def run(sparse):
    data, prior, ei = (sd, ps, ei_s) if sparse else (dd, pd_, ei_d)
    np.random.seed(0); torch.manual_seed(0)
    feat = torch.from_numpy(data.feat); eit = torch.from_numpy(ei)
    ci = communities_to_index(prior.communities)
    model = CommunityAffiliation(data.num_features, 512, k=prior.k, temperature=30.0, row_normalize=sparse)
    if sparse:
        A = torch.sparse_coo_tensor(eit, torch.ones(eit.shape[1]), (data.num_nodes,) * 2).coalesce()
        deg = torch.sparse.sum(A, 1).to_dense(); tm = deg.sum().item()
        f = lambda p: soft_modularity_loss_sparse(p, A, deg, tm)
    else:
        adj = torch.from_numpy(data.adj); mod = modularity_matrix(adj)
        tm = (adj.sum() - adj.diagonal().sum()).item(); f = lambda p: soft_modularity_loss(p, mod, tm)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3, weight_decay=5e-3)
    out = []
    for _ in range(15):
        opt.zero_grad(); _, _, p = model(feat, eit, ci); loss = 1e-3 * f(p); loss.backward(); opt.step(); out.append(loss.item())
    return np.array(out)
a, b = run(False), run(True)
rel = np.abs(a - b) / np.abs(a)
print(f"  pérdida por época, dif. relativa: época1={rel[0]:.1e} máx(1–15)={rel.max():.1e}")
