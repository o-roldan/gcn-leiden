"""Regenerate main result tables (resultados.tex) from CSVs.
GCN columns use the min-loss checkpoint (nmi/ari/q/dbi); baselines unchanged source.
Usage: tables.py RESULTS_DIR TEX_IN TEX_OUT"""
import pandas as pd, sys, re, math
R, TIN, TOUT = sys.argv[1:4]
def load(f):
    d = pd.read_csv(f"{R}/{f}"); return d[d.seed.isin(range(5))]
NAME = {'Cora':'cora','CiteSeer':'citeseer','PubMed':'pubmed','Coauthor CS':'cocs',
        'Coauthor Physics':'cophysics','Amazon Computers':'amac','Amazon Photo':'amap',
        'Actor':'film','WikiCS':'wikics','SBM-1k':'sbm_1000_5','SBM-5k':'sbm_5000_10',
        'SBM-10k':'sbm_10000_20'}
METHODS = ['louvain','leiden','deepwalk','dgi','dmon','gcn-louvain','gcn-leiden']
def runs(ds, m):
    d = load(f"runs_{ds}.csv")
    if m in ('louvain','leiden'):
        return d[(d.method==m) & d.config.str.contains('resolution=1.0')]
    if ds.startswith('sbm') and m=='gcn-louvain':
        v = load(f"runs_validate_{ds}.csv")
        return v[(v.method==m) & v.config.str.contains('beta=0.5;')]
    if ds.startswith('sbm') and m=='gcn-leiden':
        r = load(f"runs_recal_{ds}.csv")
        return r[r.config.str.contains('prior_objective=cpm') & r.config.str.contains('beta=0.5;')]
    return d[d.method==m]
MET = {'$NMI$':'nmi','$ARI$':'ari','$Q$':'q','$DBI$':'dbi'}
def stat(ds, m, col):
    d = runs(ds, m)
    if len(d)==0 or (col=='dbi' and m in ('louvain','leiden')): return None
    x = d[col].astype(float)
    if x.isna().all(): return None
    assert len(d)==5, (ds,m,len(d))
    return x.mean(), x.std(ddof=1)
def fmt(s, bold):
    if s is None: return '---'
    c = f"{s[0]:.3f}{{\\scriptsize$\\pm${s[1]:.3f}}}"
    return f"\\textbf{{{c}}}" if bold else c
out, cur, mism = [], None, []
for line in open(TIN).read().split('\n'):
    mm = re.match(r'\\multirow\{4\}\{\*\}\{([^}]*)\}', line.strip())
    if mm: cur = mm.group(1)
    hit = [k for k in MET if f'& {k} &' in line]
    if cur in NAME and hit:
        key, col, ds = hit[0], MET[hit[0]], NAME[cur]
        stats = [stat(ds, m, col) for m in METHODS]
        vals = [s[0] for s in stats if s is not None]
        best = (min if col=='dbi' else max)(vals)
        cells = [fmt(s, s is not None and abs(s[0]-best)<1e-12) for s in stats]
        prefix = line.split(f'& {key} &')[0]
        old = [c.strip() for c in line.split(f'& {key} &')[1].rstrip('\\ ').split('&')]
        for m, o, n in zip(METHODS, old, cells):
            strip = lambda c: re.sub(r'\\textbf\{(.*)\}$', r'\1', c)
            if not m.startswith('gcn') and strip(o)!=strip(n): mism.append((cur,key,m,o,n))
        line = f"{prefix}& {key} & " + ' & '.join(cells) + r' \\'
    out.append(line)
open(TOUT,'w').write('\n'.join(out))
print("baseline mismatches:", len(mism))
for x in mism: print(x)
