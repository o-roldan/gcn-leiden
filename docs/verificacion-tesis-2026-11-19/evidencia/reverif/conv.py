import pandas as pd, numpy as np
from scipy.stats import wilcoxon
H="/Users/omar/Developer/me/gcn-leiden/results/history"
DS=["cora","citeseer","pubmed","cocs","amac","amap","wikics"]
A=1e-3
runs={}
for ds in DS:
    for m in ["gcn-louvain","gcn-leiden"]:
        for s in range(5):
            h=pd.read_csv(f"{H}/history_{ds}/{m}_{ds}_seed{s}.csv")
            h["qp"]=-h.loss/A
            runs[(ds,m,s)]=h
def first_epoch(h,thr):
    r=h[h.qp>=thr]
    return np.nan if len(r)==0 else int(r.epoch.iloc[0])
print("grid:",{ds:int(runs[(ds,'gcn-louvain',0)].epoch.diff().dropna().mode()[0]) for ds in DS})
qmax={k:h.qp.max() for k,h in runs.items()}
q0={k:h.qp.iloc[0] for k,h in runs.items()}
e0={k:int(h.epoch.iloc[0]) for k,h in runs.items()}
argmax={k:int(h.epoch.iloc[h.qp.values.argmax()]) for k,h in runs.items()}
for frac in [0.9,0.95,0.99]:
    rows=[]
    for ds in DS:
        mlou=np.mean([qmax[(ds,'gcn-louvain',s)] for s in range(5)]); mlei=np.mean([qmax[(ds,'gcn-leiden',s)] for s in range(5)])
        thr=frac*min(mlou,mlei)
        for s in range(5):
            a=first_epoch(runs[(ds,'gcn-louvain',s)],thr); b=first_epoch(runs[(ds,'gcn-leiden',s)],thr)
            rows.append((ds,s,thr,a,b))
    df=pd.DataFrame(rows,columns=["ds","seed","thr","lou","lei"])
    miss=df[df.lou.isna()|df.lei.isna()]
    ok=df.dropna()
    d=ok.lei-ok.lou
    print(f"\nfrac={frac}: missing={miss[['ds','seed','lou','lei']].values.tolist()} n={len(ok)} before(Leiden earlier)={int((d<0).sum())} after={int((d>0).sum())} tie={int((d==0).sum())} p={wilcoxon(ok.lei,ok.lou).pvalue:.4f}")
    if frac==0.95:
        for ds in DS:
            x=df[df.ds==ds]; print(f"  {ds:9s} thr={x.thr.iloc[0]:.3f} lou {x.lou.mean():.1f}±{x.lou.std(ddof=1):.1f} lei {x.lei.mean():.1f}±{x.lei.std(ddof=1):.1f} ties={int((x.lou==x.lei).sum())} after={int((x.lei>x.lou).sum())} before={int((x.lei<x.lou).sum())}")
        nw=ok[ok.ds!="wikics"]; dd=nw.lei-nw.lou
        print(f"  without wikics: n={len(nw)} before={int((dd<0).sum())} after={int((dd>0).sum())} tie={int((dd==0).sum())} p={wilcoxon(nw.lei,nw.lou).pvalue:.4f}")
        for zm in ["wilcox","pratt","zsplit"]:
            try: print("   zero_method",zm, wilcoxon(nw.lei,nw.lou,zero_method=zm).pvalue, "| all:", wilcoxon(ok.lei,ok.lou,zero_method=zm).pvalue)
            except Exception as e: print(zm,e)
        # ties by grid
        ok2=ok.copy(); ok2["tie"]=(ok2.lei==ok2.lou)
        print("  ties by ds:", ok2.groupby("ds").tie.sum().to_dict())
# relative measure
for frac in [0.9,0.95]:
    la=[];lb=[]
    for ds in DS:
        for s in range(5):
            r=[]
            for m in ["gcn-louvain","gcn-leiden"]:
                k=(ds,m,s); thr=q0[k]+frac*(qmax[k]-q0[k]); r.append(first_epoch(runs[k],thr))
            la.append(r[0]); lb.append(r[1])
    la=np.array(la); lb=np.array(lb); d=lb-la
    print(f"relative frac={frac}: before={int((d<0).sum())} after={int((d>0).sum())} tie={int((d==0).sum())} p={wilcoxon(lb,la).pvalue:.4f}")
QA=np.array([q0[(ds,'gcn-louvain',s)] for ds in DS for s in range(5)]); QB=np.array([q0[(ds,'gcn-leiden',s)] for ds in DS for s in range(5)])
MA=np.array([qmax[(ds,'gcn-louvain',s)] for ds in DS for s in range(5)]); MB=np.array([qmax[(ds,'gcn-leiden',s)] for ds in DS for s in range(5)])
print("Q'0 p=",wilcoxon(QB,QA).pvalue," Q'max p=",wilcoxon(MB,MA).pvalue)
for ds in DS:
    da=[qmax[(ds,'gcn-leiden',s)]-qmax[(ds,'gcn-louvain',s)] for s in range(5)]
    d0=[q0[(ds,'gcn-leiden',s)]-q0[(ds,'gcn-louvain',s)] for s in range(5)]
    am=[argmax[(ds,m,s)] for m in ['gcn-louvain','gcn-leiden'] for s in range(5)]
    print(f"{ds:9s} Qmax Lei-Lou per seed {np.round(da,4).tolist()} | Q0 diff {np.round(d0,4).tolist()} | first eval epoch {e0[(ds,'gcn-louvain',0)]} | mean argmax epoch {np.mean(am):.1f} (lou {np.mean(am[:5]):.0f}, lei {np.mean(am[5:]):.0f})")
# history len
print({k:len(h) for k,h in runs.items() if len(h) not in (150,60,30)})
