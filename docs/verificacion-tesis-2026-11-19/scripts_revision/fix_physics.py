import sys
T = sys.argv[1]
def rep(path, pairs):
    p = f"{T}/{path}"; s = open(p).read()
    for old, new in pairs:
        n = s.count(old); assert n == 1, (path, n, old[:100])
        s = s.replace(old, new)
    open(p, 'w').write(s)
rep("frontmatter/resumen.tex", [
(r"""La propuesta se evalúa en ocho de los grafos reales, ya que en Coauthor Physics (34\,493 nodos) la matriz de modularidad densa excede la memoria de la \textsc{gpu}.""",
 r"""La propuesta se evalúa en ocho de los grafos reales: en Coauthor Physics (34\,493 nodos) sus corridas no completaron, y la implementación mantiene en la \textsc{gpu} varias matrices densas de $n \times n$."""),
])
rep("frontmatter/abstract.tex", [
(r"""The proposal is evaluated on eight of the real-world graphs, since on Coauthor Physics (34{,}493 nodes) the dense modularity matrix exceeds the \textsc{gpu} memory.""",
 r"""The proposal is evaluated on eight of the real-world graphs: on Coauthor Physics (34{,}493 nodes) its runs did not complete, and the implementation keeps several dense $n \times n$ matrices on the \textsc{gpu}."""),
])
rep("chapters/resultados/resultados.tex", [
(r"""En Coauthor Physics ($n = 34\,493$) las variantes \textsc{gcn} no completan, porque la implementación de $Q'$ materializa la matriz de modularidad $\mathbf{B} \in \mathbb{R}^{n \times n}$ densa en la \textsc{gpu} y excede los 24~\textsc{gb} de la L4.""",
 r"""En Coauthor Physics ($n = 34\,493$) las corridas de las variantes \textsc{gcn} no completaron, y no se conservan registros de la causa. La implementación mantiene en la \textsc{gpu} varias matrices densas de $n \times n$ (la adyacencia, la matriz de modularidad $\mathbf{B}$ y la matriz diagonal de la normalización $L_2$), de unos 4.4~\textsc{gib} cada una en este grafo."""),
])
rep("chapters/conclusiones/conclusiones.tex", [
(r"""    \item La implementación de $Q'$ materializa la matriz $\mathbf{B}$ densa, de tamaño $n \times n$, lo que impidió evaluar la propuesta en Coauthor Physics.""",
 r"""    \item Las corridas de la propuesta en Coauthor Physics no completaron y no se conservan registros de la causa. La implementación mantiene en la \textsc{gpu} varias matrices densas de $n \times n$, cuyo costo de memoria crece como $O(n^2)$."""),
])
print("ok")
