import pandas as pd, numpy as np
from scipy import stats
exec(open('conv.py').read().split("print('scipy'")[0])
def fe(h,thr):
    m=h[h.qp>=thr]; return np.nan if m.empty else int(m.epoch.iloc[0])
I={k:dict(q0=h.qp.iloc[0],qmax=h.qp.max()) for k,h in runs.items()}
def E_for(frac):
    E={}
    for ds in DS:
        lvl=frac*min(np.mean([I[(ds,p,s)]['qmax'] for s in SEEDS]) for p in PR)
        for p in PR:
            for s in SEEDS: E[(ds,p,s)]=fe(runs[(ds,p,s)],lvl)
    return E
E=E_for(0.99)
print({k:v for k,v in E.items() if k[0]=='cora'})
for fill in ['drop',300,302,310,1000]:
    d=[]
    for ds in DS:
        for s in SEEDS:
            a,b=E[(ds,'leiden',s)],E[(ds,'louvain',s)]
            if np.isnan(a) or np.isnan(b):
                if fill=='drop': continue
                a=fill if np.isnan(a) else a; b=fill if np.isnan(b) else b
            d.append(a-b)
    d=np.array(d,float); nz=d[d!=0]
    print(fill, len(d), 'earlier',(d<0).sum(),'later',(d>0).sum(),'tie',(d==0).sum(), 'p auto',round(stats.wilcoxon(nz).pvalue,4),'p exact',round(stats.wilcoxon(nz,method='exact').pvalue,4), 'pratt', round(stats.wilcoxon(d,zero_method='pratt').pvalue,4))
# 95% without wikics / without each ds
E=E_for(0.95)
for excl in [None]+DS:
    d=np.array([E[(ds,'leiden',s)]-E[(ds,'louvain',s)] for ds in DS if ds!=excl for s in SEEDS],float); nz=d[d!=0]
    print('95 excl',excl,'later',(d>0).sum(),'earlier',(d<0).sum(),'p',round(stats.wilcoxon(nz).pvalue,4), 'diffs', sorted(nz.tolist()))
# cora louvain qmax per seed vs level
print([round(I[('cora','louvain',s)]['qmax'],4) for s in SEEDS], 0.99*np.mean([I[('cora','louvain',s)]['qmax'] for s in SEEDS]))
