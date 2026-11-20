# Informe del verificador: artículo frente a la tesis (grupo P)

> Informe textual del verificador independiente (effort xhigh) sobre `gnn-paper/main.tex` sincronizado. Las correcciones que propone se adjudicaron en `00_adjudicacion.md`.

## Verificación de `gnn-paper/main.tex` (working tree) frente a la tesis y `results/`

No hay ❌ ni ❓. Cada párrafo del artículo coincide con su fuente en la tesis salvo ajustes mecánicos y las 5 excepciones aprobadas. Todas las celdas de las tablas coinciden con los CSV (semillas 0–4, desviación estándar con ddof=1). Los hallazgos son ⚠️: referencias colgantes que dejaron los recortes, un resto de notación en la Figura 1 y un matiz compartido con la tesis.

Numeración del PDF: la Tabla 1 es la de conjuntos de datos, las Tablas 2–4 son los resultados (las "Tablas 1–3" del brief), la Tabla 5 es la de valores pico y la Tabla 6 la de convergencia.

### 1. Tabla de hallazgos

| id | ubicación en el artículo | afirmación/cambio (≤15 palabras) | veredicto | por qué (≤1 línea) | evidencia |
|---|---|---|---|---|---|
| P-01 | main.tex:647, 670, 684 | "incluso con el *pipeline* restaurado"; barrido de β en Actor; "en Actor no hay señal en ninguna configuración" | ⚠️ | Se omitió la subsección "Resolución en Actor"; el artículo usa un barrido que nunca describe, y la Sección 5.5 no trata Actor aunque se dice que "motiva el estudio" | tesis resultados.tex:211-214; runs_recal_film.csv (γ=1.0: k 4–9, Q' máx 0.28–0.34, NMI pico medio ≤0.009) |
| P-02 | main.tex:461 | "(el mínimo en el caso de $DBI$)" en el protocolo | ⚠️ | El DBI ya no se define ni se reporta (excepción 1); queda una sigla huérfana | propuesta_solucion.tex:646 frente a la excepción 1 |
| P-03 | main.tex:384-399 y Fig. 1 (222-318) | La sección "Fases 2–4 … y modularidad suave" solo trae la afiliación suave | ⚠️ | $\mathbf h_i$, H, Z, W, Â, U, m, α, $\mathcal L$ y la fórmula de Q' solo aparecen en la Figura 1, que el texto nunca cita; B se define a medias en 575. Venía del borrador original | propuesta_solucion.tex:199-230 y Fase 4 (Def. modularidad suave, B) |
| P-04 | main.tex:281 (Fig. 1) | `\mathrm{Softmax}(\delta\cdot\mathrm{sim}(…))` | ⚠️ | No es un ajuste mecánico; es un resto del texto viejo (la tesis y el resto del artículo usan `\operatorname{softmax}`/`\operatorname{sim}`). Solo notación | propuesta_solucion.tex:65 |
| P-05 | main.tex:647 | "…y se retoma como trabajo futuro." | ⚠️ | El artículo no tiene sección de trabajo futuro; la tesis remitía a `sec:trabajo-futuro` | resultados.tex:194; conclusiones.tex:76 |
| P-06 | main.tex:652 (y 670, 684) | "De los cuatro valores probados…", "siguiente valor de la malla" | ⚠️ | Al quitar la Tabla A.1 la malla β∈{−0.5, 0, 0.25, 0.5} no se enuncia en ninguna parte; solo se deduce del texto | app0A.tex:104-114 |
| P-07 | main.tex:670 | "en sbm-10k el ARI de GCN-Leiden baja de 0.787 a 0.182" | ⚠️ | El dato es correcto, pero sin la tabla de recalibración se puede confundir con la GCN-Leiden de la Tabla 4 (CPM, ARI 1.000) | runs_recal_sbm_10000_20.csv: modularidad, β=−0.5 ARI 0.7869; β≥0 ARI 0.1823 (pico y *checkpoint*) |
| P-08 | main.tex:452, 640, 686 | "durante 300 épocas" / "límite de 300 épocas" | ⚠️ | 300 es el máximo: hay parada temprana con patience=200. 10 corridas GCN de 80 terminan antes (Actor-Leiden en 201; otras entre 273 y 295). Es idéntico en la tesis, así que no es infidelidad | gcn_leiden/trainer.py:27,94; columna `epochs` de runs_{film,cora,citeseer,amac}.csv |
| P-09 | Resumen (152-156) | Tres párrafos | ✅ | Literal, con "Esta tesis"→"Este trabajo" y la excepción 1 | resumen.tex:4,7,9 |
| P-10 | Introducción (175-204) | Planteamiento, Preguntas, Contribuciones | ✅ | Planteamiento = chap01:61+64, recorte de S aprobado. Preguntas 1:1 con P1–P4. Contribuciones literales, con la referencia ajustada a `sec:fases-2-4` | chap01.tex:61-64,69-79; conclusiones.tex:46-50 |
| P-11 | Trabajo relacionado (213) | Trabajo base de Wang | ✅ | Literal; el párrafo de DMoN se quitó (aprobado) | trabajos_relacionados.tex:116 |
| P-12 | Fase 1 y Fases 2–4 (323-399) | Leiden, porcentajes de Traag 25/16/1 %, CPM, filtro, τ=0.25, k, softmax | ✅ | Literal. Se quitaron referencias a Definiciones, "Esa partición…", ", según el segundo objetivo", la fila $\binom{n_c}{2}$ y el *where* de la afiliación suave: todo son recortes válidos | propuesta_solucion.tex:146-196, 261-277; marco_teorico.tex:393-406 |
| P-13 | Protocolo (408-461) | Métricas, datos, Tabla 1, paridad, hiperparámetros, γ/β, *baselines*, rejilla | ✅ | Literal, con la excepción 1 y sin la salvedad PyG/ADGC (aprobado). Los hiperparámetros coinciden con `config`. La rejilla 2/5/10 coincide con `history/`. SBM: p_in, p_out, 64 *features* y bloques iguales coinciden con datasets.py:30,87-94 | propuesta_solucion.tex:480,601-646 |
| P-14 | Tablas 2–4 | 11 grafos × 4 filas × 7 columnas, incluida la fila k | ✅ | Las 44 filas coinciden con los CSV en media, std y k. GCN-Louvain SBM viene de runs_validate_sbm_*; GCN-Leiden SBM, de recal cpm β=0.5. Las negritas son correctas (mejor media sin redondear, incluido SBM-1k Q). Leyendas = tesis + excepción 2. Único caso límite: SBM-1k Leiden ARI = 0.98850 exacto, mostrado como 0.989 (redondeo al alza, igual que la tesis) | runs_*.csv; resultados.tex:12-120 |
| P-15 | Tabla 5 (pico) y texto 609-611 | 8×4 celdas; +0.013 (4/5), +0.022, +0.004, empates, derrotas, "1 a 3 σ" | ✅ | Todas coinciden. Cocientes Δ/σ: Cora 1.33, PubMed 1.52, Photo 1.91, CiteSeer 1.09, WikiCS 2.92. ARI en Cora y CiteSeer < 1σ | `peak_nmi`/`peak_ari` en runs_*.csv |
| P-16 | Tabla 6 y texto 616-642 | Objetivos de Q', épocas y estadísticos | ✅ | Recalculado desde history (Q' = −loss/1e-3), todo coincide: 3/11/21 con p=0.0088; sin WikiCS p=0.167; al 99 % p=0.659 con n=34 (cae Cora-Louvain s3); medida relativa p=0.053; Q'₀ p=0.994; Q'máx p=0.916; Cora 5/5, CiteSeer 0/5; 56/70; pérdida de NMI 0.0027–0.0544; época media de Q'máx 273/226/250.5 | results/history/* |
| P-17 | Calidad (575-577) | Cifras de Cora, PubMed, CS, Amazon, WikiCS; empates frente al mejor modelo profundo; colapsos de DGI; 0.374; 4.4 GiB | ✅ | Cada empate o derrota se reprodujo con el criterio de σ máxima. DGI en Computers colapsa en las semillas 1–4 (s0 = 0.315) y en Photo en 5/5. 34 493²×4 B = 4.43 GiB (adyacencia float32) | runs_*.csv; datasets.py:39 |
| P-18 | Actor (647) | Leiden k=1, Louvain k=2, NMI 0.007 | ✅ | Coincide | runs_film.csv |
| P-19 | Recalibración (652-658) | Tendencias de β, 0.378→0.442, 0.146→0.315, NMI 0.530 y 0.352→0.338, SBM 2–3 bloques, CPM 1.000/0.991, k₀ 16/18 → k 3/1, CV, bit a bit | ✅ | Todo coincide. CV calculado como (T−μ)/β con μ=n/k₀: reales 1.22–11.46; CPM 1.37–1.76; ≤0.0071; sbm-10k 0.41–0.45. validate = main en Cora y CiteSeer, bit a bit | runs_recal_*, runs_validate_*; resultados.tex:204,209,219,221 |
| P-20 | Conclusiones y Limitaciones (667-686) | Respuestas 1–4 sin veredictos; 6 limitaciones | ✅ | Excepción 4 aplicada correctamente; limitaciones literales | conclusiones.tex:29-38,58-65 |
| P-21 | Todo el texto | Restos del texto viejo | ✅ | No queda ninguno: ni telemetría de RAM/VRAM, ni "mejor ARI en Amazon", ni "β óptimo", ni "τ∈[0.1,0.5]", ni el 16 % aislado, ni causa afirmada de Physics. "No es ejecutable" en la leyenda de la Tabla 4 = tesis:95 | grep de main.tex |
| P-22 | Compilación | Copia compilada fuera del repo | ✅ | 8 páginas, sin "??" y con todas las `\ref` resueltas. Las citas [1]–[7] resuelven. "There were undefined references" y "Please (re)run BibTeX" también salen al compilar el commit original | out/compile/main.log |

### 2. Referencias colgantes o frases que remiten a contenido eliminado

- **main.tex:461:** "$DBI$" no está definido en el artículo.
- **main.tex:647:** "incluso con el *pipeline* restaurado" y "motiva el estudio de la Sección 5.5". La restauración (γ=1.0) solo estaba en la subsección omitida, y la Sección 5.5 del artículo no trata Actor.
- **main.tex:684 y 670:** "…y Actor (este último, sin señal)" y "en Actor no hay señal en ninguna configuración" remiten al mismo barrido no descrito.
- **main.tex:647:** "se retoma como trabajo futuro" no tiene sección a la que remitir.
- **Fases 2–4 (384-399):**
  - $\mathbf h_i$ (393), $\mathbf u_c$, H, Z, W, Â, U, m, α (452), $\mathcal L$, la fórmula de Q' y la "normalización $L_2$" (575) solo se definen en la Figura 1.
  - La Figura 1 (`fig:pipeline-arquitectura`) nunca se cita en el texto.
  - El título promete "modularidad suave", pero la sección no tiene texto sobre Q'.
- **"La malla" / "cuatro valores probados" (652, 670, 684):** la malla de β no se enuncia.
- **Leves:**
  - "límite de resolución" (329, 658) aparece sin definición; se quitó la referencia a la definición, que es un cambio mecánico.
  - $\mathbf P$ se usa en 325 antes de definirse en 399.
- **Sin problemas:** no hay `\ref` rotas. "Primera", "tercera" y "cuarta pregunta" (577, 582, 616) corresponden bien a P1–P4.

### 3. Correcciones mínimas

- **P-01:** reinsertar textualmente resultados.tex:214 como párrafo de 5.5: "En Actor se evalúa el barrido completo sobre $\gamma \in \{0.3, 1.0\}$ y $\beta$. Con $\gamma = 1.0$, el \textit{prior} de Leiden retiene entre $4$ y $9$ comunidades para todo $\beta \geq 0$. El \textit{pipeline} corre con normalidad y alcanza $Q' \approx 0.31$, similar a GCN-Louvain. Ningún ajuste eleva el $NMI$ por encima de $0.01$."
  - Los datos lo respaldan con medias: la mayor media de NMI pico es 0.0089, aunque semillas sueltas llegan a 0.0135.
  - La columna derecha de la página 8 tiene unas 12 líneas libres; hay que confirmar que el artículo siga en 8 páginas.
- **P-02:** quitar "(el mínimo en el caso de $DBI$)" en 461 (recorte).
- **P-03:** como mínimo, añadir una referencia a la Figura 1 donde aparece $\mathbf h_i$ (393). Si cabe, es mejor insertar literalmente propuesta_solucion.tex:224, primera oración (Z → $\mathbf h_i$ por normalización L2), y la Definición de modularidad suave de la Fase 4.
- **P-04:** en 281, cambiar a `\operatorname{softmax}(\delta\cdot\operatorname{sim}(\mathbf{h}_i,\mathbf{u}_c))`, como en la tesis:65.
- **P-05:** recortar a "Verificar esta hipótesis queda fuera del alcance de este trabajo."
- **P-06 (opcional):** enunciar la malla $\beta\in\{-0.5,0,0.25,0.5\}$ al inicio de 652, tomada del encabezado de la Tabla A.1. No es texto literal; requiere aprobación.
- **P-07 (opcional):** precisar "(\textit{prior} de modularidad)" tras "GCN-Leiden" en 670. No es texto literal; requiere aprobación.
- **P-08:** no tocar el artículo si no se corrige antes la tesis, por ejemplo con "hasta $300$ épocas", porque ambos dicen lo mismo.

### 4. No verificado

- Cifras externas: el 25/16/1 % de Traag y lo que se atribuye a Wang (sensibilidad 0.1–1.0 con óptimo 0.4–0.6, Ecuación 6, signo negativo, código del repositorio). Solo las contrasté con la tesis.
- La paridad bit a bit con el código original en Cora: no hay ese artefacto en `results/`.
- La ausencia de registros del fallo en Physics.
- n/F/k de la Tabla 1 contra los datos de PyG cargados: los comparé con la tesis y con las estadísticas conocidas, sin cargarlos.

Scripts y salidas en `/private/tmp/claude-501/-Users-omar-Developer-me-gcn-leiden/ddebb875-fe4a-43f3-ab25-1ab06b6b4a1f/scratchpad/verify_paper/out/`: `match_out.txt` (diff por párrafo), `tables.py`, `peak_conv.py`, `text_claims.py`, `cv.py`, `film.py`, `compile/main.pdf`. No modifiqué nada en los repos.
