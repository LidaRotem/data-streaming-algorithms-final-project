"""Synthetic stream generators.

Generates item streams for the four synthetic datasets:
  - uniform: items drawn uniformly from [0, vocab_size)
  - zipf_1_1: Zipf distribution with alpha=1.1
  - zipf_1_3: Zipf distribution with alpha=1.3
  - mixture: k_heavy heavy-hitters with probability p_heavy; remainder uniform

Each call to generate_stream() returns a fresh independent generator.
Seeding is handled internally via numpy.random.default_rng(seed).
"""

import numpy as np


def generate_stream(dataset_type: str, N: int, seed: int, **kwargs):
    """Generator — yields one integer item at a time.

    Parameters
    ----------
    dataset_type:
        One of 'uniform', 'zipf_1_1', 'zipf_1_3', 'mixture'.
    N:
        Number of items to generate.
    seed:
        Random seed passed directly to numpy.random.default_rng(seed).
    **kwargs:
        Generator-specific parameters forwarded from config:
          - uniform: vocab_size (int, default 10000)
          - zipf_1_1, zipf_1_3: vocab_size (int, default 10000)
          - mixture: k_heavy (int), p_heavy (float), vocab_size (int, default 10000)
    """
    rng = np.random.default_rng(seed)

    if dataset_type == "uniform":
        vocab_size = int(kwargs.get("vocab_size", 10000))
        items = rng.integers(0, vocab_size, size=N)
        yield from items.tolist()

    elif dataset_type == "zipf_1_1":
        vocab_size = int(kwargs.get("vocab_size", 10000))
        ranks = np.arange(1, vocab_size + 1, dtype=np.float64)
        weights = 1.0 / np.power(ranks, 1.1)
        weights /= weights.sum()
        items = rng.choice(vocab_size, size=N, replace=True, p=weights)
        yield from items.tolist()

    elif dataset_type == "zipf_1_3":
        vocab_size = int(kwargs.get("vocab_size", 10000))
        ranks = np.arange(1, vocab_size + 1, dtype=np.float64)
        weights = 1.0 / np.power(ranks, 1.3)
        weights /= weights.sum()
        items = rng.choice(vocab_size, size=N, replace=True, p=weights)
        yield from items.tolist()

    elif dataset_type == "mixture":
        k_heavy = int(kwargs.get("k_heavy", 50))
        p_heavy = float(kwargs.get("p_heavy", 0.5))
        vocab_size = int(kwargs.get("vocab_size", 10000))
        background_size = vocab_size - k_heavy
        probs = np.array(
            [p_heavy / k_heavy] * k_heavy +
            [(1.0 - p_heavy) / background_size] * background_size,
            dtype=np.float64,
        )
        probs /= probs.sum()
        all_ids = np.arange(vocab_size, dtype=np.int64)
        items = rng.choice(all_ids, size=N, replace=True, p=probs)
        yield from items.tolist()

    else:
        raise ValueError(
            f"Unknown dataset_type '{dataset_type}'. "
            "Expected one of: 'uniform', 'zipf_1_1', 'zipf_1_3', 'mixture'."
        )