import sys
from pypdf import PdfReader
r=PdfReader(sys.argv[1])
print("pages",len(r.pages))
for i,p in enumerate(r.pages,1):
    t=p.extract_text()
    open(sys.argv[2]+f"_p{i}.txt","w").write(t)
    print(i, "??" in t, t.count("?"))
