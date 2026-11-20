import pandas as pd
R='/Users/omar/Developer/me/gcn-leiden/results'
for ds in ['cora','citeseer']:
    d=pd.read_csv(f'{R}/runs_recal_{ds}.csv'); d=d[d.seed.between(0,4)]
    d['beta']=d.config.str.extract(r'beta=([-\d.]+)')[0].astype(float)
    g=d[d.beta.isin([-0.5,0.5])].groupby(['method','beta'])[['nmi','ari','peak_nmi','peak_ari']].agg(['mean','std']).round(3)
    print(ds); print(g.to_string())
