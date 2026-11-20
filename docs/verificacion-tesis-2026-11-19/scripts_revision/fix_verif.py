import sys, re
T, G = sys.argv[1], sys.argv[2]
def rep(path, pairs):
    s = open(path).read()
    for old, new in pairs:
        n = s.count(old); assert n == 1, (path, n, old[:110])
        s = s.replace(old, new)
    open(path, 'w').write(s)
P = f"{T}/chapters/propuesta_solucion/propuesta_solucion.tex"
R = f"{T}/chapters/resultados/resultados.tex"
C = f"{T}/chapters/conclusiones/conclusiones.tex"
I = f"{T}/chapters/chapter01/chap01.tex"
TR = f"{T}/chapters/trabajos_relacionados/trabajos_relacionados.tex"

# ---------------- Cap. 4 ----------------
rep(P, [
(r"""hasta el 25\% de las comunidades de Louvain resultaron mal conectadas y hasta el 16\% desconectadas \cite{Traag2019}.""",
 r"""hasta el 25\% de las comunidades de Louvain resultaron mal conectadas y hasta el 16\% desconectadas; estos máximos aparecen al iterar el algoritmo, mientras que en la primera iteración las comunidades desconectadas suelen rondar el 1\% \cite{Traag2019}."""),
(r"""Wang et al. fijan el coeficiente en $0.5$ sin reportar un análisis de sensibilidad sobre él \cite{Wang2025}, y lo emplean con particiones de Louvain. Leiden produce una distribución de tamaños distinta, por lo que no hay garantía de que el mismo valor sea adecuado.""",
 r"""El análisis de sensibilidad de Wang et al., que varía el coeficiente entre $0.1$ y $1.0$ sobre particiones de Louvain, halla el mejor desempeño entre $0.4$ y $0.6$ y fija $0.5$ \cite{Wang2025}. Leiden puede producir una distribución de tamaños distinta, por lo que no hay garantía de que el mismo valor sea el adecuado."""),
(r"""y, solo para Leiden, \textsc{cpm} con $\gamma = 0.0275$. Este último valor es el punto medio""",
 r"""y, solo para Leiden, \textsc{cpm} con $\gamma = 0.0275$, en ambos casos con $\beta = 0.5$. La resolución $\gamma = 0.0275$ es el punto medio"""),
(r"""Por eso las tablas de resultados reportan el $k$ de cada método, y las comparaciones se apoyan sobre todo en el $ARI$.""",
 r"""Por eso las tablas de resultados reportan el $k$ de cada método junto con el $NMI$ y el $ARI$, y cuando dos configuraciones difieren mucho en $k$, como al activar o desactivar el filtro, la comparación se apoya en el $ARI$ (Sección~\ref{subsec:recal-redes-reales})."""),
(r"""Por otro, al terminar restaura el \textit{checkpoint} de pérdida mínima, es decir, el de máxima $Q'$, y lo evalúa.""",
 r"""Por otro, al terminar restaura el \textit{checkpoint} de pérdida mínima (el estado guardado tras el paso de optimización de la época de máxima $Q'$) y lo evalúa."""),
(r"""reportan el pico, como el protocolo original, porque ambos brazos se miden con la misma regla.""",
 r"""reportan el pico, como el protocolo original, porque ambos brazos se miden con la misma regla. A diferencia del original, que evalúa cada dos épocas, aquí la evaluación se hace cada 2, 5 o 10 épocas según el grafo (5 en Amazon Computers y WikiCS; 10 en PubMed y Coauthor CS), y el pico se toma sobre esa rejilla."""),
(r"""Cada corrida se ejecuta en un subproceso aislado; las trayectorias completas de entrenamiento se almacenan para el estudio de convergencia.""",
 r"""Cada corrida se ejecuta en un subproceso aislado. De las variantes \textsc{gcn} se almacenan las trayectorias de entrenamiento, muestreadas en cada evaluación, para el estudio de convergencia."""),
])

# ---------------- Cap. 1: H2 en ARI ----------------
s = open(I).read()
old_h2 = re.search(r"\\item El filtro dinámico \(\$T\$\) mejora el \\textsc\{nmi\} de la", s)
assert old_h2, "H2 not found"
s = s.replace(r"\item El filtro dinámico ($T$) mejora el \textsc{nmi} de la", r"\item El filtro dinámico ($T$) mejora el \textsc{ari} de la", 1)
open(I, 'w').write(s)

# ---------------- Cap. 3 ----------------
rep(TR, [
(r"""El principio coincide con esta tesis: una heurística como \textit{prior} estructural reduce el costo de los modelos de aprendizaje.""",
 r"""El principio coincide en parte con esta tesis: en ambos casos, una heurística aporta un \textit{prior} estructural al modelo de aprendizaje."""),
(r"""Estos métodos modelan grafos cuyas aristas cambian en el tiempo y se excluyen de la comparación experimental. Requieren registros temporales que el modelo estático de esta tesis no usa. Además, su componente recurrente choca con el objetivo de un bloque ligero y de bajo consumo de \textsc{vram} \cite{Xu2020, Rossi2020, Pareja2020}.""",
 r"""Estos métodos modelan grafos cuyas aristas cambian en el tiempo \cite{Xu2020, Rossi2020, Pareja2020} y se excluyen de la comparación experimental. Requieren registros temporales que el modelo estático de esta tesis no usa."""),
])

# ---------------- Resumen / Abstract (sin Physics) ----------------
rep(f"{T}/frontmatter/resumen.tex", [
(r"""Los modelos neuronales profundos integran la topología""", r"""Muchos modelos neuronales profundos integran la topología"""),
(r"""obtiene particiones de calidad competitiva con la de los modelos profundos, aunque no los supera, sin recibir $k$ como entrada y con mayor estabilidad entre semillas que \textsc{dgi}.""",
 r"""obtiene particiones de calidad comparable a la de los modelos profundos en parte de los grafos, aunque no los supera en ninguno, sin recibir $k$ como entrada y sin los colapsos que presenta \textsc{dgi} en los grafos de Amazon."""),
])
rep(f"{T}/frontmatter/abstract.tex", [
(r"""Deep neural models integrate topology and node features""", r"""Many deep neural models integrate topology and node features"""),
(r"""yields partitions of competitive quality with respect to deep models, although it does not outperform them, without receiving $k$ as input and with greater stability across seeds than \textsc{dgi}.""",
 r"""yields partitions of quality comparable to that of deep models on some of the graphs, although it outperforms them on none, without receiving $k$ as input and without the collapses that \textsc{dgi} shows on the Amazon graphs."""),
])

# ---------------- Cap. 5 ----------------
rep(R, [
# leyenda 5.1
(r"""Fila $k$: número de comunidades; DeepWalk, \textsc{dgi} y DMoN reciben el $k$ de referencia. El $DBI$ se calcula en el espacio de representaciones de cada método, por lo que solo es comparable dentro de un mismo método. Negritas: mejor valor por fila.""",
 r"""Fila $k$: número de comunidades; en las columnas GCN son las comunidades ancla del \textit{prior} tras el filtro, y DeepWalk, \textsc{dgi} y DMoN reciben el $k$ de referencia. El $DBI$ se calcula en el espacio de representaciones de cada método, por lo que solo es comparable dentro de un mismo método y no se marca en negritas. Negritas: mejor media por fila en $NMI$, $ARI$ y $Q$, calculada sin redondear."""),
# leyenda 5.3
(r"""GCN-Louvain usa \textit{prior} de modularidad ($\gamma=1.0$) con el filtro condicionado, sin el cual estas corridas no son ejecutables (Sección~\ref{sec:estudio-recalibracion}); en \textsc{sbm}-10k ese filtro reduce el \textit{prior} a una sola comunidad (Sección~\ref{subsec:recal-validacion}). GCN-Leiden usa \textsc{cpm} con $\gamma = (p_{in}+p_{out})/2$,""",
 r"""GCN-Louvain usa \textit{prior} de modularidad ($\gamma=1.0$, $\beta=0.5$) con el filtro condicionado; sin él, la corrida no es ejecutable en \textsc{sbm}-5k y en \textsc{sbm}-1k el \textit{prior} conserva solo 2 de los 5 bloques (Sección~\ref{sec:estudio-recalibracion}). En \textsc{sbm}-10k ese filtro reduce el \textit{prior} a una sola comunidad (Sección~\ref{subsec:recal-validacion}). GCN-Leiden usa \textsc{cpm} con $\gamma = (p_{in}+p_{out})/2$ y $\beta = 0.5$,"""),
# 5.1.1 parrafo 1
(r"""En Cora, GCN-Leiden queda en segundo lugar ($NMI""",
 r"""En Cora, GCN-Leiden obtiene la segunda mejor media, a menos de una desviación estándar de GCN-Louvain ($NMI"""),
(r"""En Coauthor CS, \textsc{dgi} y DMoN superan a ambas variantes \textsc{gcn}. En los grafos de compra conjunta, GCN-Louvain obtiene el mejor $NMI$ y $ARI$ en Amazon Computers ($0.529 \pm 0.016$ y $0.439 \pm 0.013$); en Amazon Photo y WikiCS, las heurísticas clásicas superan a todos los métodos entrenables.""",
 r"""En Coauthor CS, \textsc{dgi} supera a ambas variantes \textsc{gcn} en $NMI$ y $ARI$ (en $ARI$, por menos de una desviación estándar), y DMoN las supera solo en $NMI$. En los grafos de compra conjunta, GCN-Louvain obtiene la mejor media de $NMI$ y $ARI$ en Amazon Computers ($0.529 \pm 0.016$ y $0.439 \pm 0.013$), aunque a menos de una desviación estándar de Leiden clásico en $NMI$ y de GCN-Leiden en $ARI$. En Amazon Photo, las heurísticas clásicas superan a todos los métodos entrenables; en WikiCS, solo DeepWalk las iguala."""),
(r"""recuperan casi exactamente los bloques de \textsc{sbm}-1k y \textsc{sbm}-5k, igual que los modelos profundos (Tabla~\ref{tab:resultados-sbm}).""",
 r"""recuperan casi exactamente los bloques de \textsc{sbm}-1k y \textsc{sbm}-5k, igual que \textsc{dgi} y DMoN (Tabla~\ref{tab:resultados-sbm})."""),
# 5.1.1 parrafo 2
(r"""Una \textsc{gcn} de una sola capa resulta así competitiva, pero no superior, frente a los modelos profundos, sin recibir $k$ como entrada: se acerca a \textsc{dgi} en Cora e iguala o supera a los modelos profundos en los dos grafos de Amazon, pero queda por debajo de \textsc{dgi} en CiteSeer, PubMed y Coauthor CS. Esto responde la cuarta pregunta de investigación.""",
 r"""Frente al mejor modelo profundo de cada grafo, y considerando empate toda diferencia menor que la mayor de las dos desviaciones estándar, GCN-Leiden empata en CiteSeer, Amazon Computers y Amazon Photo, y queda por debajo en Cora, PubMed y WikiCS; en Coauthor CS queda por debajo en $NMI$ y empata en $ARI$ (Actor se discute en la Sección~\ref{subsec:analisis-film}). Una \textsc{gcn} de una sola capa resulta así comparable a los modelos profundos en parte de los grafos, sin recibir $k$ como entrada, pero no los supera en ninguno. Esto responde la cuarta pregunta de investigación."""),
(r"""Su ventaja está en la estabilidad frente al método contrastivo: \textsc{dgi} colapsa en Amazon Computers en cuatro de cinco semillas ($NMI = 0.094 \pm 0.124$) y en Amazon Photo en las cinco. Las variantes \textsc{gcn} no colapsan en estos grafos, aunque""",
 r"""La ventaja de las variantes \textsc{gcn} frente al método contrastivo es la ausencia de colapsos: \textsc{dgi} colapsa en Amazon Computers en cuatro de cinco semillas ($NMI = 0.094 \pm 0.124$) y en Amazon Photo en las cinco, mientras que las variantes \textsc{gcn} no colapsan en estos grafos, aunque"""),
# 5.1.2
(r"""Como ambos brazos comparten la regla de reporte, esta sección usa el valor pico del protocolo de Wang et al. (Tabla~\ref{tab:prior-pico}).""",
 r"""Como ambos brazos comparten la regla de reporte, esta sección usa el valor pico, como el protocolo de Wang et al., tomado sobre la rejilla de evaluación de cada grafo (Tabla~\ref{tab:prior-pico} y Sección~\ref{subsec:lineas-base-protocolo})."""),
(r"""{GCN-Louvain frente a GCN-Leiden con el valor pico del protocolo de Wang et al.: media$\pm$desviación estándar sobre cinco semillas.}""",
 r"""{GCN-Louvain frente a GCN-Leiden con el valor pico (máximo sobre las evaluaciones, cada 2, 5 o 10 épocas según el grafo): media$\pm$desviación estándar sobre cinco semillas.}"""),
(r"""Si se considera empate toda diferencia menor a una desviación estándar, Leiden gana en Cora ($+0.013$ de $NMI$, en cuatro de cinco semillas) y PubMed ($+0.022$), y por un margen mínimo en Amazon Photo ($+0.004$); empata en Coauthor CS ($+0.004$) y Amazon Computers ($-0.002$); y pierde en CiteSeer ($0.388 \pm 0.012$ frente a $0.401 \pm 0.008$), WikiCS ($0.410 \pm 0.003$ frente a $0.419 \pm 0.001$) y Actor, donde el filtro reduce el \textit{prior} de Leiden a una sola comunidad (Sección~\ref{subsec:analisis-film}).""",
 r"""Si se considera empate toda diferencia en $NMI$ menor que la mayor de las dos desviaciones estándar, Leiden gana en Cora ($+0.013$, en cuatro de cinco semillas) y PubMed ($+0.022$), y por un margen mínimo en Amazon Photo ($+0.005$); empata en Coauthor CS ($+0.004$) y Amazon Computers ($-0.002$); y pierde en CiteSeer ($0.388 \pm 0.012$ frente a $0.401 \pm 0.008$) y WikiCS ($0.410 \pm 0.003$ frente a $0.419 \pm 0.001$). Actor se trata aparte: con Leiden, el filtro reduce el \textit{prior} a una sola comunidad y el \textit{pipeline} degenera, mientras que con Louvain sobrevive sin señal ($NMI = 0.007$; Sección~\ref{subsec:analisis-film}). En $ARI$, las diferencias en Cora y CiteSeer son menores a una desviación estándar."""),
# 5.1.3
(r"""que registran $Q'$ cada dos épocas.""",
 r"""que registran $Q'$ en cada evaluación: cada 2 épocas en Cora, CiteSeer y Amazon Photo, cada 5 en Amazon Computers y WikiCS, y cada 10 en PubMed y Coauthor CS."""),
(r"""La evaluación se realiza cada dos épocas.}""",
 r"""La evaluación se realiza cada 2, 5 o 10 épocas según el grafo.}"""),
(r"""El retraso se concentra en WikiCS. Al 99\,\% del nivel no hay diferencia ($p = 0.66$), y una medida relativa""",
 r"""El retraso se concentra en WikiCS: sin ese grafo, la diferencia deja de ser significativa ($p > 0.1$). Además, las cinco semillas de un grafo comparten el mismo \textit{prior}, por lo que no son réplicas independientes de su efecto. Al 99\,\% del nivel no hay diferencia ($p = 0.66$, excluido un par de Cora cuya corrida con Louvain no alcanza ese nivel), y una medida relativa"""),
(r"""El \textit{prior} tampoco cambia los niveles de la optimización: ni el $Q'$ inicial ni el máximo difieren entre Leiden y Louvain ($p = 0.99$ y $p = 0.92$). Hay dos salvedades. La evaluación cada dos épocas produce muchos empates, y cada \textit{prior} fija un $k$ distinto,""",
 r"""El \textit{prior} tampoco desplaza de forma sistemática los niveles de la optimización: en conjunto, ni el $Q'$ de la primera evaluación ni el máximo difieren entre Leiden y Louvain ($p = 0.99$ y $p = 0.92$), aunque por grafo hay diferencias en sentidos opuestos (con Leiden, el $Q'$ máximo es mayor en Cora y menor en CiteSeer en las cinco semillas). Hay dos salvedades más. La evaluación discreta produce muchos empates, sobre todo en los grafos evaluados cada 5 o 10 épocas, y en Cora y PubMed cada \textit{prior} fija un $k$ distinto,"""),
# 5.2.1
(r"""De los cuatro valores probados, $\beta = 0.5$ da el mejor $NMI$ también para Leiden, aunque es el extremo superior de la malla, por lo que no se descarta que valores mayores lo mejoren. En el extremo $\beta = -0.5$ el filtro se apaga y el $NMI$ cae en todos los casos. El filtro aporta valor en distribuciones sesgadas. En Cora y CiteSeer no hace falta recalibrar: $\beta = 0.5$ se transfiere de Louvain a Leiden. La ventaja de GCN-Leiden en Cora se sostiene en los cuatro valores de $\beta$; la de GCN-Louvain en CiteSeer, solo con $\beta \geq 0.25$.""",
 r"""De los cuatro valores probados, $\beta = 0.5$ da el mejor $NMI$ también para Leiden (en Cora, empatado con $\beta = 0.25$), aunque es el extremo superior de la malla, por lo que no se descarta que valores mayores lo mejoren. En el extremo $\beta = -0.5$ el filtro se apaga y el $NMI$ pico cae en todos los casos. Esta comparación en $NMI$ está sesgada por $k$: sin filtro, el \textit{prior} conserva unas 90 comunidades en Cora y 450 en CiteSeer, y el $NMI$ tiende a crecer con el número de clústeres. El $ARI$, que corrige el acuerdo por azar, muestra el aporte del filtro con ambas vistas. Con el \textit{checkpoint} de pérdida mínima, al filtrar con $\beta = 0.5$ el $ARI$ de GCN-Leiden pasa de $0.378$ a $0.442$ en Cora y de $0.146$ a $0.315$ en CiteSeer (con GCN-Louvain sube de forma similar), mientras que su $NMI$ no mejora ($0.530$ en ambos casos en Cora; de $0.352$ a $0.338$ en CiteSeer). El filtro aporta valor en distribuciones sesgadas. En Cora y CiteSeer no hace falta recalibrar: $\beta = 0.5$ se transfiere de Louvain a Leiden. La media de GCN-Leiden en Cora es mayor en los cuatro valores de $\beta$ (con $\beta = 0$, por menos de una desviación estándar); la ventaja de GCN-Louvain en CiteSeer aparece solo con $\beta \geq 0.25$."""),
# 5.2.4
(r"""como máximo $0.007$ en los \textsc{sbm} cuyos bloques recupera la modularidad""",
 r"""alrededor de $0.007$ en los \textsc{sbm} cuyos bloques recupera la modularidad"""),
(r"""En \textsc{sbm}-1k y \textsc{sbm}-5k, las corridas antes imposibles ahora se completan.""",
 r"""En \textsc{sbm}-5k, las corridas antes imposibles ahora se completan, y en \textsc{sbm}-1k el \textit{prior} conserva los 5 bloques en lugar de 2 o 3."""),
])
# quitar negritas de las filas DBI de las tablas 5.1-5.3
s = open(R).read(); out = []; nb = 0
for line in s.split('\n'):
    if '& $DBI$ &' in line and r'\textbf{' in line:
        new = re.sub(r'\\textbf\{([0-9.]+\{\\scriptsize\$\\pm\$[0-9.]+\})\}', r'\1', line)
        nb += line.count(r'\textbf{') - new.count(r'\textbf{'); line = new
    out.append(line)
open(R, 'w').write('\n'.join(out)); print("DBI bold removed:", nb)

# ---------------- Conclusiones ----------------
rep(C, [
(r"""2 & H2 & 2 & \ref{sec:estudio-recalibracion} & Aceptada con tamaños sesgados (Cora, CiteSeer); rechazada con tamaños uniformes (\textsc{sbm} con modularidad). \\""",
 r"""2 & H2 & 2 & \ref{sec:estudio-recalibracion} & Aceptada en Cora y CiteSeer con ambas vistas; rechazada con tamaños uniformes (\textsc{sbm} con modularidad); sin señal en Actor. \\"""),
(r"""4 & Central & 1, 3 & \ref{subsec:analisis-calidad} & Aceptada parcialmente: calidad comparable, pero no superior, a la de los modelos profundos. \\""",
 r"""4 & Central & 1, 3 & \ref{subsec:analisis-calidad} & Aceptada parcialmente: comparable en CiteSeer y en los grafos de Amazon; inferior en Cora, PubMed y WikiCS, y en Coauthor CS en $NMI$. \\"""),
(r"""Con el valor pico, Leiden supera a Louvain en Cora y PubMed, y por un margen mínimo en Amazon Photo; empata en Coauthor CS y Amazon Computers, y pierde en CiteSeer, WikiCS y Actor (Sección~\ref{subsec:analisis-ablacion-prior}).""",
 r"""Con el valor pico y en $NMI$, Leiden supera a Louvain en Cora y PubMed, y por un margen mínimo en Amazon Photo; empata en Coauthor CS y Amazon Computers, y pierde en CiteSeer y WikiCS. En Actor, el filtro reduce el \textit{prior} de Leiden a una sola comunidad (Sección~\ref{subsec:analisis-ablacion-prior})."""),
(r"""En Cora y CiteSeer, $\beta = 0.5$ es el mejor de los valores probados tanto con Louvain como con Leiden,""",
 r"""En Cora y CiteSeer, $\beta = 0.5$ es el mejor de los valores probados tanto con Louvain como con Leiden (en Cora, empatado con $\beta = 0.25$),"""),
(r"""La segunda hipótesis específica (H2) se acepta cuando la distribución de tamaños es sesgada: en Cora y CiteSeer, filtrar con $\beta = 0.5$ eleva el $NMI$ frente a no filtrar ($\beta = -0.5$) con ambos \textit{priors} (Tabla~\ref{tab:recal-beta}). Se rechaza con tamaños uniformes, donde el filtro reduce el $NMI$ del \textit{prior} de modularidad (Tabla~\ref{tab:recal-sbm}).""",
 r"""La segunda hipótesis específica (H2) se acepta en Cora y CiteSeer: filtrar con $\beta = 0.5$ eleva el $ARI$ frente a no filtrar ($\beta = -0.5$) con ambos \textit{priors} y con ambas vistas (Sección~\ref{subsec:recal-redes-reales}). Se rechaza con tamaños uniformes, donde el filtro reduce la calidad del \textit{prior} de modularidad (Tabla~\ref{tab:recal-sbm}; por ejemplo, en \textsc{sbm}-10k el $ARI$ de GCN-Leiden baja de $0.787$ a $0.182$), y en Actor no hay señal en ninguna configuración."""),
(r"""requiere las mismas épocas que Louvain o, en grafos como WikiCS, más (Sección~\ref{subsec:analisis-convergencia}). Tampoco cambia el $Q'$ inicial ni el máximo.""",
 r"""requiere en general las mismas épocas que Louvain, y más en WikiCS (Sección~\ref{subsec:analisis-convergencia}). Tampoco desplaza de forma sistemática el $Q'$ inicial ni el máximo."""),
(r"""Es comparable, pero no superior, por lo que la hipótesis central se acepta parcialmente. Con el \textit{checkpoint} de pérdida mínima, la arquitectura propuesta se acerca a \textsc{dgi} en Cora e iguala o supera a los modelos profundos en los dos grafos de Amazon, pero queda por debajo de \textsc{dgi} en CiteSeer, PubMed y Coauthor CS, y de las heurísticas clásicas en Amazon Photo y WikiCS. Al igual que la arquitectura base, estima $k$ sin supervisión, a diferencia de los \textit{baselines} profundos, y es más estable entre semillas que \textsc{dgi}, que colapsa en los grafos de Amazon.""",
 r"""Solo en parte, por lo que la hipótesis central se acepta parcialmente. Con el \textit{checkpoint} de pérdida mínima y frente al mejor modelo profundo de cada grafo, la arquitectura propuesta empata en CiteSeer y en los dos grafos de Amazon, pero queda por debajo en Cora, PubMed y WikiCS, y en Coauthor CS en $NMI$ (Sección~\ref{subsec:analisis-calidad}); en ningún grafo los supera. En Amazon Photo y WikiCS, además, las heurísticas clásicas superan o igualan a todos los métodos entrenables. Al igual que la arquitectura base, estima $k$ sin supervisión, a diferencia de los \textit{baselines} profundos, aunque ese $k$ difiere del de referencia en casi todos los grafos, y no presenta los colapsos de \textsc{dgi} en los grafos de Amazon."""),
(r"""muestra, en Cora y CiteSeer, que el valor original sigue siendo el mejor de los probados con otro \textit{prior},""",
 r"""muestra, en Cora y CiteSeer, que el valor original sigue siendo el mejor de los probados con otro \textit{prior} (en Cora, empatado con $\beta = 0.25$),"""),
(r"""El barrido de $\beta$ en grafos reales cubre solo Cora y CiteSeer, y su mejor valor está en el extremo de la malla.""",
 r"""El barrido de $\beta$ en grafos reales cubre solo Cora, CiteSeer y Actor (este último, sin señal), y su mejor valor está en el extremo de la malla."""),
(r"""evitaría materializar $\mathbf{B}$ y permitiría evaluar grafos como Coauthor Physics.""",
 r"""evitaría materializar $\mathbf{B}$. Junto con una adyacencia dispersa y una normalización que no construya una matriz diagonal densa, podría permitir evaluar grafos como Coauthor Physics."""),
])

# ---------------- Repo: docstrings ----------------
rep(f"{G}/experiments/analysis/convergence.py", [
("""optimisation of Q'?" from the stored training histories (one row every
``eval_every`` = 2 epochs). Since""",
 """optimisation of Q'?" from the stored training histories (one row per
evaluation: every 2 epochs on cora/citeseer/amap/film, 5 on amac/wikics and
10 on pubmed/cocs, as set per shard in experiments/deploy/launch_shards.sh).
Q'_0 is the first evaluated value, not epoch 0. Since"""),
("""    dataset, a level every run of both arms reaches.""",
 """    dataset. Every run reaches it for frac <= 0.95; at frac = 0.99 one Cora
    run (gcn-louvain, seed 3) falls short and its pair is dropped (n = 34)."""),
("""zero differences (frequent, because of the
2-epoch evaluation grid) are dropped by the test and reported separately.""",
 """zero differences (frequent, because of the
coarse 2/5/10-epoch evaluation grid) are dropped by the test and reported
separately. The five seeds of a dataset share the same prior, so they are not
independent replicates of the prior's effect."""),
])
rep(f"{G}/gcn_leiden/prior.py", [
("""                          1.2-11.5 on real networks, <= 0.007 on SBM priors
                          that recover every block, and 0.41-0.45 on""",
 """                          1.2-11.5 on real networks, 1.4-1.8 on CPM priors of
                          the SBM graphs, ~0.007 on modularity SBM priors
                          that recover every block, and 0.41-0.45 on"""),
])
rep(f"{G}/experiments/baselines/__init__.py", [
("""  * Deep baselines that need a cluster count receive the ground-truth k,
    mirroring the protocol of Wang et al. (2025) and the deep-clustering
    literature; this favors the baselines, making our comparisons
    conservative.""",
 """  * Deep baselines that need a cluster count receive the ground-truth k
    (number of label classes). Wang et al. (2025) instead give their
    baselines the k detected by their own method. Knowing k does not favor a
    method on every metric (NMI tends to grow with the number of clusters)."""),
])
rep(f"{G}/experiments/baselines/deepwalk.py", [
("""Embeddings are clustered with k-means using the ground-truth k
(protocol of Wang et al. 2025; see baselines/__init__.py).""",
 """Embeddings are clustered with k-means using the ground-truth k
(see baselines/__init__.py)."""),
])
print("ok")
