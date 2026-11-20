import pandas as pd
R='/Users/omar/Developer/me/gcn-leiden/results/'
for ds in ['cora','citeseer']:
    d=pd.read_csv(R+f'runs_recal_{ds}.csv'); d=d[d.seed.isin(range(5))]
    d['beta']=d.config.str.extract(r'beta=([-0-9.]+)')[0].astype(float)
    g=d.groupby(['method','beta']).agg(ck_nmi=('nmi','mean'),ck_sd=('nmi','std'),pk_nmi=('peak_nmi','mean'),ck_ari=('ari','mean'),pk_ari=('peak_ari','mean'),n=('seed','count'))
    print(ds); print(g.round(4).to_string())
