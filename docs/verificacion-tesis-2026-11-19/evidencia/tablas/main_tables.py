"""Verify tab:resultados-citas-coautoria, tab:resultados-compra-web, tab:resultados-sbm."""
import re
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, "/private/tmp/claude-501/-Users-omar-Developer-me-gcn-leiden/ddebb875-fe4a-43f3-ab25-1ab06b6b4a1f/scratchpad/verify/tablas")
from texparse import parse_cell, split_row, table_lines  # noqa

R = "/Users/omar/Developer/me/gcn-leiden/results"
TEX = "/Users/omar/Developer/me/gnn-thesis/chapters/resultados/resultados.tex"

NAME2DS = {"Cora": "cora", "CiteSeer": "citeseer", "PubMed": "pubmed",
           "Coauthor CS": "cocs", "Coauthor Physics": "cophysics",
           "Amazon Computers": "amac", "Amazon Photo": "amap", "Actor": "film",
           "WikiCS": "wikics", "SBM-1k": "sbm_1000_5", "SBM-5k": "sbm_5000_10",
           "SBM-10k": "sbm_10000_20"}
COLS = ["louvain", "leiden", "deepwalk", "dgi", "dmon", "gcn-louvain", "gcn-leiden"]
MET = {"$NMI$": "nmi", "$ARI$": "ari", "$Q$": "q", "$DBI$": "dbi", "$k$": "k"}


def cfg(df):
    def p(s):
        return dict(kv.split("=", 1) for kv in s.split(";"))
    c = df.config.apply(p).apply(pd.Series)
    return pd.concat([df.reset_index(drop=True), c.reset_index(drop=True)], axis=1)


def load(name):
    df = pd.read_csv(f"{R}/{name}")
    df = cfg(df)
    return df[df.seed.isin([0, 1, 2, 3, 4])]


def source_rows(ds, method, sbm_leiden_beta="0.5", view="best"):
    """Rows feeding one column of the main tables, per my reading of protocol."""
    if method in ("louvain", "leiden"):
        df = load(f"runs_{ds}.csv")
        return df[(df.method == method) & (df.resolution == "1.0")], f"runs_{ds}.csv method={method} resolution=1.0"
    if method in ("deepwalk", "dgi", "dmon"):
        df = load(f"runs_{ds}.csv")
        return df[df.method == method], f"runs_{ds}.csv method={method}"
    if not ds.startswith("sbm"):
        df = load(f"runs_{ds}.csv")
        sel = df[(df.method == method)]
        return sel, f"runs_{ds}.csv method={method} (beta=0.5,res=0.3,modularity)"
    # SBM
    if method == "gcn-louvain":
        df = load(f"runs_validate_{ds}.csv")
        return df[df.method == method], f"runs_validate_{ds}.csv method=gcn-louvain recalibrado mod g=1.0 b=0.5"
    df = load(f"runs_recal_{ds}.csv")
    sel = df[(df.method == "gcn-leiden") & (df.prior_objective == "cpm") & (df.beta == sbm_leiden_beta)]
    return sel, f"runs_recal_{ds}.csv gcn-leiden cpm g=0.0275 b={sbm_leiden_beta}"


def stat(sel, metric, view="best"):
    col = metric if (view == "best" or metric == "k") else f"peak_{metric}"
    x = pd.to_numeric(sel[col], errors="coerce")
    if len(x) == 0:
        return None
    if x.isna().all():
        return (np.nan, np.nan, len(x), x.tolist())
    return (x.mean(), x.std(ddof=1), len(x), x.tolist())


def boundary(v, nd=3):
    """True if v lies (within 1e-9) on a rounding boundary at nd decimals."""
    s = v * 10 ** nd
    return abs((s - np.floor(s)) - 0.5) < 1e-6


def fmt(v, nd=3):
    return f"{v:.{nd}f}"


def main(view="best", sbm_leiden_beta="0.5"):
    out = []
    for label in ["tab:resultados-citas-coautoria", "tab:resultados-compra-web", "tab:resultados-sbm"]:
        cur = None
        for ln, line in table_lines(TEX, label):
            cells = split_row(line)
            m = re.search(r"\\multirow\{\d+\}\{\*\}\{(.+?)\}", cells[0])
            if m:
                cur = m.group(1)
            ds = NAME2DS[cur]
            metric = MET[cells[1]]
            vals = [parse_cell(c) for c in cells[2:]]
            computed = {}
            for col, cell in zip(COLS, vals):
                sel, src = source_rows(ds, col, sbm_leiden_beta)
                st = stat(sel, metric, view)
                computed[col] = st
                status = ""
                if st is None or (isinstance(st[0], float) and np.isnan(st[0])):
                    mine = "---"
                    status = "OK" if cell["val"] is None else "MISMATCH"
                else:
                    mean, sd, n, xs = st
                    if metric == "k":
                        if np.isclose(sd, 0) or np.isnan(sd):
                            mine = f"{mean:g}"
                            ok = cell["val"] is not None and float(cell["val"]) == mean and (cell["sd"] is None)
                        else:
                            mine = f"{mean:.1f}±{sd:.1f}"
                            ok = cell["val"] == f"{mean:.1f}" and cell["sd"] == f"{sd:.1f}"
                    else:
                        mine = f"{fmt(mean)}±{fmt(sd)}"
                        ok = (cell["val"] is not None and cell["sd"] is not None and
                              (cell["val"] == fmt(mean) or (cell["val"] == "-0.000" and fmt(mean) in ("-0.000", "0.000"))) and cell["sd"] == fmt(sd))
                    status = "OK" if ok else "MISMATCH"
                    if boundary(mean) or (not np.isnan(sd) and boundary(sd)):
                        status += " (BOUNDARY)"
                    if n != 5:
                        status += f" (n={n})"
                thesis = "---" if cell["val"] is None else f"{cell['val']}±{cell['sd']}" if cell["sd"] else cell["val"]
                out.append(dict(table=label, line=ln, ds=ds, metric=metric, col=col,
                                thesis=thesis, bold=cell["bold"], mine=mine, status=status, src=src,
                                raw_mean=None if st is None else st[0]))
    return pd.DataFrame(out)


if __name__ == "__main__":
    view = sys.argv[1] if len(sys.argv) > 1 else "best"
    beta = sys.argv[2] if len(sys.argv) > 2 else "0.5"
    df = main(view, beta)
    pd.set_option("display.width", 250, "display.max_rows", 2000, "display.max_colwidth", 80)
    print(df[["line", "ds", "metric", "col", "thesis", "bold", "mine", "status"]].to_string())
    df.to_csv(f"/private/tmp/claude-501/-Users-omar-Developer-me-gcn-leiden/ddebb875-fe4a-43f3-ab25-1ab06b6b4a1f/scratchpad/verify/tablas/main_{view}_b{beta}.csv", index=False)
