"""Synthetic stream generators.

Stage 1: all generators are stubs returning random integer streams.
Real generators (uniform, zipf, mixture) to be implemented in Stage 3.
"""

import random


def generate_stream(dataset_type: str, N: int, seed: int, **kwargs) -> list:
    """Generate a synthetic item stream.

    Parameters
    ----------
    dataset_type:
        One of 'uniform', 'zipf', 'mixture'. Ignored in stub — all return the same stream.
    N:
        Number of items to generate.
    seed:
        Random seed (set globally via set_seed before calling this function).
    **kwargs:
        Reserved for future generator parameters (e.g., alpha for Zipf).

    Returns
    -------
    list
        List of N integer items.

    Notes
    -----
    Stub: returns N random integers in range [0, 1000).
    Will be replaced with real generators in Stage 3.
    """
    # stub: returns N random integers in range [0, 1000)
    # will be replaced with real generators in Stage 3
    return [random.randint(0, 999) for _ in range(N)]
