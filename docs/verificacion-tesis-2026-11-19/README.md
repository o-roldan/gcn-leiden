# Verificación sistemática de la revisión de la tesis (2026-11-19)

Registro de la verificación de contenido de los cambios hechos a la tesis (`../gnn-thesis`) en la revisión del 2026-11-19. El objetivo fue comprobar que cada afirmación modificada fuera cierta, con evidencia, antes de presentarla al comité. Solo se revisó el contenido; la ortografía y el estilo quedaron fuera.

## Método

1. **Congelar (F0).** Se guardó el diff verificado: commits `b44f221..25b1c32` del repo de la tesis más los cambios sin commit de este repo (`patches/`).
2. **Verificación independiente (F1–F2).** Cuatro verificadores con effort xhigh, sin acceso a las conclusiones ni a los scripts de quien editó, recalcularon cada afirmación desde las fuentes originales. Se dividieron por tipo: tablas, prosa de Resultados y Conclusiones, metodología/código/literatura y consistencia global. Las reglas comunes están en `brief_comun.md`.
3. **Adjudicación (F3).** Cada ❌/❓/⚠️ se comprobó con evidencia propia y se propuso una corrección mínima. Las correcciones se aplicaron solo tras la aprobación del autor.
4. **Reverificación.** Un quinto verificador independiente revisó las correcciones; sus hallazgos se corrigieron con el mismo procedimiento.

## Contenido

| Ruta | Qué es |
|---|---|
| `informes/00_adjudicacion.md` | **Empieza aquí.** Tablas consolidadas de las dos rondas, la búsqueda de evidencia sobre Coauthor Physics y los pendientes |
| `informes/01_consistencia.md` … `05_reverificacion_ronda2.md` | Informe textual de cada verificador: tabla de afirmaciones, cobertura de números, correcciones propuestas y lo no verificado |
| `brief_comun.md` | Instrucciones y reglas de evidencia que recibieron los verificadores |
| `patches/1_*` | Diff verificado en la ronda 1 (tesis `b44f221..25b1c32` y código) |
| `patches/2_*` | Correcciones de la ronda 1, verificadas en la ronda 2 |
| `patches/3_*` | Estado final sin commit respecto de `25b1c32` (tesis) y del código |
| `evidencia/<grupo>/` | Scripts y salidas de cada verificador (`tablas`, `texto`, `metodo`, `consistencia`, `reverif`) y el listado del bucket (`physics/`) |
| `scripts_revision/` | Scripts con los que se hicieron las ediciones de la revisión (procedencia) |

## Notas para reutilizar

- Los scripts usan rutas absolutas del scratchpad de la sesión (`/private/tmp/claude-501/...`), que ya no existe. Para volver a ejecutarlos, cambia esas rutas por `results/` de este repo y la ruta de la tesis.
- No se copiaron builds de LaTeX, logs, PDFs ni textos completos de artículos. Fuentes usadas:
  - Wang et al., *Simple yet effective heuristic community detection with graph convolution network*, Scientific Reports 15:39249 (2025), DOI 10.1038/s41598-025-22860-z (texto en Europe PMC, PMC12603060). Preprint: arXiv 2501.12946. Código: https://github.com/wuanghoong/Less-is-More
  - Traag, Waltman y van Eck, *From Louvain to Leiden: guaranteeing well-connected communities*, Scientific Reports (2019); arXiv 1810.08473.
- El análisis de convergencia (P3) se reproduce con `uv run --extra analysis python -m experiments.analysis.convergence results`.
