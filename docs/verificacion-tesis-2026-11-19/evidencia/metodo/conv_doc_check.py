import glob, os, re
import pandas as pd
H = "/Users/omar/Developer/me/gcn-leiden/results/history"
rows = []
for d in ["cora","citeseer","pubmed","cocs","amac","amap","wikics","film"]:
    for f in sorted(glob.glob(f"{H}/history_{d}/*.csv")):
        m = re.search(r"(gcn-\w+)_(\w+)_seed(\d+)\.csv$", os.path.basename(f))
        if not m or int(m.group(3)) > 4: continue
        h = pd.read_csv(f); q = -h.loss / 1e-3
        rows.append(dict(ds=d, method=m.group(1), seed=int(m.group(3)),
                         step=int(h.epoch.diff().dropna().mode()[0]), first=int(h.epoch.iloc[0]),
                         qmax=q.max(), q0=q.iloc[0], loss_absmax=h.loss.abs().max()))
s = pd.DataFrame(rows)
print(s.groupby("ds").step.unique())
print("film:", s[s.ds=="film"][["method","seed","qmax","loss_absmax"]].to_string())
s = s[s.ds!="film"]
for frac in (0.9, 0.95, 0.99):
    for ds, g in s.groupby("ds"):
        target = frac * g.groupby("method").qmax.mean().min()
        miss = g[g.qmax < target]
        if len(miss):
            print(f"frac={frac} {ds}: target={target:.4f} not reached by", miss[["method","seed","qmax"]].values.tolist())
