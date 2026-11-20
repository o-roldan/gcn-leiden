# Informe del verificador: Tablas de resultados y apéndice (grupo T)

> Informe textual tal como lo entregó el verificador (effort xhigh), extraído de su transcripción. Las rutas `/private/tmp/...` apuntan al scratchpad de la sesión del 2026-11-19; los scripts y salidas que cita están copiados en `../evidencia/`.

## Reporte del grupo `tablas`: verificación de las tablas de resultados y del apéndice

**Resultado general.** Recalculé desde los CSV y las trayectorias **todas las celdas** de las 3 tablas principales, `tab:prior-pico`, `tab:convergencia-prior`, `tab:recal-beta` y `tab:recal-sbm`.
- **Ninguna celda numérica está mal.** La única diferencia es la de Leiden en SBM-1k, fila ARI, y se debe solo al redondeo en el límite (media exacta 0.98850).
- **Los problemas están en las leyendas:** hay 2 afirmaciones falsas (❌) y 6 matices (⚠️).

Scripts y salidas, todos en `/private/tmp/claude-501/-Users-omar-Developer-me-gcn-leiden/ddebb875-fe4a-43f3-ab25-1ab06b6b4a1f/scratchpad/verify/tablas/`:
- Scripts: `texparse.py`, `main_tables.py`, `bold_check.py`, `other_tables.py`, `convergence_check.py`, `report_rows.py`.
- Salidas: `main_best_b0.5.csv`, `other_out.txt`, `conv_out.txt`, `rows_all.md`.

**Qué alimenta cada columna (deducido y comprobado).** En todos los casos uso las semillas 0–4 y excluyo `runs.csv` (semilla 24).
- **Louvain y Leiden clásicos:** `runs_<ds>.csv`, con `resolution=1.0`.
- **DeepWalk, DGI y DMoN:** `runs_<ds>.csv`, que tiene una sola configuración por método.
- **GCN en grafos reales:** `runs_<ds>.csv` con `gcn-*`, `beta=0.5`, `resolution=0.3`, `modularity`, `prior_seed=123` y filtro estricto (`wang` por defecto, `runners/gcn.py:42`). Columnas `nmi/ari/q/dbi/k`, que corresponden a `result.best` (`runners/gcn.py:110-112`, `trainer.py:88-98`).
- **GCN-Louvain en SBM:** `runs_validate_<sbm>.csv`, con filtro condicionado (`recalibrado`), `γ=1.0` y `β=0.5`.
- **GCN-Leiden en SBM:** `runs_recal_<sbm>.csv`, con `cpm`, `γ=0.0275` y filtro `wang`. Con `β∈{0, 0.25, 0.5}` los resultados son idénticos.
- **`tab:prior-pico`, `tab:recal-beta` y `tab:recal-sbm`:** columnas `peak_nmi`/`peak_ari`.
- **`tab:convergencia-prior`:** `history_<ds>/gcn-*_<ds>_seed{0-4}.csv`, con Q' = −loss/α, α=1e-3 (`trainer.py:71`, `loss.py:18-22`). Coinciden las 35 cifras; las variantes "máximo de la trayectoria media" y "q dura" no coinciden.

### 1. Tabla de afirmaciones

| id | archivo:línea | afirmación (≤15 palabras) | veredicto | por qué (≤1 línea) | evidencia (fuente exacta) |
|---|---|---|---|---|---|
| T-01 | resultados.tex:170 (y prosa dependiente en :165 y :187) | "La evaluación se realiza cada dos épocas" | ❌ | Es falso en 4 de los 7 grafos: PubMed y Coauthor CS se evalúan cada 10 épocas; Amazon Computers y WikiCS, cada 5 | `results/history/history_{pubmed,cocs}/*.csv`: épocas 10,20,…,300 (30 filas); `history_{amac,wikics}/*.csv`: paso 5; `experiments/deploy/launch_shards.sh:48,51` (`wikics:5`; `amac:5 pubmed:10 cocs:10`). Solo Cora, CiteSeer y Amazon Photo usan paso 2 |
| T-02 | resultados.tex:95 | Sin filtro condicionado "estas corridas no son ejecutables" | ❌ | Solo es cierto en SBM-5k. Con el filtro de Wang, SBM-1k corre con k=2 (NMI 0.566 en checkpoint, 0.580 en pico) y SBM-10k corre con k=1 | `runs_recal_sbm_1000_5.csv` y `runs_recal_sbm_10000_20.csv`, gcn-louvain `beta=0.5;resolution=1.0`; `runs_recal_sbm_5000_10.csv` no tiene filas de modularidad. Contradice resultados.tex:209 y app0A:139,157 |
| T-03 | resultados.tex:15 + filas DBI (25,31,37,43,49,68,74,80,86,105,111,117) | DBI "solo comparable dentro de un mismo método" | ⚠️ | El dato es cierto, pero las negritas marcan el mejor DBI entre métodos distintos, lo que contradice la leyenda | Espacios de representación distintos: GCN, `z` 512-d normalizado L2 (`model.py:61`, `trainer.py:107-110`); DGI, 512-d (`dgi.py:72`); DMoN, SELU (`dmon.py:28,57-59`); DeepWalk, 128-d. Cálculo en `metrics.py:32-35` |
| T-04 | resultados.tex:95; propuesta_solucion.tex:639 | Configuración del *prior* de las columnas GCN en SBM | ⚠️ | No se indica β (el protocolo fija β=0.5 solo "en los grafos reales"). En GCN-Leiden da igual β∈{0, 0.25, 0.5}, pero β=−0.5 cambia el resultado. En SBM-10k, el k=1 de GCN-Louvain depende de β=0.5 | GCN-Leiden SBM-1k con β=−0.5: NMI 0.982±0.006, k=13 (`runs_recal_sbm_1000_5.csv`). GCN-Louvain SBM-10k con β=−0.5: k=18, NMI pico 0.976 (`runs_recal_sbm_10000_20.csv`). `validate.py:48` usa β=0.5 |
| T-05 | resultados.tex:15 | "Fila k: número de comunidades" | ⚠️ | En las columnas GCN, k es el número de comunidades del *prior* tras el filtro (dimensión de P), no el de clústeres no vacíos de la partición final; esto último no se registra | `runners/gcn.py:109` (k=`prior.k`), `prior.py:33-35`, `model.py:86-87`; en los clásicos, k = número de comunidades de la partición (`classical.py:27`) |
| T-06 | propuesta_solucion.tex:646; resultados.tex:15 | Checkpoint de pérdida mínima, "es decir, el de máxima Q'" | ⚠️ (menor) | El estado guardado es el posterior al paso del optimizador en la época de pérdida mínima: un paso de Adam más allá de los parámetros que dieron la pérdida mínima. Se hereda del código de Wang. Las cifras sí son las columnas `best` | `trainer.py:70-79` (pérdida y luego `step`), `trainer.py:88-90` (guardado posterior); Wang `main.py:74-82,192-196` |
| T-07 | resultados.tex:138 (y propuesta_solucion.tex:646) | `tab:prior-pico` usa el "valor pico del protocolo de Wang et al." | ⚠️ | Wang evalúa cada 2 épocas. Aquí el pico se toma cada 5 épocas (Amazon Computers, WikiCS) o cada 10 (PubMed, Coauthor CS); una malla más gruesa da un pico menor o igual en ambos brazos | Wang `main.py:181`; mismas fuentes que T-01 |
| T-08 | resultados.tex:104 | Negritas de la fila Q en SBM-1k | ⚠️ (menor) | Seis celdas muestran 0.518, pero solo cuatro están en negrita: DGI (0.5181) y DMoN (0.5180) no lo están. La regla sigue las medias sin redondear | `runs_sbm_1000_5.csv`, col `q`; Louvain, Leiden y ambas GCN = 0.5182 |
| T-09 | resultados.tex:15,58,95,138,170; propuesta_solucion.tex:646 | "media±desviación estándar sobre cinco semillas" | ✅ | n=5 (semillas 0–4) en todas las celdas que no son "---" | todos los CSV usados; la semilla 24 solo aparece en `runs.csv` |
| T-10 | resultados.tex:15 | Las columnas GCN corresponden al checkpoint de pérdida mínima | ✅ | Todas las celdas GCN coinciden con `nmi/ari/q/dbi` y no con `peak_*` (Cora GCN-Leiden: pico 0.554, tabla 0.530) | `runners/gcn.py:110-112`; `trainer.py:97-98` |
| T-11 | resultados.tex:15 | Los demás métodos entrenables usan su modelo entrenado, sin elegir épocas con etiquetas | ✅ | DGI: parada temprana por pérdida y modelo final. DMoN: 300 épocas y modelo final. DeepWalk: embeddings finales. Las etiquetas solo se usan para k y para evaluar | `dgi.py:55-77`; `dmon.py:48-62`; `deepwalk.py:62-66` |
| T-12 | resultados.tex:15 | DeepWalk, DGI y DMoN reciben el k de referencia | ✅ | k = número de clases. Fila k: 7, 6, 3, 15, 5, 10, 8, 5, 10, 5, 10, 20, igual que `tab:conjuntos-datos` | `dgi.py:74`, `dmon.py:43`, `deepwalk.py:63` |
| T-13 | resultados.tex:15 | El DBI se calcula en el espacio de representaciones de cada método | ✅ | Cada método pasa sus propios embeddings; los clásicos no tienen embeddings, así que su DBI es NaN | `metrics.py:32-35,47-48`; `classical.py:25`; `baseline.py:71` |
| T-14 | resultados.tex:15; propuesta_solucion.tex:639,644 | Louvain y Leiden clásicos a γ=1.0 | ✅ | Las filas con `resolution=1.0` reproducen todas las celdas; las de 0.3 no (Cora Louvain, semilla 0: NMI 0.4996 frente a 0.447) | `runs_<ds>.csv` |
| T-15 | resultados.tex:15 | "---": métrica no aplicable o corrida no completada | ✅ | DBI de los clásicos: no aplica. Actor GCN-Leiden y SBM-10k GCN-Louvain tienen k=1, así que el DBI es NaN. Coauthor Physics no tiene filas gcn-* | `metrics.py:33-34`; `runs_cophysics.csv` |
| T-16 | resultados.tex:95; propuesta_solucion.tex:639 | p_in=0.05, p_out=0.005; γ=(p_in+p_out)/2=0.0275, tomado del generador | ✅ | Coincide con el generador y con la configuración de las corridas (`cpm`, `resolution=0.0275`) | `datasets.py:29,84-85`; `recal.py:38` |
| T-17 | resultados.tex:95 | GCN-Louvain: modularidad γ=1.0 con filtro condicionado; en SBM-10k el *prior* queda en una comunidad | ✅ | Configuración `recalibrado`, `resolution=1.0`. En SBM-10k, k=1 con k0=18; σ/μ = 229.1/555.6 = 0.41 ≥ 0.25 | `runs_validate_sbm_*.csv`; `prior.py:88-91`; `validate.py:38-48` |
| T-18 | resultados.tex:95 | "con CPM ambos filtros coinciden" | ✅ | σ/μ de CPM = 1.76 / 1.71 / 1.37, mayor que τ. Con T(β=0.5) = 75.14 / 231.78 / 285.87 (no enteros), `>` y `≥` seleccionan lo mismo. Los datos vienen del filtro `wang` | `prior.py:86-91`; umbral `threshold` en `runs_recal_sbm_*.csv` |
| T-19 | propuesta_solucion.tex:639 | Grafos reales: modularidad γ=0.3, semilla 123, β=0.5 (configuración original) | ✅ | Es la configuración de todas las filas gcn-* de grafos reales y coincide con el código de Wang. El filtro estricto equivale aquí al condicionado porque T no es entero | `runs_<real>.csv`; Wang `main.py:133,138,140` |
| T-20 | propuesta_solucion.tex:646 | Comparaciones internas usan el pico; las externas, el checkpoint | ✅ | `tab:prior-pico` y `tab:recal-*` coinciden con `peak_*`; las tablas principales, con `best` (matiz en T-07) | ver T-10 y T-84 a T-116 |
| T-21 | resultados.tex:165,170 | Nivel común = 95 % del menor Q' máximo medio; primera época que lo alcanza; Actor excluido | ✅ | La definición reproduce las 35 cifras (con `≥` y con `>` igual). Actor: Q' constante en −2.9e-6 en las 5 corridas de Leiden | `convergence_check.py`; `history_film/gcn-leiden_*` |
| T-22 | app0A.tex:104 | `tab:recal-beta`: γ=0.3, modularidad, NMI pico, k; β=−0.5 desactiva el filtro | ✅ | Con β=−0.5, T<0 (−18.57, −16.44, −12.03, −12.39), así que k=k0 (89, 90, 452, 451) | `runs_recal_{cora,citeseer}.csv` |
| T-23 | app0A.tex:122 | `tab:recal-sbm`: k verdadero 5/10/20; a γ=0.3 colapsa; celdas ausentes por σ_s=0 | ✅ | Los clásicos a γ=0.3 dan k=1 en las 15 corridas, y con el filtro estricto se descarta todo (`prior.py:84-87,99-102`). SBM-5k: `threshold`=500.0=μ con β=0.5, luego σ=0 | `runs_sbm_*.csv` (res=0.3); `runs_validate_sbm_5000_10.csv` |
| T-24…T-48 | resultados.tex:22–50 | `tab:resultados-citas-coautoria`: Cora, CiteSeer, PubMed, Coauthor CS y Coauthor Physics × NMI, ARI, Q, DBI, k | ✅ | 25 filas: 7/7 celdas coinciden en cada una, negritas incluidas. Límite x.xxx5: Cora Q GCN-Louvain (0.7625→0.762), Cora DBI DMoN (0.9235→0.923), Coauthor Physics Q DeepWalk (0.4735→0.474) y DGI (0.5175→0.517) | `runs_<ds>.csv` (filtros arriba); detalle por fila en `rows_all.md` |
| T-49…T-68 | resultados.tex:65–87 | `tab:resultados-compra-web`: Amazon Computers, Amazon Photo, Actor y WikiCS × 5 métricas | ✅ | 20 filas: 7/7 en cada una, negritas incluidas. Límite: Amazon Photo DBI DMoN (1.2495→1.250), Actor Q Leiden (0.5165→0.516). Signos −0.000 correctos (Actor GCN-Louvain ARI = −0.00002) | `runs_{amac,amap,film,wikics}.csv` |
| T-69…T-83 | resultados.tex:102–118 | `tab:resultados-sbm`: SBM-1k, SBM-5k y SBM-10k × 5 métricas | ✅ | 15 filas, 7/7 en cada una. SBM-1k ARI Leiden: la tesis da 0.989 y mi cálculo en coma flotante 0.988, pero la media decimal exacta es 0.98850, así que es solo redondeo en el límite (Louvain, DGI y ambas GCN también caen en x.xxx5). Negritas: T-03 y T-08 | `runs_sbm_*.csv` + `runs_validate_sbm_*.csv` (GCN-Louvain) + `runs_recal_sbm_*.csv` (GCN-Leiden, cpm, β=0.5) |
| T-84…T-99 | resultados.tex:146–153 | `tab:prior-pico`: 8 grafos × NMI y ARI pico | ✅ | 32/32 celdas coinciden. Límite: Amazon Photo NMI GCN-Leiden (0.6535→0.653) | `runs_<ds>.csv` gcn-*, `peak_nmi`/`peak_ari` |
| T-100 | resultados.tex:176 | Cora: 0.724; 64.8±1.1; 63.2±1.8 | ✅ | Objetivo 0.72361; épocas [66,64,64,64,66] y [64,64,60,64,64] | `history_cora` |
| T-101 | resultados.tex:177 | CiteSeer: 0.740; 42.4±0.9; 44.8±1.1 | ✅ | Objetivo 0.73952 | `history_citeseer` |
| T-102 | resultados.tex:178 | PubMed: 0.616; 100.0±0.0; 104.0±5.5 | ✅ | Leiden [100,100,100,110,110], en malla de 10 épocas (T-01) | `history_pubmed` |
| T-103 | resultados.tex:179 | Coauthor CS: 0.620; 30.0±0.0; 30.0±0.0 | ✅ | Malla de 10 épocas (T-01) | `history_cocs` |
| T-104 | resultados.tex:180 | Amazon Computers: 0.519; 58.0±2.7; 58.0±2.7 | ✅ | [55,60,55,60,60] en ambos, malla de 5 épocas | `history_amac` |
| T-105 | resultados.tex:181 | Amazon Photo: 0.612; 49.2±1.1; 49.2±1.1 | ✅ | Objetivo 0.61188 | `history_amap` |
| T-106 | resultados.tex:182 | WikiCS: 0.522; 79.0±2.2; 94.0±4.2 | ✅ | Malla de 5 épocas | `history_wikics` |
| T-107/108 | app0A.tex:110–111 | `tab:recal-beta`, Cora: NMI pico (8 celdas) y k | ✅ | 8/8 coinciden; k = 89,10,9,9 / 90,11,10,10; negritas (empate en β=0.25 y 0.5) correctas | `runs_recal_cora.csv`, `peak_nmi`, k |
| T-109/110 | app0A.tex:113–114 | `tab:recal-beta`, CiteSeer: NMI pico y k | ✅ | 8/8 coinciden; k = 452,32,13,11 / 451,31,13,11; negrita en β=0.5 correcta | `runs_recal_citeseer.csv` |
| T-111/112 | app0A.tex:128–139 | `tab:recal-sbm`, SBM-1k: NMI y k (12 filas) | ✅ | 12/12 coinciden; k = 13,5,5,5 / 3,2,2,2 / 3,2,2,2 | `runs_recal_sbm_1000_5.csv`, `peak_nmi` |
| T-113/114 | app0A.tex:141–144 | `tab:recal-sbm`, SBM-5k: NMI y k | ✅ | 4/4 coinciden (1.000, k=10) | `runs_recal_sbm_5000_10.csv` |
| T-115/116 | app0A.tex:146–157 | `tab:recal-sbm`, SBM-10k: NMI y k | ✅ | 12/12 coinciden; k = 20×4 / 16,3,3,3 / 18,1,1,1 | `runs_recal_sbm_10000_20.csv` |

(En `rows_all.md` está una fila por (tabla, dataset, métrica) para T-24…T-99, con el filtro exacto de cada una.)

### 2. Cobertura de los números en líneas añadidas (`+`) dentro de mi alcance
- **resultados.tex:15** ("cinco semillas", γ=1.0) → T-09, T-14. Celdas en :22–50 → T-24…T-48.
- **resultados.tex:58** ("cinco semillas") → T-09. Celdas en :65–87 → T-49…T-68.
- **resultados.tex:95:**
  - p_in, p_out y (p_in+p_out)/2 → T-16
  - γ=1.0, SBM-10k, "una sola comunidad" → T-17
  - "no ejecutables" → T-02
  - β no declarado → T-04
- **resultados.tex:102–118** → T-69…T-83.
- **resultados.tex:138** → T-07, T-09. Celdas en :146–153 → T-84…T-99.
- **resultados.tex:165 y :170** (95 %, "cada dos épocas", k=1, "cinco semillas") → T-21, T-01, T-09. Celdas en :176–182 → T-100…T-106.
- **propuesta_solucion.tex:639** (γ=0.3, 123, β=0.5, γ=1.0, 0.0275, punto medio) → T-19, T-16, T-17, T-14.
- **propuesta_solucion.tex:646:**
  - "cinco semillas" → T-09
  - "cada dos épocas", referido al código de Wang → cierto según `main.py:181`; la regla de vistas está en T-20, con el matiz de T-07
- **Apéndice:** `app0A.tex` no cambió en el diff. Lo verifiqué igualmente por estar en mi alcance: T-22, T-23, T-107…T-116.
- **Fuera de mi alcance:** el resto de números de la prosa de :123–222 corresponde a otros grupos.

### 3. Correcciones mínimas propuestas
- **T-01:** "La evaluación se realiza cada dos épocas (cada cinco en Amazon Computers y WikiCS, y cada diez en PubMed y Coauthor CS)". Ajustar igual :165 ("registran $Q'$ cada dos épocas") y :187.
- **T-02:** "…con el filtro condicionado, sin el cual el *prior* conserva solo 2 de los 5 bloques en SBM-1k y la corrida no es ejecutable en SBM-5k (Sección…)".
- **T-03:** quitar las negritas de las filas DBI, o escribir "Negritas: mejor valor por fila en $NMI$, $ARI$ y $Q$".
- **T-04:** añadir "$\beta = 0.5$" a la leyenda SBM, o en propuesta:639 ("En los grafos SBM … y $\beta = 0.5$").
- **T-05:** "Fila $k$: número de comunidades; en las columnas GCN, comunidades ancla del *prior* tras el filtro".
- **T-06 (opcional):** "el estado guardado en la época de pérdida mínima (tras su paso de optimización, como en el código original)".
- **T-07:** añadir a la leyenda de `tab:prior-pico`: "evaluación cada 2 épocas (cada 5 en Amazon Computers y WikiCS; cada 10 en PubMed y Coauthor CS)".
- **T-08:** poner en negrita las seis celdas 0.518 de la fila Q de SBM-1k, o indicar que las negritas se asignan sobre valores sin redondear.

### 4. Lo que no pude verificar
- **k de las GCN:** si coincide con el número de clústeres no vacíos de la partición final. No se registra en ningún CSV.
- **Colapso de SBM a γ=0.3 con la semilla del *prior* (123):** no hay corridas GCN a γ=0.3 en SBM (`recal.py:43-44` las excluye). Lo infiero de los clásicos con semillas 0–4, que dan k=1 en los 15 casos.
- **Causa de que Coauthor Physics no complete (memoria de la GPU):** no hay registros; solo consta que no existen filas gcn-*.
