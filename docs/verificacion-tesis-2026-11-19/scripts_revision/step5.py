import sys
T = sys.argv[1]
def rep(path, pairs):
    p = f"{T}/{path}"; s = open(p).read()
    for old, new in pairs:
        n = s.count(old); assert n == 1, (path, n, old[:100])
        s = s.replace(old, new)
    open(p, 'w').write(s)

rep("chapters/chapter01/chap01.tex", [
(r"""    \item ¿En qué medida el algoritmo de Leiden, frente a Louvain,
    mejora la calidad de los centroides iniciales ($\mathbf{u}_j$) utilizados
    como \textit{prior} estructural?""",
 r"""    \item ¿En qué medida sustituir Louvain por Leiden como
    \textit{prior} estructural mejora la calidad de la partición final
    (\textsc{nmi}, \textsc{ari})?"""),
(r"""    \item El \textit{prior} de Leiden produce centroides iniciales de
    mayor calidad que el de Louvain.
    \item El filtro dinámico ($T$) mejora la cohesión de las
    particiones utilizadas como ancla de los vectores latentes.""",
 r"""    \item Usar Leiden en lugar de Louvain como \textit{prior} mejora
    el \textsc{nmi} y el \textsc{ari} de la partición final.
    \item El filtro dinámico ($T$) mejora el \textsc{nmi} de la
    partición final respecto a no filtrar las comunidades del
    \textit{prior}."""),
])

rep("chapters/propuesta_solucion/propuesta_solucion.tex", [
(r"""que produce comunidades mal conectadas o desconectadas (Definición~\ref{def:comunidades-desconectadas}) hasta en el 16\% de los casos en grafos reales \cite{Traag2019}. Esto daña el diseño. Cada centroide $\mathbf{u}_j$ es el promedio de los miembros de $C_j$. Si la comunidad agrupa fragmentos desconexos, el promedio cae en una zona que no representa a ninguno y el error se propaga a $\mathbf{P}$.""",
 r"""que puede producir comunidades mal conectadas e incluso desconectadas (Definición~\ref{def:comunidades-desconectadas}). En los experimentos de Traag et al. sobre grafos reales, hasta el 25\% de las comunidades de Louvain resultaron mal conectadas y hasta el 16\% desconectadas \cite{Traag2019}. Esto puede afectar al diseño. Cada centroide $\mathbf{u}_j$ es el promedio de los miembros de $C_j$. Si la comunidad agrupa fragmentos desconexos, el promedio puede caer en una zona que no representa a ninguno, y el error se propagaría a $\mathbf{P}$."""),
(r"""Su refinamiento garantiza la conectividad interna de cada comunidad, mejora la calidad de la partición y reduce el tiempo en grafos reales grandes. Así, cada centroide se promedia sobre un subgrafo conexo y el desplazamiento anterior desaparece.""",
 r"""Su refinamiento garantiza que cada comunidad sea internamente conexa y, en los experimentos de sus autores, mejora la calidad de la partición y reduce el tiempo en grafos reales grandes \cite{Traag2019}. Así, cada centroide se promedia sobre un subgrafo conexo. La garantía aplica a las comunidades ancla del \textit{prior}, no a la partición final que produce la \textsc{gcn}, y esta tesis no mide su efecto directo sobre los centroides, sino sobre la calidad de la partición final (Capítulo~\ref{chap:resultados})."""),
])

table = r"""
La Tabla~\ref{tab:veredictos} resume la relación entre preguntas, hipótesis y objetivos, junto con el veredicto de cada hipótesis.

\begin{table}[H]
\centering
\renewcommand{\arraystretch}{1.3}
\mycaption[Veredicto de las hipótesis]{Relación entre preguntas de investigación, hipótesis, objetivos y veredicto de cada hipótesis.}
\label{tab:veredictos}
\begin{tabular}{@{}cccc p{7.2cm}@{}}
\toprule
\textbf{Pregunta} & \textbf{Hipótesis} & \textbf{Objetivo} & \textbf{Sección} & \textbf{Veredicto} \\
\midrule
1 & H1 & 4 & \ref{subsec:analisis-ablacion-prior} & Rechazada: la ventaja de Leiden depende del grafo. \\
2 & H2 & 2 & \ref{sec:estudio-recalibracion} & Aceptada con tamaños sesgados (Cora, CiteSeer); rechazada con tamaños uniformes (\textsc{sbm} con modularidad). \\
3 & H3 & 4 & \ref{subsec:analisis-convergencia} & Rechazada: Leiden no acelera la optimización de $Q'$. \\
4 & Central & 1, 3 & \ref{subsec:analisis-calidad} & Aceptada parcialmente: calidad comparable, pero no superior, a la de los modelos profundos. \\
\bottomrule
\end{tabular}
\end{table}
"""
rep("chapters/conclusiones/conclusiones.tex", [
(r"""\label{sec:respuestas-preguntas}
% -----------------------------------------------------------------------
""", r"""\label{sec:respuestas-preguntas}
% -----------------------------------------------------------------------
""" + table),
(r"""y pierde en CiteSeer, WikiCS y Actor (Sección~\ref{subsec:analisis-ablacion-prior}). """,
 r"""y pierde en CiteSeer, WikiCS y Actor (Sección~\ref{subsec:analisis-ablacion-prior}). Por tanto, la primera hipótesis específica (H1) se rechaza. """),
(r"""El \textit{prior} \textsc{cpm} recupera los bloques en los tres \textsc{sbm}, aunque con una resolución tomada del generador.""",
 r"""El \textit{prior} \textsc{cpm} recupera los bloques en los tres \textsc{sbm}, aunque con una resolución tomada del generador. La segunda hipótesis específica (H2) se acepta cuando la distribución de tamaños es sesgada: en Cora y CiteSeer, filtrar con $\beta = 0.5$ eleva el $NMI$ frente a no filtrar ($\beta = -0.5$) con ambos \textit{priors} (Tabla~\ref{tab:recal-beta}). Se rechaza con tamaños uniformes, donde el filtro reduce el $NMI$ del \textit{prior} de modularidad (Tabla~\ref{tab:recal-sbm})."""),
(r"""Tampoco cambia el $Q'$ inicial ni el máximo.""",
 r"""Tampoco cambia el $Q'$ inicial ni el máximo. La tercera hipótesis específica (H3) se rechaza."""),
(r"""Es comparable, pero no superior. Con el""",
 r"""Es comparable, pero no superior, por lo que la hipótesis central se acepta parcialmente. Con el"""),
])
print("ok")
