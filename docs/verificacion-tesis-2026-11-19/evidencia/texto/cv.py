import pandas as pd, numpy as np, glob, os
R='/Users/omar/Developer/me/gcn-leiden/results'
N={"cora":2708,"citeseer":3327,"pubmed":19717,"cocs":18333,"cophysics":34493,"amac":13752,"amap":7650,"film":7600,"wikics":11701,"sbm_1000_5":1000,"sbm_5000_10":5000,"sbm_10000_20":10000}
pd.set_option('display.width',250)
rows=[]
for f in sorted(glob.glob(R+'/runs_*.csv')):
    if os.path.basename(f)=='runs.csv': continue
    d=pd.read_csv(f); d=d[d.method.str.startswith('gcn')&d.seed.between(0,4)]
    if d.empty: continue
    c=d.config.apply(lambda s: dict(kv.split('=',1) for kv in s.split(';') if '=' in kv))
    for key in ['beta','k0','threshold','resolution','prior_objective','filter_variant']:
        d[key]=c.apply(lambda x:x.get(key))
    d['filter_variant']=d.filter_variant.fillna('wang')
    for key in ['beta','k0','threshold','resolution']: d[key]=d[key].astype(float)
    for (m,ds,obj,res,b,fv),g in d.groupby(['method','dataset','prior_objective','resolution','beta','filter_variant']):
        n=N[ds]; k0=g.k0.unique(); T=g.threshold.unique(); k=g.k.unique()
        mu=n/k0[0]
        cv=(T[0]/mu-1)/b if b!=0 else np.nan
        rows.append(dict(file=os.path.basename(f).replace('runs_','').replace('.csv',''),method=m,obj=obj,res=res,beta=b,fv=fv,k0=list(k0),T=list(T),k=list(k),mu=round(mu,2),cv=cv,
                         nmi=round(g.nmi.mean(),3),nmi_sd=round(g.nmi.std(),3),peak=round(g.peak_nmi.mean(),3),peak_sd=round(g.peak_nmi.std(),3)))
D=pd.DataFrame(rows)
print(D.to_string())
D.to_csv('cv_table.csv',index=False)
