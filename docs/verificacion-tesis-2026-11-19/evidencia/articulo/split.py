import sys
from pypdf import PdfReader, PdfWriter
r=PdfReader(sys.argv[1])
for i in (int(x) for x in sys.argv[3:]):
    w=PdfWriter(); w.add_page(r.pages[i-1]); w.write(f"{sys.argv[2]}_p{i}.pdf")
