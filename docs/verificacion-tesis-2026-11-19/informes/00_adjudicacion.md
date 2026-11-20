# Adjudicación consolidada

Síntesis de los cuatro informes de la primera ronda (`01`–`04`) y de la reverificación (`05`). Cada ❌/❓/⚠️ se contrastó con evidencia propia antes de proponer una corrección. Todas las correcciones se aplicaron con aprobación explícita. Ninguna tiene commit al cierre de esta verificación.

Veredictos: ✅ verificado · ⚠️ cierto con matiz · ❌ falso · ❓ sin evidencia en los artefactos.

## Ronda 1: revisión `b44f221..25b1c32` (≈257 afirmaciones)

Las cifras de todas las tablas (≈600 celdas) se recalcularon desde los CSV y las trayectorias, y coinciden: solo hay un caso de redondeo en el límite (0.98850). Los problemas estaban en la redacción. Siete de los nueve ❌ los introdujo la propia revisión.

| # | Dónde | Afirmación | Veredicto | Por qué | Corrección aplicada |
|---|---|---|---|---|---|
| 1 | Cap. 4, filtro | Wang fija 0.5 "sin análisis de sensibilidad" | ❌ | La versión citada (Sci. Rep. 15:39249) barre 0.1–1.0, con el mejor resultado entre 0.4 y 0.6. Solo el preprint arXiv v1 omite este análisis. | Se restauró la afirmación original, ahora con detalle |
| 2 | 5.1.3, `convergence.py` | "Q' se registra cada dos épocas" | ❌ | Se registra cada 5 en Amazon Computers y WikiCS, y cada 10 en PubMed y Coauthor CS | Se indica la rejilla de cada grafo |
| 3 | Leyenda de la Tabla 5.3 | Sin filtro condicionado "no son ejecutables" | ❌ | SBM-1k corre con k=2 y SBM-10k con k=1. Solo SBM-5k es imposible | Precisado |
| 4 | 5.2.4 | "En SBM-1k y SBM-5k las corridas imposibles se completan" | ❌ | El mismo problema que la fila 3 | Precisado |
| 5 | Cap. 4, protocolo | Las comparaciones "se apoyan sobre todo en el ARI" | ❌ | P1, la recalibración y H1/H2 usaban NMI | Reescrito (H2 pasa a ARI) |
| 6 | Limitaciones | El barrido de β "cubre solo Cora y CiteSeer" | ❌ | También se barrió Actor | Se añadió Actor |
| 7 | Trabajo relacionado:73 | "choca con el objetivo de bajo consumo de VRAM" | ❌ | Es un resto del objetivo de memoria eliminado | Se quitó la cláusula |
| 8 | `convergence.py` | Todas las corridas alcanzan el nivel fijo | ❌ | Al 99 % un par de Cora no lo alcanza y se descarta (n=34) | Documentado, también en la tesis |
| 9 | `baselines/__init__.py` | Dar el k real "mirrors Wang" | ❌ | Wang entrega a sus baselines el k detectado por su método | Docstring corregido |
| 10 | Resumen, Abstract, 5.1.1, Conclusiones | Physics falla porque "B densa excede la GPU" | ❓ | No hay log (ver más abajo). B ocupa 4.4 GiB; el total son varias matrices n×n | Se quitó la afirmación causal |
| 11 | H2 y veredictos | El filtro mejora el NMI | ⚠️ | Solo con el pico. Con el checkpoint, el NMI no sube y el ARI sí; sin filtro quedan ~450 comunidades | H2 se reformuló en ARI |
| 12 | P4 / hipótesis central | "Se acerca a DGI en Cora… debajo en CiteSeer" | ⚠️ | Con la regla de 1σ, Cora y CiteSeer estaban invertidos y faltaba WikiCS | Reescrito con la clasificación correcta |
| 13 | Resumen y Abstract | "no los supera"; "más estable que DGI"; "los profundos integran características" | ⚠️ | En Amazon la media de la GCN es mayor; el problema de DGI es el colapso, no la varianza; DeepWalk no usa características | Matizado |
| 14 | 5.1.1 | Comparativos en CS, WikiCS, Amazon y SBM; referente de "Su" | ⚠️ | Dependían de la métrica o estaban por debajo de 1σ | Precisado |
| 15 | P1 / H1 | Gana, empata o pierde según 1σ | ⚠️ | No se decía qué σ ni qué métrica; Actor es un colapso | Precisado |
| 16 | Recalibración | "β=0.5 es el mejor"; "Leiden gana en Cora con los cuatro β" | ⚠️ | Empata con 0.25; con β=0 la diferencia es ≈1σ | Matizado |
| 17 | Convergencia | p=0.009; k distinto; niveles de Q' | ⚠️ | Sin WikiCS, p>0.1; las semillas comparten el prior; k solo difiere en Cora y PubMed; hay diferencias por grafo | Se añadieron las salvedades |
| 18 | Leyendas y protocolo | Negritas en DBI; β en SBM; fila k; pico; trayectorias | ⚠️ | Contradicciones internas y omisiones | Ajustado |
| 19 | Cap. 4 (Traag) | Hasta 25 %/16 % | ⚠️ | Son los máximos al iterar; en la primera iteración rondan el 1 % | Matizado |
| 20 | Trabajo relacionado:44, Trabajo futuro, Intro | "el prior reduce el costo"; la descomposición de B permitiría Physics; CLIQUE | ⚠️ | El costo no se mide; A y la diagonal siguen densas; la cita de CLIQUE no la respalda | Suavizado. Para CLIQUE se añadió después la cita de Karp (1972), con metadatos verificados en Crossref |

### Verificado como correcto (✅)

| Área | Resultado |
|---|---|
| Tablas 5.1–5.5, A.2 y A.3 | ≈600 celdas recalculadas; todas coinciden |
| Regla de las dos vistas | La correspondencia de columnas, los baselines sin selección por etiquetas y el k de referencia coinciden con el código |
| Configuración del prior | γ=0.3, semilla 123 y β=0.5 coinciden con el código de Wang; CPM usa el punto medio del generador |
| Wang (ambas versiones) | Max por métrica, checkpoint de pérdida mínima, una corrida, k detectado, ≥ frente a >, signo de δ |
| Prosa de Resultados | Todas las cifras se reproducen |
| Convergencia | La tabla y los estadísticos se reproducen con un cálculo independiente |
| Filtro condicionado | σ/μ, el rango de τ y la paridad bit a bit en Cora y CiteSeer |
| Consistencia | Compila; las `\ref` son correctas; la numeración P/H/O es coherente; el Resumen equivale al Abstract |

## Coauthor Physics: búsqueda de evidencia del OOM

- `runs_cophysics.csv` (local y bucket, archivos idénticos, creado el 2026-06-12T07:46:47Z) no tiene filas GCN, y no existe `history_cophysics`.
- El bucket `gs://gcn-leiden-results` solo contiene CSV y trayectorias, sin logs. El listado está en `../evidencia/physics/bucket_listing.txt`.
- El bucket `_Default` de Cloud Logging retiene 30 días, así que los logs de junio expiraron. Solo quedan los de auditoría (`_Required`, 400 días), que no registran errores de proceso.
- La única referencia es el comentario `launch_shards.sh:63` ("dense loss OOMs"), añadido después de las corridas.
- Estimación desde el código: la GPU mantiene varias matrices densas n×n (adyacencia, B, temporales y la normalización diagonal de `model.py:61` con su gradiente), de 4.43 GiB cada una.

**Decisión:** la tesis afirma solo que las corridas no completaron y describe las matrices densas, sin atribuir la causa.

## Ronda 2: reverificación de las correcciones

| # | Dónde | Problema | Veredicto | Corrección aplicada |
|---|---|---|---|---|
| 1 | 5.2.4 y `prior.py` | "alrededor de 0.007" (los valores son 0.0071, 0.0045 y 0) | ❌ | "como máximo 0.0071" |
| 2 | Trabajo relacionado:44 | LCCF no se puede verificar sin el artículo | ❓ | Sin cambio (reformula la descripción citada) |
| 3 | 5.1.1, P4, veredicto 4, Resumen y Abstract | "No los supera en ninguno" solo vale en NMI y ARI. En Q supera al mejor profundo en Cora, CiteSeer y PubMed | ⚠️ | Precisado, con la observación sobre Q |
| 4 | 5.2.1, P2, Contribución 3 | "β=0.5 es el mejor": el siguiente valor empata dentro de 1σ, y en Cora β=0 iguala o supera en ARI | ⚠️ | "ningún valor lo supera con claridad" |
| 5 | 5.1.2 | Convención de diferencias inconsistente | ⚠️ | Se usan las diferencias de la tabla (Photo +0.004) |
| 6 | 5.1.1 | Photo, WikiCS y Amazon Computers: empates incompletos | ⚠️ | Precisado |
| 7 | Leyenda de la Tabla 5.2 | "mejor valor por fila" frente a DBI sin negritas | ⚠️ | "como en la Tabla 5.1" |
| 8 | Protocolo | Rejilla de evaluación sin los SBM | ⚠️ | Se añadió (5 en SBM-1k/5k, 10 en SBM-10k) |
| 9 | 5.1.3 | "Empates sobre todo en rejillas de 5/10" (apoyo débil) | ⚠️ | Cláusula eliminada |
| 10 | Leyenda de la Tabla 5.3 | Parecía que β también venía del generador | ⚠️ | Redacción corregida |

La comprobación final de las líneas de esta ronda la hizo quien editó, no un verificador independiente. Se recalcularon Q, ARI por β, los empates, las rejillas de SBM y la compilación.

## Otros cambios y pendientes

- `frontmatter/simbolos.tex:75`: "Sección~5" estaba escrito a mano y apuntaba al capítulo de Resultados. Ahora es `Definición~\ref{def:modularidad}` (Definición 16, Sección 2.5).
- `propuesta_solucion.tex:637`: decía "La Ecuación~6 conserva las comunidades con |C_i| ≥ T", lo que se podía confundir con la numeración de la tesis. En el artículo, la Ec. 6 define T y la condición ≥ aparece en la frase siguiente. Ahora dice: "Wang et al. definen el umbral en su Ecuación~6 y conservan las comunidades con |C_i| ≥ T, pero su código usa la desigualdad estricta |C_i| > T". Se verificó que la Ec. 6 es T = μ + 0.5σ también en la versión publicada (Sci. Rep., PMC12603060, `<label>6</label>`).
