import re, glob, os, pandas as pd, numpy as np
from scipy.stats import wilcoxon
R="/Users/omar/Developer/me/gcn-leiden/results/"
def load(name):
    df=pd.read_csv(R+f"runs_{name}.csv"); return df[df.seed.isin(range(5))]
DS={"Cora":"cora","CiteSeer":"citeseer","PubMed":"pubmed","Coauthor CS":"cocs","Amazon Computers":"amac","Amazon Photo":"amap","Actor":"film","WikiCS":"wikics"}
paper_peak={
"Cora":("0.541","0.007","0.554","0.009","0.480","0.022","0.492","0.020"),
"CiteSeer":("0.401","0.008","0.388","0.012","0.391","0.014","0.375","0.020"),
"PubMed":("0.291","0.014","0.313","0.004","0.250","0.011","0.274","0.005"),
"Coauthor CS":("0.625","0.008","0.629","0.008","0.497","0.005","0.500","0.004"),
"Amazon Computers":("0.543","0.008","0.541","0.003","0.494","0.018","0.489","0.008"),
"Amazon Photo":("0.649","0.002","0.653","0.003","0.489","0.002","0.492","0.001"),
"Actor":("0.007","0.007","0.000","0.000","0.009","0.009","0.000","0.000"),
"WikiCS":("0.419","0.001","0.410","0.003","0.373","0.004","0.369","0.002"),
}
print("== PEAK TABLE")
peak={}
for name,key in DS.items():
    df=load(key)
    got=[]
    for col in ("peak_nmi","peak_ari"):
        for m in ("gcn-louvain","gcn-leiden"):
            x=df[df.method==m][col].astype(float)
            peak[(name,m,col)]=x.values
            got += [f"{x.mean():.3f}", f"{x.std(ddof=1):.3f}"]
    flag = "OK" if tuple(got)==paper_peak[name] else "MISMATCH"
    print(name, flag, got if flag!="OK" else "")
# text claims prior pico
print("== peak diffs (unrounded)")
for name in DS:
    a=peak[(name,"gcn-louvain","peak_nmi")]; b=peak[(name,"gcn-leiden","peak_nmi")]
    d=b.mean()-a.mean(); mx=max(a.std(ddof=1),b.std(ddof=1))
    wins=(b>a).sum()
    print(f"{name}: NMI diff {d:+.4f} maxsd {mx:.4f} ratio {abs(d)/mx if mx>0 else float('nan'):.2f} leiden>louvain seeds {wins}/5")
    a2=peak[(name,"gcn-louvain","peak_ari")]; b2=peak[(name,"gcn-leiden","peak_ari")]
    d2=b2.mean()-a2.mean(); mx2=max(a2.std(ddof=1),b2.std(ddof=1))
    print(f"   ARI diff {d2:+.4f} maxsd {mx2:.4f}")
# Convergence
print("== CONVERGENCE")
H=R+"history/"
rows=[]
for key in ["cora","citeseer","pubmed","cocs","amac","amap","wikics"]:
    for m in ("gcn-louvain","gcn-leiden"):
        for s in range(5):
            f=H+f"history_{key}/{m}_{key}_seed{s}.csv"
            h=pd.read_csv(f); h["qs"]=-h["loss"]/1e-3
            rows.append(dict(ds=key,m=m,seed=s,h=h))
def first(h,level):
    r=h[h.qs>=level]
    return float(r.epoch.iloc[0]) if len(r) else np.nan
paper_conv={"cora":("0.724","64.8","1.1","63.2","1.8"),"citeseer":("0.740","42.4","0.9","44.8","1.1"),"pubmed":("0.616","100.0","0.0","104.0","5.5"),"cocs":("0.620","30.0","0.0","30.0","0.0"),"amac":("0.519","58.0","2.7","58.0","2.7"),"amap":("0.612","49.2","1.1","49.2","1.1"),"wikics":("0.522","79.0","2.2","94.0","4.2")}
def table(frac):
    out={};pairs=[]
    for key in paper_conv:
        rr=[r for r in rows if r["ds"]==key]
        qmax={m:np.mean([r["h"].qs.max() for r in rr if r["m"]==m]) for m in ("gcn-louvain","gcn-leiden")}
        tgt=frac*min(qmax.values())
        ep={m:[first(r["h"],tgt) for r in sorted([r for r in rr if r["m"]==m],key=lambda r:r["seed"])] for m in qmax}
        out[key]=(tgt,ep)
        for s in range(5): pairs.append((key,s,ep["gcn-louvain"][s],ep["gcn-leiden"][s]))
    return out,pairs
out,pairs=table(0.95)
for key,(tgt,ep) in out.items():
    a=np.array(ep["gcn-louvain"]);b=np.array(ep["gcn-leiden"])
    got=(f"{tgt:.3f}",f"{a.mean():.1f}",f"{a.std(ddof=1):.1f}",f"{b.mean():.1f}",f"{b.std(ddof=1):.1f}")
    print(key, "OK" if got==paper_conv[key] else ("MISMATCH",got,paper_conv[key]))
def stats(pairs,label):
    p=[x for x in pairs if not(np.isnan(x[2]) or np.isnan(x[3]))]
    a=np.array([x[2] for x in p]);b=np.array([x[3] for x in p]); d=b-a
    pv=wilcoxon(b,a).pvalue
    print(f"{label}: n={len(p)} leiden earlier={int((d<0).sum())} later={int((d>0).sum())} ties={int((d==0).sum())} p={pv:.4f}")
stats(pairs,"95% fixed")
stats([x for x in pairs if x[0]!="wikics"],"95% fixed sin wikics")
out99,pairs99=table(0.99); stats(pairs99,"99% fixed")
print(" pairs with nan at 99%:",[x for x in pairs99 if np.isnan(x[2]) or np.isnan(x[3])])
# relative t95, q0, qmax
summ=[]
for r in rows:
    h=r["h"]; q=h.qs.values; e=h.epoch.values; q0=q[0]; qm=q.max()
    t95=first(h,q0+0.95*(qm-q0))
    summ.append(dict(ds=r["ds"],m=r["m"],seed=r["seed"],q0=q0,qmax=qm,t95=t95,epq=e[q.argmax()],epn=e[h.nmi.values.argmax()],nmipk=h.nmi.max(),nmiatq=h.nmi.values[q.argmax()],last=e[-1]))
S=pd.DataFrame(summ)
for v in ("t95","q0","qmax"):
    w=S.pivot_table(index=["ds","seed"],columns="m",values=v)
    d=w["gcn-leiden"]-w["gcn-louvain"]
    print(v, "p=%.4f"%wilcoxon(w["gcn-leiden"],w["gcn-louvain"]).pvalue, "leiden>:",int((d>0).sum()),"<:",int((d<0).sum()),"=",int((d==0).sum()))
w=S.pivot_table(index=["ds","seed"],columns="m",values="qmax"); d=(w["gcn-leiden"]-w["gcn-louvain"]).groupby(level=0).apply(lambda x:((x>0).sum(),(x<0).sum()))
print("qmax leiden>louvain per ds:",d.to_dict())
print("NMI peak before Qmax:",int((S.epn<S.epq).sum()),"/",len(S), " equal:",int((S.epn==S.epq).sum()))
print("mean NMI loss:",(S.nmipk-S.nmiatq).groupby(S.ds).mean().round(4).to_dict())
print("mean epoch qmax:",S.groupby("ds").epq.mean().round(1).to_dict())
print("last epochs:",S.groupby("ds").last.agg(['min','max']).to_dict())
