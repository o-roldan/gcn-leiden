import pandas as pd
R='/Users/omar/Developer/me/gcn-leiden/results/'
def load(f):
    d=pd.read_csv(R+f); d=d[d.seed.isin(range(5))]
    cfg=d.config.fillna('').str.split(';').apply(lambda xs: dict(x.split('=',1) for x in xs if '=' in x))
    c=pd.DataFrame(list(cfg),index=d.index)
    return pd.concat([d.drop(columns='config'),c],axis=1)
for ds in ['cora','citeseer','pubmed','cocs','amac','amap','film','wikics']:
    d=load(f'runs_{ds}.csv')
    d=d[d.method.isin(['gcn-louvain','gcn-leiden'])]
    keys=[k for k in ['resolution','beta','prior_objective','filter_variant'] if k in d.columns]
    out=[]
    for m in ['gcn-louvain','gcn-leiden']:
        x=d[d.method==m]
        if len(x)!=5: print(ds,m,'n=',len(x), x[keys].drop_duplicates().to_dict('records'))
        out.append((m,x.peak_nmi.mean(),x.peak_nmi.std(),x.peak_ari.mean(),x.peak_ari.std(),x.nmi.mean(),x.nmi.std(),x.ari.mean(),x.ari.std()))
    (a,b)=out
    def cls(da,sa,sb):
        lo,hi=min(sa,sb),max(sa,sb)
        r='tie' if abs(da)<lo else ('win' if da>0 else 'loss') if abs(da)>=hi else 'ambig'
        return r
    dn=b[1]-a[1]; da=b[3]-a[3]
    print(f"{ds:9s} pkNMI L={a[1]:.4f}±{a[2]:.4f} Ld={b[1]:.4f}±{b[2]:.4f} d={dn:+.4f} {cls(dn,a[2],b[2])} | pkARI L={a[3]:.4f}±{a[4]:.4f} Ld={b[3]:.4f}±{b[4]:.4f} d={da:+.4f} {cls(da,a[4],b[4])} | ckNMI d={b[5]-a[5]:+.4f} sd {a[6]:.3f}/{b[6]:.3f} {cls(b[5]-a[5],a[6],b[6])} ckARI d={b[7]-a[7]:+.4f} {cls(b[7]-a[7],a[8],b[8])}")
# recal cora beta grid
for ds in ['cora','citeseer']:
    d=load(f'runs_recal_{ds}.csv')
    for bt,g in d.groupby('beta'):
        a=g[g.method=='gcn-louvain'].peak_nmi; b=g[g.method=='gcn-leiden'].peak_nmi
        print(ds,'beta',bt,f"L={a.mean():.4f}±{a.std():.4f} Ld={b.mean():.4f}±{b.std():.4f} d={b.mean()-a.mean():+.4f}", len(a),len(b))
