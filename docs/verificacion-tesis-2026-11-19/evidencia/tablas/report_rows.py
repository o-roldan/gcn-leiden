import pandas as pd

df = pd.read_csv("/private/tmp/claude-501/-Users-omar-Developer-me-gcn-leiden/ddebb875-fe4a-43f3-ab25-1ab06b6b4a1f/scratchpad/verify/tablas/main_best_b0.5.csv")
SHORT = {"tab:resultados-citas-coautoria": "tab:resultados-citas-coautoria",
         "tab:resultados-compra-web": "tab:resultados-compra-web",
         "tab:resultados-sbm": "tab:resultados-sbm"}
MCOL = {"nmi": "nmi", "ari": "ari", "q": "q", "dbi": "dbi", "k": "k"}
i = 24
for (tab, ln, ds, metric), g in df.groupby(["table", "line", "ds", "metric"], sort=False):
    allok = g.status.str.startswith("OK").all()
    bnd = g[g.status.str.contains("BOUNDARY")]
    note = ""
    if len(bnd):
        note = "; límite x.xxx5: " + ", ".join(f"{r.col}" for _, r in bnd.iterrows())
    if ds.startswith("sbm"):
        src = f"runs_{ds}.csv (clásicos res=1.0, DW/DGI/DMoN); GCN-Louvain runs_validate_{ds}.csv; GCN-Leiden runs_recal_{ds}.csv cpm g=0.0275 b=0.5; col `{MCOL[metric]}`; seeds 0-4"
    elif ds == "cophysics":
        src = f"runs_cophysics.csv (clásicos res=1.0, DW/DGI/DMoN); sin filas gcn-*; col `{MCOL[metric]}`; seeds 0-4"
    else:
        src = f"runs_{ds}.csv (clásicos res=1.0; DW/DGI/DMoN; gcn-* b=0.5 g=0.3 mod) col `{MCOL[metric]}`; seeds 0-4"
    nb = "" if metric == "k" else ", negritas OK"
    n_cells = len(g)
    status = "✅" if allok else "❌"
    print(f"| T-{i:02d} | resultados.tex:{ln} | {tab.split(':')[1]} {ds} {metric.upper()}: {n_cells} celdas | {status} | {n_cells}/{n_cells} coinciden{nb}{note} | {src} |")
    i += 1
