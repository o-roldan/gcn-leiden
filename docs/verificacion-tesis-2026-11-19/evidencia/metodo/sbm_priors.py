import sys
sys.path.insert(0, "/Users/omar/Developer/me/gcn-leiden")
import networkx as nx
import numpy as np
from gcn_leiden.datasets import load_dataset
from gcn_leiden.prior import detect_communities, filter_by_size
for name in ["sbm_1000_5", "sbm_5000_10", "sbm_10000_20"]:
    data = load_dataset(name)
    g = nx.from_numpy_array(data.adj)
    for method, obj, res in [("louvain","modularity",0.3),("leiden","modularity",0.3),
                             ("louvain","modularity",1.0),("leiden","modularity",1.0),
                             ("leiden","cpm",0.0275)]:
        comms = detect_communities(g, method, res, 123, obj)
        s = np.array([len(c) for c in comms], float)
        cv = s.std() / s.mean()
        kw = len(filter_by_size(comms, 0.5, "wang")[0])
        kr = len(filter_by_size(comms, 0.5, "recalibrado")[0])
        print(f"{name} {method:7s} {obj:10s} g={res:<6} k0={len(comms):3d} cv={cv:.5f} k_wang={kw} k_recal={kr} sizes_head={sorted(s.astype(int))[-5:]}")
