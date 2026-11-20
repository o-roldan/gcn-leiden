# Informe del verificador: Consistencia global (grupo C)

> Informe textual tal como lo entregó el verificador (effort xhigh), extraído de su transcripción. Las rutas `/private/tmp/...` apuntan al scratchpad de la sesión del 2026-11-19; los scripts y salidas que cita están copiados en `../evidencia/`.

## Informe del grupo `consistencia` (C-xx)

Revisé la consistencia interna de la tesis en HEAD (25b1c32) frente a `b44f221`, sin entrar en `chapters/marco_teorico/`. No modifiqué nada: el repo de la tesis no tiene cambios nuevos (`thesis.pdf` ya aparecía como modificado antes de empezar). Mis scripts y compilaciones están en `/private/tmp/claude-501/-Users-omar-Developer-me-gcn-leiden/ddebb875-fe4a-43f3-ab25-1ab06b6b4a1f/scratchpad/verify/consistencia/` (`build/`, `basebuild/`, `boxes.py`, `h1.py`, `h2.py`, `k0.py`).

Los hallazgos principales son cuatro contradicciones internas (C-01 a C-04) y un problema de fondo en H2 (C-05): su veredicto cambia según la vista de reporte.

### 1. Tabla

| id | archivo:línea | afirmación (≤15 palabras) | veredicto | por qué (≤1 línea) | evidencia (fuente exacta) |
|---|---|---|---|---|---|
| C-01 | trabajos_relacionados.tex:73 | "choca con el objetivo de un bloque ligero y de bajo consumo de VRAM" | ❌ | Queda de la pregunta y el objetivo de memoria que se eliminaron. Contradice que la implementación sea O(n²) y que falle en Physics | chap01.tex:103-133 (ya no hay objetivo de memoria); trabajos_relacionados.tex:158 (O(n²)); resultados.tex:126 (Physics no completa) |
| C-02 | conclusiones.tex:62 | "El barrido de β en grafos reales cubre solo Cora y CiteSeer" | ❌ | La propia tesis también barre β en Actor | resultados.tex:214 ("barrido completo sobre γ∈{0.3,1.0} y β"); `runs_recal_film.csv` (β∈{−0.5,0,0.25,0.5} × γ∈{0.3,1.0}, semillas 0–4); app0A.tex:99 llama "completas" a mallas que no incluyen Actor |
| C-03 | resultados.tex:219 | "En SBM-1k y SBM-5k, las corridas antes imposibles ahora se completan" | ❌ | Con el filtro original, SBM-1k sí se completa (k=2–3). Solo SBM-5k era imposible | resultados.tex:209 ("en SBM-1k solo sobreviven 2–3"); app0A.tex:132-139 (Louvain/Leiden modularidad: NMI 0.58, k=2); `runs_recal_sbm_1000_5.csv` |
| C-04 | resultados.tex:95 (leyenda Tabla 5.3) | GCN-Louvain sin filtro condicionado: "estas corridas no son ejecutables" | ❌ | Es falso para SBM-1k (k=2) y SBM-10k (k=1, sí corre) | app0A.tex:136-139 y 154-157; `runs_recal_sbm_10000_20.csv` (gcn-louvain modularidad, β≥0: k=1, 5 filas) |
| C-05 | chap01.tex:96-98 ↔ conclusiones.tex:21,32 | H2: el filtro "mejora el NMI de la partición final"; aceptada en Cora/CiteSeer | ⚠️ | Se evalúa con el NMI **pico**. Con el checkpoint (la partición final), en CiteSeer el filtro **baja** el NMI y en Cora-Leiden lo deja igual | app0A.tex:104 (NMI pico); propuesta:646 (el checkpoint es la partición sin etiquetas); `runs_recal_{cora,citeseer}.csv`, columna `nmi`, semillas 0–4: CiteSeer Leiden β=−0.5 0.352 → β=0.5 0.338; Louvain 0.357 → 0.342; Cora Leiden 0.530 → 0.530 |
| C-06 | propuesta_solucion.tex:644 | "las comparaciones se apoyan sobre todo en el ARI" | ⚠️ | No se cumple: la comparación de priors, la recalibración y H2 usan solo NMI | resultados.tex:158 ("+0.013 de NMI"), 204; conclusiones.tex:29,32; chap01.tex:96; las Tablas A.2 y A.3 solo reportan NMI |
| C-07 | resultados.tex:158; conclusiones.tex:29 | "Leiden gana en Cora" (P1/H1 se definen en NMI **y** ARI) | ⚠️ | Solo se cumple en NMI pico. En ARI pico la diferencia es menor a 1 sd (empate) | Tabla 5.4 (resultados.tex:146): ARI 0.480±0.022 vs 0.492±0.020; chap01.tex:69-71, 94-95 |
| C-08 | resultados.tex:158, 204 | Regla "empate si diferencia < 1 sd"; Actor "pierde"; Cora gana "en los cuatro β" | ⚠️ | La regla no dice qué sd usar. Actor (NMI 0.0071 frente a sd 0.0073) y Cora con β=0 (0.011 frente a sd 0.014) quedarían en empate | `runs_film.csv`, `runs_recal_cora.csv` (columna `peak_nmi`, semillas 0–4) |
| C-09 | conclusiones.tex:38; resultados.tex:128 | GCN "queda por debajo de DGI en CiteSeer, PubMed y Coauthor CS" | ⚠️ | Falta WikiCS, donde DeepWalk supera a GCN-Leiden en NMI y en ARI | Tabla 5.2 (WikiCS): DeepWalk 0.466/0.404 vs GCN-Leiden 0.401/0.357 |
| C-10 | conclusiones.tex:38 | "Es comparable, pero no superior, por lo que … se acepta parcialmente" | ⚠️ | No se sigue: la hipótesis afirma "comparable", no "superior", así que este argumento justificaría aceptarla completa | chap01.tex:85-90; tabla de veredictos, conclusiones.tex:23 |
| C-11 | resumen.tex:9; abstract.tex:7; conclusiones.tex:38; resultados.tex:128 | "mayor estabilidad entre semillas que DGI" | ⚠️ | La desviación estándar de DGI es menor en PubMed, Amazon Photo y en el ARI de Amazon Computers. Lo que le pasa a DGI es colapso (medias bajas), no varianza | Tabla 5.1 PubMed: 0.009 vs 0.021. Tabla 5.2 Photo: 0.000 vs 0.005; Amazon Computers ARI: 0.083 vs 0.091 |
| C-12 | resumen.tex:9; abstract.tex:7; resultados.tex:126; conclusiones.tex:59,75 | En Physics, "la matriz de modularidad densa excede la memoria de la GPU" | ⚠️ | Una sola **B** en float32 ocupa unos 4.4 GiB, menos que 24 GB. El código también deja densa la adyacencia en la GPU. El texto anterior hablaba de "las matrices densas". Sin la telemetría no queda evidencia del OOM | gcn_leiden/datasets.py:104-107, 115-121 ("the pipeline allocates several"); trainer.py:50,53; loss.py:12; `runs_cophysics.csv` sin filas GCN |
| C-13 | trabajos_relacionados.tex:44 | Esta tesis comparte el principio: el prior "reduce el costo de los modelos de aprendizaje" | ⚠️ | Ya no hay ningún resultado de costo, y GCN no completa Physics, que DGI/DMoN sí completan | resultados.tex:126; Tabla 5.1 (Physics) |
| C-14 | conclusiones.tex:35 | Leiden "requiere las mismas épocas que Louvain o … más" | ⚠️ | Leiden llega antes en 3 pares; en Cora llega antes en promedio | resultados.tex:187 ("antes en 3 pares"); Tabla 5.5 Cora: 63.2 vs 64.8 |
| C-15 | conclusiones.tex:32,48; resultados.tex:204 | "β = 0.5 es el mejor de los valores probados" | ⚠️ | En Cora empata exactamente con β=0.25 (las dos en negrita) | app0A.tex:110-111 |
| C-16 | conclusiones.tex:21,32 | H2 "se acepta cuando la distribución de tamaños es sesgada" | ⚠️ | Actor también tiene tamaños sesgados y ahí el filtro deja el prior de Leiden con k=1 (la propia tesis lo llama "fallo del filtro") | resultados.tex:194; `runs_recal_film.csv` (Leiden γ=0.3: k0=26 → k=1) |
| C-17 | resultados.tex:15 (leyenda de las Tablas 5.1–5.3) | El DBI "solo es comparable dentro de un mismo método" + "Negritas: mejor valor por fila" | ⚠️ | Las filas de DBI marcan en negrita un "mejor" entre métodos distintos | resultados.tex:25, 31, 74, 103 (negritas en DBI) |
| C-18 | resultados.tex:126 | "En Coauthor CS, DGI y DMoN superan a ambas variantes GCN" | ⚠️ | Solo es cierto en NMI. En ARI, DMoN queda por debajo de las dos variantes | Tabla 5.1 CS, ARI: DMoN 0.450 vs GCN 0.493/0.494 |
| C-19 | resultados.tex:126 | En WikiCS, "las heurísticas clásicas superan a todos los métodos entrenables" | ⚠️ | En NMI, Louvain 0.459 < DeepWalk 0.466, y Leiden 0.467 empata | Tabla 5.2 WikiCS |
| C-20 | resultados.tex:128 | "Su ventaja está en la estabilidad frente al método contrastivo" | ⚠️ | Por la sintaxis, "Su" se refiere a las heurísticas clásicas (frase anterior), pero el sentido es GCN. Cambia de quién es la afirmación | resultados.tex:128 (frase previa: "Las heurísticas clásicas producen…") |
| C-21 | resumen.tex:5; abstract.tex:3 | "Los modelos neuronales profundos integran la topología y las características" | ⚠️ | DeepWalk, uno de los tres baselines profundos, no usa características | trabajos_relacionados.tex:89, 137 ("Integra caract.: No") |
| C-22 | conclusiones.tex:22-23 | Compilación: advertencia de caja nueva | ⚠️ | Única advertencia nueva respecto de b44f221: Underfull \hbox (badness 1910) en la fila H3 de tab:veredictos. Es cosmética | build/thesis.log vs basebuild/thesis.log (36 vs 35; el resto coincide) |
| C-23 | toda la tesis | Compilación sin referencias ni citas indefinidas, etiquetas duplicadas ni errores | ✅ | 0 "undefined"/"multiply defined"; BibTeX con 0 advertencias; 41 avisos de hyperref, igual que en la base | build/thesis.log, thesis.blg; `latexmk -outdir` en ambas compilaciones |
| C-24 | todas las `\ref` añadidas | Las referencias cruzadas apuntan al contenido que describe la frase | ✅ | Comprobé 28 etiquetas usadas en texto nuevo. Las eliminadas (subsec:analisis-telemetria, tab:telemetria-memoria) ya no se citan | build/thesis.aux: p. ej. tab:prior-pico=5.4, tab:convergencia-prior=5.5, tab:recal-beta=A.2, tab:recal-sbm=A.3, subsec:recal-validacion=5.2.4, def:cpm=Def. 20 |
| C-25 | chap01.tex:68-133 ↔ conclusiones.tex:20-38; resultados.tex:128,133,165; propuesta:171 | Correspondencia P1–P4 / H1–H3 + central / O1–O4 | ✅ | Coinciden la tabla de veredictos, los párrafos 1–4, "primera/tercera/cuarta pregunta" y "segundo objetivo". No queda ninguna mención a una P5 o un O5 | chap01.tex (enumeraciones); conclusiones.tex:20-23. Nota: las etiquetas "H1–H3" no aparecen en el cap. 1 |
| C-26 | resultados.tex:158 ↔ conclusiones.tex:20,29 | Leiden vs Louvain: 3 gana / 2 empata / 3 pierde | ✅ | Los mismos grafos en los tres lugares, y las diferencias coinciden con la Tabla 5.4 | resultados.tex:146-153; `peak_nmi` en `runs_<ds>.csv` |
| C-27 | propuesta:646 ↔ leyendas | Qué vista se reporta en cada tabla | ✅ | 5.1–5.3 usan checkpoint; 5.4, A.2 y A.3 usan pico; conclusiones.tex:29 dice pico y :38 checkpoint, todo según el protocolo | resultados.tex:15, 58, 95, 138; app0A.tex:104, 122 |
| C-28 | resumen:9; abstract:7; propuesta:601; resultados:126,165,187 | 9 grafos reales en 4 dominios; la propuesta se evalúa en 8; 7 en convergencia; 35 pares y 70 corridas | ✅ | Todo cuadra entre sí y con las columnas GCN de las tablas (falta Physics) y con Actor excluido | propuesta:610-623 (tabla de 4 dominios); Tablas 5.1, 5.2, 5.5 |
| C-29 | propuesta:171,185,639; resultados:209,219; app0A | Valores de β, τ y γ | ✅ | β=0.5 y malla {−0.5, 0, 0.25, 0.5}; τ=0.25 y rango 0.01–0.4 compatible con las dispersiones citadas; γ=0.3/1.0; 0.0275=(0.05+0.005)/2 | gcn_leiden/prior.py:65, 81, 85-91; config de los CSV (`prior_seed=123`) |
| C-30 | resultados.tex:126,128,158,209,221 | Las cifras de la prosa coinciden con las tablas | ✅ | Todas coinciden con 5.1–5.4 y A.3. Los valores por semilla 0.374 y ≈0.535 dan una media de 0.503, como la tabla | Tablas 5.1–5.4; app0A.tex:128-157 |
| C-31 | resultados:221 ↔ conclusiones:32,73; leyenda 5.3 | Relato de SBM-10k (16 y 18 comunidades → k=3 y k=1) | ✅ | Coherente entre los cuatro lugares. Con β=−0.5 el prior conserva todas sus comunidades (k=k0) | `runs_recal_sbm_10000_20.csv` (k0=16/18; β=−0.5 da k=16/18) |
| C-32 | propuesta:639; leyenda 5.3; resultados:209,221; conclusiones:32,63,73 | Salvedad: la resolución CPM se toma del generador (no es estrictamente no supervisado) | ✅ | Se dice igual en los seis lugares | mismas líneas |
| C-33 | resultados:187 ↔ conclusiones:35,64 | Convergencia: épocas 225 y 300; Q' inicial y máximo sin cambios | ✅ | Coinciden | mismas líneas |
| C-34 | resumen.tex ↔ abstract.tex | Mismo contenido factual | ✅ | Los tres párrafos son equivalentes (8 de 9 grafos, Physics, 34 493 nodos, sin k, estabilidad, "no los supera") | ambos archivos |
| C-35 | trabajos_relacionados.tex:158 | La nota "B densa, O(n²)" vale para Wang y para esta tesis | ✅ | Las dos implementaciones construyen B densa | wang-code/main.py:50-53; gcn_leiden/loss.py:10-15 |
| C-36 | trabajos_relacionados.tex:26,101,109 | Saturación de memoria atribuida a otros métodos | ✅ | Son afirmaciones de la literatura citada, no resultados propios | citas Yu2025, Lobov2019, Hu2020 |

### 2. Cobertura de números en líneas añadidas

- **chap01:** "Objetivo 4", la numeración de preguntas e hipótesis → C-25. No hay más números.
- **conclusiones:** filas 1–4, H1–H3 y objetivos 4/2/4/"1, 3" → C-25. β=0.5/−0.5 → C-05, C-15. SBM-1k/5k/10k y "tres SBM" → C-31, C-32. "300 épocas" → C-33. "n×n" → C-12. `p{7.2cm}` es formato, no afirmación.
- **propuesta:** τ=0.25, γ=0.3/1.0/0.0275, semilla 123, β=0.5 → C-29. "cada dos épocas" y "Tablas 5.1–5.3" → C-27. 25 % y 16 % (Traag), y el β=0.5 de Wang: fuera de mi alcance (literatura, grupo `metodo`/`texto`).
- **resultados, prosa:** 0.530±0.008, 0.442±0.015, 0.553±0.016, 0.488±0.037, 0.770, 0.699, 0.275/0.265±0.021, 0.339±0.009, 0.529±0.016, 0.439±0.013, k=10/7, 11/6, 4/15, 5/10, 4/10, 0.328/0.091/≈470, 0.094±0.124, ±0.072, +0.013, +0.022, +0.004, −0.002, 0.388/0.401/0.410/0.419, 16/18/20, k=3/1, 0.958/0.970, 1.000 y 0.991 → C-30 (comparé solo prosa contra tabla). 0.374 y ≈0.535 → C-30. "cuatro de cinco" (Cora, DGI) → coherencia sin recalcular. "una a tres sd" → C-08. β≥0.25 y β≤0 → C-08. 34 493 y 24 GB → C-12, C-28. 35, 3/11/21 y 56/70 → C-28 (aritmética). p=0.009, 0.66, 0.053, 0.99, 0.92, 95 %, 99 %, 225, 0.003, 0.054 → recálculo fuera de mi alcance; su coherencia con conclusiones.tex está en C-33. 1.2–11.5, 1.4–1.8, 0.007, 0.41–0.45 y τ 0.01–0.4 → C-29.
- **resultados, tablas** (valores de 5.1–5.5): recálculo fuera de mi alcance (grupo `tablas`); las usé como referencia para la coherencia.
- **trabajos_relacionados:** O(n²) → C-35.
- **resumen/abstract:** nueve, cuatro, ocho, 10 000, 34 493, cinco semillas, cuatro métricas → C-28, C-34.

### 3. Correcciones mínimas propuestas (sin aplicar)

- **C-01:** borrar "choca con el objetivo de un bloque ligero y de bajo consumo de VRAM", o sustituirlo por "añade un costo que esta tesis no aborda".
- **C-02:** "cubre solo Cora y CiteSeer (y Actor, donde ningún valor eleva el NMI por encima de 0.01)". Además, en app0A.tex:99, quitar "completas" o añadir Actor.
- **C-03:** "En SBM-5k las corridas antes imposibles ahora se completan, y en SBM-1k el prior conserva los 5 bloques en lugar de 2–3."
- **C-04:** "sin el cual no son ejecutables en SBM-5k y en SBM-1k conservan solo 2 de 5 bloques".
- **C-05:** definir H1/H2 (y P1) sobre "el NMI pico", o añadir la vista checkpoint y matizar: "con el checkpoint, en CiteSeer el filtro reduce el NMI".
- **C-06:** "las tablas reportan NMI y ARI; la comparación de priors y la recalibración usan el NMI".
- **C-07:** "Leiden supera a Louvain en NMI en Cora (en ARI la diferencia es menor a 1 sd)".
- **C-08:** precisar "menor que la mayor de las dos desviaciones" y reclasificar Cora con β=0, o presentar Actor como un caso aparte (colapso) fuera de la regla.
- **C-09:** añadir "y de DeepWalk en WikiCS".
- **C-10:** "se acepta parcialmente: es comparable en Cora y en los grafos de Amazon, pero queda por debajo en CiteSeer, PubMed, Coauthor CS y WikiCS".
- **C-11:** sustituir por "sin los colapsos de DGI en los grafos de Amazon".
- **C-12:** decir "las matrices densas n×n (adyacencia y B)", y en trabajo futuro añadir "y una adyacencia dispersa".
- **C-13:** "una heurística como prior estructural guía a los modelos de aprendizaje".
- **C-14:** "requiere en general las mismas épocas".
- **C-15:** "el mejor (empatado con β = 0.25 en Cora)".
- **C-16:** "se acepta en Cora y CiteSeer; en Actor el filtro deja el prior de Leiden con k=1".
- **C-17:** quitar las negritas de las filas DBI o decir "Negritas: mejor valor por fila, salvo DBI".
- **C-18:** "en NMI".
- **C-19:** "igualan o superan".
- **C-20:** "La ventaja de las variantes GCN está en…".
- **C-21:** "muchos modelos profundos integran…".
- **C-22:** opcional: ajustar el ancho de la columna `p{7.2cm}` o el texto de la fila H3.

### 4. Lo que no verifiqué

- No recalculé los valores de las tablas, los valores p ni los conteos por semilla ("cuatro de cinco", 3/11/21, 56/70). Le tocan a los grupos `tablas`/`texto`; solo comprobé que coinciden entre lugares.
- No hay ningún artefacto (registro de error o telemetría) que documente el OOM de Physics, así que la causa exacta solo se puede inferir del código.
- Fuera del diff y sin relación con la revisión, `frontmatter/simbolos.tex:75` remite a una "Sección~5" escrita a mano, que probablemente es incorrecta.
