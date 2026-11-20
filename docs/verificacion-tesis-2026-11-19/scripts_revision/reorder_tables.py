"""Thesis tables 5.1-5.3: rows k -> Q -> NMI -> ARI, group headers, DBI to appendix."""
import re, sys
T = sys.argv[1]
R = f"{T}/chapters/resultados/resultados.tex"; A = f"{T}/chapters/appendices/app0A.tex"
s = open(R).read()
HEAD = r"\textbf{Red} & \textbf{Métrica} & Louvain & Leiden & DeepWalk & DGI & DMoN & GCN-Louvain & GCN-Leiden \\"
GROUP = (r"& & \multicolumn{2}{c}{Heurísticas} & \multicolumn{3}{c}{Profundos (reciben $k$)} & \multicolumn{2}{c}{GCN de una capa} \\"
         "\n" + r"\cmidrule(lr){3-4}\cmidrule(lr){5-7}\cmidrule(l){8-9}" + "\n")
assert s.count(HEAD) == 3
s = s.replace(HEAD, GROUP + HEAD)
lines = s.split("\n"); out = []; dbi = []; i = 0
while i < len(lines):
    m = re.match(r"\\multirow\{5\}\{\*\}\{([^}]*)\} & \$NMI\$ & (.*)$", lines[i])
    if not m:
        out.append(lines[i]); i += 1; continue
    name = m.group(1); rows = {"$NMI$": m.group(2)}
    for l in lines[i + 1:i + 5]:
        key = re.match(r" & (\$[A-Za-z]+\$) & (.*)$", l); rows[key.group(1)] = key.group(2)
    assert set(rows) == {"$NMI$", "$ARI$", "$Q$", "$DBI$", "$k$"}, (name, rows.keys())
    out.append(r"\multirow{4}{*}{" + name + "} & $k$ & " + rows["$k$"])
    out.append(r"\addlinespace[2pt]")
    for key in ["$Q$", "$NMI$", "$ARI$"]:
        out.append(f" & {key} & " + rows[key])
    dbi.append((name, rows["$DBI$"]))
    i += 5
s = "\n".join(out)
old = r"El $DBI$ se calcula en el espacio de representaciones de cada método, por lo que solo es comparable dentro de un mismo método y no se marca en negritas."
assert s.count(old) == 1
s = s.replace(old, r"El $DBI$, que solo es comparable dentro de un mismo método, se reporta en la Tabla~\ref{tab:dbi} (Apéndice~\ref{app:dbi}).")
old = " ---: métrica no aplicable o corrida no completada."
assert s.count(old) == 1
s = s.replace(old, " ---: corrida no completada.")
open(R, "w").write(s)
# appendix DBI table: drop the two classical columns ("---")
rows = []
for name, cells in dbi:
    c = [x.strip() for x in cells.rstrip(" \\").split(" & ")]
    assert c[0] == "---" and c[1] == "---", (name, c[:2])
    rows.append(name + " & " + " & ".join(c[2:]) + r" \\")
a = open(A).read()
sec = r"""
% -----------------------------------------------------------------------
\section{Índice Davies-Bouldin por método}
\label{app:dbi}
% -----------------------------------------------------------------------

La Tabla~\ref{tab:dbi} reporta el índice Davies-Bouldin de los métodos que producen representaciones latentes; Louvain y Leiden clásicos no las producen. Cada método calcula el $DBI$ en su propio espacio de representaciones, por lo que el índice solo es comparable dentro de un mismo método y no se marca un mejor valor.

\begin{table}[H]
\centering
\renewcommand{\arraystretch}{1.25}
\mycaption[Índice Davies-Bouldin por método]{Índice Davies-Bouldin ($DBI$, menor es más compacto) en el espacio de representaciones de cada método: media$\pm$desviación estándar sobre cinco semillas, con el mismo criterio de reporte que la Tabla~\ref{tab:resultados-citas-coautoria}. No es comparable entre métodos. ---: no definido ($k=1$) o corrida no completada.}
\label{tab:dbi}
\resizebox{\textwidth}{!}{%
\begin{tabular}{@{}lccccc@{}}
\toprule
\textbf{Red} & DeepWalk & DGI & DMoN & GCN-Louvain & GCN-Leiden \\
\midrule
""" + "\n".join(rows) + r"""
\bottomrule
\end{tabular}}%
\end{table}
"""
a = a.rstrip() + "\n" + sec
open(A, "w").write(a)
print("datasets:", [n for n, _ in dbi])
