"""Verify tab:prior-pico, tab:recal-beta, tab:recal-sbm."""
import re
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, "/private/tmp/claude-501/-Users-omar-Developer-me-gcn-leiden/ddebb875-fe4a-43f3-ab25-1ab06b6b4a1f/scratchpad/verify/tablas")
from texparse import parse_cell, split_row, table_lines  # noqa
from main_tables import load, NAME2DS, boundary  # noqa

TEX_R = "/Users/omar/Developer/me/gnn-thesis/chapters/resultados/resultados.tex"
TEX_A = "/Users/omar/Developer/me/gnn-thesis/chapters/appendices/app0A.tex"


def ms(x):
    x = pd.to_numeric(x)
    return x.mean(), x.std(ddof=1), len(x)


def cmp(cell, mean, sd):
    ok = cell["val"] == f"{mean:.3f}" and cell["sd"] == f"{sd:.3f}"
    tag = "OK" if ok else "MISMATCH"
    if boundary(mean) or boundary(sd):
        tag += " (BOUNDARY)"
    return tag


print("=== tab:prior-pico (peak_nmi / peak_ari from runs_<ds>.csv, gcn-*, seeds 0-4) ===")
for ln, line in table_lines(TEX_R, "tab:prior-pico"):
    c = split_row(line)
    ds = NAME2DS[c[0]]
    df = load(f"runs_{ds}.csv")
    for cell_raw, (metric, meth) in zip(c[1:], [("peak_nmi", "gcn-louvain"), ("peak_nmi", "gcn-leiden"),
                                                  ("peak_ari", "gcn-louvain"), ("peak_ari", "gcn-leiden")]):
        cell = parse_cell(cell_raw)
        sel = df[df.method == meth]
        m, s, n = ms(sel[metric])
        # also the checkpoint view for contrast
        print(f"L{ln} {ds:9s} {metric:8s} {meth:11s} thesis={cell['val']}±{cell['sd']} mine={m:.3f}±{s:.3f} raw={m:.5f}/{s:.5f} n={n} {cmp(cell, m, s)}")

print("\n=== tab:recal-beta (runs_recal_<ds>.csv, peak_nmi, k) ===")
BETAS = ["-0.5", "0.0", "0.25", "0.5"]
cur = None
for ln, line in table_lines(TEX_A, "tab:recal-beta"):
    c = split_row(line)
    m = re.search(r"\\multirow\{\d+\}\{\*\}\{(.+?)\}", c[0])
    if m:
        cur = m.group(1)
    ds = NAME2DS[cur]
    meth = {"GCN-Louvain": "gcn-louvain", "GCN-Leiden": "gcn-leiden"}[c[1]]
    df = load(f"runs_recal_{ds}.csv")
    row_means = {}
    for b, cell_raw in zip(BETAS, c[2:]):
        cell = parse_cell(cell_raw)
        sel = df[(df.method == meth) & (df.beta == b)]
        assert set(sel.resolution) == {"0.3"} and set(sel.prior_objective) == {"modularity"}
        mm, s, n = ms(sel.peak_nmi)
        ks = sorted(sel.k.unique())
        row_means[b] = mm
        kok = cell["paren"] is not None and [int(cell["paren"])] == ks
        print(f"L{ln} {ds:8s} {meth:11s} beta={b:5s} thesis={cell['val']}±{cell['sd']} ({cell['paren']}) bold={cell['bold']} "
              f"mine={mm:.3f}±{s:.3f} k={ks} raw={mm:.5f} n={n} {cmp(cell, mm, s)} k:{'OK' if kok else 'MISMATCH'}")
    best = max(row_means.values())
    print("    best-by-raw:", [b for b, v in row_means.items() if abs(v - best) < 1e-12],
          " best-by-display:", [b for b, v in row_means.items() if f"{v:.3f}" == f"{best:.3f}"])
    # also checkpoint view
    print("    checkpoint(nmi) view:", {b: round(df[(df.method == meth) & (df.beta == b)].nmi.mean(), 3) for b in BETAS})

print("\n=== tab:recal-sbm (runs_recal_<ds>.csv, peak_nmi, k) ===")
cur = None
for ln, line in table_lines(TEX_A, "tab:recal-sbm"):
    c = split_row(line)
    m = re.search(r"\\multirow\{\d+\}\{\*\}\{(.+?)\}", c[0])
    if m:
        cur = m.group(1)
    ds = NAME2DS[cur]
    prior = c[1]
    meth = "gcn-leiden" if prior.startswith("Leiden") else "gcn-louvain"
    obj = "cpm" if "cpm" in prior else "modularity"
    gam = "0.0275" if obj == "cpm" else "1.0"
    assert gam in prior
    b = c[2].strip("$")
    bnorm = {"-0.5": "-0.5", "0.0": "0.0", "0.25": "0.25", "0.5": "0.5"}[b]
    cell = parse_cell(c[3])
    kcell = c[4].strip()
    df = load(f"runs_recal_{ds}.csv")
    sel = df[(df.method == meth) & (df.prior_objective == obj) & (df.resolution == gam) & (df.beta == bnorm)]
    mm, s, n = ms(sel.peak_nmi)
    ks = sorted(sel.k.unique())
    k0 = sorted(sel.k0.unique())
    kok = [int(kcell)] == ks
    print(f"L{ln} {ds:13s} {meth:11s} {obj:10s} g={gam:6s} b={bnorm:5s} thesis={cell['val']}±{cell['sd']} k={kcell} | mine={mm:.3f}±{s:.3f} raw={mm:.5f} k={ks} k0={k0} n={n} "
          f"{cmp(cell, mm, s)} k:{'OK' if kok else 'MISMATCH'}")

# rows in CSV absent from table
print("\n=== combos present in recal_sbm CSVs ===")
for ds in ["sbm_1000_5", "sbm_5000_10", "sbm_10000_20"]:
    df = load(f"runs_recal_{ds}.csv")
    print(ds, sorted(set(zip(df.method, df.prior_objective, df.resolution, df.beta))))

print("\n=== classical at gamma=0.3 on SBM (k per seed) ===")
for ds in ["sbm_1000_5", "sbm_5000_10", "sbm_10000_20"]:
    df = load(f"runs_{ds}.csv")
    for meth in ["louvain", "leiden"]:
        sel = df[(df.method == meth) & (df.resolution == "0.3")]
        print(ds, meth, "k=", sel.k.tolist(), "nmi=", sel.nmi.tolist())
