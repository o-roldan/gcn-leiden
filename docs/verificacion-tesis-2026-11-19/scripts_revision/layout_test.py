import sys, re
root, stretch = sys.argv[1], sys.argv[2]
p=f"{root}/chapters/resultados/resultados.tex"; s=open(p).read()
for lab in ["tab:resultados-citas-coautoria","tab:resultados-compra-web","tab:resultados-sbm"]:
    j=s.find(r"\label{"+lab+"}"); i=s.rfind(r"\begin{table}[H]",0,j); assert i>=0
    s=s[:i]+r"\begin{table}[tbp]"+s[i+len(r"\begin{table}[H]"):]
    k=s.find(r"\renewcommand{\arraystretch}{1.25}",i); assert 0<k<j+400
    if stretch!="keep": s=s[:k]+r"\renewcommand{\arraystretch}{"+stretch+"}"+s[k+len(r"\renewcommand{\arraystretch}{1.25}"):]
open(p,"w").write(s)
