import pandas as pd, numpy as np
R='/Users/omar/Developer/me/gcn-leiden/results'
cols=['k','epochs','nmi','ari','q','dbi','peak_nmi','peak_ari','peak_q','peak_dbi']
for ds in ['cora','citeseer']:
    a=pd.read_csv(f'{R}/runs_{ds}.csv'); a=a[a.method.str.startswith('gcn')&a.seed.between(0,4)].set_index(['method','seed'])[cols].sort_index()
    b=pd.read_csv(f'{R}/runs_validate_{ds}.csv'); b=b[b.seed.between(0,4)].set_index(['method','seed'])[cols].sort_index()
    print(ds, a.dtypes.to_dict()==b.dtypes.to_dict(), np.array_equal(a.values.astype(float),b.values.astype(float),equal_nan=True), len(a), len(b))
    print({c:(str(a[c].dtype),str(b[c].dtype)) for c in cols if a[c].dtype!=b[c].dtype})
