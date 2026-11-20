exec(open("/private/tmp/claude-501/-Users-omar-Developer-me-gcn-leiden/ddebb875-fe4a-43f3-ab25-1ab06b6b4a1f/scratchpad/verify/reverif/common.py").read())
for ds in ["cora","citeseer","pubmed","cocs","amac","amap","film","wikics"]:
    df=load(f"runs_{ds}.csv")
    a=df[df.method=="gcn-louvain"].set_index("seed").sort_index(); b=df[df.method=="gcn-leiden"].set_index("seed").sort_index()
    for met in ["peak_nmi","peak_ari"]:
        d=b[met].mean()-a[met].mean(); mx=max(a[met].std(ddof=1),b[met].std(ddof=1))
        wins=int((b[met]>a[met]).sum()); 
        verdict = "tie" if abs(d)<mx else ("Leiden" if d>0 else "Louvain")
        print(f"{ds:9s} {met:8s} Lou {a[met].mean():.5f}±{a[met].std(ddof=1):.5f} Lei {b[met].mean():.5f}±{b[met].std(ddof=1):.5f} diff {d:+.5f} maxsd {mx:.5f} -> {verdict}; Leiden>Louvain seeds {wins}/5 per-seed diffs {list((b[met]-a[met]).round(4))}")
    print(f"           epochs Lou {list(a.epochs)} Lei {list(b.epochs)}")
