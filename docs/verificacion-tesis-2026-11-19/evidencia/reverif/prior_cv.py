import sys, json
sys.path.insert(0, "/Users/omar/Developer/me/gcn-leiden")
import numpy as np, networkx as nx
from gcn_leiden.datasets import load_dataset
from gcn_leiden.prior import detect_communities, filter_by_size
ds = sys.argv[1]
configs = json.loads(sys.argv[2])  # list of [method, objective, resolution]
data = load_dataset(ds, root="/Users/omar/Developer/me/gcn-leiden/datasets_pyg")
g = nx.from_numpy_array(data.adj)
del data
for method, obj, res in configs:
    comms = detect_communities(g, method, res, 123, obj)
    s = np.array([len(c) for c in comms], float)
    cv = s.std()/s.mean()
    out = {"ds": ds, "method": method, "obj": obj, "res": res, "k0": len(comms), "cv": round(float(cv), 4)}
    for b in (-0.5, 0.0, 0.25, 0.5):
        out[f"wang_b{b}"] = len(filter_by_size(comms, b, "wang")[0])
        out[f"rec_b{b}"] = len(filter_by_size(comms, b, "recalibrado")[0])
    print(json.dumps(out), flush=True)
