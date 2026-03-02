"""Timing and seeding utilities."""

import random
import time

import numpy as np


def set_seed(seed: int) -> None:
    """Set global random seeds for reproducibility.

    Must be called before generating data or initializing algorithms in any run.

    Parameters
    ----------
    seed:
        Integer seed value.
    """
    random.seed(seed)
    np.random.seed(seed)


def measure_throughput(func, items: list) -> tuple[float, float]:
    """Time a function called once per item and return (updates_per_sec, elapsed_sec).

    Parameters
    ----------
    func:
        Callable accepting a single item (e.g., algo.update).
    items:
        Stream of items to process.
    """
    t0 = time.perf_counter()
    for item in items:
        func(item)
    elapsed = time.perf_counter() - t0
    updates_per_sec = len(items) / elapsed if elapsed > 0 else float("inf")
    return updates_per_sec, elapsed
