"""Unified results schema: every run (GCN variants and baselines) appends
one row with the same columns, so multi-instance results merge by simple
concatenation. Method-specific hyperparameters go into `config`.
"""

import csv
import datetime
from pathlib import Path

FIELDNAMES = [
    "timestamp", "method", "dataset", "seed", "k", "epochs", "runtime_s",
    "nmi", "ari", "q", "dbi",
    "peak_nmi", "peak_ari", "peak_q", "peak_dbi",
    "ram_peak_mb", "vram_peak_mb", "config",
]


def append_result(path, **row):
    unknown = set(row) - set(FIELDNAMES)
    if unknown:
        raise ValueError(f"Unknown result fields: {sorted(unknown)}")
    row.setdefault(
        "timestamp", datetime.datetime.now().isoformat(timespec="seconds"))
    row = {key: _fmt(val) for key, val in row.items()}

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not path.exists()
    with path.open("a", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, restval="")
        if write_header:
            writer.writeheader()
        writer.writerow(row)


def config_string(**params):
    return ";".join(f"{key}={val}" for key, val in sorted(params.items()))


def _fmt(val):
    if isinstance(val, float):
        return round(val, 4)
    return val
