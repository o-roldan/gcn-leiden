# Informe del verificador: Metodología, código y literatura (grupo M)

> Informe textual tal como lo entregó el verificador (effort xhigh), extraído de su transcripción. Las rutas `/private/tmp/...` apuntan al scratchpad de la sesión del 2026-11-19; los scripts y salidas que cita están copiados en `../evidencia/`.

## Grupo `metodo`: verificación (sin ediciones; scripts y salidas en `/private/tmp/claude-501/-Users-omar-Developer-me-gcn-leiden/ddebb875-fe4a-43f3-ab25-1ab06b6b4a1f/scratchpad/verify/metodo/`)

**Hallazgo principal.** `references.bib` cita la versión publicada de Wang et al.: *Sci. Rep.* 15:39249, DOI 10.1038/s41598-025-22860-z. En cambio, `SCRATCH/wang/wang.txt` es arXiv v1, y las dos versiones no dicen lo mismo. Descargué la versión publicada (Europe PMC, PMC12603060) en `.../metodo/wang_scirep/scirep_f.txt`. Ahí sí aparece un análisis de sensibilidad del coeficiente del filtro (ver M-01). Las demás afirmaciones sobre Wang las comprobé en ambas versiones.

### 1. Tabla

| id | archivo:línea | afirmación (≤15 palabras) | veredicto | por qué (≤1 línea) | evidencia (fuente exacta) |
|---|---|---|---|---|---|
| M-01 | propuesta_solucion.tex:171 | Wang fijan 0.5 "sin reportar un análisis de sensibilidad" | ❌ | La versión citada sí lo tiene: coeficiente de 0.1 a 1.0; lo mejor está entre 0.4 y 0.6. Solo arXiv v1 no lo trae. | scirep_f.txt:1631-1636 «Experiment 1: Sensitivity Analysis of the Threshold Filtering Mechanism… in the range of 0.4-0.6, most metrics achieve both superior and stable performance» |
| M-02 | propuesta_solucion.tex:644 | "las comparaciones se apoyan sobre todo en el ARI" | ❌ | En la tesis predomina el NMI: comparación controlada, tablas de recalibración y H1/H2. | En la prosa de resultados.tex (desde la l.123) hay 18 `$NMI` frente a 5 `$ARI`; l.158 compara solo en NMI; app0A tab:recal-* reporta solo NMI |
| M-03 | convergence.py:4-5 (code.patch) | "one row every eval_every = 2 epochs" | ❌ | La cadencia real es 2 en cora/citeseer/amap/film, 5 en amac/wikics y 10 en pubmed/cocs. | history_*/ (paso entre épocas); launch_shards.sh:44-51 (`pubmed:10 cocs:10 amac:5 wikics:5`) |
| M-04 | resultados.tex:165, 170, 187 (dependiente) | "registran Q' cada dos épocas" / "La evaluación se realiza cada dos épocas" | ❌ | Mismo hecho que M-03, que afecta a 4 de los 7 grafos de la Tabla de convergencia. | ídem M-03 (Coauthor CS 30.0±0.0 en ambos brazos refleja la rejilla de 10 épocas) |
| M-05 | convergence.py:12-14 | El objetivo fijo es "a level every run of both arms reaches" | ❌ | Falla con frac=0.99: en Cora, gcn-louvain s3 llega a Q'max 0.7526 < 0.7541, así que se descarta un par (n=34). Es cierto con 0.90 y 0.95. | metodo/conv_doc_check.py; salida del comando del README (`fixed target 0.99: n=34`) |
| M-06 | resumen.tex:9; abstract.tex:7 (también resultados:126 y conclusiones:59) | En Coauthor Physics "la matriz de modularidad densa excede la memoria de la GPU" | ⚠️ | El fallo está respaldado y el OOM es verosímil, pero no hay log. B sola ocupa 4.4 GiB; lo que se desborda es la suma de ~4-5 matrices n×n. | Ver la sección "Coauthor Physics" |
| M-07 | resumen.tex:9; abstract.tex:7 | La propuesta es competitiva "aunque no los supera" (a los modelos profundos) | ⚠️ | En los dos grafos de Amazon, ambas GCN superan en media a todos los modelos profundos. Contradice resultados:128 y conclusiones:38 ("iguala o supera… Amazon"). | runs_amac: GCN-Louvain 0.529/0.439 frente a DeepWalk 0.500/0.378; runs_amap: GCN-Leiden 0.649/0.485 frente a 0.630/0.461 (dentro de 1 de) |
| M-08 | resumen.tex:9; abstract.tex:7 | "con mayor estabilidad entre semillas que DGI" | ⚠️ | No ocurre en todos los grafos. En NMI la de GCN-Leiden es menor en 5 de 8; es mayor en PubMed (0.021 frente a 0.009) y en Amazon Photo (0.005 frente a 0.000, colapso de DGI). En ARI también es mayor en amac (0.091 frente a 0.083). | metodo/main_table.py (ddof=1, semillas 0-4) |
| M-09 | resumen.tex:3; abstract.tex:3 | "Los modelos profundos integran la topología y las características de los nodos" | ⚠️ | DeepWalk, que es un baseline, no usa atributos; la propia tabla de trabajos relacionados lo marca así. | deepwalk.py:23-67 (no usa `data.feat`); trabajos_relacionados.tex:137 ("No") |
| M-10 | propuesta_solucion.tex:148 | Traag: hasta 25% de comunidades mal conectadas y 16% desconectadas | ⚠️ | Las cifras son exactas, pero los máximos aparecen al *iterar* Louvain. En una sola ejecución (como en el prior), las desconectadas rondan el 1% (más del 5% en WoS). | traag2019.txt p.1 «up to 25%… up to 16%»; p.7 «The percentage of disconnected communities is more limited, usually around 1%… jumps to 16% for the DBLP» |
| M-11 | propuesta_solucion.tex:171 | "Leiden produce una distribución de tamaños distinta" | ⚠️ | Empíricamente casi igual: k0 difiere en ≤2 en 7 de 8 grafos reales (cora 89/90, citeseer 452/451, pubmed 14/16, cocs 13/13, amac 322/320, amap 143/143, wikics 359/360); solo Actor difiere (13/26). | metodo/cv_from_csv.py (config `k0`, `threshold`) |
| M-12 | propuesta_solucion.tex:646 | Las comparaciones internas reportan el pico "como el protocolo original" | ⚠️ | Aquí el pico se evalúa cada 2, 5 o 10 épocas según el grafo; Wang evalúa cada 2. Entre los dos brazos sí es simétrico. | main.py:181 (wang-code); launch_shards.sh:44-51 |
| M-13 | propuesta_solucion.tex:646 | El checkpoint de pérdida mínima "es decir, el de máxima Q'" | ⚠️ | Se guardan los parámetros *posteriores* al paso de optimización de la época con menor pérdida previa al paso: hay un desfase de un paso, igual en el código de Wang. | trainer.py:70-90; wang main.py:180-196 |
| M-14 | propuesta_solucion.tex:646 | "las trayectorias completas de entrenamiento se almacenan" | ⚠️ | Se muestrean cada 2, 5 o 10 épocas y solo para las variantes GCN. | trainer.py:81-85; runners/baseline.py (sin historial) |
| M-15 | chap01.tex:24-26 | Decidir un clique de tamaño k (k en la entrada) es NP-completo | ⚠️ | Correcto (Karp 1972), pero sin cita: Prosser2012 respalda otra cosa y no hay Karp ni Garey-Johnson en el .bib. | references.bib (grep karp/garey: 0) |
| M-16 | prior.py:77-82 (code.patch) | CV "<= 0.007" en SBM que recuperan los bloques | ⚠️ | Louvain en SBM-1k da CV = 0.00707. Además el docstring omite los priors CPM en SBM (1.37-1.76). La conclusión [0.01, 0.4] sigue siendo válida. | metodo/sbm_priors.py |
| M-17 | convergence.py:17-18 | Los empates son frecuentes "because of the 2-epoch evaluation grid" | ⚠️ | Los empates vienen sobre todo de las rejillas de 5 y 10 épocas. | ídem M-03 |
| M-18 | propuesta_solucion.tex:639 | Prior en grafos reales: modularidad γ=0.3, semilla 123, β=0.5, igual que el código original | ✅ | La config de todas las filas gcn de runs_* coincide con el código de Wang. | wang main.py:133,138; CSV config `resolution=0.3;prior_seed=123;beta=0.5;prior_objective=modularity` |
| M-19 | propuesta_solucion.tex:639 | En los SBM, γ=0.3 fusiona todos los bloques | ✅ | k0=1 con Louvain y Leiden en los 3 SBM. | metodo/sbm_priors.py; runs_sbm_* res 0.3 → k=1 |
| M-20 | propuesta_solucion.tex:639 | En SBM: modularidad γ=1.0; CPM γ=0.0275 solo para Leiden, punto medio de p_in/p_out | ✅ | (0.05+0.005)/2 = 0.0275. | recal.py:36-55; datasets.py:29; prior.py:42-43 |
| M-21 | propuesta_solucion.tex:639, 644 | Las heurísticas clásicas de las tablas se reportan con γ=1.0 | ✅ | Las celdas coinciden con las filas de resolution=1.0. | cora Louvain 0.452±0.010; SBM-10k 0.958 (runs_*.csv) |
| M-22 | propuesta_solucion.tex:644 | Los modelos profundos reciben el k de referencia; la propuesta lo estima del prior | ✅ | | deepwalk.py:63; dgi.py:74; dmon.py:43 (`k_source=ground_truth`); gcn.py:85-87 |
| M-23 | propuesta_solucion.tex:644 | Wang dan a sus baselines el k detectado por su método | ✅ | | wang.txt p.12 «set to the number of communities detected in this experiment»; scirep_f.txt:1430 (idéntico) |
| M-24 | propuesta_solucion.tex:644 | El NMI crece con el nº de clústeres; el ARI corrige el azar | ✅ | Correcto; ya está citado en la l.504 (Romano2016) y la l.511 (Hubert1985). Conviene una referencia cruzada. | propuesta_solucion.tex:504, 511-522 |
| M-25 | propuesta_solucion.tex:646; chap01.tex:142-143 | Wang publican una única ejecución por configuración | ✅ | Ni seeds ni ± en ninguna de las dos versiones; el Wilcoxon de Sci Rep empareja datasets, no corridas. | wang main.py:44,149-150; scirep_f.txt:1461-1467 |
| M-26 | propuesta_solucion.tex:646 | El código de Wang guarda cada 2 épocas el máximo por métrica (mínimo de DBI); el artículo publica ese pico | ✅ | | main.py:181-190, 215-223; tablas «Max NMI… Min DBI» (wang.txt p.13; scirep 11×"Max NMI") |
| M-27 | propuesta_solucion.tex:646 | Wang restaura el checkpoint de mínima pérdida y lo evalúa | ✅ | Ver el matiz de M-13. | main.py:192-206 |
| M-28 | propuesta_solucion.tex:646 | El pico usa las etiquetas y cada métrica puede salir de una época distinta | ✅ | | trainer.py:113-117; main.py:185-190 |
| M-29 | propuesta_solucion.tex:646 | La tesis conserva ambas vistas (columnas del CSV) | ✅ | `nmi/ari/q/dbi` = checkpoint de pérdida mínima; `peak_*` = pico. | gcn.py:111-115; trainer.py:97-99 |
| M-30 | propuesta_solucion.tex:646 | Las tablas entre métodos usan el checkpoint de pérdida mínima; prior-pico y recalibración usan el pico | ✅ | Comprobado celda a celda. | Cora GCN-Leiden nmi 0.530 (pico 0.554); SBM-1k 0.988 (pico 0.991); amac en tab:prior-pico 0.543/0.541 = `peak_nmi` |
| M-31 | propuesta_solucion.tex:646 | DeepWalk, DGI y DMoN se evalúan sin elegir épocas por etiqueta | ✅ | Usan el modelo final; DGI aplica early stopping por pérdida. | deepwalk.py:40-67; dgi.py:55-78; dmon.py:48-61 |
| M-32 | propuesta_solucion.tex:646 | Cinco semillas; la semilla controla pesos, caminatas y muestreo; un subproceso por corrida | ✅ | | gcn.py:77-78; deepwalk.py:25-27; dgi.py:33,42-43; sweep.py:84-87; CSV seeds 0-4 |
| M-33 | propuesta_solucion.tex:148, 150 | Louvain puede desconectar comunidades; Leiden garantiza conexidad, mejor calidad y menos tiempo | ✅ | | traag2019.txt p.1; p.5 «All communities are γ-connected»; p.6 «higher quality in less time… up to 20 times faster» |
| M-34 | propuesta_solucion.tex:185 | τ = 0.25 | ✅ | | prior.py:65,89; build_prior usa el valor por defecto |
| M-35 | propuesta_solucion.tex:637 (pedido) | El artículo dice ≥ T y el código usa > T | ✅ | Matiz: en Sci Rep la prosa también dice «exceeding this threshold». | wang.txt p.7; scirep_f.txt:601, 640; main.py:140 |
| M-36 | propuesta_solucion.tex:275 (pedido) | En el artículo exp(−δ·sim); en el código +δ | ✅ | | wang.txt p.8 Eq.9; scirep_f.txt:860; DGI.py:52 |
| M-37 | chap01.tex:52 | La mayoría de los modelos profundos requiere fijar k (cita Wang2025) | ✅ | | scirep_f.txt:12 «most current algorithms require predefining the number of communities» |
| M-38 | trabajos_relacionados.tex:116 | Según los autores: competitivo y más rápido que los profundos comparados | ✅ | El tiempo se comparó solo en 4 grafos pequeños. | wang.txt p.12 «best or runner-up»; p.15 / scirep_f.txt:1698 «fastest runtime» |
| M-39 | trabajos_relacionados.tex:158 | La implementación materializa B densa, con memoria O(n²) | ✅ | | wang main.py:50-54,126; loss.py:10-15; trainer.py:53 |
| M-40 | resumen.tex:9; abstract.tex:7 | 9 grafos reales en 4 dominios; propuesta en 8; SBM hasta 10 000; 5 semillas; 4 métricas; lista de métodos | ✅ | Hay filas gcn en 8 runs_*; 0 en cophysics. | results/runs_*.csv |
| M-41 | resumen.tex:7; abstract.tex:5 | Leiden define los centroides; el filtro conserva las comunidades más grandes | ✅ | | model.py:62-63; prior.py:84-91 |
| M-42 | resumen ↔ abstract | El Abstract dice lo mismo que el Resumen | ✅ | Equivalentes en todas las frases modificadas. | frontmatter/*.tex |
| M-43 | prior.py:77-82 | CV de 1.2 a 11.5 en grafos reales y de 0.41 a 0.45 en SBM-10k; cualquier τ en [0.01, 0.4] decide igual | ✅ | Real: 1.224-11.458; SBM-10k: 0.412/0.447 (k0 18 y 16); CPM ≥1.37. | metodo/cv_from_csv.py, sbm_priors.py |
| M-44 | experiments/README.md (+) | El comando de convergencia (P3) funciona y produce lo descrito | ✅ | Lo ejecuté con `--frozen`. | salida: Wilcoxon, t95, desalineación NMI-Q', filas LaTeX |
| M-45 | convergence.py:3-21, 37-40 | Q' = −loss/α (α=1e-3); emparejado por semilla; Wilcoxon descarta ceros; Actor excluido (k=1, Q'≈0) | ✅ | Matiz: `loss` se calcula antes del paso y `nmi` después (desfase de un paso). | trainer.py:70-85; model.py:44-54; runs_film gcn-leiden k=1, \|loss\|≤2.9e-9 |
| M-46 | chap01.tex:142-146 | Varias semillas; aísla el prior al cambiar solo Louvain↔Leiden | ✅ | Vale para los grafos reales. En SBM la comparación usa CPM y otro filtro, pero el texto lo declara. | full.py:50-55; config idéntico salvo `--prior` |
| M-47 | chap01.tex:130 y otros | Renumeración de objetivos coherente | ✅ | P1→Obj 4, P2→Obj 2, P3→Obj 4, P4→Obj 1 y 3; "segundo objetivo" en la l.171 = Obj 2. | conclusiones.tex:20-23 |
| M-48 | chap01.tex:150-152 | "una sola matriz de pesos que estima k" | ✅ | El `weight` 512×512 es un resto sin uso. | model.py:44-54 |
| M-49 | propuesta_solucion.tex:150 | La tesis no mide el efecto sobre los centroides, sino sobre la partición final | ✅ | | resultados.tex (solo NMI/ARI/Q/DBI) |
| M-50 | .bib | Traag2019 y Wang2025 existen y son correctas | ✅ | Wang2025 coincide con los metadatos de PMC (vol. 15, 39249). | references.bib:115-130, 180-192 |

### Coauthor Physics (todas las menciones: resumen.tex:9, abstract.tex:7, resultados.tex:126, conclusiones.tex:59 y 75)

**Evidencia de que las corridas fallaron:**
- `runs_cophysics.csv` tiene 35 filas: 5 semillas × (louvain×2, leiden×2, deepwalk, dgi, dmon). No hay ninguna fila gcn-*, aunque `full.py:34-35` las lanza.
- No existe `history_cophysics`; cada uno de los otros 8 grafos tiene 10 historiales.
- Por semilla, entre `dmon` y el siguiente `louvain` pasan unos 100 s, de los que unos 64-70 s corresponden a los dos intentos GCN. Cargar el grafo (~18 s) y construir el prior (5-16 s) ya explica ese tiempo, así que ambos murieron al empezar `train()`. Como referencia, en cocs cada corrida GCN dura ~70 s, de ellos 57 s de entrenamiento.

**Evidencia sobre la causa:**
- `launch_shards.sh:63` dice «(no cophysics: dense loss OOMs)». Se añadió en el commit a5a0092 (12-jun 13:15 UTC), después de las corridas (05:50-07:45 UTC). Es una afirmación del autor, no un log.
- `datasets.py:115-122` advierte que cada matriz n×n ocupa ~4.4 GiB.

**Estimación de memoria** (`vram_peak_mb` está en MiB = `max_memory_allocated/2^20`, telemetry.py:16-19):
- Para n=34 493, cada matriz n×n en float32 ocupa 4 538.6 MiB.
- En la GPU se crean: la adyacencia (trainer.py:50); en `modularity_matrix`, un clon, el producto ddᵀ, su copia escalada y B (pico de 4 n²; loss.py:12-15); la matriz diagonal `torch.diag(1/‖z‖)` (model.py:61) y su gradiente en el backward. Además: características (1 107 MiB), mensajes E×512 (1 036 MiB ×2, transitorios) y activaciones n×512 (67 MiB cada una).
- Calibración con datos medidos: pubmed 6 154.3 = 4n² + X + 4.8·(n×512); cocs 5 826.3 = 4n² + X + 6.2·(n×512); amac 3 557.5 ≈ 2n² + X + 2 mensajes.
- Extrapolado a Coauthor Physics: unos **19 600 MiB asignados (≈19.2 GiB)**, por debajo de los ~23 034 MiB de una L4.
- Con el asignador de caché por defecto, las activaciones parten uno de los bloques n×n liberados, y el gradiente de la matriz diagonal exige un 5.º segmento. La memoria reservada sería ≈5n² + X ≈ **23 800 MiB**, por encima de la capacidad: el OOM es verosímil.

**Conclusión:**
- Que no hay resultados GCN en Coauthor Physics está respaldado.
- Que la causa sea un OOM es verosímil y coherente con los artefactos, pero sin log local. Lo está buscando otro proceso.
- La causa tal como está redactada («la matriz de modularidad densa excede la memoria») queda contradicha por la aritmética: B sola ocupa 4.4 GiB, ~20 % de la L4. Lo que agota la memoria es el conjunto de ~4-5 matrices n×n densas.

### 2. Cobertura de números en líneas `+`
- **chap01:** "Objetivo 4" → M-47. No hay más números añadidos; los eliminados (34 493, 10 000) no cuentan.
- **propuesta:**
  - 25 %, 16 % → M-10.
  - 0.5 (l.171) → M-01.
  - β = 0.5 (l.171) es un parámetro de diseño, no una afirmación.
  - τ = 0.25 → M-34.
  - γ = 0.3, semilla 123, β = 0.5 → M-18.
  - γ = 1.0 en SBM → M-19 y M-20.
  - 0.0275 y "punto medio" → M-20.
  - γ = 1.0 de las heurísticas clásicas → M-21.
  - "siete métodos" → M-22 (contados en la propia frase: 2 + 3 + 2).
  - "cinco semillas" → M-32.
  - "cada dos épocas" (Wang) → M-26.
- **trabajos:** "(2025)" → M-38; "Media*" es una valoración, no una afirmación; O(n²) → M-39.
- **resumen y abstract:** nueve, cuatro dominios, 10 000, ocho, cinco semillas, cuatro métricas → M-40; 34 493 → M-06.
- **code.patch:**
  - 1.2-11.5, 0.41-0.45, [0.01, 0.4] → M-43; ≤ 0.007 → M-16.
  - "P3" → M-44.
  - eval_every = 2 → M-03; α = 1e-3 y k=1 → M-45; "2-epoch grid" → M-17.
  - Las constantes `fracs`, `DATASETS` y `range(5)` son código, no afirmaciones.

### 3. Correcciones mínimas propuestas
- **M-01:** "Wang et al. fijan el coeficiente en 0.5; su análisis de sensibilidad (coeficiente de 0.1 a 1.0, con particiones de Louvain) halla métricas superiores y estables entre 0.4 y 0.6 \cite{Wang2025}." Mantener el resto de la frase.
- **M-02:** Sustituir por "…las tablas reportan el $k$ de cada método y las comparaciones se dan en $NMI$ y $ARI$."
- **M-03 y M-17:** "one row every ``eval_every`` epochs (2: Cora/CiteSeer/Photo/Actor; 5: Computers/WikiCS; 10: PubMed/CS)"; "because of the coarse 2–10-epoch grid".
- **M-04:** "registran $Q'$ cada 2, 5 o 10 épocas según el grafo (10 en PubMed y Coauthor CS, 5 en Amazon Computers y WikiCS)". Ajustar igual el caption (l.170) y la l.187.
- **M-05:** "a level every run reaches for frac ≤ 0.95 (at 0.99 one Cora run falls short and its pair is dropped)".
- **M-06:** "…ya que en Coauthor Physics la implementación densa (adyacencia, matriz $\mathbf{B}$ y normalización diagonal, ~4.4 GiB cada una) agota la memoria de la GPU." Idealmente, citar el log de la nube.
- **M-07:** "…aunque en general no los supera (sí en los dos grafos de Amazon)…"
- **M-08:** "…y, a diferencia de DGI, sin colapsar en los grafos de Amazon" (o "con menor dispersión que DGI en la mayoría de los grafos").
- **M-09:** "Muchos modelos profundos, como las GNN, integran…" (EN: "Many deep models, such as GNNs, integrate…").
- **M-10:** Añadir "al iterar Louvain; en una sola ejecución las desconectadas suelen rondar el 1 %".
- **M-11:** "Leiden puede producir una distribución de tamaños distinta…"
- **M-12:** "…reportan el pico (evaluado cada 2, 5 o 10 épocas según el grafo; el original usa 2)…"
- **M-13:** Cambiar "es decir, el de máxima $Q'$" por "aproximadamente el de máxima $Q'$".
- **M-14:** "las trayectorias de entrenamiento de las variantes GCN, muestreadas cada 2-10 épocas".
- **M-15:** Añadir una cita a Karp (1972) o Garey y Johnson (1979).
- **M-16:** "≈0.007 (≤0.0071)" y añadir "1.4-1.8 on CPM SBM priors".

Fuera del diff pero relacionado con M-23: `experiments/baselines/__init__.py:6-9` y `deepwalk.py:6-7` dicen que dar el k de referencia "mirrors the protocol of Wang et al.". Eso contradice Wang p.12, que da a sus baselines el k detectado por su propio método.

### 4. No verificado
- Ningún log de la nube confirma el OOM en Coauthor Physics.
- La capacidad de la L4 la tomé del valor nominal (23 034 MiB), no la medí.
- No pude saber si se usó `c2d-standard-8` (propuesta:648, línea sin cambios): el script tiene `n2-standard-8` por defecto con posibilidad de sobrescribirlo, y no hay registro.
- No verifiqué la "paridad bit a bit" ni la estadística interna de `convergence.py`.
- Las cifras de Traag las tomé del preprint en `traag2019.txt` (fechado oct-2019), no del PDF de *Sci. Rep.*
