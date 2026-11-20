import sys
T, G = sys.argv[1], sys.argv[2]
def rep(p, pairs):
    s = open(p).read()
    for old, new in pairs:
        n = s.count(old); assert n == 1, (p, n, old[:100])
        s = s.replace(old, new)
    open(p, 'w').write(s)

rep(f"{T}/chapters/trabajos_relacionados/trabajos_relacionados.tex", [
(r"""El método es competitivo y mucho más rápido que los modelos profundos. Pero hereda las debilidades de Louvain, que puede generar comunidades mal conectadas y sesgar los centroides \cite{Traag2019}. Su estudio tampoco mide la memoria. Esta tesis corrige ambos. Sustituye Louvain por Leiden, ajusta el filtro dinámico y mide \textsc{ram} y \textsc{vram}.""",
 r"""Según sus autores, el método es competitivo y más rápido que los modelos profundos con los que se compara. Pero hereda las debilidades de Louvain, que puede generar comunidades mal conectadas \cite{Traag2019} y, con ello, podría sesgar los centroides. Esta tesis sustituye Louvain por Leiden, estudia la calibración del filtro dinámico y evalúa la arquitectura con varias semillas."""),
])
rep(f"{T}/chapters/chapter01/chap01.tex", [
(r"""que \textit{decidir} la existencia de \textit{cliques} de tamaño
$k \ge 3$ constituye un problema \textsc{np}-completo.""",
 r"""que \textit{decidir} si un grafo contiene un \textit{clique} de tamaño
$k$, cuando $k$ forma parte de la entrada, constituye un problema \textsc{np}-completo."""),
])
s = open(f"{T}/frontmatter/resumen.tex").read()
i = s.index("La arquitectura emplea"); j = s.index("\n", i)
print("RESUMEN OLD:", s[i:j])
s = s[:i] + r"""La arquitectura emplea el algoritmo de Leiden como \textit{prior} estructural para definir los centroides de las comunidades. Un filtro dinámico conserva las comunidades de mayor tamaño, que anclan los vectores latentes antes de maximizar $Q'$ mediante el ascenso de gradiente.""" + s[j:]
open(f"{T}/frontmatter/resumen.tex", 'w').write(s)
s = open(f"{T}/frontmatter/abstract.tex").read()
i = s.index("The architecture employs"); j = s.index("\n", i)
print("ABSTRACT OLD:", s[i:j])
s = s[:i] + r"""The architecture employs the Leiden algorithm as a structural prior to define the community centroids. A dynamic filter keeps the largest communities, which anchor the latent vectors before maximizing $Q'$ via gradient ascent.""" + s[j:]
open(f"{T}/frontmatter/abstract.tex", 'w').write(s)

rep(f"{G}/gcn_leiden/prior.py", [
("""                          len(c) >= T. Real networks sit at CV >~ 1 and SBM
                          partitions at ~1e-2, so cv_threshold is uncritical.""",
 """                          len(c) >= T. In the thesis priors the CV is
                          1.2-11.5 on real networks, <= 0.007 on SBM priors
                          that recover every block, and 0.41-0.45 on
                          modularity priors of SBM-10k (a few merged blocks),
                          so any cv_threshold in [0.01, 0.4] gives the same
                          decisions."""),
])
print("ok")
