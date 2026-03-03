"""Count-Min Sketch with Bounded Candidate Counter (CMS-B).

Identical to CountMinSketch except the candidates Counter is capped at M entries.
When a new unseen item arrives and the Counter is full, the item with the lowest
count is evicted. This bounds auxiliary memory to O(M) key-count pairs, making
total memory directly comparable to MG and SS under a strict M-slot budget.
"""

import sys
from collections import Counter
import numpy as np
from src.utils.hashing import HashFamily


class CountMinSketchBounded:
    """CMS with bounded candidates Counter (size <= M).

    Parameters
    ----------
    M : int
        Memory budget. Sketch: d x w counters where w=floor(M/d).
        Candidates: capped at M entries with min-count eviction.
    d : int
        Sketch depth. Defaults to 5.
    seed : int
        Hash seed. Defaults to 0.
    """

    def __init__(self, M: int, d: int = 5, seed: int = 0, **kwargs):
        if M <= 0:
            raise ValueError(f"M must be positive, got {M}")
        if d <= 0:
            raise ValueError(f"d must be positive, got {d}")
        self._M = M
        self._d = d
        self._w = max(1, M // d)
        self._table = np.zeros((d, self._w), dtype=np.int64)
        self._candidates: Counter = Counter()
        self._hf = HashFamily(d, self._w, seed)

    def update(self, item) -> None:
        """Process one item. Candidates Counter bounded to M entries."""
        if item in self._candidates:
            self._candidates[item] += 1
        elif len(self._candidates) < self._M:
            self._candidates[item] = 1
        else:
            min_item = min(self._candidates, key=self._candidates.__getitem__)
            del self._candidates[min_item]
            self._candidates[item] = 1
        for i in range(self._d):
            self._table[i, self._hf.hash(i, item)] += 1

    def query(self, item) -> float:
        """Return min-estimate from sketch table."""
        return float(min(self._table[i, self._hf.hash(i, item)]
                         for i in range(self._d)))

    def topk(self, k: int) -> list:
        """Return top-k from bounded candidates, scored by sketch query."""
        scored = [(item, self.query(item)) for item in self._candidates]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:k]

    def reset(self) -> None:
        """Reset internal state."""
        self._table[:] = 0
        self._candidates.clear()

    def memory_bytes(self) -> int:
        """Return approximate memory usage in bytes (table + bounded candidates dict)."""
        size = self._table.nbytes
        size += sys.getsizeof(self._candidates)
        for k, v in self._candidates.items():
            size += sys.getsizeof(k) + sys.getsizeof(v)
        return size
