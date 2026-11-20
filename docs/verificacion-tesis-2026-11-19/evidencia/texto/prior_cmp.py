import pandas as pd, numpy as np
R='/Users/omar/Developer/me/gcn-leiden/results'
def load(f):
    d=pd.read_csv(f); d=d[d.seed.between(0,4)&d.method.str.startswith('gcn')].copy()
    d['beta']=d.config.str.extract(r'beta=([-\d.]+)')[0].astype(float); return d
print('ds metric  Lou mean sd | Lei mean sd | diff | diff/sdLou diff/sdLei diff/maxsd diff/pooled | verdict(maxsd) verdict(minsd) | Leiden>Louvain seeds')
for ds in ['cora','citeseer','pubmed','cocs','amac','amap','film','wikics']:
    d=load(f'{R}/runs_{ds}.csv')
    for met in ['peak_nmi','peak_ari']:
        a=d[d.method=='gcn-louvain'].sort_values('seed')[met].values; b=d[d.method=='gcn-leiden'].sort_values('seed')[met].values
        ma,mb=a.mean(),b.mean(); sa,sb=a.std(ddof=1),b.std(ddof=1); df=mb-ma
        mx,mn,pl=max(sa,sb),min(sa,sb),np.sqrt((sa**2+sb**2)/2)
        v=lambda s:'tie' if abs(df)<s else ('Leiden' if df>0 else 'Louvain')
        print(f'{ds:9s}{met:9s} {ma:.4f} {sa:.4f} | {mb:.4f} {sb:.4f} | {df:+.4f} | {df/sa if sa else np.inf:6.2f} {df/sb if sb else np.inf:6.2f} {df/mx if mx else np.inf:6.2f} {df/pl if pl else np.inf:6.2f} | {v(mx):7s} {v(mn):7s} | {(b>a).sum()}/5 (ties {(b==a).sum()})')
    if ds=='cora':
        print('   cora peak_nmi per seed Lou',d[d.method=='gcn-louvain'].sort_values('seed').peak_nmi.round(4).tolist(),'Lei',d[d.method=='gcn-leiden'].sort_values('seed').peak_nmi.round(4).tolist())
    if ds=='film':
        print('   film Lou peak_nmi',d[d.method=='gcn-louvain'].sort_values('seed').peak_nmi.tolist(),'k',d.groupby('method').k.unique().to_dict())
print('==== recal beta sweep (peak_nmi) ===')
for ds in ['cora','citeseer']:
    d=load(f'{R}/runs_recal_{ds}.csv')
    for b,g in d.groupby('beta'):
        a=g[g.method=='gcn-louvain'].sort_values('seed'); c=g[g.method=='gcn-leiden'].sort_values('seed')
        for met in ['peak_nmi','peak_ari','nmi']:
            x,y=a[met].values,c[met].values; df=y.mean()-x.mean(); mx=max(x.std(ddof=1),y.std(ddof=1)); mn=min(x.std(ddof=1),y.std(ddof=1))
            print(f'{ds} beta={b:5} {met:8s} Lou {x.mean():.4f}±{x.std(ddof=1):.4f} k={a.k.iloc[0]} | Lei {y.mean():.4f}±{y.std(ddof=1):.4f} k={c.k.iloc[0]} | diff {df:+.4f} maxsd {mx:.4f} -> {"tie" if abs(df)<mx else ("Leiden" if df>0 else "Louvain")} (minsd: {"tie" if abs(df)<mn else ("Leiden" if df>0 else "Louvain")}) Lei>Lou seeds {(y>x).sum()}')
