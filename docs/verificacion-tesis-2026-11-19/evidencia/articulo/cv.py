import pandas as pd, numpy as np, glob, os
R="/Users/omar/Developer/me/gcn-leiden/results/"
N={"cora":2708,"citeseer":3327,"pubmed":19717,"cocs":18333,"amac":13752,"amap":7650,"film":7600,"wikics":11701,"sbm_1000_5":1000,"sbm_5000_10":5000,"sbm_10000_20":10000,"cophysics":34493}
def cfg(s):
    d={}
    for kv in str(s).split(";"):
        if "=" in kv: a,b=kv.split("=",1); d[a]=b
    return d
seen={}
for f in sorted(glob.glob(R+"runs_*.csv")):
    name=os.path.basename(f)[5:-4]
    if name=="" or name=="runs": continue
    ds=name.replace("recal_","").replace("validate_","")
    if ds not in N: continue
    df=pd.read_csv(f); df=df[df.seed.isin(range(5))]
    for _,r in df[df.method.str.startswith("gcn")].iterrows():
        c=cfg(r.config); b=float(c["beta"]); k0=int(c["k0"]); T=float(c["threshold"])
        mu=N[ds]/k0
        if b==0: 
            key=(ds,r.method,c.get("prior_objective"),c.get("resolution"))
            seen.setdefault(key,{})["mu_check"]=(T,round(mu,2)); continue
        sd=(T-mu)/b
        key=(ds,r.method,c.get("prior_objective"),c.get("resolution"))
        seen.setdefault(key,{}).setdefault("cv",set()).add(round(sd/mu,4))
        seen[key]["k0"]=k0
for k,v in sorted(seen.items()): print(k,v)
# bit-for-bit validate vs main
for ds in ("cora","citeseer"):
    a=pd.read_csv(R+f"runs_{ds}.csv"); a=a[a.method.str.startswith("gcn")&a.seed.isin(range(5))]
    b=pd.read_csv(R+f"runs_validate_{ds}.csv"); b=b[b.seed.isin(range(5))]
    cols=["method","seed","k","nmi","ari","q","peak_nmi","peak_ari","peak_q"]
    m=a[cols].merge(b[cols],on=["method","seed"],suffixes=("_a","_b"))
    same=all((m[c+"_a"]==m[c+"_b"]).all() for c in cols[2:])
    print(ds,"validate == main:",same,len(m))
print("4.4GiB:",34493**2*4/2**30)
