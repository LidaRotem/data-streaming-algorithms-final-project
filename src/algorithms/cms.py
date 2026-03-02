"""Count-Min Sketch frequency estimator."""

import sys
from collections import Counter

import numpy as np

from src.utils.hashing import HashFamily


class CountMinSketch:
    """Count-Min Sketch frequency estimator.

    Uses a d×w table of counters and d pairwise-independent hash functions.
    Maintains a candidate Counter to support topk() queries.

    Parameters
    ----------
    M:
        Memory budget in total number of counters. w = floor(M / d).
    d:
        Number of hash functions (sketch depth). Defaults to 5.
    seed:
        Seed for hash function generation. Defaults to 0.
    """

    def __init__(self, M: int, d: int = 5, seed: int = 0, **kwargs):
        if M <= 0:
            raise ValueError(f"Memory budget M must be positive, got {M}")
        if d <= 0:
            raise ValueError(f"d must be positive, got {d}")
        self._d = d
        self._w = max(1, M // d)
        self._table = np.zeros((d, self._w), dtype=np.int64)
        self._candidates: Counter = Counter()
        self._hf = HashFamily(d, self._w, seed)

    def update(self, item) -> None:
        """Process one item from the stream."""
        self._candidates[item] += 1
        for i in range(self._d):
            self._table[i, self._hf.hash(i, item)] += 1

    def query(self, item) -> float:
        """Return estimated frequency f_hat(item) = min over rows of table[i][h_i(item)]."""
        return float(min(self._table[i, self._hf.hash(i, item)] for i in range(self._d)))

    def topk(self, k: int) -> list:
        """Return list of (item, estimated_count) for top-k candidates, sorted descending."""
        scored = [(item, self.query(item)) for item in self._candidates]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:k]

    def reset(self) -> None:
        """Reset internal state."""
        self._table[:] = 0
        self._candidates.clear()

    def memory_bytes(self) -> int:
        """Return approximate memory usage in bytes (table + candidate Counter)."""
        size = self._table.nbytes
        size += sys.getsizeof(self._candidates)
        for k, v in self._candidates.items():
            size += sys.getsizeof(k) + sys.getsizeof(v)
        return size
