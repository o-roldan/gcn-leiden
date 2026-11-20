import pandas as pd, numpy as np
I=pd.read_csv('conv_runinfo.csv')
for col in ['q0','qmax']:
    for ds,g in I.groupby('ds'):
        a=g[g.prior=='louvain'].sort_values('seed')[col].values; b=g[g.prior=='leiden'].sort_values('seed')[col].values
        d=b-a; mx=max(a.std(ddof=1),b.std(ddof=1))
        print(f'{col} {ds:9s} Lou {a.mean():.4f}±{a.std(ddof=1):.4f} Lei {b.mean():.4f}±{b.std(ddof=1):.4f} diff {d.mean():+.4f} = {d.mean()/mx:+.2f} maxσ; Lei>Lou {int((d>0).sum())}/5')
