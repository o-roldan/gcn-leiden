import pandas as pd, numpy as np
R="/Users/omar/Developer/me/gcn-leiden/results"
def cfg(s):
    d={}
    for kv in str(s).split(";"):
        if "=" in kv:
            k,v=kv.split("=",1); d[k]=v
    return d
def load(f):
    df=pd.read_csv(f"{R}/{f}")
    c=df.config.apply(cfg).apply(pd.Series)
    df=pd.concat([df,c],axis=1)
    for col in ["filter_variant","beta","resolution","prior_objective","k0","objective"]:
        if col not in df: df[col]=np.nan
    df["filter_variant"]=df["filter_variant"].fillna("wang")
    df=df.fillna({"beta":"NA","resolution":"NA","prior_objective":"NA","k0":"NA","objective":"NA"})
    return df[df.seed.isin([0,1,2,3,4])]
def ms(x): return f"{x.mean():.4f}±{x.std(ddof=1):.4f}"
