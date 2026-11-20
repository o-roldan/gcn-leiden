"""Rebuild the paper (gnn-paper/main.tex) from the revised thesis.

Rule (TODO.md): text is extracted verbatim from the thesis; only mechanical
adjustments are allowed. Non-mechanical edits are listed in FLAGS for the
author's approval. Writes OUT and prints a report; does not touch main.tex.
Usage: sync_paper.py THESIS_DIR PAPER_TEX OUT_TEX
"""
import re
import sys

TH, PAPER, OUT = sys.argv[1:4]
rd = lambda p: open(f"{TH}/{p}").read()
RES = rd("frontmatter/resumen.tex")
CH1 = rd("chapters/chapter01/chap01.tex")
TR = rd("chapters/trabajos_relacionados/trabajos_relacionados.tex")
PS = rd("chapters/propuesta_solucion/propuesta_solucion.tex")
R = rd("chapters/resultados/resultados.tex")
C = rd("chapters/conclusiones/conclusiones.tex")
paper = open(PAPER).read()
FLAGS = []


def para(src, start):
    """Paragraph (to next blank line) containing `start`, from line start."""
    i = src.find(start)
    assert i >= 0, f"not found: {start[:60]}"
    i = src.rfind("\n", 0, i) + 1
    j = src.find("\n\n", i)
    return src[i:j if j >= 0 else len(src)]


def blk(src, start, end):
    """Text from the line containing `start` up to (excluding) `end`."""
    i = src.find(start)
    assert i >= 0, f"not found: {start[:60]}"
    i = src.rfind("\n", 0, i) + 1
    j = src.find(end, i)
    assert j >= 0, f"end not found: {end[:60]}"
    return src[i:j]


def sub(s, old, new, flag=None, must=True):
    n = s.count(old)
    if must:
        assert n >= 1, f"sub not found: {old[:70]}"
    if n and flag:
        FLAGS.append(flag)
    return s.replace(old, new)


MECH = [
    (r"\initial{L}a ", "La "),
    ("Esta tesis", "Este trabajo"),
    ("esta tesis", "este trabajo"),
    (" (Definición~\\ref{def:comunidades-desconectadas})", ""),
    (" (Definición~\\ref{def:regla-propagacion-gcn})", ""),
    (" (Definición~\\ref{def:modularidad-suave})", ""),
    (" (Definición~\\ref{def:sbm})", ""),
    (" (Definición~\\ref{def:limite-resolucion})", ""),
    (" (Definición~\\ref{def:softmax-temperatura})", ""),
    (" (Definición~\\ref{def:modularidad})", ""),
    (" (Definición~\\ref{def:distribucion-discreta})", ""),
    ("(Capítulo~\\ref{chap:resultados})", "(Sección~\\ref{sec:resultados})"),
    ("(Capítulo~\\ref{chap:propuesta-solucion})", "(Sección~\\ref{sec:fases-2-4})"),
    (" (Sección~\\ref{sec:trabajo-futuro})", ""),
    ("\\ref{subsec:recal-redes-reales}", "\\ref{sec:estudio-recalibracion}"),
    ("\\ref{subsec:recal-validacion}", "\\ref{sec:estudio-recalibracion}"),
    ("\\ref{subsec:recal-sbm}", "\\ref{sec:estudio-recalibracion}"),
    ("\\begin{table}[H]", "\\begin{table}[htbp]"),
]


def mech(s):
    for old, new in MECH:
        s = s.replace(old, new)
    s = re.sub(r"\\mycaption\[[^\]]*\]\{", r"\\caption{", s)
    return s


def swap(text, start, new):
    """Replace the paper paragraph containing `start` with `new`."""
    old = para(text, start)
    assert text.count(old) == 1, f"ambiguous paper paragraph: {start[:60]}"
    return text.replace(old, new)


def swap_blk(text, start, end, new):
    old = blk(text, start, end)
    assert text.count(old) == 1, f"ambiguous paper block: {start[:60]}"
    return text.replace(old, new)


P = paper

# ---------------- Resumen ----------------
r1 = mech(para(RES, r"\initial{L}a detección"))
r2 = mech(para(RES, "Esta tesis propone una"))
r3 = mech(para(RES, "Este trabajo evalúa el modelo"))
r3 = sub(r3, r"cuatro métricas (\textsc{nmi}, \textsc{ari}, modularidad $Q$ y \textsc{dbi})",
         r"tres métricas (\textsc{nmi}, \textsc{ari} y modularidad $Q$)",
         "Resumen: 'cuatro métricas (… y DBI)' → 'tres métricas' (consecuencia del recorte de DBI)")
P = swap(P, "La detección de comunidades en grafos es un problema", r1)
P = swap(P, "Este trabajo propone una \\textit{Red Convolucional", r2)
P = swap(P, "Este trabajo evalúa el modelo con cuatro", r3)

# ---------------- Introducción ----------------
for start in ["Existen muchos problemas relacionados", "Buscar la solución del agrupamiento",
              "En los estudios es común encontrar", "El aprendizaje automático en grafos formula",
              "En forma matricial, se busca", "Este trabajo propone y valida ajustes"]:
    P = swap(P, start, mech(para(CH1, start)))
P = swap(P, "Las siguientes preguntas guían", mech(para(CH1, "Las siguientes preguntas guían")))
contrib = mech(blk(C, r"\begin{enumerate}" + "\n    \\item \\textbf{Comparación del", r"\end{enumerate}"))
P = swap_blk(P, r"\begin{enumerate}" + "\n    \\item \\textbf{Comparación del", r"\end{enumerate}" + "\n\n\\section{Trabajo relacionado}", contrib)

# ---------------- Trabajo relacionado ----------------
s1 = mech(para(TR, "Un modelo de atención tipo Transformer"))
s1 = s1[: s1.index(r"\cite{Lobov2019}.") + len(r"\cite{Lobov2019}.")]
dmon = mech(para(TR, "Tsitsulin et al. (2023) consolidan"))
P = swap(P, "Un modelo de atención tipo Transformer", s1 + " " + dmon)
P = swap(P, "Este trabajo parte del marco de Wang", mech(para(TR, "Esta tesis parte del marco de Wang")))

# ---------------- Propuesta: Fase 1 ----------------
P = swap(P, "La arquitectura necesita estimar el número", mech(para(PS, "La arquitectura necesita estimar el número")))
P = swap(P, "El marco de Wang et al. usa Louvain", mech(para(PS, "El marco de Wang et al. usa Louvain")))
leiden = mech(para(PS, "Por eso, esta tesis usa Leiden"))
leiden = sub(leiden, " Esa partición aún incluye comunidades pequeñas que la siguiente sección depura.", "")
P = swap(P, "Por eso, este trabajo usa Leiden", leiden)
for start in ["Leiden no impone un tamaño mínimo", "A partir de los tamaños"]:
    P = swap(P, start, mech(para(PS, start)))
P = swap_blk(P, r"\begin{definition}[Filtro dinámico de relevancia]", r"\end{definition}",
             mech(blk(PS, r"\begin{definition}[Filtro dinámico de relevancia]", r"\end{definition}")))
umbral = mech(para(PS, "El umbral se adapta a la escala del grafo"))
umbral = sub(umbral, ", según el segundo objetivo", "")
P = swap(P, "El umbral se adapta a la escala del grafo", umbral)
cond = mech(blk(PS, r"\paragraph{Filtro condicionado.}", "valida este criterio."))
cond = sub(cond, "El Capítulo~\\ref{chap:resultados} ", "La Sección~\\ref{sec:estudio-recalibracion} ")
P = swap_blk(P, r"\paragraph{Filtro condicionado.}", "valida este criterio.", cond)
microk = mech(para(PS, "El filtro marca como microcomunidad"))
microk = sub(microk, r" Con $k$ y $\mathcal{P}'$, la extracción de estructura queda completa.", "")
P = swap(P, "El filtro marca como microcomunidad", microk)

# ---------------- Propuesta: Fases 2-4 ----------------
P = swap(P, "Las puntuaciones de similitud brutas", mech(para(PS, "Las puntuaciones de similitud brutas")))
d_new = mech(blk(PS, r"\begin{definition}[Afiliación suave]", r"\begin{where}"))
P = swap_blk(P, r"\begin{definition}[Afiliación suave]", r"\end{definition}" + "\n\nEsta formulación", d_new)
P = swap(P, "Esta formulación corrige un error", mech(para(PS, "Esta formulación corrige un error")))
P = swap(P, "La matriz resultante $\\mathbf{P}", mech(para(PS, "La matriz resultante $\\mathbf{P}")))

# ---------------- Protocolo ----------------
met = mech(para(PS, "emplea cuatro métricas"))
met = sub(met, " La Tabla~\\ref{tab:resumen-metricas} resume estas métricas.", "")
met = sub(met, "emplea cuatro métricas", "emplea tres métricas",
          "Métricas: 'cuatro' → 'tres' y se quita la frase del DBI (consecuencia del recorte de DBI)")
met = sub(met, r"; la \textbf{modularidad} $Q$ de Newman-Girvan, que evalúa la estructura comunitaria intrínseca sin referencia externa; y el \textbf{índice Davies-Bouldin} ($DBI$), que diagnostica la geometría del espacio latente.",
          r", y la \textbf{modularidad} $Q$ de Newman-Girvan, que evalúa la estructura comunitaria intrínseca sin referencia externa.")
P = swap(P, "emplea cuatro métricas", met)
for start in ["La evaluación abarca nueve grafos", "Cabe una salvedad de comparabilidad"]:
    P = swap(P, start, mech(para(PS, start)))
par1 = mech(para(PS, "La arquitectura se reimplementó"))
par2 = mech(para(PS, r"En los grafos reales, el \textit{prior} usa la configuración"))
P = swap(P, "La arquitectura se reimplementó", par1 + "\n\n" + par2)
P = swap(P, "Se comparan siete métodos", mech(para(PS, "Se comparan siete métodos")))
P = swap(P, "A diferencia de Wang et al., que", mech(para(PS, "A diferencia de Wang et al., que")))

# ---------------- Resultados: tablas ----------------
def thesis_rows(dataset):
    lines = R.split("\n")
    i = next(n for n, l in enumerate(lines) if l.strip().startswith(r"\multirow{4}{*}{" + dataset + "}"))
    rows = {}
    for l in lines[i:i + 5]:
        for key in ["$NMI$", "$ARI$", "$Q$", "$k$"]:
            if f"& {key} &" in l:
                rows[key] = l.split(f"& {key} &")[1].strip()
    return rows


def paper_block(datasets):
    out = []
    for n, ds in enumerate(datasets):
        rows = thesis_rows(ds)
        out.append(r"\multirow{4}{*}{" + ds + "} & $k$ & " + rows["$k$"])
        out.append(r"\addlinespace[2pt]")
        for key in ["$Q$", "$NMI$", "$ARI$"]:
            out.append(f" & {key} & " + rows[key])
        out.append(r"\midrule" if n < len(datasets) - 1 else r"\bottomrule")
    return "\n".join(out) + "\n"


def caption_of(label):
    i = R.find(r"\label{" + label + "}")
    j = R.rfind(r"\mycaption[", 0, i)
    k = R.find("]{", j) + 2
    depth, m = 1, k
    while depth:
        depth += {"{": 1, "}": -1}.get(R[m], 0)
        m += 1
    return R[k:m - 1]


GROUP = (r"& & \multicolumn{2}{c}{Heurísticas} & \multicolumn{3}{c}{Profundos (reciben $k$)} & \multicolumn{2}{c}{GCN de una capa} \\"
         "\n" + r"\cmidrule(lr){3-4}\cmidrule(lr){5-7}\cmidrule(l){8-9}" + "\n")


def set_table(text, label, datasets, caption):
    i = text.find(r"\label{" + label + "}")
    cs = text.rfind(r"\caption{", 0, i)
    ce = text.find("\n", cs)
    text = text[:cs] + r"\caption{" + caption + "}" + text[ce:]
    i = text.find(r"\label{" + label + "}")
    h = text.find(r"\textbf{Red} & \textbf{Métrica}", i)
    if r"\multicolumn{2}{c}{Heurísticas}" not in text[i:h]:
        text = text[:h] + GROUP + text[h:]
        h = text.find(r"\textbf{Red} & \textbf{Métrica}", i)
    a = text.find(r"\midrule", h) + len(r"\midrule") + 1
    b = text.find(r"\end{tabular}", a)
    return text[:a] + paper_block(datasets) + text[b:]


cap1 = mech(caption_of("tab:resultados-citas-coautoria"))
cap1 = sub(cap1, r" El $DBI$, que solo es comparable dentro de un mismo método, se reporta en la Tabla~\ref{tab:dbi} (Apéndice~\ref{app:dbi}).", "",
           "Leyenda Tabla 1: se quita la frase del DBI (recorte de DBI)")
cap1 = sub(cap1, " ---: corrida no completada.",
           " Coauthor Physics se omite porque las corridas de las variantes \\textsc{gcn} no completaron (Sección~\\ref{subsec:analisis-calidad}).",
           "Leyenda Tabla 1: se reemplaza la nota '---' por la nota de que Physics se omite (recorte de Physics)")
P = set_table(P, "tab:resultados-citas-coautoria", ["Cora", "CiteSeer", "PubMed", "Coauthor CS"], cap1)
P = set_table(P, "tab:resultados-compra-web", ["Amazon Computers", "Amazon Photo", "Actor", "WikiCS"],
              mech(caption_of("tab:resultados-compra-web")))
P = set_table(P, "tab:resultados-sbm", ["SBM-1k", "SBM-5k", "SBM-10k"], mech(caption_of("tab:resultados-sbm")))

# ---------------- Resultados: prosa ----------------
calidad = mech(blk(R, "En los grafos de citas, \\textsc{dgi} obtiene", r"\subsection{Comparación controlada"))
P = swap_blk(P, "En los grafos de citas, la propuesta GCN-Leiden", r"\subsection{Comparación controlada", calidad)


def to_column_table(block):
    """Thesis [H] table -> paper single-column table with adjustbox."""
    block = mech(block)
    block = block.replace(r"\begin{tabular}", r"\adjustbox{max width=\columnwidth}{%" + "\n" + r"\begin{tabular}")
    block = block.replace(r"\end{tabular}", r"\end{tabular}%" + "\n}")
    return block


prior = blk(R, r"\subsection{Comparación controlada del \textit{prior}}", r"\subsection{Convergencia según el \textit{prior}}")
conv = blk(R, r"\subsection{Convergencia según el \textit{prior}}", r"\subsection{Heterofilia en Actor}")
P = swap_blk(P, r"\subsection{Comparación controlada del \textit{prior}}", r"\subsection{Heterofilia en Actor}",
             to_column_table(prior) + to_column_table(conv))
actor = mech(blk(R, r"\subsection{Heterofilia en Actor}", "% ---"))
P = swap_blk(P, r"\subsection{Heterofilia en Actor}", r"\subsection{Telemetría de memoria}", actor.rstrip() + "\n\n")
P = swap_blk(P, r"\subsection{Telemetría de memoria}", r"\subsection{Recalibración del filtro dinámico}", "")

b1 = para(R, "En el barrido de $\\beta$ sobre Cora y CiteSeer")
b1 = sub(b1, r" (Tabla~\ref{tab:recal-beta}, Apéndice~\ref{app:recal-completo})", "")
b2 = para(R, "En los grafos \\textsc{sbm} el diagnóstico se invierte")
b2 = sub(b2, r"con el $k$ exacto (Tabla~\ref{tab:recal-sbm}).", r"con el $k$ exacto (valores pico).",
         "Recalibración (SBM): '(Tabla A.3)' → '(valores pico)', porque el artículo no incluye esa tabla y las tablas principales muestran el checkpoint")
b3 = para(R, "El criterio que activa el filtro condicionado")
b4 = para(R, "\\textsc{sbm}-10k muestra el límite del criterio")
b4 = sub(b4, r" (Tabla~\ref{tab:recal-sbm}, $\beta = -0.5$)", r" (con $\beta = -0.5$)")
b4 = sub(b4, r" (Sección~\ref{subsec:recal-sbm})", "")
recal = "\n\n".join(mech(x) for x in [b1, b2, b3, b4]) + "\n\n"
P = swap_blk(P, "En el barrido de $\\beta$ sobre Cora y CiteSeer", r"\section{Conclusiones}", recal)
B158 = r"(Tabla~\ref{tab:recal-beta})"
if B158 in P:
    P = P.replace(" " + B158, "")

# ---------------- Conclusiones ----------------
ans = blk(C, r"\paragraph{1. Leiden frente a Louvain.}", "% ---")
ans = sub(ans, " Por tanto, la primera hipótesis específica (H1) se rechaza.", "",
          "Conclusiones: se quitan las frases de veredicto de hipótesis (el artículo no tiene hipótesis)")
ans = sub(ans, "La segunda hipótesis específica (H2) se acepta en Cora y CiteSeer: filtrar con", "En Cora y CiteSeer, filtrar con")
ans = sub(ans, " Se rechaza con tamaños uniformes, donde el filtro reduce", " Con tamaños uniformes, en cambio, el filtro reduce")
ans = sub(ans, r"(Tabla~\ref{tab:recal-sbm}; por ejemplo,", "(por ejemplo,")
ans = sub(ans, " La tercera hipótesis específica (H3) se rechaza.", "")
ans = sub(ans, "Solo en parte, por lo que la hipótesis central se acepta parcialmente.", "Solo en parte.")
ans = mech(ans).rstrip() + "\n\n"
P = swap_blk(P, r"\paragraph{1. Leiden frente a Louvain.}", r"\subsection{Limitaciones}", ans)
lim = mech(blk(C, r"\begin{enumerate}" + "\n    \\item Las corridas de la propuesta", r"\end{enumerate}"))
P = swap_blk(P, r"\begin{enumerate}" + "\n    \\item La implementación de $Q'$ consume", r"\end{enumerate}" + "\n\n\\balance", lim)

# ---------------- Trim to 8 pages (option B, approved 2026-11-19) ----------------
def drop(text, start, end):
    i = text.find(start)
    j = text.find(end, i)
    assert i >= 0 and j > i, f"drop failed: {start[:50]}"
    return text[:i] + text[j:]


P = re.sub(r"\\renewcommand\{\\arraystretch\}\{[0-9.]+\}", r"\\renewcommand{\\arraystretch}{1.05}", P)
P = drop(P, "Existen muchos problemas", r"\subsection{Planteamiento del problema}")
P = drop(P, "El aprendizaje automático en grafos formula", "Este trabajo propone y valida ajustes")
P = sub(P, "\nDebido a que la optimización por gradiente requiere variables continuas, el modelo no opera directamente sobre $\\mathbf{S}$, sino sobre una matriz de afiliación suave $\\mathbf{P} \\in \\mathbb{R}^{n \\times k}$.\nNo obstante, se puede regresar a la forma discreta $\\mathbf{S}$ mediante $\\arg\\max$ sobre cada fila de $\\mathbf{P}$.", "",
        "Recorte: se quitan las dos frases sobre S, que dependían de la definición formal eliminada")
P = drop(P, "Un modelo de atención tipo Transformer", r"\subsection{Trabajo base")
P = drop(P, "Cabe una salvedad de comparabilidad", r"\subsection{Verificación de paridad}")
P = drop(P, "La modularidad $Q$ mide", "El marco de Wang et al. usa Louvain")

# ---------------- Post-verification fixes (P-01, P-02, P-04, P-05) ----------------
P = sub(P, r"$p_{ic}=\mathrm{Softmax}(\delta\cdot\mathrm{sim}(\mathbf{h}_i,\mathbf{u}_c))$",
        r"$p_{ic}=\operatorname{softmax}(\delta\cdot\operatorname{sim}(\mathbf{h}_i,\mathbf{u}_c))$")
P = sub(P, " (el mínimo en el caso de $DBI$)", "")
P = sub(P, "Verificar esta hipótesis queda fuera del alcance de este trabajo y se retoma como trabajo futuro.",
        "Verificar esta hipótesis queda fuera del alcance de este trabajo.")
_sbm = para(P, "En los grafos \\textsc{sbm} el diagnóstico se invierte")
P = P.replace(_sbm, _sbm + "\n\n" + mech(para(R, "En Actor se evalúa el barrido completo")))

# ---------------- Approved additions (P-03, P-06; 2026-11-20) ----------------
P = sub(P, "La arquitectura necesita estimar el número de comunidades $k$ sin supervisión",
        "La arquitectura (Figura~\\ref{fig:pipeline-arquitectura}) necesita estimar el número de comunidades $k$ sin supervisión",
        "P-03: se cita la Figura 1 al inicio de la Sección 3 (aprobado)")
P = sub(P, "En el barrido de $\\beta$ sobre Cora y CiteSeer, el $NMI$ crece",
        "En el barrido de $\\beta \\in \\{-0.5, 0, 0.25, 0.5\\}$ sobre Cora y CiteSeer, el $NMI$ crece",
        "P-06: se enuncia la malla de beta (aprobado)")

open(OUT, "w").write(P)

# ---------------- Checks ----------------
labels = set(re.findall(r"\\label\{([^}]+)\}", P))
refs = set(re.findall(r"\\ref\{([^}]+)\}", P))
bib = open(PAPER.replace("main.tex", "references.bib")).read()
cites = set(k.strip() for c in re.findall(r"\\cite\{([^}]+)\}", P) for k in c.split(","))
print("missing labels:", sorted(refs - labels))
print("missing bib keys:", sorted(k for k in cites if "{" + k + "," not in bib))
for w in ["tesis", "hipótesis", "DBI", "dbi", "Telemetría", "vram", "Physics"]:
    print(f"'{w}':", len(re.findall(w, P)))
print("FLAGS:")
for f in dict.fromkeys(FLAGS):
    print(" -", f)
