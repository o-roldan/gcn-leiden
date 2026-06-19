"""Memory telemetry for the scalability study (thesis pregunta 5)."""

import resource
import sys

import torch


def peak_ram_mb():
    """Peak resident set size of this process, in MiB."""
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    # ru_maxrss is bytes on macOS, kilobytes on Linux.
    return peak / 2**20 if sys.platform == "darwin" else peak / 2**10


def peak_vram_mb():
    """Peak CUDA memory allocated by torch, in MiB (NaN without a GPU)."""
    if torch.cuda.is_available():
        return torch.cuda.max_memory_allocated() / 2**20
    return float("nan")
