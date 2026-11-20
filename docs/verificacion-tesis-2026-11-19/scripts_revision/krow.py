"""Insert a k row after each DBI row of the main result tables."""
import sys, re, importlib.util
R, TEX = sys.argv[1:3]
spec = importlib.util.spec_from_file_location("t", sys.argv[3]); 
src = open(sys.argv[3]).read().split("out, cur, mism")[0]   # reuse loaders only
sys.argv = ['x', R, '', '']; exec(src)
def kcell(ds, m):
    d = runs(ds, m)
    if len(d) == 0: return '---'
    k = d.k.astype(float); assert len(k) == 5
    return f"{k.mean():.0f}" if k.std(ddof=1) == 0 else f"{k.mean():.1f}{{\\scriptsize$\\pm${k.std(ddof=1):.1f}}}"
out, cur, n = [], None, 0
for line in open(TEX).read().split('\n'):
    mm = re.match(r'\\multirow\{4\}\{\*\}\{([^}]*)\}', line.strip())
    if mm and mm.group(1) in NAME:
        cur = mm.group(1); line = line.replace(r'\multirow{4}{*}', r'\multirow{5}{*}', 1)
    out.append(line)
    if cur in NAME and '& $DBI$ &' in line:
        out.append(r" & $k$ & " + ' & '.join(kcell(NAME[cur], m) for m in METHODS) + r' \\'); n += 1
open(TEX, 'w').write('\n'.join(out)); print("k rows:", n)
