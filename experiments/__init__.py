"""Thesis experiment harness for the GCN-Leiden architecture.

Everything in this package is research code used to validate the
architecture (baselines, single-run CLIs, sweep drivers, results/telemetry
plumbing, cloud-sharding deploy). It depends on the `gcn_leiden` library;
the library never depends on it. Reusers of the architecture can ignore
this package entirely.

Run from the repository root, e.g.::

    python -m experiments.runners.gcn --dataset cora --prior leiden
    python -m experiments.sweeps.full --dataset cora --dry-run
"""
