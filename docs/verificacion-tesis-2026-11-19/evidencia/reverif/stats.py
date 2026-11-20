import pandas as pd, numpy as np, glob, os
R="/Users/omar/Developer/me/gcn-leiden/results"
def cfg(s):
    d={}
    for kv in str(s).split(";"):
        if "=" in kv:
            k,v=kv.split("=",1); d[k]=v
    return d
def load(f):
    df=pd.read_csv(f"{R}/{f}")
    c=df.config.apply(cfg).apply(pd.Series)
    df=pd.concat([df,c],axis=1)
    for col in ["filter_variant","beta","resolution","prior_objective","k0"]:
        if col not in df: df[col]="NA"
    df=df.fillna({"filter_variant":"wang"})
    return df[df.seed.isin([0,1,2,3,4])]
def ms(x): return f"{x.mean():.4f}±{x.std(ddof=1):.4f}"
# Recal beta Cora/CiteSeer
for ds in ["cora","citeseer"]:
    df=load(f"runs_recal_{ds}.csv")
    print("==",ds, df.groupby(["method","beta","resolution","prior_objective","filter_variant"]).size().to_dict())
    for m in ["gcn-louvain","gcn-leiden"]:
        for b in sorted(df.beta.unique(), key=float):
            s=df[(df.method==m)&(df.beta==b)]
            print(f"{m:12s} b={b:5s} n={len(s)} k={sorted(s.k.unique())} k0={sorted(s.k0.unique())} | NMI {ms(s.nmi)} ARI {ms(s.ari)} | pNMI {ms(s.peak_nmi)} pARI {ms(s.peak_ari)}")
