import pandas as pd, numpy as np
R="/Users/omar/Developer/me/gcn-leiden/results/"
def cfg(s):
    d={}
    for kv in str(s).split(";"):
        if "=" in kv: a,b=kv.split("=",1); d[a]=b
    return d
def load(name):
    df=pd.read_csv(R+f"runs_{name}.csv"); df=df[df.seed.isin(range(5))].copy()
    c=df.config.apply(cfg)
    for key in ["resolution","beta","prior_objective","k0","threshold","filter_variant"]:
        df[key]=c.apply(lambda d:d.get(key))
    return df
reals=["cora","citeseer","pubmed","cocs","amac","amap","film","wikics"]
print("== GCN-Leiden vs best deep (ckpt), tie = |diff| < max sd")
for ds in reals:
    df=load(ds)
    for col in ("nmi","ari","q"):
        deep={m:df[df.method==m][col] for m in ("deepwalk","dgi","dmon")}
        best=max(deep,key=lambda m:deep[m].mean())
        g=df[df.method=="gcn-leiden"][col]
        d=g.mean()-deep[best].mean(); mx=max(g.std(),deep[best].std())
        verdict="TIE" if abs(d)<mx else ("ABOVE" if d>0 else "BELOW")
        print(f"{ds:9s} {col}: best={best} {deep[best].mean():.4f}±{deep[best].std():.4f} gcnL={g.mean():.4f}±{g.std():.4f} diff={d:+.4f} -> {verdict}")
print("== DGI per-seed NMI amac/amap; GCN-Leiden amac per-seed")
for ds in ("amac","amap"):
    df=load(ds); print(ds,"dgi nmi",df[df.method=="dgi"].sort_values("seed").nmi.tolist())
df=load("amac"); print("amac gcn-leiden nmi",df[df.method=="gcn-leiden"].sort_values("seed").nmi.tolist(), "louvain-gcn", df[df.method=="gcn-louvain"].sort_values("seed").nmi.tolist())
print("== Actor main: k gcn", load("film").query("method in ['gcn-louvain','gcn-leiden']")[["method","seed","k","nmi","peak_nmi","q"]].to_string())
print("== RECAL real")
for ds in ("cora","citeseer"):
    df=load("recal_"+ds)
    for m in ("gcn-louvain","gcn-leiden"):
        for b in ("-0.5","0.0","0.25","0.5"):
            d=df[(df.method==m)&(df.beta==b)]
            print(f"{ds} {m} b={b:5s} n={len(d)} k={d.k.mean():.1f} peakNMI={d.peak_nmi.mean():.4f}±{d.peak_nmi.std():.4f} peakARI={d.peak_ari.mean():.4f}±{d.peak_ari.std():.4f} | ckNMI={d.nmi.mean():.4f}±{d.nmi.std():.4f} ckARI={d.ari.mean():.4f}±{d.ari.std():.4f}")
print("== RECAL SBM-10k (modularity) gcn-leiden")
for ds in ("sbm_1000_5","sbm_5000_10","sbm_10000_20"):
    df=load("recal_"+ds)
    g=df.groupby(["method","prior_objective","resolution","beta"]).agg(n=("seed","size"),k=("k","mean"),k0=("k0","first"),ck_nmi=("nmi","mean"),ck_ari=("ari","mean"),pk_nmi=("peak_nmi","mean"),pk_nmi_sd=("peak_nmi","std"),pk_ari=("peak_ari","mean"),thr=("threshold","first"))
    print(ds); print(g.round(4).to_string())
    v=load("validate_"+ds)
    print(" validate:"); print(v.groupby(["method"]).agg(n=("seed","size"),k=("k","mean"),k0=("k0","first"),ck_nmi=("nmi","mean"),ck_ari=("ari","mean"),pk_nmi=("peak_nmi","mean"),thr=("threshold","first")).round(4).to_string())
