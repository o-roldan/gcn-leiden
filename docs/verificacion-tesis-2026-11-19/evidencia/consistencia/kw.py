import re,sys
pat=re.compile(sys.argv[1],re.I)
for f in sys.argv[2:]:
    for i,l in enumerate(open(f,encoding='utf-8'),1):
        for m in pat.finditer(l):
            s=max(0,m.start()-70); e=min(len(l),m.end()+50)
            print(f"{f}:{i}: ...{l[s:e].strip()}...")
