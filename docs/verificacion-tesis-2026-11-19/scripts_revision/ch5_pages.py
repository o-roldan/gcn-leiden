import pypdf, sys
r=pypdf.PdfReader(sys.argv[1])
st=next(i for i,p in enumerate(r.pages) if 'RESULTADOS Y DISCUSIÓN' in (p.extract_text() or '') and 'C A P Í T U L O' in (p.extract_text() or ''))
print("total", len(r.pages))
for i in range(st, st+7):
    L=(r.pages[i].extract_text() or '').splitlines(); tabs=[l[6:9] for l in L if l.startswith('TABLA')]
    print(f"  pdf {i+1}: {len(L):3d} lines, tables {tabs}")
