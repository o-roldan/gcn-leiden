import re, glob, pandas as pd, numpy as np
R="/Users/omar/Developer/me/gcn-leiden/results/"
PAPER="/Users/omar/Developer/me/gnn-paper/main.tex"
def cfg(s):
    d={}
    for kv in str(s).split(";"):
        if "=" in kv: a,b=kv.split("=",1); d[a]=b
    return d
def load(name):
    df=pd.read_csv(R+f"runs_{name}.csv")
    df=df[df.seed.isin(range(5))].copy()
    c=df.config.apply(cfg)
    for key in ["resolution","beta","prior_objective","k0","threshold","filter_variant","objective"]:
        df[key]=c.apply(lambda d:d.get(key))
    return df
DS={"Cora":"cora","CiteSeer":"citeseer","PubMed":"pubmed","Coauthor CS":"cocs","Amazon Computers":"amac","Amazon Photo":"amap","Actor":"film","WikiCS":"wikics","SBM-1k":"sbm_1000_5","SBM-5k":"sbm_5000_10","SBM-10k":"sbm_10000_20"}
METH=["louvain","leiden","deepwalk","dgi","dmon","gcn-louvain","gcn-leiden"]
def rows_for(dsname):
    key=DS[dsname]; df=load(key); out={}
    for m in METH:
        if key.startswith("sbm") and m in("gcn-louvain","gcn-leiden"):
            if m=="gcn-louvain":
                d=load("validate_"+key); d=d[d.method==m]
            else:
                d=load("recal_"+key); d=d[(d.method==m)&(d.prior_objective=="cpm")&(d.beta=="0.5")]
        else:
            d=df[df.method==m]
            if m in("louvain","leiden"): d=d[d.resolution=="1.0"]
        out[m]=d
    return out
def fmt(v,s): return f"{v:.3f}", f"{s:.3f}"
# parse paper tables
tex=open(PAPER).read()
cells={}
cur=None
for line in tex.split("\n"):
    m=re.match(r"\\multirow\{\d\}\{\*\}\{([^}]*)\}\s*&\s*(.*)",line.strip())
    if m: cur=m.group(1); rest=m.group(2)
    elif line.strip().startswith("& $") and cur: rest=line.strip()[1:].strip()
    else: continue
    parts=[p.strip() for p in rest.rstrip("\\").strip().rstrip("\\").split("&")]
    metric=parts[0].strip("$ ")
    cells[(cur,metric)]=parts[1:]
def parse(c):
    bold="\\textbf" in c
    nums=re.findall(r"-?\d+\.\d+|-?\d+",c.replace("\\scriptsize",""))
    return bold,nums
issues=[]
for (ds,metric),vals in cells.items():
    if ds not in DS: continue
    data=rows_for(ds)
    col={"NMI":"nmi","ARI":"ari","Q":"q","k":"k"}[metric]
    means={}
    for m,c in zip(METH,vals):
        d=data[m]
        n=len(d)
        x=d[col].astype(float)
        mu=x.mean(); sd1=x.std(ddof=1); sd0=x.std(ddof=0)
        means[m]=mu
        bold,nums=parse(c)
        if metric=="k":
            exp = f"{mu:.1f}" if sd1>0 else f"{int(round(mu))}"
            ok = (nums[0]==exp) or (len(nums)==1 and float(nums[0])==mu)
            if sd1>0:
                ok = ok and len(nums)>1 and nums[1]==f"{sd1:.1f}"
            if not ok: issues.append((ds,metric,m,c,f"{mu:.2f}±{sd1:.2f} n={n}"))
        else:
            e=(f"{mu:.3f}",f"{sd1:.3f}")
            if mu<0 and round(mu,3)==0: e=("-0.000",e[1])
            if tuple(nums[:2])!=e:
                issues.append((ds,metric,m,c,f"{mu:.4f}±{sd1:.4f} (ddof0 {sd0:.4f}) n={n}"))
            if n!=5: issues.append((ds,metric,m,"n!=5",n))
    if metric!="k":
        best=max(means.values())
        for m,c in zip(METH,vals):
            bold,_=parse(c)
            isbest=abs(means[m]-best)<1e-12
            if bold!=isbest:
                issues.append((ds,metric,m,"BOLD mismatch", f"bold={bold} mean={means[m]:.6f} best={best:.6f}"))
print("Main tables checked cells:",len(cells))
for i in issues: print("ISSUE",i)
