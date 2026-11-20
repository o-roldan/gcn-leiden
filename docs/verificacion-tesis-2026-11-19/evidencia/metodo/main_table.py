import glob, os
import pandas as pd
R = "/Users/omar/Developer/me/gcn-leiden/results"
ds = ["cora","citeseer","pubmed","cocs","cophysics","amac","amap","film","wikics"]
frames = [pd.read_csv(f"{R}/runs_{d}.csv") for d in ds]
df = pd.concat(frames)
df = df[df.seed.isin(range(5))]
cfg = df.config.str.split(";").apply(lambda kv: dict(x.split("=", 1) for x in kv))
df["resolution"] = cfg.apply(lambda d: d.get("resolution"))
df = df[~(df.method.isin(["louvain","leiden"]) & (df.resolution != "1.0"))]
out = []
for (d, m), g in df.groupby(["dataset","method"]):
    row = dict(ds=d, m=m, n=len(g))
    for c in ["nmi","ari","peak_nmi","peak_ari"]:
        if g[c].notna().any():
            row[c] = f"{g[c].mean():.3f}±{g[c].std(ddof=1):.3f}"
    out.append(row)
t = pd.DataFrame(out)
pd.set_option("display.width", 200)
print(t.to_string())
# who wins among deep vs gcn per dataset (means)
print()
for d in ds:
    g = df[df.dataset == d].groupby("method")[["nmi","ari"]].agg(["mean","std"])
    deep = g.loc[[m for m in ["deepwalk","dgi","dmon"] if m in g.index]]
    gcn = g.loc[[m for m in ["gcn-louvain","gcn-leiden"] if m in g.index]]
    if len(gcn)==0: continue
    for metric in ["nmi","ari"]:
        bd = deep[(metric,"mean")].idxmax(); bv = deep.loc[bd,(metric,"mean")]; bs = deep.loc[bd,(metric,"std")]
        for gm in gcn.index:
            v = gcn.loc[gm,(metric,"mean")]; s = gcn.loc[gm,(metric,"std")]
            flag = "GCN>deep" if v > bv else "deep>=GCN"
            print(f"{d:9s} {metric} best deep={bd}:{bv:.3f}±{bs:.3f}  {gm}:{v:.3f}±{s:.3f}  {flag} diff={v-bv:+.3f}")
