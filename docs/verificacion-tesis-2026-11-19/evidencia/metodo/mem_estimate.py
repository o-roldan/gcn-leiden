"""Static GPU-memory estimate for the GCN path, calibrated with vram_peak_mb."""
import torch
from torch_geometric.datasets import Coauthor, Planetoid, Amazon
from torch_geometric.utils import to_undirected, remove_self_loops
import pandas as pd

ROOT = "/Users/omar/Developer/me/gcn-leiden/datasets_pyg"
RES = "/Users/omar/Developer/me/gcn-leiden/results"
MiB = 2**20
loaders = {"pubmed": lambda: Planetoid(ROOT, name="PubMed"),
           "cocs": lambda: Coauthor(ROOT, name="CS"),
           "amac": lambda: Amazon(ROOT, name="Computers"),
           "cophysics": lambda: Coauthor(ROOT, name="Physics")}
for name, load in loaders.items():
    d = load()[0]
    ei, _ = remove_self_loops(to_undirected(d.edge_index))
    n, F, E = d.num_nodes, d.x.shape[1], ei.shape[1]
    nn_ = n * n * 4 / MiB
    feat = n * F * 4 / MiB
    nh = n * 512 * 4 / MiB
    msg = (E + n) * 512 * 4 / MiB
    est_a = 4 * nn_ + feat          # 4 dense n x n + features
    est_b = 2 * nn_ + feat + 2 * msg
    row = f"{name}: n={n} F={F} E_dir={E} | n^2 f32={nn_:.1f} MiB feat={feat:.1f} n*512={nh:.1f} msgE*512={msg:.1f}"
    row += f" | 4n^2+feat={est_a:.1f} 2n^2+feat+2msg={est_b:.1f} 5n^2+feat={5*nn_+feat:.1f}"
    try:
        df = pd.read_csv(f"{RES}/runs_{name}.csv")
        g = df[df.method.str.startswith("gcn") & df.seed.isin(range(5))]
        if len(g):
            v = g.vram_peak_mb.unique()
            row += f" | measured gcn vram_peak_mb={v} -> residual vs 4n^2+feat={v[0]-est_a:.1f} ({(v[0]-est_a)/nh:.1f} n*512 units)"
    except FileNotFoundError:
        pass
    print(row)
