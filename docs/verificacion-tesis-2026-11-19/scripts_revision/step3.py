import sys
T = sys.argv[1]
def rep(path, pairs):
    p = f"{T}/{path}"; s = open(p).read()
    for old, new in pairs:
        n = s.count(old); assert n == 1, (path, n, old[:90])
        s = s.replace(old, new)
    open(p, 'w').write(s)

conv = r"""\subsection{Convergencia según el \textit{prior}}
\label{subsec:analisis-convergencia}

La tercera pregunta se responde con las trayectorias de entrenamiento, que registran $Q'$ cada dos épocas. Para cada grafo se fija un nivel común de $Q'$, igual al 95\,\% del menor de los $Q'$ máximos medios de ambos \textit{priors}, y se mide la primera época en que cada corrida lo alcanza (Tabla~\ref{tab:convergencia-prior}). Actor se excluye porque el \textit{prior} de Leiden colapsa a $k=1$ y $Q'$ es nulo durante todo el entrenamiento.

\begin{table}[H]
\centering
\renewcommand{\arraystretch}{1.25}
\mycaption[Convergencia de $Q'$ según el \textit{prior}]{Épocas necesarias para alcanzar un nivel común de $Q'$ (95\,\% del menor de los $Q'$ máximos medios de ambos \textit{priors}): media$\pm$desviación estándar sobre cinco semillas. La evaluación se realiza cada dos épocas.}
\label{tab:convergencia-prior}
\begin{tabular}{@{}lccc@{}}
\toprule
\textbf{Red} & $Q'$ objetivo & GCN-Louvain & GCN-Leiden \\
\midrule
Cora & 0.724 & 64.8{\scriptsize$\pm$1.1} & 63.2{\scriptsize$\pm$1.8} \\
CiteSeer & 0.740 & 42.4{\scriptsize$\pm$0.9} & 44.8{\scriptsize$\pm$1.1} \\
PubMed & 0.616 & 100.0{\scriptsize$\pm$0.0} & 104.0{\scriptsize$\pm$5.5} \\
Coauthor CS & 0.620 & 30.0{\scriptsize$\pm$0.0} & 30.0{\scriptsize$\pm$0.0} \\
Amazon Computers & 0.519 & 58.0{\scriptsize$\pm$2.7} & 58.0{\scriptsize$\pm$2.7} \\
Amazon Photo & 0.612 & 49.2{\scriptsize$\pm$1.1} & 49.2{\scriptsize$\pm$1.1} \\
WikiCS & 0.522 & 79.0{\scriptsize$\pm$2.2} & 94.0{\scriptsize$\pm$4.2} \\
\bottomrule
\end{tabular}
\end{table}

El \textit{prior} de Leiden no acelera la optimización. En los 35 pares de corridas con la misma semilla (siete grafos y cinco semillas), Leiden alcanza el nivel antes en 3 pares, después en 11 y empata en 21 (prueba de Wilcoxon pareada sobre los pares no empatados, $p = 0.009$). El retraso se concentra en WikiCS. Al 99\,\% del nivel no hay diferencia ($p = 0.66$), y una medida relativa, las épocas hasta cubrir el 95\,\% de la mejora propia de cada corrida, tampoco muestra aceleración ($p = 0.053$). El \textit{prior} tampoco cambia los niveles de la optimización: ni el $Q'$ inicial ni el máximo difieren entre Leiden y Louvain ($p = 0.99$ y $p = 0.92$). Hay dos salvedades. La evaluación cada dos épocas produce muchos empates, y cada \textit{prior} fija un $k$ distinto, por lo que $Q'$ no es exactamente el mismo objetivo en ambos brazos; por eso se reportan las dos medidas. Además, en PubMed, Coauthor CS y WikiCS el $Q'$ máximo llega en promedio después de la época 225, cerca del límite de 300 épocas del protocolo.

Las trayectorias muestran también que maximizar $Q'$ no equivale a recuperar las etiquetas. En 56 de 70 corridas el pico de $NMI$ precede al máximo de $Q'$, y la pérdida media de $NMI$ entre ambos puntos va de $0.003$ (Amazon Photo) a $0.054$ (CiteSeer). Esto explica por qué el valor pico del protocolo de Wang et al. es optimista frente al \textit{checkpoint} de pérdida mínima (Sección~\ref{subsec:lineas-base-protocolo}).

"""
rep("chapters/resultados/resultados.tex", [
(r"""\subsection{Heterofilia en Actor}""", conv + r"""\subsection{Heterofilia en Actor}"""),
])
p = f"{T}/chapters/conclusiones/conclusiones.tex"; s = open(p).read()
a = s.index(r"\paragraph{3. Convergencia según el \textit{prior}.}")
b = s.index(r"\paragraph{4.", a)
print("OLD P3:\n" + s[a:b])
s = s[:a] + r"""\paragraph{3. Convergencia según el \textit{prior}.}
No. El \textit{prior} de Leiden no acelera la optimización de $Q'$: para alcanzar un mismo nivel de $Q'$ requiere las mismas épocas que Louvain o, en grafos como WikiCS, más (Sección~\ref{subsec:analisis-convergencia}). Tampoco cambia el $Q'$ inicial ni el máximo.

""" + s[b:]
open(p, 'w').write(s)
rep("chapters/conclusiones/conclusiones.tex", [
(r"""    \item Falta un análisis más sistemático para evaluar la convergencia de la optimización de $Q'$.""",
 r"""    \item En PubMed, Coauthor CS y WikiCS el máximo de $Q'$ llega cerca del límite de 300 épocas del protocolo de Wang et al., por lo que esas corridas podrían no haber convergido por completo."""),
])
p = f"{T}/chapters/conclusiones/conclusiones.tex"; s = open(p).read()
import re
m = re.search(r"    \\item \\textbf\{Convergencia\.\}[^\n]*\n", s); assert m
print("REMOVED FW:", m.group(0)); s = s.replace(m.group(0), ""); open(p,'w').write(s)
print("ok")
