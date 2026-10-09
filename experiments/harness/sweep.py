"""Shared sweep runner.

A sweep driver under ``experiments.sweeps`` only has to describe its grid of
runs as a list of runner commands; the argument plumbing, dry-run printing,
sequential execution, failure collection and exit code all live here.

Each run executes in its own subprocess so the peak-RAM telemetry of one run
cannot contaminate another's. Results land in a per-dataset CSV; merging
cloud shards is then just concatenating CSVs.

Every sweep invocation writes under its own batch directory,
``results/<batch>/`` (default: a launch timestamp), so a new sweep never
mixes with an earlier one's CSVs and histories unless it reuses the batch.
"""

import datetime
import subprocess
import sys
import time
from pathlib import Path

PYTHON = sys.executable
RESULTS_ROOT = Path("results")


def gcn_command(*args):
    """A ``python -m experiments.runners.gcn`` invocation (args stringified)."""
    return [PYTHON, "-m", "experiments.runners.gcn", *map(str, args)]


def baseline_command(*args):
    """A ``python -m experiments.runners.baseline`` invocation."""
    return [PYTHON, "-m", "experiments.runners.baseline", *map(str, args)]


def add_common_sweep_args(parser):
    """Register the arguments every sweep shares."""
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--seeds", default="0,1,2,3,4",
                        help="comma-separated seeds")
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--eval-every", type=int, default=2,
                        help="evaluation cadence for GCN runs (raise to 10 on "
                             "large datasets to cut metric overhead)")
    parser.add_argument("--batch",
                        default=datetime.datetime.now().strftime(
                            "%Y%m%d-%H%M%S"),
                        help="output directory under results/ (default: "
                             "launch timestamp); reuse a name to group "
                             "several sweeps into one batch")
    parser.add_argument("--results", default=None,
                        help="results CSV path (default: "
                             "results/<batch>/<sweep-specific name>)")
    parser.add_argument("--dry-run", action="store_true",
                        help="print the planned commands without running")
    return parser


def batch_dir(args):
    """The directory this sweep's CSVs and histories are written under."""
    return RESULTS_ROOT / args.batch


def parse_seeds(seeds):
    """Parse the comma-separated ``--seeds`` value into a list of ints."""
    return [int(s) for s in seeds.split(",")]


def run_sweep(name, commands, dry_run=False, output=None):
    """Run ``commands`` sequentially with progress and a failure report.

    Exits with status 1 if any run failed, so a cloud shard surfaces errors.
    """
    print(f"[{name}] {len(commands)} runs planned"
          + (f" -> {output}/" if output else ""))

    if dry_run:
        for command in commands:
            print("  " + " ".join(command[2:]))
        return

    failures = []
    start = time.perf_counter()
    for index, command in enumerate(commands, 1):
        label = " ".join(command[2:])
        print(f"--- [{index}/{len(commands)}] {label}")
        completed = subprocess.run(command)
        if completed.returncode != 0:
            failures.append(label)
            print(f"    FAILED (exit {completed.returncode}) — continuing")

    elapsed = time.perf_counter() - start
    print(f"\ndone: {len(commands) - len(failures)}/{len(commands)} runs ok "
          f"in {elapsed/60:.1f} min")
    if failures:
        print("failed runs:")
        for label in failures:
            print(f"  {label}")
        sys.exit(1)
