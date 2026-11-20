import sys
p=sys.argv[1]+'/chapters/propuesta_solucion/propuesta_solucion.tex'; s=open(p).read()
R=[
# C1: duplicate of the next paragraph ("reportadas a resolución canónica")
(" Las heurísticas clásicas de las tablas de resultados se reportan a la resolución canónica $\\gamma = 1.0$.", ""),
# C2: two sentences -> one
("Conocer $k$ no favorece necesariamente a un método en todas las métricas: el $NMI$ tiende a crecer con el número de clústeres, mientras que el $ARI$ corrige el acuerdo por azar. Por eso las tablas de resultados reportan el $k$ de cada método junto con el $NMI$ y el $ARI$, y cuando dos configuraciones difieren mucho en $k$, como al activar o desactivar el filtro, la comparación se apoya en el $ARI$",
 "Conocer $k$ no favorece necesariamente a un método: como el $NMI$ tiende a crecer con el número de clústeres y el $ARI$ corrige el acuerdo por azar, las tablas reportan el $k$ de cada método, y cuando $k$ difiere mucho entre configuraciones (por ejemplo, al activar o desactivar el filtro) la comparación se apoya en el $ARI$"),
# C3: merge / tighten the two-views paragraph
("Por otro, al terminar restaura el \\textit{checkpoint} de pérdida mínima (el estado guardado tras el paso de optimización de la época de máxima $Q'$) y lo evalúa.",
 "Por otro, al terminar evalúa el \\textit{checkpoint} de pérdida mínima (el estado tras el paso de optimización de la época de máxima $Q'$)."),
("Esta tesis conserva ambas vistas y emplea cada una donde la comparación es simétrica. Las comparaciones internas",
 "Esta tesis emplea cada vista donde la comparación es simétrica: las comparaciones internas"),
("A diferencia del original, que evalúa cada dos épocas, aquí la evaluación se hace cada 2, 5 o 10 épocas según el grafo",
 "A diferencia del original, aquí se evalúa cada 2, 5 o 10 épocas según el grafo"),
]
for o,n in R:
    assert s.count(o)==1,(s.count(o),o[:60]); s=s.replace(o,n)
open(p,'w').write(s); print("ok")
