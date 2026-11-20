import pandas as pd
import numpy as np

df = pd.read_csv("/private/tmp/claude-501/-Users-omar-Developer-me-gcn-leiden/ddebb875-fe4a-43f3-ab25-1ab06b6b4a1f/scratchpad/verify/tablas/main_best_b0.5.csv")
df = df[df.metric != "k"]
for (tab, line, ds, metric), g in df.groupby(["table", "line", "ds", "metric"], sort=False):
    thesis_bold = set(g[g.bold].col)
    # displayed thesis values
    disp = {}
    for _, r in g.iterrows():
        if r.thesis != "---":
            disp[r.col] = float(r.thesis.split("±")[0])
    raw = {r.col: r.raw_mean for _, r in g.iterrows() if r.raw_mean == r.raw_mean and r.raw_mean is not None}
    if metric == "dbi":
        bd = min(disp.values()); br = min(raw.values())
    else:
        bd = max(disp.values()); br = max(raw.values())
    best_disp = {c for c, v in disp.items() if v == bd}
    best_raw = {c for c, v in raw.items() if abs(v - br) < 1e-12}
    flag = "OK" if thesis_bold == best_disp else ("OK-raw" if thesis_bold == best_raw else "MISMATCH")
    print(f"{line:4d} {ds:13s} {metric:4s} thesis={sorted(thesis_bold)} disp={sorted(best_disp)} raw={sorted(best_raw)} -> {flag}")
    if flag != "OK":
        print("      raw means:", {c: round(v, 5) for c, v in raw.items()})
