exec(open("/private/tmp/claude-501/-Users-omar-Developer-me-gcn-leiden/ddebb875-fe4a-43f3-ab25-1ab06b6b4a1f/scratchpad/verify/reverif/common.py").read())
for ds in ["amac","amap"]:
    df=load(f"runs_{ds}.csv")
    for m in ["dgi","gcn-leiden","gcn-louvain"]:
        s=df[df.method==m].sort_values("seed")
        print(ds,m,"nmi per seed",s.nmi.round(4).tolist())
