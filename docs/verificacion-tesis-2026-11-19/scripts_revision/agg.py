import pandas as pd, sys
R = sys.argv[1]
def load(f): 
    d = pd.read_csv(f"{R}/{f}"); return d[d.seed.isin(range(5))]
rows = {}
real = ['cora','citeseer','pubmed','cocs','amac','amap','film','wikics']
for ds in real:
    d = load(f"runs_{ds}.csv")
    for m in ['gcn-louvain','gcn-leiden']:
        rows[(ds,m)] = d[d.method==m]
for ds in ['sbm_1000_5','sbm_5000_10','sbm_10000_20']:
    v = load(f"runs_validate_{ds}.csv")
    rows[(ds,'gcn-louvain')] = v[(v.method=='gcn-louvain') & v.config.str.contains('beta=0.5;')]
    r = load(f"runs_recal_{ds}.csv")
    rows[(ds,'gcn-leiden')] = r[r.config.str.contains('prior_objective=cpm') & r.config.str.contains('beta=0.5;')]
for (ds,m),d in rows.items():
    out=[ds,m,f"n={len(d)}",f"k={d.k.mean():.1f}"]
    for c in ['nmi','ari','q','dbi','peak_nmi','peak_ari','peak_q','peak_dbi']:
        out.append(f"{c}={d[c].mean():.3f}±{d[c].std(ddof=0):.3f}/{d[c].std(ddof=1):.3f}")
    print(' '.join(out))
