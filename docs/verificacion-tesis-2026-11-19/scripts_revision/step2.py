import sys, re
T = sys.argv[1]
def rep(path, pairs):
    p = f"{T}/{path}"; s = open(p).read()
    for old, new in pairs:
        n = s.count(old)
        assert n == 1, (path, n, old[:90])
        s = s.replace(old, new)
    open(p, 'w').write(s)

# ---------- Resumen ----------
rep("frontmatter/resumen.tex", [
(r"""Los modelos neuronales profundos ofrecen gran capacidad expresiva, pero a costa de un consumo de memoria prohibitivo. Este costo se agrava por el encarecimiento del \textit{hardware}, impulsado por la demanda computacional para \textsc{ia}. Por otra parte,""",
 r"""Los modelos neuronales profundos integran la topología y las características de los nodos, pero la mayoría requiere fijar de antemano el número de comunidades $k$. Por otra parte,"""),
(r"""Los datos son nueve grafos reales de cuatro dominios (hasta 34\,493 nodos) y grafos sintéticos \textit{Stochastic Block Model} (hasta 10\,000 nodos). El desempeño se contrasta frente a Louvain, Leiden, DeepWalk, \textsc{dgi}, DMoN y la arquitectura base GCN-Louvain, con cinco semillas por configuración. Se cuantifica el consumo de \textsc{ram} y \textsc{vram} para comprobar la hipótesis central. Una arquitectura de una sola capa, guiada por un \textit{prior} modular de alta calidad, obtiene particiones de calidad comparable a las de los modelos profundos con solo una fracción del costo espacial.""",
 r"""Los datos son nueve grafos reales de cuatro dominios y grafos sintéticos \textit{Stochastic Block Model} (hasta 10\,000 nodos). La propuesta se evalúa en ocho de los grafos reales, ya que en Coauthor Physics (34\,493 nodos) la matriz de modularidad densa excede la memoria de la \textsc{gpu}. El desempeño se contrasta frente a Louvain, Leiden, DeepWalk, \textsc{dgi}, DMoN y la arquitectura base GCN-Louvain, con cinco semillas por configuración. Una arquitectura de una sola capa, guiada por un \textit{prior} modular, obtiene particiones de calidad competitiva con la de los modelos profundos, aunque no los supera, sin recibir $k$ como entrada y con mayor estabilidad entre semillas que \textsc{dgi}."""),
])
# ---------- Abstract ----------
rep("frontmatter/abstract.tex", [
(r"""Deep neural models offer great expressive power, but at the cost of prohibitive memory consumption. This cost is worsened by rising hardware prices, driven by the computational demand for AI. Classical""",
 r"""Deep neural models integrate topology and node features, but most of them require the number of communities $k$ to be fixed in advance. Classical"""),
(r"""The data are nine real-world graphs from four domains (up to 34{,}493 nodes) and synthetic Stochastic Block Model graphs (up to 10{,}000 nodes). Performance is compared against Louvain, Leiden, DeepWalk, \textsc{dgi}, DMoN, and the base GCN-Louvain architecture, with five seeds per configuration. \textsc{ram} and \textsc{vram} consumption is quantified to test the central hypothesis. A single-layer architecture, guided by a high-quality modular prior, matches deep models in topological quality at a fraction of their memory footprint.""",
 r"""The data are nine real-world graphs from four domains and synthetic Stochastic Block Model graphs (up to 10{,}000 nodes). The proposal is evaluated on eight of the real-world graphs, since on Coauthor Physics (34{,}493 nodes) the dense modularity matrix exceeds the \textsc{gpu} memory. Performance is compared against Louvain, Leiden, DeepWalk, \textsc{dgi}, DMoN, and the base GCN-Louvain architecture, with five seeds per configuration. A single-layer architecture, guided by a modular prior, yields partitions of competitive quality with respect to deep models, although it does not outperform them, without receiving $k$ as input and with greater stability across seeds than \textsc{dgi}."""),
])
# ---------- Introducción ----------
rep("chapters/chapter01/chap01.tex", [
(r"""Los modelos profundos generan una proyección del grafo de entrada hacia un espacio continuo, pero esto puede derivar en costos prohibitivos de \textsc{ram} y tiempo de ejecución \cite{tsitsulin2023}.""",
 r"""Los modelos profundos generan una proyección del grafo de entrada hacia un espacio continuo, pero la mayoría requiere fijar de antemano el número de comunidades $k$ \cite{Wang2025}."""),
(r"""    \textsc{ari}, $Q$) de los modelos profundos?
    \item ¿Se sostiene la eficiencia en tiempo y memoria (\textsc{ram},
    \textsc{vram}) del método propuesto al escalar a grafos reales de
    hasta 34\,493 nodos y grafos sintéticos de hasta 10\,000?
\end{enumerate}""",
 r"""    \textsc{ari}, $Q$) de los modelos profundos?
\end{enumerate}"""),
(r"""la de los modelos profundos de detección de comunidades, con un consumo
de memoria (\textsc{ram}, \textsc{vram}) significativamente menor, en
grafos de decenas de miles de nodos.""",
 r"""la de los modelos profundos de detección de comunidades, sin recibir el
número de comunidades como entrada."""),
(r"""redes neuronales en grafos cuando no hay etiquetas y mantener un
costo espacial eficiente.""",
 r"""redes neuronales en grafos cuando no hay etiquetas."""),
(r"""\paragraph{Objetivo 4.}
Medir el consumo de \textsc{ram}/\textsc{vram} del modelo y de los demás
\textit{baselines} sobre grafos sintéticos de hasta
10\,000 nodos y grafos reales de hasta 34\,493 nodos.

\paragraph{Objetivo 5.}""",
 r"""\paragraph{Objetivo 4.}"""),
(r"""En la literatura de referencia para este trabajo, no se identificó
una medición o comparación de la memoria (\textsc{ram}, \textsc{vram})
de las \textsc{gcn} simplificadas frente a heurísticas del estado del
arte y modelos profundos. En ese sentido, este proyecto aporta un marco
cuantitativo para encontrar las condiciones operativas bajo las cuales
una \textsc{gcn} de una sola capa, guiada por un \textit{prior} de
Leiden, hace viable la detección de comunidades con recursos de cómputo
limitados. 
Además, el trabajo aporta evidencia""",
 r"""La arquitectura de referencia de Wang et al. \cite{Wang2025} publica
una sola ejecución por configuración y usa Louvain como \textit{prior}.
Este proyecto la evalúa con varias semillas, lo que separa los efectos
reales del azar de inicialización, y aísla el efecto del \textit{prior}
al sustituir Louvain por Leiden sin cambiar el resto de la arquitectura.
Además, el trabajo aporta evidencia"""),
(r"""Finalmente, en lo práctico, este trabajo plantea la adopción de arquitecturas
livianas sobre grafos, lo cual resulta especialmente relevante en un
contexto de encarecimiento del \textit{hardware} de cómputo y de acceso desigual
a \textsc{gpu} de gran tamaño.""",
 r"""Finalmente, en lo práctico, una arquitectura con una sola matriz de
pesos que estima $k$ desde la topología resulta útil cuando no se
conoce el número de comunidades."""),
])
# ---------- Trabajo relacionado: tabla 3.1 ----------
rep("chapters/trabajos_relacionados/trabajos_relacionados.tex", [
(r"""GCN-Louvain + $Q'$ (Wang et al.) & Neuronal (GNN) & Modularidad suave $Q'$ & No & Sí & Alta & 2025 \\""",
 r"""GCN-Louvain + $Q'$ (Wang et al.) & Neuronal (GNN) & Modularidad suave $Q'$ & No & Sí & Media$^{*}$ & 2025 \\"""),
(r"""\textbf{GCN-Leiden + $Q'$ (esta tesis)} & \textbf{Neuronal (GNN)} & \textbf{Modularidad suave $Q'$} & \textbf{No} & \textbf{Sí} & \textbf{Alta} & \textbf{2026} \\
\hline
\end{tabular}%
}""",
 r"""\textbf{GCN-Leiden + $Q'$ (esta tesis)} & \textbf{Neuronal (GNN)} & \textbf{Modularidad suave $Q'$} & \textbf{No} & \textbf{Sí} & \textbf{Media$^{*}$} & \textbf{2026} \\
\hline
\end{tabular}%
}
\par\smallskip{\footnotesize $^{*}$La implementación materializa la matriz de modularidad $\mathbf{B}$ densa, por lo que su memoria crece como $O(n^2)$.}"""),
])
# ---------- Protocolo ----------
rep("chapters/propuesta_solucion/propuesta_solucion.tex", [
(r"""Cada corrida se ejecuta en un subproceso aislado, lo que permite medir su consumo pico de \textsc{ram} y \textsc{vram} sin contaminación entre métodos; las trayectorias""",
 r"""Cada corrida se ejecuta en un subproceso aislado; las trayectorias"""),
])
# ---------- Resultados ----------
p = f"{T}/chapters/resultados/resultados.tex"; s = open(p).read()
start = s.index(r"\subsection{Telemetría de memoria}")
end = s.index(r"% -----------------------------------------------------------------------" + "\n" + r"\section{Recalibración del filtro dinámico}")
s = s[:start] + s[end:]
open(p, 'w').write(s)
rep("chapters/resultados/resultados.tex", [
(r"""recuperan casi exactamente los bloques de \textsc{sbm}-1k y \textsc{sbm}-5k, igual que los modelos profundos (Tabla~\ref{tab:resultados-sbm}).""",
 r"""recuperan casi exactamente los bloques de \textsc{sbm}-1k y \textsc{sbm}-5k, igual que los modelos profundos (Tabla~\ref{tab:resultados-sbm}). En Coauthor Physics ($n = 34\,493$) las variantes \textsc{gcn} no completan, porque la implementación de $Q'$ materializa la matriz de modularidad $\mathbf{B} \in \mathbb{R}^{n \times n}$ densa en la \textsc{gpu} y excede los 24~\textsc{gb} de la L4."""),
(r"""Negritas: mejor valor por fila. Louvain y Leiden clásicos a resolución $\gamma=1.0$.}""",
 r"""Negritas: mejor valor por fila. Louvain y Leiden clásicos a resolución $\gamma=1.0$. ---: métrica no aplicable o corrida no completada.}"""),
])
# ---------- Conclusiones ----------
rep("chapters/conclusiones/conclusiones.tex", [
(r"""\paragraph{5. Eficiencia de memoria.}""", r"""%%P5DEL"""),
(r"""    \item \textbf{Infraestructura reproducible.} Código versionado, semillas controladas y memoria de cada proceso guardada en la nube.""",
 r"""    \item \textbf{Infraestructura reproducible.} Código versionado, semillas controladas y resultados de cada corrida guardados en la nube."""),
(r"""    \item La implementación de $Q'$ consume demasiada \textsc{vram}, lo que impidió evaluar Coauthor Physics.""",
 r"""    \item La implementación de $Q'$ materializa la matriz $\mathbf{B}$ densa, de tamaño $n \times n$, lo que impidió evaluar la propuesta en Coauthor Physics."""),
])
# remove P5 body: from marker to blank line before next % ---- section
p = f"{T}/chapters/conclusiones/conclusiones.tex"; s = open(p).read()
a = s.index("%%P5DEL"); b = s.index("% -----", a)
print("REMOVED P5 BLOCK:\n" + s[a:b])
s = s[:a] + s[b:]
open(p, 'w').write(s)
print("ok")
