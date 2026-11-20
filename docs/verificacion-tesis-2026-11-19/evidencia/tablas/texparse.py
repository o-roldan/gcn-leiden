"""Parse thesis LaTeX tables into cells: (value, sd, bold, raw)."""
import re

CELL_RE = re.compile(r"^(?P<val>-?[0-9.]+)(?:\{\\scriptsize\$\\pm\$(?P<sd>[0-9.]+)\})?(?:\s*\((?P<paren>[0-9]+)\))?$")


def parse_cell(raw):
    s = raw.strip()
    bold = False
    m = re.fullmatch(r"\\textbf\{(.*)\}", s)
    if m:
        bold = True
        s = m.group(1).strip()
    if s in ("---", ""):
        return dict(val=None, sd=None, bold=bold, raw=raw.strip(), paren=None)
    m = CELL_RE.match(s)
    if not m:
        return dict(val=s, sd=None, bold=bold, raw=raw.strip(), paren=None)
    return dict(val=m.group("val"), sd=m.group("sd"), bold=bold,
                raw=raw.strip(), paren=m.group("paren"))


def split_row(line):
    line = line.strip()
    if line.endswith("\\\\"):
        line = line[:-2]
    # split on & not inside braces
    parts, depth, cur = [], 0, ""
    for ch in line:
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
        if ch == "&" and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    parts.append(cur)
    return [p.strip() for p in parts]


def table_lines(path, label):
    """Return (lineno, text) of tabular rows of the table with \\label{label}."""
    lines = open(path, encoding="utf-8").read().split("\n")
    idx = next(i for i, l in enumerate(lines) if f"\\label{{{label}}}" in l)
    # find \midrule after idx, and \bottomrule
    start = next(i for i in range(idx, len(lines)) if "\\midrule" in lines[i])
    end = next(i for i in range(idx, len(lines)) if "\\bottomrule" in lines[i])
    out = []
    for i in range(start + 1, end):
        l = lines[i]
        if l.strip().startswith("\\midrule") or not l.strip():
            continue
        out.append((i + 1, l))
    return out
