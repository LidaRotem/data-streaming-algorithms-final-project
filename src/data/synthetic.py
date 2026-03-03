"""Synthetic stream generators.

Generates item streams for the four synthetic datasets:
  - uniform: items drawn uniformly from [0, vocab_size)
  - zipf_1_1: Zipf distribution with alpha=1.1
  - zipf_1_3: Zipf distribution with alpha=1.3
  - mixture: k_heavy heavy-hitters with probability p_heavy; remainder uniform

Call set_seed(seed) before calling generate_stream().
"""

import random
import numpy as np


def _generate_uniform(N: int, vocab_size: int) -> list:
    """Draw N items uniformly at random from [0, vocab_size)."""
    return [random.randint(0, vocab_size - 1) for _ in range(N)]


def _generate_zipf(N: int, alpha: float, vocab_size: int = 10000) -> list:
    """Draw N items from a Zipf distribution with the given alpha.

    Uses numpy to build the PMF over [1, vocab_size], then samples via
    numpy.random.choice. Item IDs are mapped to 0-indexed integers.

    Parameters
    ----------
    N:
        Number of items to generate.
    alpha:
        Zipf exponent (> 0). Larger alpha → heavier tail.
    vocab_size:
        Size of the vocabulary (number of distinct possible items).
    """
    ranks = np.arange(1, vocab_size + 1, dtype=np.float64)
    weights = 1.0 / np.power(ranks, alpha)
    weights /= weights.sum()
    # Sample using numpy; subtract 1 to get 0-indexed item IDs
    items = np.random.choice(vocab_size, size=N, replace=True, p=weights)
    return items.tolist()


def _generate_mixture(N: int, k_heavy: int, p_heavy: float) -> list:
    """Generate a mixture stream.

    k_heavy items share probability p_heavy equally.
    The remaining probability (1 - p_heavy) is spread uniformly over a
    background vocabulary of vocab_size=10000 - k_heavy items.

    Heavy items are IDs 0 … k_heavy-1.
    Background items are IDs k_heavy … 9999.

    Parameters
    ----------
    N:
        Number of items to generate.
    k_heavy:
        Number of heavy-hitter items.
    p_heavy:
        Total probability mass assigned to the heavy-hitter items.
    """
    background_size = 10000 - k_heavy
    p_per_heavy = p_heavy / k_heavy
    p_per_background = (1.0 - p_heavy) / background_size

    heavy_ids = list(range(k_heavy))
    background_ids = list(range(k_heavy, 10000))

    # Build full probability vector
    probs = np.array(
        [p_per_heavy] * k_heavy + [p_per_background] * background_size,
        dtype=np.float64,
    )
    probs /= probs.sum()  # normalise for floating-point safety

    all_ids = np.array(heavy_ids + background_ids, dtype=np.int64)
    sampled = np.random.choice(all_ids, size=N, replace=True, p=probs)
    return sampled.tolist()


def generate_stream(dataset_type: str, N: int, seed: int, **kwargs) -> list:
    """Generate a synthetic item stream.

    Parameters
    ----------
    dataset_type:
        One of 'uniform', 'zipf_1_1', 'zipf_1_3', 'mixture'.
    N:
        Number of items to generate.
    seed:
        Random seed. set_seed(seed) must have been called before this function
        in each run context; seed is accepted here for documentation purposes.
    **kwargs:
        Generator-specific parameters forwarded from config:
          - uniform: vocab_size (int, default 10000)
          - zipf_1_1, zipf_1_3: alpha (float), vocab_size (int, default 10000)
          - mixture: k_heavy (int), p_heavy (float)

    Returns
    -------
    list
        List of N integer item IDs.
    """
    if dataset_type == "uniform":
        vocab_size = int(kwargs.get("vocab_size", 10000))
        return _generate_uniform(N, vocab_size)

    elif dataset_type == "zipf_1_1":
        alpha = float(kwargs.get("alpha", 1.1))
        vocab_size = int(kwargs.get("vocab_size", 10000))
        return _generate_zipf(N, alpha, vocab_size)

    elif dataset_type == "zipf_1_3":
        alpha = float(kwargs.get("alpha", 1.3))
        vocab_size = int(kwargs.get("vocab_size", 10000))
        return _generate_zipf(N, alpha, vocab_size)

    elif dataset_type == "mixture":
        k_heavy = int(kwargs.get("k_heavy", 50))
        p_heavy = float(kwargs.get("p_heavy", 0.5))
        return _generate_mixture(N, k_heavy, p_heavy)

    else:
        raise ValueError(
            f"Unknown dataset_type '{dataset_type}'. "
            "Expected one of: 'uniform', 'zipf_1_1', 'zipf_1_3', 'mixture'."
        )