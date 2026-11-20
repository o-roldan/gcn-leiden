import pandas as pd, numpy as np, glob
R='/Users/omar/Developer/me/gcn-leiden/results'
cols=['k','epochs','nmi','ari','q','dbi','peak_nmi','peak_ari','peak_q','peak_dbi']
for ds in ['cora','citeseer']:
    a=pd.read_csv(f'{R}/runs_{ds}.csv'); a=a[a.method.str.startswith('gcn')&a.seed.between(0,4)].set_index(['method','seed'])[cols].sort_index()
    b=pd.read_csv(f'{R}/runs_validate_{ds}.csv'); b=b[b.seed.between(0,4)].set_index(['method','seed'])[cols].sort_index()
    print(ds, 'identical all cols:', a.equals(b), '| max abs diff', float((a-b).abs().max().max()))
    # compare histories too
    for m in ['gcn-louvain','gcn-leiden']:
        for s in range(5):
            h1=pd.read_csv(f'{R}/history/history_{ds}/{m}_{ds}_seed{s}.csv')
            fs=glob.glob(f'{R}/history/history_validate_{ds}/**/{m}_{ds}_seed{s}*.csv',recursive=True)
            if fs:
                h2=pd.read_csv(fs[0]); print('  hist',m,s,'equal' if h1[['epoch','loss','nmi']].equals(h2[['epoch','loss','nmi']]) else 'DIFF', len(fs))
