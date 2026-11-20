# Verificación de contenido de una tesis — instrucciones comunes

## Objetivo
Determinar, con evidencia, si cada afirmación factual dentro de tu alcance es cierta.
Postura adversarial: una afirmación es "no verificada" hasta que encuentres evidencia
directa en las fuentes. **No edites nada**: solo reporta. No revises ortografía ni
estilo; solo contenido (verdad, precisión, consistencia).

## Qué se verifica
Una revisión reciente modificó la tesis. El objeto a verificar es el diff entre el
commit `b44f221` (antes de la revisión) y `HEAD` del repo de la tesis:
- Diff completo: `SCRATCH/verify/thesis.patch` (equivale a `git -C THESIS diff b44f221 HEAD -- '*.tex'`).
- Cambios en el repo de código: `SCRATCH/verify/code.patch` (working tree sin commit).
- El texto vigente está en los archivos de la tesis (cita siempre `archivo:línea` del archivo actual).
- Puedes ver el texto anterior con `git -C THESIS show b44f221:<ruta>`.

Además de las líneas añadidas, entra en tu alcance el texto **no modificado que dependa
de lo modificado** (p. ej., una frase vieja que cite un número, sección o pregunta que cambió).

## Rutas
- THESIS = `/Users/omar/Developer/me/gnn-thesis` (LaTeX, español). Capítulos en
  `chapters/*/*.tex`; resumen y abstract en `frontmatter/`. **Fuera de alcance:**
  `chapters/marco_teorico/`.
- CODE = `/Users/omar/Developer/me/gcn-leiden` (código y resultados de los experimentos).
- SCRATCH = `/private/tmp/claude-501/-Users-omar-Developer-me-gcn-leiden/ddebb875-fe4a-43f3-ab25-1ab06b6b4a1f/scratchpad`

## Fuentes de verdad
- Resultados en `CODE/results/`:
  - `runs_<dataset>.csv`: barrido principal. `runs_recal_<dataset>.csv`: barrido de
    recalibración del filtro. `runs_validate_<dataset>.csv`: validación del filtro
    condicionado.
  - Columnas: `timestamp,method,dataset,seed,k,epochs,runtime_s,nmi,ari,q,dbi,peak_nmi,peak_ari,peak_q,peak_dbi,ram_peak_mb,vram_peak_mb,config`.
    `config` es `clave=valor;...` (p. ej. `beta`, `resolution`, `prior_objective`,
    `filter_variant`, `k0` = comunidades del prior antes del filtro, `threshold` = umbral T,
    `prior_seed`).
  - Trayectorias por época: `CODE/results/history/history_<grupo>/<método>_<dataset>_seed<s>.csv`
    (columnas `epoch,loss,nmi,ari,q,dbi`, a veces `grad_norm`).
  - Los experimentos de la tesis usan **semillas 0–4**. Filas/archivos con seed 24 son
    corridas locales sueltas: exclúyelas salvo que el texto se refiera a ellas.
  - Datasets: cora, citeseer, pubmed, cocs (Coauthor CS), cophysics (Coauthor Physics),
    amac (Amazon Computers), amap (Amazon Photo), film (Actor), wikics, sbm_1000_5,
    sbm_5000_10, sbm_10000_20 (SBM-1k, -5k, -10k).
- Código: `CODE/gcn_leiden/` (arquitectura) y `CODE/experiments/` (baselines, runners,
  barridos, despliegue, análisis).
- Artículo de referencia, Wang et al. 2025 (arXiv 2501.12946): texto extraído en
  `SCRATCH/wang/wang.txt` (marcadores `=== PAGE n`), PDF en `SCRATCH/wang/wang.pdf`.
  Código oficial clonado en `SCRATCH/wang-code/` (`main.py`, `model.py`). Solo lectura;
  **no ejecutes** ese código.
- Traag, Waltman y van Eck 2019 (Leiden): texto extraído en
  `SCRATCH/verify/sources/traag2019.txt`, PDF en `SCRATCH/verify/sources/traag2019.pdf`.
- Bibliografía de la tesis: `THESIS/references.bib`.

## Herramientas y límites
- Python: `uv run --no-project -q --with pandas --with scipy python -I tu_script.py`.
  (Si quieres usar el paquete del repo: `cd CODE && uv run --extra analysis python ...`.)
- Escribe tus scripts y salidas **solo** en tu carpeta `SCRATCH/verify/<tu-grupo>/`.
- **No leas ni ejecutes** nada en `SCRATCH/scripts/`, ni archivos `*_new.tex`, ni
  `SCRATCH/conv_runs.csv`: son artefactos de quien hizo la revisión, y esta verificación
  debe ser independiente. Recalcula todo por tu cuenta.
- No modifiques archivos de la tesis ni del repo. No hagas commits.

## Reglas de evidencia
- **Números**: recalcúlalos desde los CSV o las trayectorias. Indica el filtro exacto que
  usaste (archivo, `method`, semillas, valores de `config`). Salvo que el texto diga otra
  cosa: media ± desviación estándar muestral (ddof=1) sobre las 5 semillas, redondeo a 3
  decimales. Si dos fuentes plausibles dan valores distintos, repórtalo.
- **Código**: cita `archivo:línea`.
- **Literatura**: cita textual breve con página.
- **Comparativos** ("gana", "supera", "mejor", "empata", "se acerca", "iguala"): si el
  texto no especifica la métrica, verifica en NMI y en ARI. Señala si la diferencia es
  menor a una desviación estándar.
- Afirmación = cualquier proposición verificable: números, comparaciones, conteos,
  descripciones de lo que hace el código o un artículo, referencias cruzadas,
  definiciones operativas.

## Veredictos
✅ verificado · ⚠️ cierto con matiz (impreciso, ambiguo o dependiente de la métrica) ·
❌ falso · ❓ sin evidencia en los artefactos disponibles

## Entrega (tu respuesta final)
1. Tabla markdown:
   `| id | archivo:línea | afirmación (≤15 palabras) | veredicto | por qué (≤1 línea) | evidencia (fuente exacta) |`
   con ids prefijados por tu grupo (p. ej. `T-01`). Orden: ❌, ❓, ⚠️, ✅.
2. **Cobertura**: todos los números que aparecen en líneas añadidas (`+`) del diff dentro de
   tu alcance, cada uno asociado a un id (o marcado "no es afirmación" con razón breve).
   Puedes agrupar números que pertenezcan a una misma afirmación o celda de tabla.
3. Para cada ❌/⚠️/❓: la **corrección mínima** que propondrías (no la apliques).
4. Al final, una línea con lo que **no** pudiste verificar y por qué.
