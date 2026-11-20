import sys
T = sys.argv[1]
def rep(path, pairs):
    p = f"{T}/{path}"; s = open(p).read()
    for old, new in pairs:
        n = s.count(old)
        assert n == 1, (path, n, old[:80])
        s = s.replace(old, new)
    open(p, 'w').write(s)

# ---------------- Protocolo (Cap. 4) ----------------
rep("chapters/propuesta_solucion/propuesta_solucion.tex", [
(r"""vuelve conservadora cualquier ventaja de la propuesta, cuyo $k$ se estima sin supervisión desde el \textit{prior}.""",
 r"""vuelve conservadora cualquier ventaja de la propuesta, cuyo $k$ se estima sin supervisión desde el \textit{prior}. Esto difiere de Wang et al., que entregan a sus \textit{baselines} el $k$ que detecta su propio método \cite{Wang2025}."""),
(r"""En los métodos entrenables, cada métrica se toma en su valor \emph{pico} durante el entrenamiento, como en el protocolo original.""",
 r"""El código de Wang et al. evalúa cada corrida de dos maneras. Por un lado, cada dos épocas registra el máximo de cada métrica (el mínimo en el caso de $DBI$); este valor \emph{pico} es el que publica el artículo \cite{Wang2025}. Por otro, al terminar restaura el \textit{checkpoint} de pérdida mínima, es decir, el de máxima $Q'$, y lo evalúa. El pico elige la época consultando las etiquetas, y cada métrica puede provenir de una época distinta, por lo que es una cota optimista; el \textit{checkpoint} de pérdida mínima no usa etiquetas. Esta tesis conserva ambas vistas y emplea cada una donde la comparación es simétrica. Las comparaciones internas de la arquitectura (GCN-Leiden frente a GCN-Louvain y el estudio de recalibración) reportan el pico, como el protocolo original, porque ambos brazos se miden con la misma regla. Las comparaciones contra los demás métodos (Tablas~\ref{tab:resultados-citas-coautoria}--\ref{tab:resultados-sbm}) reportan el \textit{checkpoint} de pérdida mínima, ya que DeepWalk, \textsc{dgi} y DMoN se evalúan sobre su modelo entrenado, sin seleccionar épocas con las etiquetas."""),
])

# ---------------- Resultados (Cap. 5) ----------------
rep("chapters/resultados/resultados.tex", [
(r"""media$\pm$desviación estándar sobre cinco semillas (valor pico durante el entrenamiento para los métodos profundos). Negritas""",
 r"""media$\pm$desviación estándar sobre cinco semillas. Las columnas GCN corresponden al \textit{checkpoint} de pérdida mínima y los demás métodos entrenables a su modelo entrenado; ninguno selecciona épocas con las etiquetas (Sección~\ref{subsec:lineas-base-protocolo}). Negritas"""),
(r"""coocurrencia (Actor) e hipervínculos (WikiCS): media$\pm$desviación estándar sobre cinco semillas. Negritas: mejor valor por fila.}""",
 r"""coocurrencia (Actor) e hipervínculos (WikiCS): media$\pm$desviación estándar sobre cinco semillas, con el mismo criterio de reporte que la Tabla~\ref{tab:resultados-citas-coautoria}. Negritas: mejor valor por fila.}"""),
(r"""($p_{in}=0.05$, $p_{out}=0.005$): media$\pm$desviación estándar sobre cinco semillas. Las columnas""",
 r"""($p_{in}=0.05$, $p_{out}=0.005$): media$\pm$desviación estándar sobre cinco semillas, con el mismo criterio de reporte que la Tabla~\ref{tab:resultados-citas-coautoria}. Las columnas"""),
# 5.1.1
(r"""En los grafos de citas, la propuesta GCN-Leiden alcanza el mejor $NMI$ y $ARI$ en Cora ($0.554 \pm 0.009$ y $0.492 \pm 0.020$) e iguala el $NMI$ de \textsc{dgi} ($0.553 \pm 0.016$) con una modularidad $Q$ muy superior ($0.771$ frente a $0.699$) y un $DBI$ un orden de magnitud menor ($0.45$ frente a $2.96$): el espacio latente que produce la \textsc{gcn} de una capa anclada al \textit{prior} es geométricamente más compacto que el del modelo contrastivo. En PubMed, GCN-Leiden supera a GCN-Louvain ($0.313 \pm 0.004$ frente a $0.291 \pm 0.014$) y a DMoN, aunque \textsc{dgi} retiene el mejor $NMI$. En los grafos de coautoría y de compra conjunta los siete métodos compiten en una franja estrecha; GCN-Leiden obtiene el mejor $ARI$ en Amazon Photo y Amazon Computers, y se mantiene a menos de una desviación estándar de GCN-Louvain en Coauthor CS. En los grafos sintéticos, con el filtro condicionado, ambas variantes \textsc{gcn} igualan la recuperación casi exacta de los mejores modelos profundos y obtienen el mejor $DBI$ (Tabla~\ref{tab:resultados-sbm}).""",
 r"""En los grafos de citas, \textsc{dgi} obtiene el mejor $NMI$ y $ARI$ en Cora, CiteSeer y PubMed. En Cora, GCN-Leiden queda en segundo lugar ($NMI = 0.530 \pm 0.008$ y $ARI = 0.442 \pm 0.015$, frente a $0.553 \pm 0.016$ y $0.488 \pm 0.037$ de \textsc{dgi}), con una modularidad $Q$ mayor ($0.770$ frente a $0.699$). En PubMed, las dos variantes \textsc{gcn} superan a DMoN, pero quedan por debajo de \textsc{dgi} ($0.275 \pm 0.021$ y $0.265 \pm 0.021$ frente a $0.339 \pm 0.009$). En Coauthor CS, \textsc{dgi} y DMoN superan a ambas variantes \textsc{gcn}. En los grafos de compra conjunta, GCN-Louvain obtiene el mejor $NMI$ y $ARI$ en Amazon Computers ($0.529 \pm 0.016$ y $0.439 \pm 0.013$); en Amazon Photo y WikiCS, las heurísticas clásicas superan a todos los métodos entrenables. En los grafos sintéticos, ambas variantes \textsc{gcn} recuperan casi exactamente los bloques de \textsc{sbm}-1k y \textsc{sbm}-5k, igual que los modelos profundos (Tabla~\ref{tab:resultados-sbm})."""),
(r"""Una \textsc{gcn} de una sola capa equipara así la calidad de partición de los modelos profundos contrastivos sin recibir $k$ como entrada, lo que responde la cuarta pregunta de investigación. El caso de \textsc{dgi} en Amazon Computers ilustra además la fragilidad contrastiva: su $NMI$ se desploma a $0.094 \pm 0.124$ (colapso en tres de cinco semillas), mientras que las arquitecturas con \textit{prior} estructural se mantienen estables, con desviaciones típicas de $\pm 0.01$.""",
 r"""Una \textsc{gcn} de una sola capa resulta así competitiva, pero no superior, frente a los modelos profundos, sin recibir $k$ como entrada: se acerca a \textsc{dgi} en Cora e iguala o supera a los modelos profundos en los dos grafos de Amazon, pero queda por debajo de \textsc{dgi} en CiteSeer, PubMed y Coauthor CS. Esto responde la cuarta pregunta de investigación. Su ventaja está en la estabilidad frente al método contrastivo: \textsc{dgi} colapsa en Amazon Computers en cuatro de cinco semillas ($NMI = 0.094 \pm 0.124$) y en Amazon Photo en las cinco. Las variantes \textsc{gcn} no colapsan en estos grafos, aunque en Amazon Computers una semilla de GCN-Leiden termina en un \textit{checkpoint} degradado ($NMI = 0.374$, frente a $\approx 0.535$ en las otras cuatro), lo que explica su desviación de $\pm 0.072$."""),
# 5.1.2: P1 uses peak view + compact table
(r"""La comparación directa entre GCN-Leiden y GCN-Louvain (idénticos en todo salvo el algoritmo del \textit{prior}) responde la primera pregunta de investigación con un resultado matizado.""",
 r"""La comparación directa entre GCN-Leiden y GCN-Louvain (idénticos en todo salvo el algoritmo del \textit{prior}) responde la primera pregunta de investigación. Como ambos brazos comparten la regla de reporte, esta sección usa el valor pico del protocolo de Wang et al. (Tabla~\ref{tab:prior-pico}).

\begin{table}[H]
\centering
\renewcommand{\arraystretch}{1.25}
\mycaption[Comparación controlada del \textit{prior} (valor pico)]{GCN-Louvain frente a GCN-Leiden con el valor pico del protocolo de Wang et al.: media$\pm$desviación estándar sobre cinco semillas.}
\label{tab:prior-pico}
\begin{tabular}{@{}lcccc@{}}
\toprule
 & \multicolumn{2}{c}{$NMI$} & \multicolumn{2}{c}{$ARI$} \\
\cmidrule(lr){2-3}\cmidrule(lr){4-5}
\textbf{Red} & GCN-Louvain & GCN-Leiden & GCN-Louvain & GCN-Leiden \\
\midrule
Cora & 0.541{\scriptsize$\pm$0.007} & 0.554{\scriptsize$\pm$0.009} & 0.480{\scriptsize$\pm$0.022} & 0.492{\scriptsize$\pm$0.020} \\
CiteSeer & 0.401{\scriptsize$\pm$0.008} & 0.388{\scriptsize$\pm$0.012} & 0.391{\scriptsize$\pm$0.014} & 0.375{\scriptsize$\pm$0.020} \\
PubMed & 0.291{\scriptsize$\pm$0.014} & 0.313{\scriptsize$\pm$0.004} & 0.250{\scriptsize$\pm$0.011} & 0.274{\scriptsize$\pm$0.005} \\
Coauthor CS & 0.625{\scriptsize$\pm$0.008} & 0.629{\scriptsize$\pm$0.008} & 0.497{\scriptsize$\pm$0.005} & 0.500{\scriptsize$\pm$0.004} \\
Amazon Computers & 0.543{\scriptsize$\pm$0.008} & 0.541{\scriptsize$\pm$0.003} & 0.494{\scriptsize$\pm$0.018} & 0.489{\scriptsize$\pm$0.008} \\
Amazon Photo & 0.649{\scriptsize$\pm$0.002} & 0.653{\scriptsize$\pm$0.003} & 0.489{\scriptsize$\pm$0.002} & 0.492{\scriptsize$\pm$0.001} \\
Actor & 0.007{\scriptsize$\pm$0.007} & 0.000{\scriptsize$\pm$0.000} & 0.009{\scriptsize$\pm$0.009} & 0.000{\scriptsize$\pm$0.000} \\
WikiCS & 0.419{\scriptsize$\pm$0.001} & 0.410{\scriptsize$\pm$0.003} & 0.373{\scriptsize$\pm$0.004} & 0.369{\scriptsize$\pm$0.002} \\
\bottomrule
\end{tabular}
\end{table}

"""),
# 5.2.2 references the peak value -> point to appendix (peak) table
(r"""$NMI = 1.000 \pm 0.000$ en \textsc{sbm}-5k y $0.991 \pm 0.002$ en \textsc{sbm}-1k, con el $k$ exacto (Tabla~\ref{tab:resultados-sbm}).""",
 r"""$NMI = 1.000 \pm 0.000$ en \textsc{sbm}-5k y $0.991 \pm 0.002$ en \textsc{sbm}-1k, con el $k$ exacto (Tabla~\ref{tab:recal-sbm})."""),
])

# ---------------- Conclusiones: P4 ----------------
rep("chapters/conclusiones/conclusiones.tex", [
(r"""Sí, ya que la arquitectura propuesta alcanza el mejor $NMI$ y $ARI$ en Cora y el mejor $ARI$ en ambos grafos de Amazon. Además de que al igual que la arquitectura base, estima $k$ sin supervisión a diferencia de los \textit{baselines} profundos. Adicionalmente, los métodos contrastivos tienen mayor fragilidad entre semillas. """,
 r"""Es comparable, pero no superior. Con el \textit{checkpoint} de pérdida mínima, la arquitectura propuesta se acerca a \textsc{dgi} en Cora e iguala o supera a los modelos profundos en los dos grafos de Amazon, pero queda por debajo de \textsc{dgi} en CiteSeer, PubMed y Coauthor CS, y de las heurísticas clásicas en Amazon Photo y WikiCS. Al igual que la arquitectura base, estima $k$ sin supervisión, a diferencia de los \textit{baselines} profundos, y es más estable entre semillas que \textsc{dgi}, que colapsa en los grafos de Amazon. """),
])
print("ok")
