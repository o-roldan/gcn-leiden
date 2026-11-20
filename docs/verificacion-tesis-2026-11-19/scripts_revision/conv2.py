import pandas as pd, numpy as np, sys, os
from scipy.stats import wilcoxon
H=sys.argv[1]; d=pd.read_csv(sys.argv[2])
def first(ds,m,s,target):
    h=pd.read_csv(f"{H}/history_{ds}/gcn-{m}_{ds}_seed{s}.csv"); q=-h.loss.values/1e-3
    i=np.argmax(q>=target); return h.epoch.values[i] if (q>=target).any() else np.nan
out=[]
for ds in ['cora','citeseer','pubmed','cocs','amac','amap','wikics']:
    x=d[d.ds==ds]
    for frac in [0.9,0.95,0.99]:
        target=frac*min(x[x.m=='louvain'].qmax.mean(), x[x.m=='leiden'].qmax.mean())
        for s in range(5):
            out.append(dict(ds=ds,frac=frac,seed=s,lou=first(ds,'louvain',s,target),lei=first(ds,'leiden',s,target)))
o=pd.DataFrame(out)
print(o.groupby(['ds','frac'],sort=False)[['lou','lei']].mean().unstack('frac').round(1).to_string())
for frac in [0.9,0.95,0.99]:
    z=o[o.frac==frac].dropna(); diff=z.lei-z.lou
    p=wilcoxon(z.lei,z.lou).pvalue if (diff!=0).any() else 1
    print(f"fixed-target {frac}: n={len(z)} Leiden faster in {(diff<0).sum()}, slower in {(diff>0).sum()}, ties {(diff==0).sum()}, median diff={diff.median()} p={p:.3f}")
r=d[d.ds!='film'].pivot_table(index=['ds','seed'],columns='m',values=['t95','q0','qmax'])
for v in ['t95','q0','qmax']:
    a,b=r[(v,'leiden')],r[(v,'louvain')]; diff=a-b
    print(f"{v}: Leiden>Louvain in {(diff>0).sum()}/35, median diff={diff.median():.3f}, p={wilcoxon(a,b).pvalue:.3f}")
x=d[d.ds!='film']
print("NMI peak epoch < Q'max epoch:", (x.ep_nmi_peak<x.ep_qmax).sum(), "/", len(x))
print("mean NMI loss from peak to Q'max ckpt:", (x.nmi_peak-x.nmi_at_qmax).groupby(x.ds).mean().round(3).to_dict())
print("runs early-stopped (<300):", (d.last<300).sum(), d[d.last<300][['ds','m','seed','last']].values.tolist())
