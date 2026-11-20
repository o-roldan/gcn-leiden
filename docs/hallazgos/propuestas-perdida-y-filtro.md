# Propuestas para la pérdida y el filtro de GCN-Leiden

Análisis del 2026-11-20 para decidir la siguiente vuelta de experimentos. No incluye entrenamientos nuevos de la GCN. Las cifras salen de los CSV de `results/`, del código, de cálculos sobre los datos (grafo y etiquetas) y de una prueba exploratoria del criterio para elegir γ en Cora y CiteSeer (Sección 5.4), que tampoco entrena la GCN.

**Alcance.** La nueva vuelta evalúa solo la arquitectura propia (Wang et al. + ajustes + *prior* de Leiden) en los grafos reales. Los SBM quedan fuera, porque servían para mostrar límites de la arquitectura de Wang. **Objetivo:** mejorar el ARI.

## Mensaje principal

1. **Pérdida.** Sustituir la Q′ de Wang (γ = 1) por Q′_γ, la versión suave de la función que optimiza el *prior* de Leiden (modularidad con resolución γ). El argumento es la coherencia entre *prior* y pérdida. No es exclusiva de Leiden y no hereda su conectividad.
2. **Mecanismos del paper de Leiden.** Todos optimizan topología, así que ninguno promete subir el ARI. Solo conviene *medir* si la conectividad del *prior* sobrevive al entrenamiento. Reparar, fusionar, re-anclar o regularizar se descartan.
3. **Métricas.** Cuando *k* difiere entre configuraciones, decide el ARI. El NMI premia fragmentar: en CiteSeer, poner cada nodo solo da NMI = 0.356, más que GCN-Leiden (0.338).
4. **Filtro.** T = μ + βσ mezcla dos trabajos. La Etapa 1 propuesta (anclas solo de la componente gigante) sigue en pie, sin probar. La Etapa 2 (elegir la γ del *prior* por acuerdo entre topología y características) se probó en Cora y CiteSeer y no supera a γ = 0.3: el acuerdo sigue la tendencia de grueso a fino, pero no encuentra sin etiquetas la γ óptima.

## 1. Qué optimiza la arquitectura

- **Fase 1.** Leiden (`RBConfigurationVertexPartition`, γ = 0.3; `gcn_leiden/prior.py:22`, `experiments/runners/gcn.py:39`) produce K₀ comunidades, y el filtro conserva *k* anclas.
- **Fases 2–3.** Una GCN de una capa, Z = PReLU(ÂXW), normalizada. Cada centroide es la media de su ancla, y P = softmax(δ · sim(z_i, u_c)) con δ = 30.
- **Fase 4.** Pérdida −α·Q′, con Q′ = tr(PᵀBP)/2m y B = A − ddᵀ/2m, es decir, γ = 1 (`gcn_leiden/loss.py:10`, `gcn_leiden/trainer.py:53,71`). Cada época usa el grafo completo.
- **Lo que se entrena (W) solo transforma las características, pero el objetivo es solo topológico.** Las características son el medio y la topología el criterio; la topología además define las anclas.
- **El código de Wang tiene la misma estructura:** *prior* con γ = 0.3 (`main.py:133`) y pérdida con γ = 1 (`main.py:51`, `DGI.py:80`).

## 2. Pérdida: Q′_γ, coherente con el *prior*

### 2.1 Funciones de calidad de Leiden

Leiden acepta funciones de la forma `H = Σ_ij (A_ij − γ·n_ij)·δ(c_i, c_j)`. Solo cambia `n_ij`, el número de aristas que se esperarían por azar:

| | Modularidad con γ | CPM |
|---|---|---|
| Modelo nulo `n_ij` | d_i·d_j / 2m (conserva grados) | 1 (constante) |
| Penaliza | volumen² de cada comunidad | pares de nodos |
| γ | sin unidades; valor canónico 1 | densidad; sin valor canónico |
| Límite de resolución | sí | no |
| Uso como *prior* en la tesis | grafos reales (γ = 0.3), Louvain y Leiden | solo SBM, solo Leiden |

En los grafos reales, el *prior* optimiza modularidad con γ = 0.3, así que la pérdida coherente es la modularidad, no CPM. Usar CPM obligaría a cambiar también el *prior* y a elegir γ sin respaldo.

### 2.2 Propuesta

```
Q′_γ = tr( Pᵀ (A − γ·ddᵀ/2m) P ) / 2m        L = −α·Q′_γ
```

- **γ es la del *prior*:** 0.3 con la configuración actual. El criterio que se probó para elegirla a partir de los datos no funcionó (Sección 5.4).
- **Generaliza a Wang en vez de reemplazarlo:** su Q′ es el caso γ = 1. En código solo cambia la matriz B.
- **Admite una forma dispersa, sin matrices n × n:** `Q′_γ = [ tr(PᵀAP) − γ·‖Pᵀd‖²/2m ] / 2m`. Se verificó numéricamente que su valor y su gradiente coinciden con los de la forma densa.
- **Cubre parte de un trabajo futuro:** junto con una normalización sin matriz diagonal densa, resuelve el Trabajo futuro 2 de la tesis (`chapters/conclusiones/conclusiones.tex:73`).

### 2.3 Advertencias

1. **Presión a fusionar.** Se cumple la identidad (verificada) `Q′_γ = Q′ + (1 − γ)·Σ_c (K_c/2m)²`. Con γ = 0.3, el término extra premia concentrar el volumen en pocas comunidades, y el *k* efectivo puede quedar por debajo del *k* del *prior*.
2. **Desalineación con la métrica Q.** Las tablas reportan la Q de Newman (γ = 1), que hoy es el objetivo. Con Q′_γ es probable que Q baje sin que la partición empeore, así que conviene reportar también Q_γ.
3. **Actor.** Con el *prior* de Leiden, *k* = 1. Con una sola comunidad, Q′_γ = 1 − γ es constante y no hay gradiente con ninguna pérdida.
4. **No es exclusiva de Leiden.** Louvain y Leiden son dos algoritmos que optimizan la misma función. Se verificó en tres frentes:
   - Wang: `nx.community.louvain_communities(graph, resolution=0.3, ...)` (`main.py:133`).
   - networkx: la ganancia de cada movimiento usa `resolution` (`louvain.py:285–311`).
   - `leidenalg`: `RBConfigurationVertexPartition` optimiza `Σ_ij (A_ij − γ·k_i·k_j/2m)·δ`.

   Las mismas particiones, evaluadas con ambas implementaciones (configuración de la tesis, semilla del *prior* 123):

   | Grafo | *Prior* | K₀ | Q_0.3 (networkx) | Q_0.3 (leidenalg / 2m) |
   |---|---|---|---|---|
   | Cora | Louvain | 89 | 0.8817841449 | 0.8817841449 |
   | Cora | Leiden | 90 | 0.8843554005 | 0.8843554005 |
   | CiteSeer | Louvain | 452 | 0.9367529815 | 0.9367529815 |
   | CiteSeer | Leiden | 451 | 0.9359101240 | 0.9359101240 |

   - **Se puede decir:** con el *prior* de Leiden, la pérdida se alinea con la función que ese *prior* optimiza.
   - **No conviene decir:** que exista una «modularidad de Leiden» ni que Leiden haga posible esta pérdida.
   - **Si un revisor pregunta «¿por qué no se aplica a GCN-Louvain?»:** sí es aplicable, y el trabajo la evalúa solo en su arquitectura.
5. **No hereda la conectividad.** La propia tesis define la desconexión como «un fallo del procedimiento del algoritmo de Louvain […] independientemente de la función de calidad utilizada» (`chapters/marco_teorico/marco_teorico.tex:383`). Además, la modularidad y CPM ya prefieren comunidades conexas: dividir una comunidad desconectada en sus componentes siempre aumenta la calidad. Es un requisito de las funciones que acepta Leiden (suplemento de Traag et al., p. 1).

## 3. Mecanismos del algoritmo de Leiden

Fuente: Traag, Waltman y van Eck (2019), *Sci. Rep.* 9:5233, y su información suplementaria, leídos completos.

### 3.1 Lo que la GCN ya hace y lo que le falta

La derivada de la pérdida respecto a la afiliación es la ganancia de mover un nodo:

```
∂Q′_γ/∂p_ic = (1/m)·[ (A·p_c)_i − γ·d_i·K_c/2m ]
```

- **La GCN ya hace el movimiento local.** La derivada es la versión suave de la ganancia ΔH(v ↦ C) que Leiden evalúa en esa fase (escrita con la forma de la Ec. A5 del suplemento). El entrenamiento equivale a un movimiento local continuo que además usa las características.
- **Le faltan las otras dos fases:** el **refinamiento**, que da la γ-conectividad (Teorema 5), y la **iteración desde la partición actual** con mejoras estrictas (Lema 8). Por eso la garantía cubre solo las anclas (`chapters/propuesta_solucion/propuesta_solucion.tex:150`).
- **En la práctica, la conectividad de las anclas casi no distingue a los *priors*.** Con la configuración de la tesis, en los 8 grafos reales con resultados de la GCN solo hay una ancla desconectada: la de Louvain en CiteSeer (134 nodos = 117 + 17). Leiden tiene 0.

### 3.2 Qué se puede transferir

| Mecanismo | Qué garantiza | ¿Se transfiere? |
|---|---|---|
| Refinamiento (Alg. A.2, Teorema 5) | γ-conectividad en cada iteración | Sí → P1 |
| γ-separación (Def. 5, Teorema 4) | ningún par de comunidades se fusiona con ganancia | Sí → P2 |
| Iterar desde la partición actual con mejoras estrictas (Lema 8) | sigue mejorando y termina | Sí → P3 |
| Densidad γ uniforme (Def. 9, Ec. D1) | ningún subconjunto se separa con ganancia | Parcial → P4 |
| Aleatoriedad θ y movimientos no voraces (Apéndice C) | alcanzar óptimos que los movimientos voraces no alcanzan | No: sin análogo en un descenso de gradiente continuo |
| Movimiento local rápido con cola | solo velocidad | No |
| Cota de optimalidad (Teorema 14) | cota superior de H(P*) | No: exige una partición asintóticamente estable, que no se puede verificar |

### 3.3 Propuestas y veredicto

| | Qué hace | ¿Exclusiva de Leiden? | Efecto esperado en ARI | Veredicto |
|---|---|---|---|---|
| **P1** | Correr Leiden sobre el subgrafo de cada comunidad final; si la divide, estaba mal conectada | Sí: Louvain no garantiza γ-conectividad (Tabla 1) | Medir: ninguno. Reparar: *k* sube y el ARI queda igual o baja | **Solo medir** |
| **P2** | Fusionar pares con `E(C,D)/m − 2γ·a_C·a_D > 0`, con a_C = K_C/2m | No: Louvain también garantiza γ-separación | Casi nulo con γ = 0.3: las anclas salen de una partición ya γ-separada con la misma γ | Descartar |
| **P3** | Cada T épocas, recalcular anclas y *k* desde la partición de la GCN, aceptando solo mejoras de Q_γ | No: es autoentrenamiento | Incierto; aceptar por Q_γ empuja más la topología | Descartar por ahora |
| **P4** | Penalizar `max(0, γ·K_c/2m − μ₂(c))`, con μ₂ el segundo autovalor generalizado de `L_C x = μ D x` | Sí | Topológico | Descartar: k problemas de autovalores por época; condición solo suficiente; derivación propia sin verificar formalmente |

**P1, medición.**
- **Protocolo:** el de la Fig. 4 de Traag et al. Se corre Leiden sobre el subgrafo de cada comunidad con la función consistente con el grafo completo. En `leidenalg`: `CPMVertexPartition` con `node_sizes` = grados globales y resolución γ/2m (Ec. A5 del suplemento).
- **Qué responde:** si la conectividad, el argumento que la tesis eligió para Leiden, sobrevive al entrenamiento. Medir no cambia la partición ni las métricas.
- **Solo dentro de la componente gigante.** Fuera de ella, cada componente suelta sería su propia comunidad y *k* se inflaría como en las heurísticas clásicas. Dentro caben a lo sumo 13 comunidades del *prior* en Cora y 14 en CiteSeer, así que lo medido sería sobre todo lo que hace la GCN.

**Por qué ninguna sube el ARI.** Todas optimizan Q_γ, y la tesis muestra que más topología no acerca a las etiquetas: en 56 de 70 corridas el pico de NMI llega antes que el máximo de Q′ (`chapters/resultados/resultados.tex:195`).

## 4. Métricas: cuándo decide el ARI

- **NMI:** información compartida entre la partición y las etiquetas, normalizada por las entropías. No se corrige por azar.
- **ARI:** acuerdo sobre pares de nodos (juntos o separados en ambas particiones), corregido para que una partición aleatoria valga 0.

**Para un público no especializado.** Se toman todas las parejas de artículos y se pregunta si son del mismo tema real y si el algoritmo las juntó; el porcentaje de coincidencias es el índice de Rand. Como la mayoría de las parejas son de temas distintos, separar a todos «acierta» alrededor del 82 % de las parejas de Cora sin aprender nada. El ARI descuenta esa suerte: 1 es idéntico a los temas reales y 0 equivale al azar.

**El NMI premia fragmentar.** Particiones triviales, sin aprendizaje:

| Partición | *k* | NMI | ARI |
|---|---|---|---|
| Cora, un nodo por comunidad | 2 708 | 0.376 | 0.000 |
| CiteSeer, un nodo por comunidad | 3 327 | 0.356 | 0.000 |
| CiteSeer, aleatoria uniforme (10 semillas) | 470 | 0.104 | 0.000 |
| CiteSeer, aleatoria uniforme (10 semillas) | 6 | 0.002 | 0.000 |

En CiteSeer, la partición en nodos sueltos supera en NMI a GCN-Leiden (0.338), a GCN-Louvain (0.342) y a Louvain y Leiden clásicos (0.328). Solo DGI (0.377) la supera.

**Evidencia propia.** Al apagar el filtro (Sección 5.1), el NMI no detecta el daño y el ARI sí:
- **Cora:** el NMI se queda en 0.530 y el ARI cae de 0.442 a 0.378.
- **CiteSeer:** el NMI incluso prefiere no filtrar (0.352 frente a 0.338) y el ARI cae de 0.315 a 0.146.

**Límites del ARI.**
- Lo dominan las clases grandes, porque los pares crecen con el tamaño al cuadrado.
- Castiga dividir una clase en dos. Eso es deseable si el objetivo es recuperar las clases etiquetadas.
- Si se quiere una métrica de información justa entre distintos *k*, existe el AMI (información mutua ajustada por azar).

**Regla.** Reportar ambas. Con el mismo *k* en los brazos comparados, las dos valen. Cuando *k* difiere, decide el ARI y el NMI se lee junto a *k*.

## 5. Filtro: propuesta en dos etapas

### 5.1 Diagnóstico: el filtro mezcla dos trabajos

Barrido de β existente (`results/runs_recal_<grafo>.csv`; GCN-Leiden, modularidad con γ = 0.3, *checkpoint* de pérdida mínima, 5 semillas):

| Grafo | β | *k* | ARI | NMI |
|---|---|---|---|---|
| Cora | −0.5 (sin filtro) | 90 | 0.378 ± 0.022 | 0.530 ± 0.009 |
| Cora | 0 | 11 | 0.448 ± 0.023 | 0.534 ± 0.015 |
| Cora | 0.25 | 10 | 0.442 ± 0.015 | 0.530 ± 0.008 |
| Cora | 0.5 | 10 | 0.442 ± 0.015 | 0.530 ± 0.008 |
| CiteSeer | −0.5 (sin filtro) | 451 | 0.146 ± 0.030 | 0.352 ± 0.007 |
| CiteSeer | 0 | 31 | 0.289 ± 0.034 | 0.328 ± 0.024 |
| CiteSeer | 0.25 | 13 | 0.299 ± 0.020 | 0.322 ± 0.020 |
| CiteSeer | 0.5 | 11 | 0.315 ± 0.025 | 0.338 ± 0.022 |

Estructura del *prior* (Leiden, γ = 0.3, semilla 123, filtro de Wang):

| Grafo | Componentes | % en la gigante | K₀ | Comunidades del *prior* en la gigante | *k* tras el filtro | *k* de referencia |
|---|---|---|---|---|---|---|
| Cora | 78 | 91.8 % | 90 | ≤ 13 | 10 | 7 |
| CiteSeer | 438 | 63.7 % | 451 | ≤ 14 | 11 | 6 |
| PubMed | 1 | 100 % | 16 | 16 | 5 | 3 |
| Coauthor CS | 1 | 100 % | 13 | 13 | 4 | 15 |
| Amazon Computers | 314 | 97.3 % | 320 | ≤ 7 | 5 | 10 |
| Amazon Photo | 136 | 97.9 % | 143 | ≤ 8 | 7 | 8 |
| Actor | 1 | 100 % | 26 | 26 | 1 | 5 |
| WikiCS | 356 | 96.7 % | 360 | ≤ 5 | 4 | 10 |

La cota sale de que las comunidades de Leiden son conexas: cada componente suelta contiene al menos una comunidad.

Lectura:

1. **Quitar componentes sueltas da casi toda la ganancia de ARI.** Hay 77 en Cora y 437 en CiteSeer. Cora sube 0.07 al pasar de 90 a 11 anclas; CiteSeer, 0.14 al pasar de 451 a 31.
2. **Elegir la granularidad no lo logra:**
   - Afinar el umbral apenas mueve el ARI: en Cora, 0.448 frente a 0.442; en CiteSeer, de 0.289 a 0.315, alrededor de una desviación estándar.
   - En WikiCS y Computers, γ = 0.3 deja a lo sumo 5 y 7 comunidades en la componente gigante, frente a 10 clases. Ningún filtro puede llegar.
   - En los grafos conexos, el filtro descarta comunidades reales: 9 de 13 en CS y 11 de 16 en PubMed.
3. **El umbral depende de un accidente estructural.** μ y σ mezclan componentes sueltas con comunidades reales, así que el umbral depende también de cuántas componentes sueltas tenga el grafo.

#### Por qué quitar tantas comunidades no daña la calidad

- **Sí la afecta, y para bien, pero no en el NMI.** En el barrido de arriba, filtrar sube el ARI (Cora: de 0.378 a 0.442; CiteSeer: de 0.146 a 0.315), mientras que el NMI no mejora (Cora: 0.530 en ambos casos; CiteSeer: de 0.352 a 0.338).
- **El filtro no borra nodos, borra anclas.** Las comunidades descartadas dejan de ser centroides, pero sus nodos siguen en el grafo, y la GCN los asigna al ancla más parecida según sus características y sus vecinos.
- **Lo descartado pesa poco en nodos.** Con la configuración de la tesis, las anclas de Leiden cubren el 89 % de los nodos en Cora y el 63 % en CiteSeer. El resto son sobre todo componentes sueltas y grupos diminutos.
- **Por qué ayuda.** Si esos grupos quedaran como comunidades propias, la partición quedaría fragmentada. El ARI lo castiga, porque separa nodos del mismo tema; el NMI no lo nota, porque premia fragmentar (Sección 4). Al quitarlos, la GCN asigna esos nodos a las anclas por sus características, y el ARI sube.
- **Cuándo perjudica.** Cuando descarta comunidades reales. En CS conserva 4 de 13 (*k* = 4 frente a 15 clases) y en PubMed 5 de 16. En Actor deja una sola comunidad y el *pipeline* degenera.
- **No es una cuestión de eficiencia.** Con menos anclas, la matriz P (n × k) es más chica, pero eso es despreciable frente a las matrices densas de n × n que dominan el costo. El filtro existe por calidad: decide *k* y qué comunidades sirven de referencia.

### 5.2 Principio

- **El filtro no puede aprender del ARI.** Sin etiquetas no tiene esa señal, y la única señal interna, Q′, apunta al lado contrario: con todas las anclas (β = −0.5), el ARI fue el peor en ambos grafos.
- **Por eso, una herramienta para cada trabajo:** una regla sin hiperparámetros para el primero y un criterio sin etiquetas que use las características para el segundo.

### 5.3 Propuesta

**Etapa 1. Anclas solo de la componente gigante.**
- Las comunidades fuera de ella nunca son anclas; sus nodos los asigna la GCN por características.
- Probablemente de ahí viene que la GCN supere a las heurísticas clásicas en ARI (CiteSeer: 0.315 frente a 0.087).
- Hace sin β el trabajo que hoy da la ganancia.

**Etapa 2. Elegir la γ del *prior* por acuerdo entre topología y características.**
- **Idea:** correr Leiden con varias γ y elegir aquella cuya partición de la componente gigante coincida más con la estructura de las características originales X. Bajo homofilia, el acuerdo entre las dos vistas es lo que hace coincidir etiquetas y topología.
- **Por qué X y no ÂX:** ÂX ya contiene topología e inflaría el acuerdo; con X, las dos vistas son independientes.
- **Medida del acuerdo:** la propuesta inicial era la silueta en X. Se cambió por el ARI entre Leiden(γ) y k-means sobre X con el mismo *k* (la idea de «fusión de dos sensores»), porque la silueta no corrige por azar.
- **Resultado:** no funciona en su forma actual (Sección 5.4).

Esto buscaba concretar el Trabajo futuro 1 de la tesis, «Calibración automática» (`chapters/conclusiones/conclusiones.tex:72`).

### 5.4 Prueba exploratoria de la Etapa 2 (Cora y CiteSeer)

Solo se evaluó el criterio; no se entrenó la GCN. Configuración:
- **Malla de γ:** 13 valores entre 0.05 y 3.0. Leiden (`RBConfigurationVertexPartition`) corre sobre el grafo completo con semilla 123, como el *prior* de la tesis, y se toman las comunidades dentro de la componente gigante.
- **Exclusión:** las γ con *k* < 3. Con *k* = 1 en ambas vistas, el ARI vale 1 de forma trivial.
- **Sensor de características:** k-means sobre las filas de X con TF-IDF y normalización L2 (equivale a k-means esférico), con el mismo *k*, `n_init = 3` y semillas 0–4.
- **Uso de etiquetas:** solo para evaluar, mediante el ARI de la partición del *prior* dentro de la componente gigante. Es un sustituto del ARI final de la GCN, no el ARI final.
- **Regla de decisión:** el máximo del criterio, sin desempate. Pasa si la γ elegida da un ARI del *prior* mayor o igual que con γ = 0.3.

Criterios probados:
- **Acuerdo original:** la media de ARI(Leiden(γ), k-means(X, *k*)) sobre las semillas.
- **Regla de una desviación:** la γ mayor cuyo acuerdo quede a menos de una desviación estándar del máximo. Se definió después de ver Cora, así que en Cora no cuenta como evidencia.
- **A, corrección por atenuación:** el acuerdo dividido entre √(R_X · R_T). R_X es el ARI medio entre corridas de k-means con distintas semillas, y R_T el ARI medio entre corridas de Leiden con semillas 0–4. Es la corrección clásica para dos mediciones ruidosas (Spearman, 1904).
- **B, AMI:** el acuerdo medido con AMI en lugar de ARI.

Resultados:

| Grafo | Criterio | γ elegida (*k*) | ARI del *prior* | ¿Pasa? |
|---|---|---|---|---|
| Cora | Acuerdo original | 0.15 (6) | 0.314 | No |
| Cora | Regla de una desviación | 0.2 (8) | 0.424 | No cuenta |
| Cora | A: atenuación | 0.15 (6) | 0.314 | No |
| Cora | B: AMI | 0.7 (20) | 0.314 | No |
| Cora | γ = 0.3, la de la tesis | 0.3 (13) | 0.372 | — |
| Cora | Mejor posible, vista con etiquetas | 0.2 (8) | 0.424 | — |
| CiteSeer | Acuerdo original | 0.05 (5) | 0.284 | No |
| CiteSeer | Regla de una desviación | 0.05 (5) | 0.284 | No |
| CiteSeer | A: atenuación | 0.05 (5) | 0.284 | No |
| CiteSeer | B: AMI | 0.05 (5) | 0.284 | No |
| CiteSeer | γ = 0.3, la de la tesis | 0.3 (14) | 0.329 | — |
| CiteSeer | Mejor posible, vista con etiquetas | 0.15 (11) | 0.370 | — |

Lectura:
1. **El acuerdo original sí sigue al ARI.** La correlación de rangos entre el acuerdo y el ARI del *prior*, sobre las γ, es 0.92 en Cora y 0.78 en CiteSeer.
2. **Pero esa correlación viene casi toda de la tendencia de grueso a fino.** El acuerdo baja al subir γ, en buena parte porque el sensor de características se vuelve ruidoso con *k*: la estabilidad de k-means cae de 0.56 a 0.18 en Cora y de 0.52 a 0.10 en CiteSeer, mientras que la de Leiden queda entre 0.41 y 0.85.
3. **Al corregir ese ruido, no queda señal para distinguir γ cercanas.** Con A, la curva de CiteSeer queda casi plana (entre 0.30 y 0.38), y con B la curva es plana en ambos grafos. Los máximos son casi empates y caen en γ peores que 0.3.
4. **Hay margen, pero no se encontró sin etiquetas.** Con la γ óptima, el ARI del *prior* sería unos 0.04–0.05 mayor que con γ = 0.3.
5. **Observación lateral, con cautela:** en la componente gigante de CiteSeer, k-means esférico sobre X con *k* = 5 obtiene ARI = 0.389 frente a las etiquetas. No es comparable con el ARI de GCN-Leiden (0.315), que cubre todos los nodos, pero sugiere que la vista de características es fuerte en ese grafo.

Salvedades: son dos grafos, con una sola semilla de Leiden para la partición evaluada, y el ARI del *prior* es solo un sustituto del ARI de la GCN.

**Veredicto:** la Etapa 2 no funciona en su forma actual. Cora y CiteSeer ya se usaron para diseñar y descartar criterios. Cualquier criterio nuevo tendría que definirse antes de mirar datos y probarse solo en grafos no usados: PubMed, CS, Computers, Photo y WikiCS, con Actor como control negativo.

### 5.5 Evaluación sin fuga de etiquetas

Protocolo para cualquier versión futura del filtro:
- **Diseño:** decidir todo solo con grafos de diseño y congelarlo antes de la prueba.
- **Prueba:** grafos no usados, con el ARI del *checkpoint* de pérdida mínima (y el NMI junto con *k*), 5 semillas, frente al GCN-Leiden actual.
- **Ablación:** solo la Etapa 1 (todas las comunidades de la componente gigante con γ = 0.3) frente a la versión completa.
- **Análisis final:** ya congelado el criterio, revisar si el criterio y el ARI se mueven juntos.

### 5.6 Riesgos

- **Nada garantiza que un criterio sin etiquetas siga al ARI.** Con el acuerdo entre vistas, este riesgo se materializó (Sección 5.4).
- **Dos efectos mezclados:** si γ se elige por grafo, Q′_γ también cambia, y la ablación debe separar ambos efectos.
- **Límite de fondo:** un criterio de acuerdo encuentra la granularidad en la que topología y características coinciden. Si las clases etiquetadas son más finas o más gruesas que ese nivel, ningún criterio de ese tipo las encontrará.

### 5.7 Alternativas descartadas

- **Filtro aprendido con Q′:** aprendería a fragmentar (ver β = −0.5).
- **Ajustar β con las etiquetas:** equivale a ajustar sobre el conjunto de prueba.
- **Criterios solo topológicos,** como la γ de máxima verosimilitud de Newman (2016): eligen la granularidad de la topología, no la de las etiquetas.
- **Silueta en X:** no corrige por azar. Además, se señaló que tiende a premiar *k* pequeño en datos dispersos (no verificado).
- **Acuerdo entre vistas, con ARI, con corrección por atenuación o con AMI:** probado en la Sección 5.4; no supera a γ = 0.3.
- **Referencia fija de k-means**, es decir, que k-means elija su propio *k* por estabilidad y γ se elija por acuerdo con esa referencia: solo traslada el problema, porque la estabilidad de k-means también suele favorecer *k* pequeño. No se probó.
- **Estabilidad entre semillas:** es viable y no usa etiquetas, pero es más costosa. Sigue sin probar.

## 6. Memoria y telemetría

### 6.1 Por qué la memoria crece con n²

La implementación replica operación por operación el código de Wang, para lograr paridad bit a bit, y guarda matrices densas de n × n:
- **La adyacencia** (`gcn_leiden/datasets.py:105`). En Cora, el 99.86 % de sus entradas son ceros.
- **La matriz de modularidad B y sus temporales** (`gcn_leiden/loss.py:12–15`, llamada en `gcn_leiden/trainer.py:53`). Al construirla hay hasta 4 matrices n × n vivas, y B se queda en memoria todo el entrenamiento.
- **La normalización L2**, escrita como `torch.diag(1/‖z‖) @ z` (`gcn_leiden/model.py:61`). Crea una matriz diagonal n × n en cada pasada, más su gradiente en el *backward*.

En float32, cada matriz n × n ocupa 28 MiB en Cora, 1.45 GiB en PubMed y 4.4 GiB en Coauthor Physics.

Nada de eso hace falta. Basta un formato disperso en memoria (el que PyTorch Geometric ya usa en `edge_index`), no una base de datos externa. Con A dispersa, la identidad de la Sección 2.2 y la normalización fila por fila (`z / ‖z‖`), la memoria crece con el número de aristas y con n × k. El costo del cambio es perder la paridad bit a bit con Wang, así que habría que revalidar.

### 6.2 Por qué medimos RAM y VRAM, y Wang solo RAM

**Wang entrena en CPU.** Su código fija `device = torch.device('cpu')` (`main.py:101`); `cuda` solo se usa para la semilla. Su artículo reporta una máquina con Intel i9 y 128 GB de RAM, sin GPU. No publica mediciones de memoria, solo tiempos (Fig. 4).

**Nosotros repartimos los grafos entre dos tipos de máquina** (`experiments/deploy/launch_shards.sh:44–51`):

| Grupo | Grafos | Máquina | Dónde se entrena |
|---|---|---|---|
| CPU | Cora, CiteSeer, Photo, Actor, WikiCS y SBM | c2d-standard-8, según los registros de auditoría de GCP; el script dice n2-standard-8 | RAM |
| GPU | Computers, PubMed, CS y Physics | g2-standard-16 con una L4 | VRAM |

Los grafos grandes fueron a GPU porque las matrices densas de n × n los hacían lentos o enormes en CPU.

### 6.3 Qué midió la telemetría

Fuente: `experiments/harness/telemetry.py`.
- **`ram_peak_mb`:** el pico de memoria residente de todo el proceso (`ru_maxrss`). Cada corrida fue un subproceso propio, así que el pico es limpio.
- **`vram_peak_mb`:** `torch.cuda.max_memory_allocated`, es decir, solo los tensores de PyTorch en la GPU. No incluye el contexto de CUDA ni la caché reservada, así que el uso real de la GPU es mayor. En las corridas CPU vale NaN.

**La misma columna de RAM mide cosas distintas según el grupo:**
- **En CPU** incluye todo: la carga de datos, el grafo de networkx, el *prior* y el entrenamiento (A, B, la matriz diagonal y las activaciones).
- **En GPU** incluye solo la preparación: la adyacencia densa en numpy, que se crea en el host antes de copiarse a la GPU, el grafo de networkx y el *prior*. El entrenamiento aparece en la VRAM.

### 6.4 Cómo explicarlo

- **La memoria no era comparable entre grafos.** Los grupos CPU y GPU miden fases distintas, en máquinas distintas.
- **Tampoco hay contra qué comparar con Wang,** porque no publicó mediciones de memoria.
- **Por eso se quitó de la tesis.** En noviembre de 2026 se decidió eliminar la memoria de la tesis.
- **Lo único sólido es el diagnóstico estructural:** la memoria crece con n² por las matrices densas. Las mediciones de VRAM lo confirman: el pico de PubMed (6 154 MiB) y el de CS equivalen a unas 4 matrices n × n más lo demás (`docs/verificacion-tesis-2026-11-19/informes/04_metodo.md`).

## 7. Qué haría falta para pasar a la práctica

- **Corridas nuevas de la GCN** para Q′_γ y para la Etapa 1 del filtro. Cora y CiteSeer son baratos localmente. PubMed, CS, Computers y WikiCS son pesados con matrices densas y sin nube: requieren la forma dispersa (Sección 2.2) o una GPU.
- **Etapa 2 del filtro:** hace falta otro criterio sin etiquetas. Evaluar un criterio es barato (minutos por grafo, sin entrenar la GCN), pero los grafos de diseño ya se usaron.
- **Particiones finales.** `results/` solo guarda métricas (`runs_*.csv` y trayectorias con `epoch, loss, nmi, ari, q, dbi`). Medir P1 exige regenerarlas.
- **Verificación pendiente:** si las clases de referencia son conexas dentro de la componente gigante. Si no lo son, imponer conectividad podría costar ARI.
- **Destino:** si algo de esto pasa al artículo, debe entrar primero en la tesis, porque el artículo se regenera desde ella con `sync_paper.py`.

## 8. Fuentes y cómo verificar

- **Traag, Waltman y van Eck (2019).** *Sci. Rep.* 9:5233, DOI 10.1038/s41598-019-41695-z, e información suplementaria. Leídos completos.
- **Código de Wang et al.** (`github.com/wuanghoong/Less-is-More`, rama `master`): `main.py:51`, `main.py:101`, `main.py:133` y `DGI.py:80`. El artículo, en la versión de *Sci. Rep.*, se leyó completo.
- **networkx** (`louvain.py:285–311`) y **leidenalg** 0.12: docstring de `RBConfigurationVertexPartition`, `Optimiser.merge_nodes_constrained` y `CPMVertexPartition(node_sizes=…)`.
- **Datos.** Barrido de β en `results/runs_recal_cora.csv` y `results/runs_recal_citeseer.csv` (filas `gcn-leiden` con `modularity` y `resolution=0.3`). Tablas principales en `../gnn-paper/main.tex`.
- **Cálculos sin entrenamiento:**
  - Componentes, K₀, *k* y conectividad de las anclas: `gcn_leiden.prior` con la configuración de la tesis.
  - Particiones triviales: `sklearn.metrics`.
  - Identidades de Q′_γ y forma dispersa: verificadas numéricamente con autograd.
- **Newman (2016).** *Phys. Rev. E* 94, 052315. Localizado, no leído.
- **Prueba del criterio (Sección 5.4).** Desde la raíz del repo, con los datos en `datasets_pyg/`:
  - `uv run python docs/hallazgos/acuerdo_vistas.py cora` (y luego `citeseer`): acuerdo original, regla de una desviación y ARI de k-means frente a las etiquetas.
  - `uv run python docs/hallazgos/acuerdo_vistas_correcciones.py cora citeseer`: correcciones A y B, estabilidades R_X y R_T, y el veredicto frente a γ = 0.3.
  - Tardan unos minutos cada uno. Los resultados de k-means pueden variar ligeramente entre plataformas.
- **Referencias citadas sin verificar en esta sesión:** Spearman (1904), corrección por atenuación; Romano et al. (2016), sobre ARI frente a AMI; Dasgupta et al. (2001), co-training.
