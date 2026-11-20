import pandas as pd,sys
for f in sys.argv[1:]:
    d=pd.read_csv(f)
    d=d[d.seed.isin(range(5))]
    cfg=d.config.str.split(';').apply(lambda xs: dict(x.split('=',1) for x in xs if '=' in x))
    c=pd.DataFrame(list(cfg),index=d.index)
    d=pd.concat([d.drop(columns='config'),c],axis=1)
    cols=[x for x in ['method','prior_objective','resolution','beta','filter_variant'] if x in d.columns]
    print('==',f.split('/')[-1], 'cols:',list(c.columns))
    g=d.groupby(cols,dropna=False).agg(n=('seed','count'),k=('k','mean'),k0=('k0','first') if 'k0' in d.columns else ('k','first'),nmi=('nmi','mean'),pnmi=('peak_nmi','mean'))
    print(g.to_string())
