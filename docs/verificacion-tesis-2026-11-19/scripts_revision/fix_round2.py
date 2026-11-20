import sys
T, G = sys.argv[1], sys.argv[2]
def rep(path, pairs):
    s = open(path).read()
    for old, new in pairs:
        n = s.count(old); assert n == 1, (path, n, old[:110])
        s = s.replace(old, new)
    open(path, 'w').write(s)
R = f"{T}/chapters/resultados/resultados.tex"; C = f"{T}/chapters/conclusiones/conclusiones.tex"
P = f"{T}/chapters/propuesta_solucion/propuesta_solucion.tex"
rep(R, [
# 1
(r"""alrededor de $0.007$ en los \textsc{sbm} cuyos bloques recupera la modularidad""",
 r"""como máximo $0.0071$ en los \textsc{sbm} cuyos bloques recupera la modularidad"""),
# 3
(r"""Frente al mejor modelo profundo de cada grafo, y considerando empate""",
 r"""Frente al mejor modelo profundo de cada grafo, en $NMI$ y $ARI$ y considerando empate"""),
(r"""Una \textsc{gcn} de una sola capa resulta así comparable a los modelos profundos en parte de los grafos, sin recibir $k$ como entrada, pero no los supera en ninguno.""",
 r"""Una \textsc{gcn} de una sola capa resulta así comparable a los modelos profundos en parte de los grafos, sin recibir $k$ como entrada, pero en ningún grafo los supera en $NMI$ ni en $ARI$. En modularidad $Q$, en cambio, GCN-Leiden supera al mejor modelo profundo en Cora, CiteSeer y PubMed."""),
# 4
(r"""$\beta = 0.5$ da el mejor $NMI$ también para Leiden (en Cora, empatado con $\beta = 0.25$), aunque es el extremo superior de la malla,""",
 r"""$\beta = 0.5$ da la mayor media de $NMI$ también para Leiden (en Cora, empatado con $\beta = 0.25$), aunque a menos de una desviación estándar del siguiente valor de la malla y en su extremo superior,"""),
(r"""En Cora y CiteSeer no hace falta recalibrar: $\beta = 0.5$ se transfiere de Louvain a Leiden.""",
 r"""En Cora y CiteSeer no hace falta recalibrar: ningún otro valor de la malla supera con claridad a $\beta = 0.5$ con Leiden (en Cora, $\beta = 0$ obtiene un $ARI$ igual o algo mayor, dentro de una desviación estándar), por lo que el valor se transfiere de Louvain a Leiden."""),
# 5
(r"""Si se considera empate toda diferencia en $NMI$ menor que la mayor de las dos desviaciones estándar, Leiden gana""",
 r"""Si se considera empate toda diferencia en $NMI$ menor que la mayor de las dos desviaciones estándar, con diferencias calculadas sobre los valores de la Tabla~\ref{tab:prior-pico}, Leiden gana"""),
(r"""y por un margen mínimo en Amazon Photo ($+0.005$);""", r"""y por un margen mínimo en Amazon Photo ($+0.004$);"""),
# 6
(r"""aunque a menos de una desviación estándar de Leiden clásico en $NMI$ y de GCN-Leiden en $ARI$. En Amazon Photo, las heurísticas clásicas superan a todos los métodos entrenables; en WikiCS, solo DeepWalk las iguala.""",
 r"""aunque en $NMI$ queda a menos de una desviación estándar de Louvain y Leiden clásicos y de GCN-Leiden, y en $ARI$, de GCN-Leiden. En Amazon Photo, las heurísticas clásicas superan en media a todos los métodos entrenables (en $NMI$, DeepWalk queda a menos de una desviación estándar); en WikiCS, DeepWalk las iguala en $NMI$ e iguala a Louvain en $ARI$."""),
# 7
(r"""con el mismo criterio de reporte que la Tabla~\ref{tab:resultados-citas-coautoria}. Negritas: mejor valor por fila.}""",
 r"""con el mismo criterio de reporte que la Tabla~\ref{tab:resultados-citas-coautoria}. Negritas: como en la Tabla~\ref{tab:resultados-citas-coautoria}.}"""),
# 9
(r"""La evaluación discreta produce muchos empates, sobre todo en los grafos evaluados cada 5 o 10 épocas, y en Cora y PubMed""",
 r"""La evaluación discreta produce muchos empates, y en Cora y PubMed"""),
# 10
(r"""GCN-Leiden usa \textsc{cpm} con $\gamma = (p_{in}+p_{out})/2$ y $\beta = 0.5$, tomado del generador,""",
 r"""GCN-Leiden usa \textsc{cpm} con $\beta = 0.5$ y una resolución $\gamma = (p_{in}+p_{out})/2$ tomada del generador,"""),
])
rep(C, [
(r"""Aceptada parcialmente: comparable en CiteSeer y en los grafos de Amazon; inferior en Cora, PubMed y WikiCS, y en Coauthor CS en $NMI$. \\""",
 r"""Aceptada parcialmente: en $NMI$ y $ARI$, comparable en CiteSeer y en los grafos de Amazon, e inferior en Cora, PubMed, WikiCS y, en $NMI$, Coauthor CS. \\"""),
(r"""Con el \textit{checkpoint} de pérdida mínima y frente al mejor modelo profundo de cada grafo, la arquitectura propuesta empata""",
 r"""Con el \textit{checkpoint} de pérdida mínima y frente al mejor modelo profundo de cada grafo, en $NMI$ y $ARI$ la arquitectura propuesta empata"""),
(r"""(Sección~\ref{subsec:analisis-calidad}); en ningún grafo los supera.""",
 r"""(Sección~\ref{subsec:analisis-calidad}); en ningún grafo los supera en $NMI$ ni en $ARI$, aunque en modularidad $Q$ supera al mejor modelo profundo en Cora, CiteSeer y PubMed."""),
(r"""En Cora y CiteSeer, $\beta = 0.5$ es el mejor de los valores probados tanto con Louvain como con Leiden (en Cora, empatado con $\beta = 0.25$), por lo que no hace falta recalibrarlo al cambiar de \textit{prior}""",
 r"""En Cora y CiteSeer, ningún valor probado supera con claridad a $\beta = 0.5$, ni con Louvain ni con Leiden: obtiene la mayor media de $NMI$, aunque a menos de una desviación estándar del siguiente valor, por lo que no hace falta recalibrarlo al cambiar de \textit{prior}"""),
(r"""que el valor original sigue siendo el mejor de los probados con otro \textit{prior} (en Cora, empatado con $\beta = 0.25$),""",
 r"""que ningún valor probado supera con claridad al original con otro \textit{prior},"""),
])
rep(P, [
(r"""(5 en Amazon Computers y WikiCS; 10 en PubMed y Coauthor CS)""",
 r"""(5 en Amazon Computers, WikiCS, \textsc{sbm}-1k y \textsc{sbm}-5k; 10 en PubMed, Coauthor CS y \textsc{sbm}-10k)"""),
])
rep(f"{T}/frontmatter/resumen.tex", [
(r"""aunque no los supera en ninguno, sin recibir""", r"""aunque en ninguno los supera en \textsc{nmi} ni en \textsc{ari}, sin recibir"""),
])
rep(f"{T}/frontmatter/abstract.tex", [
(r"""although it outperforms them on none, without receiving""", r"""although on no graph does it outperform them in \textsc{nmi} or \textsc{ari}, without receiving"""),
])
rep(f"{G}/gcn_leiden/prior.py", [
("""~0.007 on modularity SBM priors""", """<= 0.0071 on modularity SBM priors"""),
])
print("ok")
