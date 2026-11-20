import re,sys
def parse(path):
    txt=open(path,encoding='latin-1').read().split('\n')
    out=[]
    # track current file via simple heuristic: last "(./chapters/..." or "(/...chapters" seen
    cur='?'
    for i,l in enumerate(txt):
        for m in re.finditer(r'\((?:\./|[^()\s]*/)?((?:chapters|frontmatter)/[^\s()]+\.tex)',l):
            cur=m.group(1)
        if re.match(r'(Overfull|Underfull) \\[hv]box',l):
            ctx=' '.join(txt[i+1:i+3]).strip()[:160]
            kind=re.sub(r' in .*| has occurred.*','',l)
            lines=re.search(r'lines? (\d+)(?:--(\d+))?',l)
            out.append((cur,kind,lines.group(0) if lines else '',ctx,l.strip()))
    return out
a=parse(sys.argv[1]); b=parse(sys.argv[2])
print(len(a),len(b))
key=lambda t:(t[0],t[1],t[3])
bk=[key(t) for t in b]
from collections import Counter
cb=Counter(bk)
for t in a:
    k=key(t)
    if cb[k]>0: cb[k]-=1; continue
    print('NEW:',t[0],'|',t[4],'|',t[3])
ca=Counter(key(t) for t in a)
for t in b:
    k=key(t)
    if ca[k]>0: ca[k]-=1; continue
    print('GONE:',t[0],'|',t[4],'|',t[3])
