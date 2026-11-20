exec(open("/private/tmp/claude-501/-Users-omar-Developer-me-gcn-leiden/ddebb875-fe4a-43f3-ab25-1ab06b6b4a1f/scratchpad/verify/reverif/common.py").read())
df=load("runs_recal_film.csv")
g=df.groupby(["method","resolution","beta"]).agg(n=("seed","size"),k=("k","first"),nmi=("nmi","mean"),ari=("ari","mean"),pnmi=("peak_nmi","mean"),pari=("peak_ari","mean"),pnmi_max=("peak_nmi","max"),pari_max=("peak_ari","max"),q=("q","mean"))
print(g.round(4).to_string())
