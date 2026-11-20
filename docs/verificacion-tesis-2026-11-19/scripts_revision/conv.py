import pandas as pd, numpy as np, sys, glob, os
H = sys.argv[1]
rows=[]
for ds in ['cora','citeseer','pubmed','cocs','amac','amap','wikics','film']:
    for m in ['gcn-louvain','gcn-leiden']:
        for s in range(5):
            f=f"{H}/history_{ds}/{m}_{ds}_seed{s}.csv"
            if not os.path.exists(f): continue
            h=pd.read_csv(f); q=-h.loss.values/1e-3; e=h.epoch.values
            q0,qmax=q[0],q.max(); gain=qmax-q0
            def t(x): return e[np.argmax(q>=q0+x*gain)] if gain>0 else np.nan
            iq=q.argmax(); inmi=h.nmi.values.argmax()
            drops=(np.diff(q)< -1e-4).sum()
            rows.append(dict(ds=ds,m=m.replace('gcn-',''),seed=s,last=e[-1],q0=q0,qmax=qmax,gain=gain,
                t50=t(.5),t90=t(.9),t95=t(.95),t99=t(.99),ep_qmax=e[iq],
                nmi0=h.nmi.values[0],nmi_at_qmax=h.nmi.values[iq],nmi_peak=h.nmi.max(),ep_nmi_peak=e[inmi],
                nmi_last=h.nmi.values[-1],drops=drops))
d=pd.DataFrame(rows)
pd.set_option('display.width',250); pd.set_option('display.max_columns',30)
g=d.groupby(['ds','m'],sort=False).mean(numeric_only=True).drop(columns='seed').round(3)
print(g.to_string())
d.to_csv(sys.argv[2],index=False)
