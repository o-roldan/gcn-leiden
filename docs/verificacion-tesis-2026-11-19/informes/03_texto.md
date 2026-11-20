# Informe del verificador: Prosa de Resultados y Conclusiones (grupo X)

> Informe textual tal como lo entregó el verificador (effort xhigh), extraído de su transcripción. Las rutas `/private/tmp/...` apuntan al scratchpad de la sesión del 2026-11-19; los scripts y salidas que cita están copiados en `../evidencia/`.

## Verificación del grupo `texto`: prosa de Resultados y Conclusiones

Archivos: R = `/Users/omar/Developer/me/gnn-thesis/chapters/resultados/resultados.tex`, C = `/Users/omar/Developer/me/gnn-thesis/chapters/conclusiones/conclusiones.tex`. CODE = `/Users/omar/Developer/me/gcn-leiden`.

Mis scripts y salidas están en `/private/tmp/claude-501/-Users-omar-Developer-me-gcn-leiden/ddebb875-fe4a-43f3-ab25-1ab06b6b4a1f/scratchpad/verify/texto/`. Los principales son `conv.py` y `conv2.py` (convergencia), `qual.py`, `prior_cmp.py`, `cv.py`, `prior_direct.py`, `h2.py`, `lv.py` y `film.py`, y cada uno tiene su `out_*.txt`.

Filtros usados:
- Semillas 0–4.
- Barrido principal `runs_<ds>.csv`: GCN con β=0.5 y γ=0.3 (modularidad, filtro `wang`). Louvain y Leiden clásicos con `resolution=1.0`.
- Columnas `nmi`/`ari` para el checkpoint y `peak_*` para el valor pico.
- Q' = −loss/1e-3, porque `loss = loss_scale·(−Q')` (`loss.py:18-22`, `trainer.py:71`, `config loss_scale=0.001`).
- Media ± desviación estándar con ddof=1.

### 1. Tabla

| id | archivo:línea | afirmación | veredicto | por qué | evidencia |
|---|---|---|---|---|---|
| X-01 | R:165 | Las trayectorias registran Q' cada dos épocas | ❌ | La rejilla es de 2 épocas solo en Cora, CiteSeer, Amazon Photo y Actor; de 5 en Amazon Computers y WikiCS; de 10 en PubMed y CS | Columna `epoch` de `results/history/history_pubmed/*` (10,20,…), `history_wikics/*` (5,10,…); `experiments/deploy/launch_shards.sh:44-51` |
| X-02 | R:170 (caption) | "La evaluación se realiza cada dos épocas" | ❌ | Mismo error que X-01 (los 100.0±0.0 y 30.0±0.0 vienen de la rejilla de 10) | Igual que X-01 |
| X-03 | R:187 | La evaluación cada dos épocas produce muchos empates | ❌ | 13 de los 21 empates vienen de rejillas de 5/10 (CS 5, Amazon Computers 5, PubMed 3) | `conv.py`: empates por grafo |
| X-04 | R:219 | En SBM-1k y SBM-5k, las corridas antes imposibles ahora se completan | ❌ | En SBM-1k sí corrían con el filtro original (k=2–3), como dice R:209; solo SBM-5k era imposible | `runs_recal_sbm_1000_5.csv`: 40 filas de modularidad, k=2/3, NMI pico 0.575–0.778 |
| X-05 | R:95 (caption SBM, dependiente) | Sin filtro condicionado, estas corridas no son ejecutables | ❌ | Es falso para SBM-1k (k=2–3) y SBM-10k (k=3 con Leiden, k=1 con Louvain); solo vale para SBM-5k | `runs_recal_sbm_1000_5.csv`, `runs_recal_sbm_10000_20.csv` (modularidad, β≥0) |
| X-06 | R:126; C:59 | No completan Physics porque B densa excede los 24 GB de la L4 | ❓ | No hay log del OOM. La extrapolación del pico de VRAM medido da unos 18–22 GiB, frente a ~22.4 GiB de la L4 (caso límite). B tampoco es el único tensor n×n | Solo el comentario `launch_shards.sh:63` ("dense loss OOMs"). Picos de 4.15–4.93×n²·4 B en `vram_peak_mb` de PubMed, CS y Amazon Computers. A densa en `trainer.py:50`; diag n×n en `model.py:61` |
| X-07 | R:158; C:29 | Con el criterio de 1σ: gana en Cora, PubMed, Photo; empata en CS, Computers; pierde en CiteSeer, WikiCS, Actor | ⚠️ | No se dice qué σ se usa. Con la σ mayor, Actor queda en empate (0.0071<0.0073). Con σ combinada coincide con el texto. En ARI, Cora (+0.013, σ 0.022) y CiteSeer (−0.016, σ 0.021) son empates | `prior_cmp.py` sobre `peak_nmi`/`peak_ari` de `runs_<ds>.csv` |
| X-08 | R:158 | Amazon Photo: +0.004 de NMI | ⚠️ | La diferencia exacta es 0.0049 (≈+0.005); el 0.004 sale de restar valores ya redondeados | 0.6535−0.6486 |
| X-09 | R:187 | Al 99 % del nivel no hay diferencia (p = 0.66) | ⚠️ | p=0.66 sale solo al descartar en silencio el par Cora semilla 3 (Louvain paró en la época 278 con Q'max 0.7526 < nivel 0.7541; n=34). Si se trata como censurado, p=0.92. La conclusión no cambia | `conv2.py`; `convergence.py:90` (`.dropna()`) |
| X-10 | R:187 | Salvedades estadísticas declaradas (Wilcoxon sobre los pares no empatados) | ⚠️ | El manejo de empates no cambia el resultado: exacta 0.0067, Pratt 0.020, zsplit 0.035. Pero la significación depende de WikiCS (sin él, p=0.23) y las 5 semillas de cada grafo comparten el mismo prior (seudorreplicación: 7 unidades independientes). Además hay 5 pruebas sin corrección | `conv.py`, `conv2.py` |
| X-11 | R:187 | Cada prior fija un k distinto | ⚠️ | k solo difiere en Cora (9 vs 10) y PubMed (4 vs 5); coincide en los otros 5 grafos | Columna `k` de `runs_<ds>.csv` |
| X-12 | R:187; C:35 | Ni el Q' inicial ni el máximo difieren (p=0.99 y 0.92) | ⚠️ | Los p se reproducen, pero la prueba agrupada oculta diferencias consistentes por grafo. "Q' inicial" es la primera evaluación (época 2, 5 o 10), no la época 0 | CiteSeer Q'max 0.778±0.009 vs 0.799±0.006, Leiden menor en 5/5 semillas (2.3σ); Cora Q'0 y Q'max mayores en 5/5 (`lv.py`) |
| X-13 | R:126 | En CS, DGI y DMoN superan a ambas variantes GCN | ⚠️ | Vale en NMI. En ARI, DMoN (0.450±0.016) está por debajo de las GCN (0.493/0.494), y DGI está dentro de 1σ (0.547±0.087). La tesis prioriza el ARI | `runs_cocs.csv` |
| X-14 | R:126, R:128; C:38 | DGI es el mejor en Cora, CiteSeer y PubMed / la GCN queda por debajo de DGI | ⚠️ | Las medias son correctas. En CiteSeer la brecha es menor a 1σ de DGI (NMI 0.377±0.056 vs 0.342; ARI 0.354±0.057 vs 0.317). En PubMed, el ARI de DGI vs DeepWalk (0.305 vs 0.301) es menor a 1σ | `runs_citeseer.csv`, `runs_pubmed.csv` |
| X-15 | R:126 | En Photo y WikiCS los clásicos superan a todos los entrenables | ⚠️ | En WikiCS, DeepWalk empata: NMI 0.466±0.009 frente a Leiden 0.467 y Louvain 0.459; ARI 0.404 frente a Louvain 0.406. Photo ✅ | `runs_wikics.csv`, `runs_amap.csv` |
| X-16 | R:126 | GCN-Louvain tiene el mejor NMI y ARI en Amazon Computers | ⚠️ | El NMI 0.529±0.016 está a menos de 1σ de Leiden clásico (0.524±0.014). En ARI está a menos de 1σ de GCN-Leiden (0.394±0.091) | `runs_amac.csv` |
| X-17 | R:126 | En Cora, GCN-Leiden queda en segundo lugar | ⚠️ | Frente a GCN-Louvain (0.521±0.028 y 0.424±0.068) la diferencia es menor a 1σ | `runs_cora.csv` |
| X-18 | R:126 | GCN recupera SBM-1k y 5k igual que los modelos profundos | ⚠️ | DeepWalk queda claramente por debajo en SBM-1k (0.947±0.012) | `runs_sbm_1000_5.csv` |
| X-19 | R:128 | "Su ventaja está en la estabilidad frente al contrastivo" | ⚠️ | Referente ambiguo: por gramática "Su" son las heurísticas clásicas, pero la evidencia que sigue habla de las GCN | Texto |
| X-20 | R:133 | Se usa el valor pico del protocolo de Wang | ⚠️ | En PubMed, CS, Computers y WikiCS el pico se toma sobre una rejilla de 5/10 épocas; Wang evalúa cada 2. La comparación sigue siendo simétrica entre brazos | `wang-code/main.py:181`; histories |
| X-21 | R:204 | La ventaja de Leiden en Cora se sostiene en los cuatro β | ⚠️ | Con β=0 la diferencia es +0.011, menor que σ_Louvain 0.014 (≈1.0 σ combinada): empate o margen mínimo según la σ que se use | `runs_recal_cora.csv` `peak_nmi` |
| X-22 | C:21, C:32 | H2 aceptada: filtrar con β=0.5 eleva el NMI frente a β=−0.5 | ⚠️ | Vale solo con el NMI pico. Con el checkpoint sin etiquetas el NMI no sube en Cora-Leiden (0.530→0.530) y baja en CiteSeer (0.356→0.342 y 0.352→0.338); el ARI del checkpoint sí sube | `h2.py` sobre `runs_recal_{cora,citeseer}.csv` |
| X-23 | C:23, C:38 | Aceptada parcialmente: "comparable, pero no superior" | ⚠️ | La hipótesis central solo pide "comparable" (`chap01.tex:85-90`). La parcialidad debería apoyarse en el desempeño inferior frente a DGI en PubMed y CS | `chap01.tex:85-90`; Tablas de R |
| X-24 | C:62 | El barrido de β en grafos reales cubre solo Cora y CiteSeer | ⚠️ | Actor también se barrió en β y γ (R:214), aunque sin señal | `runs_recal_film.csv` (80 filas) |
| X-25 | C:75 | La descomposición de B permitiría evaluar Coauthor Physics | ⚠️ | El álgebra es correcta y evita B. Pero quedan A densa en GPU y la diag n×n; no está demostrado que baste | `datasets.py:105`, `trainer.py:50`, `model.py:61` |
| X-26 | C:38 | La GCN es más estable entre semillas que DGI | ⚠️ | Vale en general, pero no en PubMed (σ GCN 0.021 frente a σ DGI 0.009) | `runs_pubmed.csv` |
| X-27 | R:187 | El Q' máximo llega después de la época 225 en PubMed, CS y WikiCS | ✅ | Medias agrupadas: 273, 226.0 y 250.5. CS pasa por poco; su brazo Louvain solo es 198 | `conv.py` |
| X-28 | R:126 | Valores de Cora (0.530±0.008, 0.442±0.015; DGI 0.553±0.016, 0.488±0.037; Q 0.770 vs 0.699) | ✅ | Coinciden | `runs_cora.csv` |
| X-29 | R:126 | En PubMed las GCN superan a DMoN y quedan bajo DGI (0.275, 0.265 vs 0.339) | ✅ | Coincide en NMI y ARI | `runs_pubmed.csv` |
| X-30 | R:126 | Amazon Computers: 0.529±0.016 y 0.439±0.013 | ✅ | Coinciden | `runs_amac.csv` |
| X-31 | R:126 | Physics tiene n=34 493 y las GCN no completan | ✅ | No hay filas GCN | `runs_cophysics.csv`; `load.py:30` |
| X-32 | R:128 | Las estimaciones de k (10/7, 11/6, 4/15, 5/10, 4/10) | ✅ | Coinciden | Columna `k` |
| X-33 | R:128 | CiteSeer clásico: NMI 0.328, ARI 0.091, k≈470 | ✅ | 470.4 y 471.8 | `runs_citeseer.csv` |
| X-34 | R:128 | DGI colapsa en Computers en 4/5 semillas (0.094±0.124) y en Photo en las 5 | ✅ | Semillas 1–4 ≈0.038; Photo 0.061 en las 5 | `qual.py` |
| X-35 | R:128 | Una semilla de GCN-Leiden en Computers da 0.374 frente a ≈0.535; explica el ±0.072 | ✅ | Semilla 2 = 0.3736; las otras promedian 0.5352 | `qual.py` |
| X-36 | R:128 | Se acerca a DGI en Cora; iguala o supera en Amazon; queda por debajo en CiteSeer, PubMed y CS | ✅ | Coincide (matiz de CiteSeer en X-14) | Tablas recalculadas |
| X-37 | R:158 | Cora +0.013 (4/5 semillas), PubMed +0.022, CS +0.004, Computers −0.002; valores de CiteSeer y WikiCS; Actor con k=1 | ✅ | Coinciden; en Cora la semilla 3 pierde | `prior_cmp.py` |
| X-38 | R:158 | En CiteSeer la desventaja aparece con β≥0.25 y hay empate con β≤0 | ✅ | NMI pico: −0.013 y −0.013 frente a σ≈0.012; con β≤0, diferencias menores a 1σ | `runs_recal_citeseer.csv` |
| X-39 | R:160 | Diferencias de una a tres σ | ✅ | Con la σ mayor, 1.1–2.9 en NMI (con σ combinada, WikiCS llega a 3.9) | `prior_cmp.py` |
| X-40 | R:165 | Nivel = 95 % del menor Q'max medio; Actor excluido con Q' nulo | ✅ | Reproduce los 7 niveles; en Actor-Leiden \|Q'\| ≤ 3e-6 con k=1 | `conv.py`, `film.py` |
| X-41 | R:187 | 35 pares: 3 antes, 11 después, 21 empates; p=0.009 | ✅ | p=0.0088 (scipy por defecto). Los 3 "antes" son de Cora; los "después" son CiteSeer 4, PubMed 2, WikiCS 5 | `conv.py` |
| X-42 | R:187 | Medida relativa: p = 0.053, no muestra aceleración | ✅ | p=0.0532: 6 antes, 15 después, 14 empates; si acaso, Leiden es más lento | `conv.py` |
| X-43 | R:189 | 56 de 70; pérdida de NMI de 0.003 (Photo) a 0.054 (CiteSeer) | ✅ | 0.0027 y 0.0544 | `conv.py` |
| X-44 | R:194 | Actor con Wang: k=1 en Leiden y k=2 en Louvain; métricas en 0; NMI ≲ 0.01 | ✅ | El máximo de todo método y barrido es 0.009 | `runs_film.csv`, `runs_recal_film.csv` |
| X-45 | R:204 | El NMI crece con β; β=0.5 es el mejor y está en el borde de la malla; β=−0.5 apaga el filtro y baja el NMI | ✅ | Con β=−0.5, T<0 y k=k0 (90/89/451/452); es el mínimo en los 4 casos. En Cora, 0.25 y 0.5 empatan | `cv.py` |
| X-46 | R:209 | γ=0.0275 es el punto medio; NMI 1.000±0.000 (5k) y 0.991±0.002 (1k) con k exacto; sobreviven 2–3 de 5; nada corre en 5k; γ=0.3 fusiona todo | ✅ | Coincide (NMI pico). Con γ=0.3 recomputé k0=1 directamente en SBM-1k y 5k | `cv.py`, `prior_direct.py` |
| X-47 | R:214 | Actor γ=1.0: Leiden retiene 4–9 comunidades; Q'≈0.31, similar a Louvain | ✅ | k=9/5/4; Q'max 0.29–0.31 frente a 0.30–0.32 | `film.py` |
| X-48 | R:219 | σ/μ en 1.2–11.5 (reales), 1.4–1.8 (CPM), ≤0.007 (modularidad recuperada), 0.41–0.45 (10k); cualquier τ en [0.01, 0.4] decide igual | ✅ | Valores: 1.224–11.458; 1.373–1.757; 0.0071; 0.412–0.447. El intervalo exacto es (0.0071, 0.4123] | CV=(T·k0/n−1)/β (`prior.py:84-85`, std con ddof=0); recomputado directamente |
| X-49 | R:219 | En reales el filtro se aplica siempre; Cora y CiteSeer bit a bit | ✅ | CV ≥ 1.22. Las 10 columnas de métricas y las historias son idénticas | `bit.py`, `bit2.py` |
| X-50 | R:221 | SBM-10k: 16/18 comunidades → k=3/1 al filtrar; clásicos 0.958/0.970; CPM recupera 20 bloques con 1.000 | ✅ | k0=16/18 con CV>τ; el filtro deja solo las comunidades fusionadas (≥1000). Validate da k=3/1 | `cv.py`, `prior_direct.py` |
| X-51 | C:20-23 | Correspondencia pregunta–hipótesis–objetivo y secciones citadas | ✅ | P1↔H1↔Obj4, P2↔H2↔Obj2, P3↔H3↔Obj4 (convergencia), P4↔central↔Obj1,3; todas las refs resuelven | `chap01.tex:66-133` |
| X-52 | C:22, C:35 | H3 rechazada: Leiden no acelera la optimización de Q' | ✅ | En ninguna medida Leiden es más rápido (90 %: 1 vs 15, p=0.0007; 95 %: 3 vs 11; 99 %: 11 vs 12; relativa: 6 vs 15) | `convergence.py`, `conv.py` |
| X-53 | C:32 | β=0.5 es el mejor; el filtro condicionado resuelve 1k y 5k pero no 10k; CPM recupera los 3 SBM; con tamaños uniformes el filtro reduce el NMI | ✅ | Validate: 0.988 y 1.000; 10k: k=3/1. Lo de "reduce" se ve más claro frente a validate sin filtro | `cv.py` |
| X-54 | C:47-50 | Contribuciones 2–5 (barras de error, filtro, δ y ≥ frente a >, resultados en la nube) | ✅ | Wang publica valores únicos (Tabla 3, p.13); el artículo dice \|ci\|≥T (p.7) y el código usa > (`main.py:140`); el artículo usa exp(−δ·sim) (Ec. 9) y el código softmax(+temp·dist) (`model.py:79`); el script hace `rsync` al bucket | `wang.txt`, `wang-code/` |
| X-55 | C:61, 63, 64; C:73-76 | Limitaciones 3, 5, 6 y trabajo futuro 1, 2, 4 | ✅ | No hay variante sin entrenamiento; CPM usa el generador; 300 épocas es el protocolo de Wang (`main.py:179`) | CSVs; código |

Información adicional: las celdas de `tab:convergencia-prior` (R:176-182) y de `tab:prior-pico` se reproducen exactamente con mis cálculos.

Revisión de `CODE/experiments/analysis/convergence.py`, hecha después de mi cálculo propio. Da los mismos resultados que mi cálculo independiente. Problemas encontrados:
- (a) El docstring (líneas 4 y 17-18) dice que la rejilla es de 2 épocas: es falso.
- (b) La línea 14 dice "a level every run of both arms reaches", pero es falso al 99 %. Además, `paired_comparison` descarta NaN en silencio (línea 90), y de ahí sale n=34 y p=0.66.
- (c) `q0` es la primera evaluación, no la época 0.
- (d) El Q' de una fila se calcula antes del paso del optimizador y las métricas después (`trainer.py:70-86`); el desfase es despreciable.
- (e) Riesgo latente sin efecto hoy: `load_history` acepta archivos de re-ejecución (sufijo `-N`, `load.py:36`) y `run_summary` agrupa sin `batch`, así que mezclaría trayectorias duplicadas.

### 2. Cobertura de números en líneas `+`

**R:15/58 (captions):** "cinco semillas" y γ=1.0 → no son afirmaciones de mi alcance (captions de tabla; coinciden con los CSV).

**R:95:**
- p_in, p_out y cinco semillas → no es afirmación.
- γ=1.0 → X-46.
- "una sola comunidad" en 10k → X-50.
- (p_in+p_out)/2 → X-46.
- "no ejecutables" → X-05.

**R:126:**
- Valores de Cora → X-28.
- PubMed → X-29.
- Computers → X-30, X-16.
- SBM-1k/5k → X-18.
- n=34 493 → X-31.
- 24 GB → X-06.
- Comparativos → X-13, X-14, X-15, X-17.

**R:128:**
- Valores de k → X-32.
- 0.328/0.091/470 → X-33.
- 4/5, 0.094±0.124 y "las cinco" → X-34.
- 0.374, 0.535 y ±0.072 → X-35.
- "cuarta pregunta" → X-51.

**R:133:** "primera pregunta" → X-51; valor pico → X-20.

**R:138:** cinco semillas → no es afirmación.

**R:158:**
- +0.013 y 4/5, +0.022, +0.004 (CS), −0.002, 0.388±0.012/0.401±0.008, 0.410±0.003/0.419±0.001, "una sola comunidad" → X-37.
- +0.004 (Photo) → X-08.
- Criterio de 1σ → X-07.
- β≥0.25 y β≤0 → X-38.

**R:160:** "una a tres σ" → X-39.

**R:165:**
- "cada dos épocas" → X-01.
- 95 % y k=1 → X-40.
- "tercera pregunta" → X-51.

**R:170:** 95 % → X-40; "cada dos épocas" → X-02.

**R:187:**
- 35, 7, 5, 3/11/21 y p=0.009 → X-41, X-10.
- 99 % y p=0.66 → X-09.
- 95 % y p=0.053 → X-42.
- p=0.99 y 0.92 → X-12.
- "dos salvedades" → X-03, X-11.
- 225 y 300 → X-27.

**R:189:** 56/70, 0.003 y 0.054 → X-43.

**R:194 (texto movido):** γ=0.3, β=0.5, k=1, k=2 y 0.01 → X-44.

**R:204:** "cuatro valores", β=0.5, −0.5 y ≥0.25 → X-45, X-21.

**R:209:** 0.0275, punto medio, 1.000±0.000, 0.991±0.002, γ=0.3/1.0 y 2–3 de 5 → X-46.

**R:219:**
- τ=0.25, 1.2–11.5, 1.4–1.8, 0.007, 0.41–0.45 y 0.01–0.4 → X-48.
- "siempre" y "bit a bit" → X-49.
- "1k y 5k imposibles" → X-04.

**R:221:** 16, 18, 20, β=−0.5, k=3, k=1, 0.958, 0.970, 20 bloques y 1.000±0.000 → X-50.

**C:20-23:** números de pregunta, hipótesis y objetivo → X-51; veredictos → X-52, X-22, X-23.

**C:29:** → X-07.

**C:32:** β=0.5, 1k/5k/10k, "tres SBM" y β=−0.5 → X-53, X-22.

**C:35:** → X-52, X-12.

**C:38:** → X-14, X-23, X-26.

**C:48:** T=μ+βσ → X-54.

**C:59–64:** n×n → X-06; "solo Cora y CiteSeer" → X-24; 300 épocas → X-55.

**C:73-75:** 10k → X-50/X-55; B=A−ddᵀ/2m → X-25.

### 3. Correcciones mínimas propuestas

- **X-01 / X-02:** "que registran Q' cada 2 épocas en Cora, CiteSeer y Amazon Photo, cada 5 en Amazon Computers y WikiCS y cada 10 en PubMed y Coauthor CS".
- **X-03:** "La evaluación discreta (cada 2, 5 o 10 épocas) produce muchos empates".
- **X-04:** "En SBM-5k las corridas antes imposibles ahora se completan, y en SBM-1k el prior conserva los 5 bloques en lugar de 2–3".
- **X-05:** "sin el cual estas corridas no son ejecutables en SBM-5k y degeneran en SBM-1k y SBM-10k".
- **X-06:** "no completan por falta de memoria en la GPU; la implementación densa (B, A y la normalización) escala como n²", o citar el log del OOM.
- **X-07:** decir qué σ se usa (p. ej., "desviación estándar combinada") y añadir "en NMI; en ARI, Cora y CiteSeer empatan".
- **X-08:** "+0.005".
- **X-09:** "Con un nivel del 99 % (excluido un par de Cora en el que Louvain no lo alcanza) no hay diferencia (p = 0.66)".
- **X-10:** añadir "sin WikiCS la diferencia no es significativa (p = 0.23); las semillas de un mismo grafo comparten el prior".
- **X-11:** "y en Cora y PubMed cada prior fija un k distinto".
- **X-12:** "no hay un desplazamiento sistemático del Q' inicial (primera evaluación) ni del máximo (p = …), aunque en algunos grafos difieren (p. ej., CiteSeer, Q'max 0.778 frente a 0.799)". Ajustar C:35 de forma análoga.
- **X-13:** "En Coauthor CS, DGI supera a ambas variantes en NMI y ARI, y DMoN solo en NMI".
- **X-14:** añadir "en CiteSeer, con diferencias menores a una desviación estándar".
- **X-15:** "en Amazon Photo las heurísticas clásicas superan a todos los entrenables; en WikiCS, solo DeepWalk las iguala".
- **X-16:** añadir "(en NMI, empatado con Leiden clásico)".
- **X-17:** añadir "(a menos de 1σ de GCN-Louvain)".
- **X-18:** "igual que DGI y DMoN".
- **X-19:** "La ventaja de las variantes GCN está en…".
- **X-20:** "usa el valor pico (máximo sobre las evaluaciones registradas, como en Wang et al.)".
- **X-21:** "se sostiene en los cuatro valores de β (con β = 0, por un margen de una σ)".
- **X-22:** añadir "con el NMI pico; con el checkpoint de pérdida mínima la mejora aparece en ARI, no en NMI".
- **X-23:** "Aceptada parcialmente: comparable en Cora y Amazon, inferior a DGI en PubMed y Coauthor CS".
- **X-24:** "cubre solo Cora, CiteSeer y Actor (sin señal en este último)".
- **X-25:** "evitaría materializar B; junto con una adyacencia dispersa y una normalización sin matriz diagonal densa, permitiría…".
- **X-26:** "más estable entre semillas que DGI en la mayoría de los grafos".

### 4. Qué no pude verificar

- La causa del fallo en Coauthor Physics y que se superen los 24 GB (X-06): no hay log del OOM, solo un comentario en el código.
- El signo de δ: lo verifiqué solo de forma superficial (Ec. 9 del artículo frente a `softmax(+temp·dist)`), porque el análisis detallado está en el capítulo de propuesta, fuera de mi alcance.
- Las celdas de las tablas: las verifica otro grupo; aquí solo las uso como dependencias.
