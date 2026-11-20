import pandas as pd, numpy as np, scipy, sys
from scipy import stats
H='/Users/omar/Developer/me/gcn-leiden/results/history'
DS=['cora','citeseer','pubmed','cocs','amac','amap','wikics']
PR=['louvain','leiden']; SEEDS=range(5); ALPHA=1e-3
runs={}
for ds in DS:
    for p in PR:
        for s in SEEDS:
            h=pd.read_csv(f'{H}/history_{ds}/gcn-{p}_{ds}_seed{s}.csv')
            h['qp']=-h['loss']/ALPHA
            runs[(ds,p,s)]=h
print('scipy',scipy.__version__)
def first_epoch(h,thr):
    m=h[h.qp>=thr]
    return np.nan if m.empty else int(m.epoch.iloc[0])
info={}
for k,h in runs.items():
    i=h.qp.values.argmax()
    j=h.nmi.values.argmax()
    info[k]=dict(q0=h.qp.iloc[0], e0=h.epoch.iloc[0], qmax=h.qp.max(), eqmax=int(h.epoch.iloc[i]),
                 nmipk=h.nmi.max(), enmipk=int(h.epoch.iloc[j]), nmi_at_qmax=h.nmi.iloc[i], last=int(h.epoch.iloc[-1]), nrec=len(h),
                 step=int(h.epoch.iloc[1]-h.epoch.iloc[0]))
I=pd.DataFrame(info).T; I.index.names=['ds','prior','seed']
I=I.astype(float)
print(I.groupby(['ds','prior'])[['step','nrec','last','q0','qmax','eqmax']].agg(['mean','std']).round(4).to_string())

def level_table(frac):
    rows=[];E={}
    for ds in DS:
        mq={p:I.loc[(ds,p)].qmax.mean() for p in PR}
        lvl=frac*min(mq.values())
        for p in PR:
            for s in SEEDS:
                E[(ds,p,s)]=first_epoch(runs[(ds,p,s)],lvl)
        rows.append(dict(ds=ds,level=lvl,mqL=mq['louvain'],mqD=mq['leiden'],
            Lou=np.mean([E[(ds,'louvain',s)] for s in SEEDS]), Lou_sd=np.std([E[(ds,'louvain',s)] for s in SEEDS],ddof=1),
            Lei=np.mean([E[(ds,'leiden',s)] for s in SEEDS]), Lei_sd=np.std([E[(ds,'leiden',s)] for s in SEEDS],ddof=1)))
    return pd.DataFrame(rows),E
def pair_stats(E,label):
    d=np.array([E[(ds,'leiden',s)]-E[(ds,'louvain',s)] for ds in DS for s in SEEDS],dtype=float)
    print(f'--- {label}: n={len(d)} nan={np.isnan(d).sum()} earlier(Leiden)={int((d<0).sum())} later={int((d>0).sum())} tie={int((d==0).sum())}')
    per=pd.Series({ds:(lambda x:(int((x<0).sum()),int((x>0).sum()),int((x==0).sum())))(np.array([E[(ds,'leiden',s)]-E[(ds,'louvain',s)] for s in SEEDS])) for ds in DS})
    print('per ds (earlier,later,tie):',per.to_dict())
    nz=d[d!=0]
    for meth in ['auto','exact','approx']:
        for corr in [False,True]:
            try:
                r=stats.wilcoxon(nz,method=meth,correction=corr) if meth=='approx' else stats.wilcoxon(nz,method=meth)
                print(f'  wilcoxon nonzero method={meth} corr={corr}: stat={r.statistic} p={r.pvalue:.4f}')
            except Exception as e: print('  err',meth,e)
            if meth!='approx': break
    for zm in ['wilcox','pratt','zsplit']:
        r=stats.wilcoxon(d,zero_method=zm); print(f'  wilcoxon all35 zero_method={zm}: p={r.pvalue:.4f}')
    return d
for frac in [0.95,0.99]:
    T,E=level_table(frac)
    print(f'===== level frac={frac}'); print(T.round(3).to_string())
    pair_stats(E,f'fixed {frac}')
# relative
E={}
for k,h in runs.items():
    q0=info[k]['q0']; qm=info[k]['qmax']
    E[k]=first_epoch(h,q0+0.95*(qm-q0))
T=pd.DataFrame([{ 'ds':ds, **{p:np.mean([E[(ds,p,s)] for s in SEEDS]) for p in PR}} for ds in DS]); print('==== relative 95% own gain'); print(T.to_string())
pair_stats(E,'relative 0.95')
# q0, qmax
for col in ['q0','qmax']:
    a=np.array([info[(ds,'leiden',s)][col] for ds in DS for s in SEEDS]); b=np.array([info[(ds,'louvain',s)][col] for ds in DS for s in SEEDS])
    r=stats.wilcoxon(a,b); print(f'{col}: wilcoxon p={r.pvalue:.4f}; leiden>louvain in {(a>b).sum()}/35; mean diff {np.mean(a-b):.4f}; ttest p={stats.ttest_rel(a,b).pvalue:.4f}')
    print('   per-ds mean diff:', {ds: round(np.mean([info[(ds,'leiden',s)][col]-info[(ds,'louvain',s)][col] for s in SEEDS]),4) for ds in DS})
# epoch of qmax
print('==== mean epoch of Qmax per ds (pooled 10 runs) and per prior')
print(I.groupby('ds').eqmax.mean().round(1).to_string()); print(I.groupby(['ds','prior']).eqmax.mean().round(1).to_string())
# NMI peak vs Qmax
I['prec']=I.enmipk<I.eqmax; I['same']=I.enmipk==I.eqmax; I['loss']=I.nmipk-I.nmi_at_qmax
print('NMI peak precedes Qmax:',int(I.prec.sum()),'/',len(I),' same epoch:',int(I.same.sum()), ' after:', int((I.enmipk>I.eqmax).sum()))
print(I.groupby('ds')[['prec','loss']].agg({'prec':'sum','loss':'mean'}).round(4).to_string())
print(I.groupby(['ds','prior'])[['loss']].mean().round(4).to_string())
I.to_csv('conv_runinfo.csv')
