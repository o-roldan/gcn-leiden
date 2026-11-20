import pandas as pd, glob, os
R='/Users/omar/Developer/me/gcn-leiden/results'
pd.set_option('display.width',250); pd.set_option('display.max_columns',30); pd.set_option('display.max_colwidth',200)
for f in sorted(glob.glob(R+'/runs_*.csv')):
    d=pd.read_csv(f)
    print('==',os.path.basename(f), len(d))
    print(d.groupby('method').seed.apply(lambda s: sorted(s.tolist())).to_string())
    g=d[d.method.str.startswith('gcn')]
    if len(g): print(g.config.str.replace(r'threshold=[^;]*|k0=[^;]*','',regex=True).value_counts().to_string())
