import re, difflib, sys, glob
PAPER="/Users/omar/Developer/me/gnn-paper/main.tex"
TH="/Users/omar/Developer/me/gnn-thesis"
files=[TH+"/frontmatter/resumen.tex"]+sorted(glob.glob(TH+"/chapters/**/*.tex",recursive=True))
def paras(path):
    lines=open(path,encoding="utf8").read().split("\n")
    out=[];cur=[];start=None
    for i,l in enumerate(lines,1):
        if l.strip()=="" :
            if cur: out.append((start," ".join(cur)));cur=[]
            continue
        if l.strip().startswith("%"): continue
        if not cur: start=i
        cur.append(l.strip())
    if cur: out.append((start," ".join(cur)))
    return out
def sents(t):
    return [s for s in re.split(r'(?<=[\.\?\!:;])\s+', t) if s]
th=[]
for f in files:
    for s,p in paras(f):
        th.append((f.replace(TH+"/",""),s,p))
pp=paras(PAPER)
# only content paragraphs after begin{document}
for s,p in pp:
    if s<148: continue
    if len(p)<60: continue
    best=None;bs=0
    for f,ts,tp in th:
        r=difflib.SequenceMatcher(None,p,tp,autojunk=False)
        q=r.quick_ratio()
        if q<bs: continue
        rr=r.ratio()
        if rr>bs: bs=rr;best=(f,ts,tp)
    print("="*100)
    print(f"PAPER L{s}  best={best[0]}:{best[1]}  ratio={bs:.3f}")
    if bs<0.999:
        a=p.split();b=best[2].split()
        sm=difflib.SequenceMatcher(None,b,a,autojunk=False)
        for op,i1,i2,j1,j2 in sm.get_opcodes():
            if op!="equal":
                print(f"  [{op}] THESIS: {' '.join(b[i1:i2])[:700]}")
                print(f"         PAPER : {' '.join(a[j1:j2])[:700]}")
