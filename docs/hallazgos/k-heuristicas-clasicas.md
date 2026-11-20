# Por qué Louvain y Leiden clásicos producen tantas comunidades

Hallazgo del 2026-11-20, pensado para una lámina de la defensa. Explica la fila *k* de las Tablas 5.1–5.3 de la tesis (y 2–4 del artículo).

## Mensaje principal

1. **DeepWalk, DGI y DMoN no estiman k: lo reciben.** El protocolo les entrega el número de clases de las etiquetas (`experiments/baselines/dgi.py:74`, `dmon.py:43`, `deepwalk.py:63`). Su *k* bajo no es un resultado.
2. **Louvain y Leiden clásicos inflan k por las componentes desconectadas.** La modularidad nunca une dos partes del grafo sin aristas entre sí, porque fusionarlas siempre reduce Q. Además, Louvain solo mueve cada nodo hacia comunidades de sus vecinos. Por eso **cada componente conexa termina como al menos una comunidad, y cada nodo aislado queda solo**.
3. **Dentro de la componente gigante, k baja a 16–40.** Sigue siendo mayor que el número de clases, porque con γ = 1.0 la modularidad detecta estructura topológica más fina que las etiquetas temáticas.
4. **Las variantes GCN obtienen k pequeños por diseño.** El *prior* usa γ = 0.3, que produce comunidades más grandes, y el filtro de tamaño descarta las pequeñas, incluidas esas componentes sueltas.

## Datos

Louvain clásico con resolución γ = 1.0 y semilla 0 (el mismo *k* que `results/runs_<dataset>.csv` registra para la semilla 0: Cora 102, CiteSeer 471, Amazon Computers 331).

| Grafo | Nodos | Componentes conexas | Nodos aislados | % en la componente gigante | k de Louvain | …componentes enteras | …dentro de la gigante | k de referencia |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Cora | 2 708 | 78 | 0 | 91.8 % | 102 | 77 | 25 | 7 |
| CiteSeer | 3 327 | 438 | 48 | 63.7 % | 471 | 437 | 34 | 6 |
| Amazon Computers | 13 752 | 314 | 281 | 97.3 % | 331 | 313 | 18 | 10 |
| Amazon Photo | 7 650 | 136 | 115 | 97.9 % | 151 | 135 | 16 | 8 |
| WikiCS | 11 701 | 356 | 337 | 96.7 % | 372 | 355 | 17 | 10 |
| PubMed | 19 717 | 1 | 0 | 100 % | 40 | 0 | 40 | 3 |
| Coauthor CS | 18 333 | 1 | 0 | 100 % | 26 | 0 | 26 | 15 |
| Actor | 7 600 | 1 | 0 | 100 % | 31 | 0 | 31 | 5 |

Columnas:
- **Componentes enteras:** comunidades de Louvain que coinciden exactamente con una componente conexa, incluidas las de un solo nodo.
- **Dentro de la gigante:** comunidades de Louvain dentro de la componente conexa más grande.

Lectura rápida:
- En CiteSeer, 437 de las 471 comunidades son componentes sueltas, y 48 de ellas son nodos aislados.
- En Amazon Computers, Amazon Photo y WikiCS, casi todo el exceso viene de nodos aislados (281, 115 y 337).
- En los grafos conexos (PubMed, Coauthor CS y Actor), el exceso se debe solo a la resolución.
- Por eso *k* varía apenas ±1–2 entre semillas: el número de componentes es fijo, y solo cambia la partición de la componente gigante. Rangos de las tablas: Cora 102–105, CiteSeer 469–472, Amazon Computers 329–332.

## Consecuencia para la lectura de resultados

El NMI tiende a crecer con el número de clústeres, y el ARI corrige el acuerdo por azar. Con cientos de comunidades, el NMI de las heurísticas clásicas aparece alto mientras su ARI queda bajo; por ejemplo, en CiteSeer el NMI es 0.328, con ARI 0.091 y k ≈ 470. Por eso la tesis apoya en el ARI las comparaciones en las que *k* difiere mucho.

## Cómo reproducirlo

Desde la raíz del repo, con los datos de PyG en `datasets_pyg/`:

```bash
uv run --extra analysis python docs/hallazgos/k_componentes.py
```

El script construye el grafo desde `edge_index` (sin lazos), cuenta las componentes conexas y ejecuta `gcn_leiden.prior.detect_communities(G, "louvain", 1.0, seed=0)`. Coauthor Physics no se incluyó porque requiere más memoria.

Pendiente, si se quiere completar la lámina: repetir con Leiden y con las semillas 1–4 (por ahora solo se midió Louvain con la semilla 0).
