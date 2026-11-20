exec(open("/private/tmp/claude-501/-Users-omar-Developer-me-gcn-leiden/ddebb875-fe4a-43f3-ab25-1ab06b6b4a1f/scratchpad/verify/reverif/common.py").read())
import json
DS=["cora","citeseer","pubmed","cocs","cophysics","amac","amap","film","wikics","sbm_1000_5","sbm_5000_10","sbm_10000_20"]
M=["louvain","leiden","deepwalk","dgi","dmon","gcn-louvain","gcn-leiden"]
out={}
for ds in DS:
    df=load(f"runs_{ds}.csv")
    rows={}
    for m in M:
        s=df[df.method==m]
        if m in ("louvain","leiden"):
            s=s[s.resolution=="1.0"]
        if ds.startswith("sbm") and m.startswith("gcn"):
            if m=="gcn-louvain":
                v=load(f"runs_validate_{ds}.csv"); s=v[v.method==m]
            else:
                v=load(f"runs_recal_{ds}.csv"); s=v[(v.method==m)&(v.prior_objective=="cpm")&(v.beta=="0.5")]
        if len(s)==0: continue
        rows[m]={met:(float(s[met].mean()), float(s[met].std(ddof=1)), len(s)) for met in ["nmi","ari","q","dbi","k"]}
        if m.startswith("gcn"):
            rows[m]["cfg"]=sorted(set(zip(s.resolution,s.beta,s.prior_objective,s.filter_variant)))
            rows[m]["peak_nmi"]=(float(s.peak_nmi.mean()),float(s.peak_nmi.std(ddof=1)),len(s))
            rows[m]["peak_ari"]=(float(s.peak_ari.mean()),float(s.peak_ari.std(ddof=1)),len(s))
    out[ds]=rows
    print("=====",ds)
    for met in ["nmi","ari","q","dbi","k"]:
        vals={m:rows[m][met] for m in rows}
        best=max((v[0],m) for m,v in vals.items() if not np.isnan(v[0]))
        line=" | ".join(f"{m}:{v[0]:.5f}±{v[1]:.4f}(n{v[2]})" for m,v in vals.items())
        print(f"{met:4s} {line}")
        if met in("nmi","ari","q"):
            ties=[m for m,v in vals.items() if v[0]==best[0]]
            print(f"     BEST(unrounded)={ties} {best[0]:.6f}")
    for m in rows:
        if "cfg" in rows[m]: print("   cfg",m,rows[m]["cfg"])
json.dump(out,open("/private/tmp/claude-501/-Users-omar-Developer-me-gcn-leiden/ddebb875-fe4a-43f3-ab25-1ab06b6b4a1f/scratchpad/verify/reverif/main_stats.json","w"),indent=1)
