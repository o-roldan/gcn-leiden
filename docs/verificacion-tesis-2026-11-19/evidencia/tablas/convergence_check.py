"""Recompute tab:convergencia-prior from training histories (independent)."""
import glob
import re
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, "/private/tmp/claude-501/-Users-omar-Developer-me-gcn-leiden/ddebb875-fe4a-43f3-ab25-1ab06b6b4a1f/scratchpad/verify/tablas")
from texparse import parse_cell, split_row, table_lines  # noqa
from main_tables import NAME2DS  # noqa

H = "/Users/omar/Developer/me/gcn-leiden/results/history"
TEX = "/Users/omar/Developer/me/gnn-thesis/chapters/resultados/resultados.tex"
ALPHA = 1e-3  # loss = alpha * (-Q')  (trainer.py:71, loss.py:22)

DS = ["cora", "citeseer", "pubmed", "cocs", "amac", "amap", "wikics", "film"]
runs = {}
for ds in DS:
    for meth in ["gcn-louvain", "gcn-leiden"]:
        for s in range(5):
            f = f"{H}/history_{ds}/{meth}_{ds}_seed{s}.csv"
            h = pd.read_csv(f)
            h["qsoft"] = -h["loss"] / ALPHA
            runs[(ds, meth, s)] = h


def first_epoch(h, col, target, strict=False):
    x = h[col].to_numpy()
    idx = np.where(x > target)[0] if strict else np.where(x >= target)[0]
    return h.epoch.to_numpy()[idx[0]] if len(idx) else np.nan


def compute(col="qsoft", frac=0.95, agg="mean_of_max", strict=False, datasets=DS[:-1]):
    res = {}
    for ds in datasets:
        qmax = {}
        for meth in ["gcn-louvain", "gcn-leiden"]:
            if agg == "mean_of_max":
                qmax[meth] = np.mean([runs[(ds, meth, s)][col].max() for s in range(5)])
            else:  # max of mean trajectory
                traj = pd.concat([runs[(ds, meth, s)].set_index("epoch")[col] for s in range(5)], axis=1).mean(axis=1)
                qmax[meth] = traj.max()
        target = frac * min(qmax.values())
        out = {"target": target, "qmax": qmax}
        for meth in ["gcn-louvain", "gcn-leiden"]:
            ep = [first_epoch(runs[(ds, meth, s)], col, target, strict) for s in range(5)]
            out[meth] = ep
        res[ds] = out
    return res


def show(res, label):
    print(f"--- {label}")
    for ds, o in res.items():
        a, b = np.array(o["gcn-louvain"], float), np.array(o["gcn-leiden"], float)
        print(f"{ds:9s} target={o['target']:.4f} qmax(lv/ld)={o['qmax']['gcn-louvain']:.4f}/{o['qmax']['gcn-leiden']:.4f} "
              f"LV={np.nanmean(a):.1f}±{np.nanstd(a, ddof=1):.1f} {a.astype(int).tolist() if not np.isnan(a).any() else a.tolist()} "
              f"LD={np.nanmean(b):.1f}±{np.nanstd(b, ddof=1):.1f} {b.astype(int).tolist() if not np.isnan(b).any() else b.tolist()}")


main = compute()
show(main, "Q' = -loss/alpha, 95% of min(mean of per-run max), first epoch with Q' >= target")

# compare to thesis
print("\n=== comparison with thesis ===")
for ln, line in table_lines(TEX, "tab:convergencia-prior"):
    c = split_row(line)
    ds = NAME2DS[c[0]]
    o = main[ds]
    tgt = c[1]
    lv, ld = parse_cell(c[2]), parse_cell(c[3])
    a, b = np.array(o["gcn-louvain"], float), np.array(o["gcn-leiden"], float)
    mine = (f"{o['target']:.3f}", f"{a.mean():.1f}", f"{a.std(ddof=1):.1f}", f"{b.mean():.1f}", f"{b.std(ddof=1):.1f}")
    th = (tgt, lv["val"], lv["sd"], ld["val"], ld["sd"])
    print(f"L{ln} {ds:9s} thesis={th} mine={mine} {'OK' if th == mine else 'MISMATCH'}  raw target={o['target']:.5f}")

# robustness variants
show(compute(agg="max_of_mean"), "variant: max of mean trajectory")
show(compute(strict=True), "variant: strict >")
show(compute(col="q"), "variant: hard modularity q column (NOT Q')")

# Actor exclusion claim: Q' of gcn-leiden on film
print("\n=== Actor (film) ===")
for meth in ["gcn-leiden", "gcn-louvain"]:
    for s in range(5):
        h = runs[("film", meth, s)]
        print(meth, s, "Q' range", h.qsoft.min(), h.qsoft.max(), "rows", len(h), "last epoch", h.epoch.max())

# also history lengths and Q' max epochs
print("\n=== per-run last epoch & epoch of Q'max ===")
for ds in DS[:-1]:
    for meth in ["gcn-louvain", "gcn-leiden"]:
        le = [runs[(ds, meth, s)].epoch.max() for s in range(5)]
        em = [int(runs[(ds, meth, s)].epoch.iloc[runs[(ds, meth, s)].qsoft.argmax()]) for s in range(5)]
        print(ds, meth, "last", le, "ep_qmax", em, "mean", np.mean(em))

# check: history columns include grad_norm?
print({ds: list(runs[(ds, 'gcn-leiden', 0)].columns) for ds in DS})
