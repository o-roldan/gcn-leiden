import pandas as pd, numpy as np
R='/Users/omar/Developer/me/gcn-leiden/results'
pd.set_option('display.width',250)
def cfg(s):
    return dict(kv.split('=',1) for kv in str(s).split(';') if '=' in kv)
rows=[]
for ds in ['cora','citeseer','pubmed','cocs','cophysics','amac','amap','film','wikics','sbm_1000_5','sbm_5000_10','sbm_10000_20']:
    d=pd.read_csv(f'{R}/runs_{ds}.csv'); d=d[d.seed.between(0,4)]
    c=d.config.apply(cfg); d['res']=c.apply(lambda x:x.get('resolution'))
    d=d[~((d.method.isin(['louvain','leiden']))&(d.res!='1.0'))]
    g=d.groupby('method')
    out=g[['nmi','ari','q','k','peak_nmi','peak_ari']].agg(['mean','std'])
    for m in out.index:
        r={'ds':ds,'m':m}
        for col in ['nmi','ari','q','k','peak_nmi','peak_ari']:
            r[col]=out.loc[m,(col,'mean')]; r[col+'_sd']=out.loc[m,(col,'std')]
        rows.append(r)
T=pd.DataFrame(rows)
print(T.round(3).to_string())
T.to_csv('quality_means.csv',index=False)
# per-seed specifics
for ds in ['amac','amap']:
    d=pd.read_csv(f'{R}/runs_{ds}.csv'); d=d[d.seed.between(0,4)]
    print(ds, 'DGI nmi per seed', d[d.method=='dgi'].sort_values('seed').nmi.round(3).tolist(), 'ari', d[d.method=='dgi'].sort_values('seed').ari.round(3).tolist())
    for m in ['gcn-louvain','gcn-leiden']:
        print(ds, m, 'nmi per seed', d[d.method==m].sort_values('seed').nmi.round(4).tolist(),'k',d[d.method==m].k.tolist())
