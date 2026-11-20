# Verificación del artículo frente a la tesis (fuente de verdad)

## Objetivo
Determinar, con evidencia, si el artículo `PAPER/main.tex` dice exactamente lo que respalda la
tesis revisada y los datos. Postura adversarial. **No edites nada**: solo reporta. No revises
ortografía ni estilo; solo contenido (verdad, fidelidad a la tesis, consistencia interna).

## Contexto
- PAPER = `/Users/omar/Developer/me/gnn-paper` (LaTeX, español, 8 páginas, dos columnas).
  El cambio que verificas es `git -C PAPER diff` (working tree contra el único commit).
- THESIS = `/Users/omar/Developer/me/gnn-thesis`: fuente de verdad, ya verificada contra los datos.
- CODE = `/Users/omar/Developer/me/gcn-leiden`: resultados en `results/` (`runs_*.csv`,
  semillas 0–4; `history/`), código en `gcn_leiden/` y `experiments/`.
- Regla editorial del artículo: su texto se extrae **textualmente** de la tesis. Solo se permiten
  ajustes mecánicos ("esta tesis" → "este trabajo", referencias cruzadas a etiquetas que el
  artículo no tiene, `\mycaption` → `\caption`) y recortes por eliminación de frases o párrafos.
  Además, el autor aprobó estas excepciones:
  1. "cuatro métricas (… y DBI)" → "tres métricas" en el Resumen y en Métricas, porque el
     artículo no reporta DBI;
  2. en la leyenda de la Tabla 1 se quita la frase del DBI y la nota "---" se reemplaza por la
     nota de que Coauthor Physics se omite;
  3. en Recalibración, "(Tabla A.3)" de la tesis → "(valores pico)";
  4. en Conclusiones, el artículo no tiene hipótesis: se quitan las frases de veredicto y la de
     H2 se reformula sin mencionar la hipótesis;
  5. recorte para entrar en 8 páginas: sin párrafos generales de la Introducción, sin la
     definición formal del problema (y sin las dos frases sobre S que dependían de ella), sin el
     párrafo de DMoN, sin la salvedad PyG/ADGC y sin el párrafo "La modularidad Q mide"; las
     tablas no tienen filas DBI ni de Coauthor Physics; interlineado de tablas 1.05.
- El artículo no tiene apéndice ni hipótesis. Sus preguntas de investigación corresponden 1:1 a
  las P1–P4 de la tesis.

## Qué verificar
1. **Fidelidad:** cada párrafo del artículo frente a su fuente en la tesis. Toda diferencia que
   no sea un ajuste mecánico o una de las excepciones aprobadas es un hallazgo. Cita las dos
   ubicaciones.
2. **Tablas:** cada celda de las Tablas 1–3 (incluida la fila k), de la tabla de valores pico y
   de la tabla de convergencia frente a la tesis y frente a los CSV; negritas (mejor media sin
   redondear en NMI, ARI y Q); leyendas.
3. **Coherencia tras los recortes:** referencias colgantes (símbolos, matrices, tablas,
   secciones o ideas que el texto usa pero que ya no se definen en el artículo), frases que
   remiten a contenido eliminado ("como se mencionó", "la siguiente sección", etc.), numeración
   y referencias a preguntas de investigación ("la cuarta pregunta", etc.).
4. **Restos del texto viejo:** cualquier frase que aún contradiga la tesis revisada (memoria
   o VRAM, valores pico usados contra baselines, "mejor ARI en Amazon", SBM "no ejecutables",
   β "óptimo", 16 % de Traag, causa de Physics, etc.).
5. **Compilación:** compila una copia con
   `PATH=/Library/TeX/texbin:$PATH latexmk -pdf -interaction=nonstopmode main.tex` dentro de tu
   carpeta (copia `main.tex` y `references.bib`; no compiles dentro del repo). Comprueba que sean
   8 páginas y que no haya referencias `\ref` rotas. La advertencia de biblatex "Please (re)run
   BibTeX" ya aparecía en el artículo original.

## Herramientas y límites
- Python: `uv run --no-project -q --with pandas --with scipy python -I script.py`.
- Trabaja solo en `SCRATCH/verify_paper/out/`
  (SCRATCH = `/private/tmp/claude-501/-Users-omar-Developer-me-gcn-leiden/ddebb875-fe4a-43f3-ab25-1ab06b6b4a1f/scratchpad`).
- No leas ni ejecutes nada en `SCRATCH/scripts/` ni `SCRATCH/paper*/` (son de quien editó).
- No modifiques archivos de los repos.

## Veredictos y entrega
✅ verificado · ⚠️ cierto con matiz · ❌ falso o infiel a la tesis · ❓ sin evidencia.
Entrega:
1. Tabla `| id | ubicación en el artículo | afirmación/cambio (≤15 palabras) | veredicto | por qué (≤1 línea) | evidencia (tesis:línea, CSV o código) |`
   (ids `P-xx`; orden ❌, ❓, ⚠️, ✅). Agrupa los ✅ por sección o tabla.
2. Lista de referencias colgantes o frases que remiten a contenido eliminado.
3. Para cada ❌/⚠️/❓, la corrección mínima, priorizando el texto literal de la tesis.
4. Una línea con lo que no pudiste verificar.
