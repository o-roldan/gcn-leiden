import pandas as pd
R="/Users/omar/Developer/me/gcn-leiden/results/"
def cfg(s):
    return dict(kv.split("=",1) for kv in str(s).split(";") if "=" in kv)
df=pd.read_csv(R+"runs_recal_film.csv"); df=df[df.seed.isin(range(5))].copy()
c=df.config.apply(cfg)
for k in ("resolution","beta","k0"): df[k]=c.apply(lambda d:d.get(k))
print(df.groupby(["method","resolution","beta"]).agg(n=("seed","size"),k=("k","mean"),kmin=("k","min"),kmax=("k","max"),nmi=("nmi","mean"),pk=("peak_nmi","mean"),pkmax=("peak_nmi","max"),q=("q","mean")).round(4).to_string())
import glob,os
H=R+"history/history_recal_film/"
print(os.listdir(H))
for d in sorted(os.listdir(H)):
    fs=sorted(glob.glob(H+d+"/*.csv"))
    qs=[]
    for f in fs:
        h=pd.read_csv(f); qs.append((os.path.basename(f), round((-h.loss/1e-3).max(),3)))
    print(d, qs[:10])
