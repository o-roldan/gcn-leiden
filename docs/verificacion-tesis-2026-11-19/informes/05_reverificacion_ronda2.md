# Informe del verificador: Reverificación de las correcciones (grupo V)

> Informe textual tal como lo entregó el verificador (effort xhigh), extraído de su transcripción. Las rutas `/private/tmp/...` apuntan al scratchpad de la sesión del 2026-11-19; los scripts y salidas que cita están copiados en `../evidencia/`.

## Verificación ronda 2 (grupo `reverif`)

Alcance: tomé las líneas `+` y `-` del snapshot `thesis_round2.patch`, más `code_round2.patch` y el docstring de `convergence.py`. Cito las líneas según los archivos actuales. No evalué las frases sobre la causa de Coauthor Physics.

Encontré 2 ❌, 1 ❓ y 12 ⚠️. Los ❌ son el mismo error en la tesis y en el código: cambiar "como máximo 0.007" por "alrededor de 0.007" convirtió una cifra correcta en una incorrecta. La tesis compila sin referencias ni citas indefinidas.

Todos los recálculos usan las semillas 0–4, la media ± desviación estándar con ddof=1 y, para empates, el criterio de la tesis ("diferencia menor que la mayor de las dos desviaciones estándar"). Los scripts y salidas están en `/private/tmp/claude-501/-Users-omar-Developer-me-gcn-leiden/ddebb875-fe4a-43f3-ab25-1ab06b6b4a1f/scratchpad/verify/reverif/`: `stats*.py`, `conv.py`, `film.py`, `misc.py`, `prior_cv.py` y `cv_out.jsonl`.

Para los coeficientes de variación (CV) reconstruí los priors con el paquete del repo (`prior_seed=123`). El k0 coincide con el `config` de los CSV en todos los casos.

### 1. Tabla

| id | archivo:línea | afirmación (≤15 palabras) | veredicto | por qué (≤1 línea) | evidencia (fuente exacta) |
|---|---|---|---|---|---|
| V-01 | resultados.tex:219 | σ/μ "alrededor de 0.007" en SBM cuyos bloques recupera la modularidad | ❌ | Los CV son 0.0071 y 0.0045 en SBM-1k, y 0 y 0 en SBM-5k; el texto eliminado ("como máximo 0.007") era el correcto | `cv_out.jsonl` (detect_communities, modularity γ=1.0, seed 123): sbm_1000_5 louvain 0.0071, leiden 0.0045; sbm_5000_10 0.0 y 0.0 (k0=10, bloques de 500) |
| V-02 | gcn_leiden/prior.py:79-80 | "~0.007 on modularity SBM priors that recover every block" | ❌ | El mismo error que V-01 | ídem |
| V-03 | trabajos_relacionados.tex:44 | En LCCF y en la tesis, una heurística aporta un prior estructural | ❓ | No hay texto del artículo; solo el título en references.bib:196-204, que es coherente | references.bib:196-204 |
| V-04 | resultados.tex:128 | La GCN de una capa "no los supera en ninguno" | ⚠️ | Es cierto en NMI y ARI. En Q, GCN-Leiden supera al mejor modelo profundo en Cora, CiteSeer y PubMed, y la pregunta 4 y la hipótesis central incluyen Q | runs_{cora,citeseer,pubmed}.csv, columna `q`: Cora 0.770±0.007 vs DeepWalk 0.710±0.006; CiteSeer 0.779±0.009 vs DMoN 0.740±0.005; PubMed 0.659±0.007 vs DMoN 0.540±0.021 |
| V-05 | conclusiones.tex:23, :38 | Veredicto 4 "inferior en Cora, PubMed…"; "en ningún grafo los supera" | ⚠️ | Depende de la métrica (como V-04): en Q es superior en Cora y PubMed | ídem |
| V-06 | resumen.tex:9; abstract.tex:7 | "no los supera en ninguno" / "outperforms them on none" | ⚠️ | Como V-04 | ídem |
| V-07 | conclusiones.tex:32, :48 | β=0.5 es el mejor de los valores probados (en Cora, empatado con 0.25) | ⚠️ | Solo por media de NMI pico. Con el criterio de empate de la tesis, β=0 empata en Cora y β=0.25 en CiteSeer. En ARI, β=0 tiene media ≥ que 0.5 en Cora con ambas vistas | runs_recal_cora/citeseer.csv. NMI pico Cora Leiden: β=0 0.548±0.008 vs β=0.5 0.554±0.009; CiteSeer Louvain: 0.392±0.011 vs 0.401±0.008. ARI pico Cora Leiden: β=0 0.500 vs 0.492; ARI con pérdida mínima: 0.448 vs 0.442 |
| V-08 | resultados.tex:158 | Cora "+0.013" de NMI pico | ⚠️ | Sin redondear la diferencia es +0.0125, que redondea a 0.012. Amazon Photo sí usa la diferencia sin redondear (+0.005, cuando la tabla daría 0.004), así que la convención es incoherente | runs_cora.csv, `peak_nmi`: 0.55360 − 0.54112 |
| V-09 | resultados.tex:126 | Amazon Photo: las heurísticas clásicas superan a todos los entrenables | ⚠️ | Cierto por media. Con el criterio de empate, DeepWalk empata con ambas heurísticas en NMI (en ARI sí pierde) | runs_amap.csv: Louvain 0.659±0.003 y Leiden 0.655±0.005 vs DeepWalk 0.630±0.031 |
| V-10 | resultados.tex:126 | WikiCS: "solo DeepWalk las iguala" | ⚠️ | Cierto en NMI. En ARI, DeepWalk empata con Louvain pero Leiden clásico la supera (0.0112 > 0.0092) | runs_wikics.csv: ARI Leiden 0.415±0.009, DeepWalk 0.404±0.009, Louvain 0.406±0.015 |
| V-11 | resultados.tex:126 | Amazon Computers: a menos de 1 desviación estándar de Leiden clásico en NMI | ⚠️ | Cierto pero incompleto: Louvain clásico (0.519) y GCN-Leiden (0.503±0.072) también quedan dentro de esa desviación en NMI | runs_amac.csv |
| V-12 | resultados.tex:58 | Leyenda de la Tabla 2: "Negritas: mejor valor por fila" | ⚠️ | Texto sin modificar que depende del cambio: las filas de DBI ya no llevan negrita, lo que contradice una lectura literal. Debería remitir a la regla de la Tabla 1 | resultados.tex:58 vs :15, :68-86 |
| V-13 | propuesta_solucion.tex:646 | Evaluación cada 2, 5 o 10 épocas (lista solo AmaC, WikiCS, PubMed, CoCS) | ⚠️ | Omite los SBM (5 en SBM-1k/5k y 10 en SBM-10k), cuyo NMI pico se reporta en tab:recal-sbm | history_validate_sbm_*, history_recal_sbm_*; launch_shards.sh:60-64 |
| V-14 | resultados.tex:187 | Muchos empates, "sobre todo" en grafos evaluados cada 5 o 10 épocas | ⚠️ | Apoyo débil: 13/20 pares (65 %) frente a 8/15 (53 %). Amazon Photo (cada 2) empata 5/5 y WikiCS (cada 5) 0/5 | `conv.py` (umbral del 95 %): empates por grafo amac 5, amap 5, cocs 5, pubmed 3, cora 2, citeseer 1, wikics 0 |
| V-15 | resultados.tex:95 | "CPM con γ=(p_in+p_out)/2 y β=0.5, tomado del generador" | ⚠️ | Redacción ambigua: solo γ se toma del generador, no β | runs_recal_sbm_*.csv `config` |
| V-16 | resultados.tex:204 | GCN-Leiden: ARI 0.378→0.442 (Cora), 0.146→0.315 (CiteSeer); NMI 0.530→0.530, 0.352→0.338 | ✅ | Coincide al redondear | runs_recal_{cora,citeseer}.csv, gcn-leiden, columnas `ari`/`nmi`, β −0.5 vs 0.5: 0.3784→0.4423; 0.1461→0.3148; 0.5297→0.5296; 0.3518→0.3378 |
| V-17 | resultados.tex:204; conclusiones.tex:21, :32; chap01.tex:96 | H2 en ARI: filtrar eleva el ARI con ambos priors y ambas vistas | ✅ | Las 8 combinaciones suben y las diferencias superan la desviación estándar. GCN-Louvain sube "de forma similar" | Con pérdida mínima, Louvain: Cora 0.332→0.424, CiteSeer 0.172→0.318. ARI pico, Louvain/Leiden: Cora 0.372/0.413→0.480/0.492; CiteSeer 0.236/0.239→0.391/0.375 |
| V-18 | resultados.tex:204 | Sin filtro el prior conserva ~90 (Cora) y ~450 (CiteSeer) comunidades | ✅ | k = 89/90 y 452/451 con β=−0.5 | runs_recal_*.csv, columna `k` |
| V-19 | resultados.tex:204 | β=0.5 da el mejor NMI para Leiden (Cora empatado con 0.25); el NMI pico cae con β=−0.5 | ✅ | Por media; las corridas de Cora con β=0.25 y β=0.5 son idénticas (mismo k) | tab:recal-beta recalculada |
| V-20 | resultados.tex:204, :158 | Leiden tiene mayor media en Cora con los 4 β (con β=0, <1 DE); ventaja de Louvain en CiteSeer solo con β≥0.25 | ✅ | Cora con β=0: diferencia 0.011 < 0.014. CiteSeer con β=0.25: 0.0132 > 0.0119 | runs_recal_*.csv, `peak_nmi` |
| V-21 | conclusiones.tex:32 | SBM-10k: el ARI de GCN-Leiden baja de 0.787 a 0.182 | ✅ | Coincide con ambas vistas (aunque el ARI no aparece en tab:recal-sbm) | runs_recal_sbm_10000_20.csv, leiden modularity γ=1, β −0.5→0.5: 0.7869→0.1823 |
| V-22 | conclusiones.tex:21, :32, :62 | Actor sin señal en ninguna configuración; el barrido de β cubre Cora, CiteSeer y Actor | ✅ | Todas las medias de NMI y ARI (pico y pérdida mínima) son ≤0.009 | runs_recal_film.csv (16 configuraciones) |
| V-23 | resultados.tex:95 | Sin filtro condicionado: SBM-5k no ejecutable; SBM-1k conserva 2 de 5 bloques; ambos filtros coinciden con CPM | ✅ | Con el filtro original, SBM-5k queda en 0 comunidades (RuntimeError) y SBM-1k en 2 con β=0.5; con CPM ambos filtros dan el mismo k | `cv_out.jsonl`; prior.py:100-103 |
| V-24 | resultados.tex:219 | CV 1.2–11.5 (reales), 1.4–1.8 (CPM), 0.41–0.45 (SBM-10k); τ∈[0.01, 0.4]; SBM-1k conserva 5 bloques en lugar de 2 o 3 | ✅ | Reales 1.22–11.46; CPM 1.37–1.76; SBM-10k 0.412/0.447; validación k=5 frente a 2 (β≥0) o 3 (β=−0.5) | `cv_out.jsonl`; runs_validate_sbm_1000_5.csv |
| V-25 | prior.py:77-83 | Los mismos rangos de CV y el intervalo [0.01, 0.4] | ✅ | Salvo "~0.007" (V-02) | ídem |
| V-26 | resultados.tex:15; tablas | k en las columnas GCN = anclas tras el filtro; negritas = mejor media sin redondear en NMI, ARI y Q; DBI sin negrita | ✅ | Las 3 tablas cumplen la regla (incluidos los empates exactos en SBM). Los valores de DBI coinciden | gcn.py:109 (`k=prior.k`); prior.py:33-35; `stats3.py` sobre runs_*.csv, runs_validate_sbm_*, runs_recal_sbm_* (cpm, β=0.5) |
| V-27 | resultados.tex:126 | Cora: GCN-Leiden es segunda, a <1 DE de GCN-Louvain; 0.530±0.008 y 0.442±0.015 frente a DGI | ✅ | Cierto solo con la desviación mayor (la de Louvain): NMI 0.008 < 0.028; ARI 0.019 < 0.068 | runs_cora.csv |
| V-28 | resultados.tex:126 | Coauthor CS: DGI supera en NMI y ARI (ARI <1 DE); DMoN solo en NMI | ✅ | NMI 0.693±0.059 vs 0.623/0.617; ARI 0.547±0.087 vs 0.494/0.493; DMoN NMI 0.663±0.012, ARI 0.450 | runs_cocs.csv |
| V-29 | resultados.tex:126 | AmaC: GCN-Louvain mejor media (0.529±0.016 / 0.439±0.013); GCN ≈ DGI y DMoN en SBM-1k/5k | ✅ | Coincide | runs_amac.csv; Tabla 3 recalculada |
| V-30 | resultados.tex:128 | Frente al mejor profundo: empata en CiteSeer, AmaC y AmaP; debajo en Cora, PubMed y WikiCS; CoCS debajo en NMI y empate en ARI | ✅ | Recalculado celda a celda en NMI y ARI | `stats3.py` |
| V-31 | resultados.tex:128 | DGI colapsa 4/5 en AmaC y 5/5 en AmaP; una semilla de GCN-Leiden en AmaC da 0.374 frente a ≈0.535 | ✅ | DGI AmaC [0.315, 0.039, 0.038, 0.038, 0.039]; AmaP ≈0.061 ×5; GCN-Leiden seed 2 0.374, el resto 0.530–0.538 | `misc.py` |
| V-32 | resultados.tex:158; conclusiones.tex:29 | Pico NMI: gana en Cora (4/5) y PubMed, AmaP +0.005, empata CoCS/AmaC, pierde CiteSeer/WikiCS; ARI Cora/CiteSeer <1 DE; Actor Louvain 0.007 | ✅ | PubMed +0.0219 > 0.0144; AmaP +0.0049 > 0.0026; CiteSeer −0.0131 > 0.0120; ARI 0.0126 < 0.0216 y 0.0156 < 0.0205 | `stats4.py` |
| V-33 | resultados.tex:133, :138, :165, :170; convergence.py:4-6 | Rejilla: cada 2 en Cora/CiteSeer/AmaP/Actor, 5 en AmaC/WikiCS, 10 en PubMed/CoCS; Q'_0 es la primera evaluación | ✅ | Coincide con las trayectorias y con launch_shards.sh | launch_shards.sh:44-56; history_*/ (primera época 2/5/10) |
| V-34 | resultados.tex:187 | Pares 3/11/21 con p=0.009; sin WikiCS p>0.1; al 99 % p=0.66 excluyendo un par de Cora; relativa p=0.053; Q'_0 p=0.99 y Q'max p=0.92 | ✅ | p=0.0088; sin WikiCS 0.167; al 99 % n=34 (falta gcn-louvain cora seed 3), p=0.659; 0.0532; 0.994 / 0.916 | `conv.py` (scipy wilcoxon por defecto) |
| V-35 | resultados.tex:187 | Q'max de Leiden mayor en Cora y menor en CiteSeer en las 5 semillas; k distinto solo en Cora/PubMed; Q'max después de la época 225; semillas con el mismo prior | ✅ | Diferencias Cora +0.0008…+0.0148, CiteSeer −0.014…−0.028; k 9/10 y 4/5; épocas 273, 226 y 250.5; k0 constante con prior_seed 123 | `conv.py`; runs_*.csv |
| V-36 | convergence.py:1-30 | Definiciones (α=1e-3, objetivo fijo, todas alcanzan con frac≤0.95, n=34 al 99 %, ceros descartados) | ✅ | Coinciden con el código y con mi recálculo | convergence.py:41-88; loss.py:18-22; trainer.py:25 |
| V-37 | propuesta_solucion.tex:646 | Checkpoint = estado tras el paso de optimización de la época de máxima Q'; Wang evalúa cada 2 épocas; solo hay trayectorias de las GCN | ✅ | Coincide con el código de la tesis y con el de Wang | trainer.py:70-90; wang-code/main.py:179-196; gcn.py:120 |
| V-38 | propuesta_solucion.tex:639 | SBM: modularidad γ=1.0 y CPM γ=0.0275 (solo Leiden), ambos con β=0.5 | ✅ | Coincide | `config` de runs_validate_sbm_* y runs_recal_sbm_* |
| V-39 | propuesta_solucion.tex:644; baselines/__init__.py:6-9; deepwalk.py:6-7 | Wang da a sus baselines el k detectado por su método; aquí reciben el k de referencia | ✅ | Sci Rep: "set to the number of communities detected in this experiment". Es correcto quitar el "protocol of Wang" | scirep_f.txt:1430; deepwalk.py:63, dgi.py:74, dmon.py:43 |
| V-40 | propuesta_solucion.tex:171 | Wang varía el coeficiente de 0.1 a 1.0 sobre Louvain, mejor entre 0.4 y 0.6, fija 0.5 | ✅ | Matiz: solo midió Q, ACC y F1 en Acm, Amap, Uat y Cocs ("most metrics achieve both superior and stable performance") | scirep_f.txt:1631-1636 |
| V-41 | propuesta_solucion.tex:148 | Traag: hasta 25 % mal conectadas y 16 % desconectadas al iterar; ~1 % en la primera iteración | ✅ | "usually around 1%" (con la excepción de Web of Science, >5 %); 16 % en DBLP iterando; 25 % en Amazon tras 4 iteraciones | traag2019.txt p.7 (líneas 606-637) |
| V-42 | conclusiones.tex:35, :38 | H3 "en general las mismas épocas, más en WikiCS"; las heurísticas "superan o igualan" en AmaP/WikiCS; k distinto en casi todos; sin colapsos de DGI | ✅ | Coherente con V-30–V-35 | ídem |
| V-43 | conclusiones.tex:75 | Además de B, hay adyacencia densa y normalización con matriz diagonal densa | ✅ | Solo los hechos del código | datasets.py `_from_pyg`; model.py:61; loss.py:10-15 |
| V-44 | trabajos_relacionados.tex:73 | TGAT, TGN y EvolveGCN modelan grafos con aristas que cambian en el tiempo | ✅ | Coincide con los títulos; quitar "componente recurrente" fue correcto | references.bib:510, 518, 526 |
| V-45 | resumen.tex:4; abstract.tex:3 | "Muchos / Many" modelos profundos integran topología y atributos | ✅ | Matiza sin afirmar nada nuevo | — |
| V-46 | compilación | La tesis compila sin referencias indefinidas | ✅ | Salida 0; 0 "Citation/Reference undefined"; 0 "LaTeX Warning"; ningún archivo creado en el repo | build/thesis.log |

### 2. Cobertura de números en líneas `+`
- **chap01 y conclusiones:** β=0.5, 0.25 y −0.5 → V-07, V-17; 0.787 y 0.182 → V-21; el resto de las líneas no tiene números.
- **propuesta_solucion.tex:**
  - 25 %, 16 % y 1 % → V-41.
  - 0.1, 1.0, 0.4, 0.6 y 0.5 → V-40.
  - γ 0.3, 1.0 y 0.0275, semilla 123, β 0.5 → V-38.
  - "siete" métodos, γ 1.0 y cinco semillas: no son afirmaciones nuevas.
  - 2, 5 y 10 → V-13, V-33.
- **resultados.tex:**
  - Leyenda de la Tabla 1 → V-26.
  - Celdas DBI de las 3 tablas → V-26 (sin cambio de valor; recalculadas).
  - Leyenda SBM: 0.05, 0.005, γ 1.0, β 0.5, "2 de 5" → V-23, V-15.
  - Línea 126 → V-27, V-28, V-29, V-09–V-11. Los 34 493 nodos y los 24 GB quedan fuera de alcance.
  - Línea 128 → V-30, V-31. Los k (10/7, 11/6, 4/15, 5/10, 4/10) y 0.328/0.091/≈470 coinciden con runs_*.csv.
  - Líneas 133, 138, 165 y 170 → V-33.
  - Línea 158 → V-32, V-08, V-20.
  - Línea 187 → V-34, V-35, V-14 (225 y 300 → V-35).
  - Línea 204 → V-16–V-20.
  - Línea 219 → V-24, V-01.
- **Código:** prior.py → V-02, V-25. convergence.py (2/5/10, α 1e-3, 0.95, 0.99, n=34, seed 3) → V-33, V-36.

### 3. Correcciones mínimas propuestas
- **V-01:** "como máximo 0.007 (0 en SBM-5k)".
- **V-02:** "≤0.007 (0 on SBM-5k)".
- **V-03:** citar una frase textual de Tokala et al. que lo respalde, o suavizar la frase.
- **V-04, V-05, V-06:** añadir "en NMI y ARI" y, si se quiere, "(en Q la supera en Cora, CiteSeer y PubMed)". En el veredicto 4: "inferior en NMI/ARI en …".
- **V-07:** "β=0.5 obtiene la mayor media de NMI pico (empatado con 0.25 en Cora); las diferencias con β=0 (Cora) y β=0.25 (CiteSeer) son menores que una desviación estándar".
- **V-08:** "+0.012", o bien usar la diferencia de los valores redondeados en todos los grafos (AmaP +0.004).
- **V-09:** "superan en media…; en NMI, DeepWalk queda dentro de una desviación estándar".
- **V-10:** "en WikiCS, DeepWalk las iguala en NMI y a Louvain en ARI".
- **V-11:** "…de Louvain y Leiden clásicos y de GCN-Leiden en NMI, y de GCN-Leiden en ARI".
- **V-12:** sustituir por "Negritas: como en la Tabla 1".
- **V-13:** añadir "y en los SBM, 5 (SBM-1k y SBM-5k) y 10 (SBM-10k)".
- **V-14:** suprimir "sobre todo en los grafos evaluados cada 5 o 10 épocas".
- **V-15:** "CPM con β=0.5 y γ=(p_in+p_out)/2, tomado del generador".

### 4. No verificado
- El contenido de Tokala et al. 2026: no hay fuente en los artefactos.
- El CV del prior de Coauthor Physics: no lo calculé porque no hay corridas GCN ahí.
- La Figura 2 de Wang (Sci Rep): solo verifiqué el texto, no la figura.
- La regla de negritas "sin redondear" la comprobé con la precisión de 4 decimales de los CSV.
