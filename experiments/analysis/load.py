"""Load the experiment CSVs into tidy DataFrames for tables and figures.

Two artifact families are produced by the runners:

  * runs CSVs  (results/runs*.csv) -- one row per run; the per-method
    hyperparameters live packed in the ``config`` column.
  * history CSVs (results/history*/**/*.csv) -- one row per evaluated epoch,
    named ``{method}_{dataset}_seed{seed}.csv``.

``load_runs`` unpacks ``config`` into real columns and tags each row with the
graph size; ``load_history`` recovers method/dataset/seed from the filename.
"""

import re
from pathlib import Path

import numpy as np
import pandas as pd

# Node counts of the empirical benchmarks, for the scalability x-axis.
REAL_NODE_COUNTS = {
    "cora": 2708, "citeseer": 3327, "pubmed": 19717,
    "cocs": 18333, "cophysics": 34493,
    "amac": 13752, "amap": 7650, "film": 7600, "wikics": 11701,
}

_HISTORY_RE = re.compile(r"(?P<method>[^_]+)_(?P<dataset>.+)_seed(?P<seed>\d+)\.csv$")
_SBM_RE = re.compile(r"sbm_(\d+)_\d+")


def load_runs(results_dir="results", pattern="runs*.csv",
              exclude=("recal", "validate")):
    """Concatenate matching run CSVs into one tidy DataFrame.

    The default skips the recal/validate sweeps (different grids); load those
    explicitly, e.g. ``load_runs(pattern="runs_recal_*.csv", exclude=())``.
    """
    paths = [p for p in sorted(Path(results_dir).glob(pattern))
             if not any(tok in p.name for tok in exclude)]
    if not paths:
        raise FileNotFoundError(
            f"no run CSVs matched {results_dir}/{pattern} (exclude={exclude})")
    df = pd.concat([pd.read_csv(p) for p in paths], ignore_index=True)
    return add_node_counts(parse_config(df))


def load_history(results_dir="results", pattern="history*/**/*.csv"):
    """Concatenate per-epoch history CSVs into one long-form DataFrame.

    method/dataset/seed are parsed from each filename and added as columns.
    """
    frames = []
    for path in sorted(Path(results_dir).glob(pattern)):
        match = _HISTORY_RE.search(path.name)
        if match is None:
            continue
        frame = pd.read_csv(path)
        frame["method"] = match["method"]
        frame["dataset"] = match["dataset"]
        frame["seed"] = int(match["seed"])
        frames.append(frame)
    if not frames:
        raise FileNotFoundError(
            f"no history CSVs matched {results_dir}/{pattern}")
    return pd.concat(frames, ignore_index=True)


def parse_config(df):
    """Expand the ``config`` column (``key=val;key=val``) into real columns.

    Numeric values are coerced; columns that would shadow an existing one are
    dropped so the run schema always wins.
    """
    if "config" not in df.columns:
        return df
    expanded = pd.json_normalize(df["config"].map(_parse_config_string))
    expanded = expanded.apply(_maybe_numeric)
    keep = [c for c in expanded.columns if c not in df.columns]
    return pd.concat([df.reset_index(drop=True),
                      expanded[keep].reset_index(drop=True)], axis=1)


def add_node_counts(df):
    """Add an ``n_nodes`` column derived from the dataset name."""
    if "dataset" in df.columns:
        df = df.copy()
        df["n_nodes"] = df["dataset"].map(node_count)
    return df


def node_count(dataset):
    match = _SBM_RE.match(str(dataset))
    if match:
        return int(match.group(1))
    return REAL_NODE_COUNTS.get(dataset, np.nan)


def _parse_config_string(value):
    out = {}
    if isinstance(value, str):
        for pair in value.split(";"):
            if "=" in pair:
                key, val = pair.split("=", 1)
                out[key] = val
    return out


def _maybe_numeric(column):
    """Coerce a column to numeric only if every value converts cleanly."""
    converted = pd.to_numeric(column, errors="coerce")
    return converted if converted.notna().all() else column
