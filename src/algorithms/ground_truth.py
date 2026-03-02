"""Ground truth exact frequency counter.
This is a real implementation (not a stub) — required for smoke test validation.
"""


class GroundTruth:
    """Exact frequency counter using a dict. Computes true Top-k and stream moments.

    Parameters
    ----------
    M:
        Memory budget (accepted for API compatibility; not used — exact counting has no budget).
    """

    def __init__(self, M: int, **kwargs):
        self._counts: dict = {}

    def update(self, item) -> None:
        """Process one item from the stream."""
        self._counts[item] = self._counts.get(item, 0) + 1

    def query(self, item) -> float:
        """Return exact frequency f(item). Returns 0.0 if item was never seen."""
        return float(self._counts.get(item, 0))

    def topk(self, k: int) -> list:
        """Return list of (item, count) for the k most frequent items, sorted descending."""
        sorted_items = sorted(self._counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_items[:k]

    def true_topk(self, k: int) -> list:
        """Return the k items with the highest true counts (alias for topk)."""
        return self.topk(k)

    def reset(self) -> None:
        """Reset internal state."""
        self._counts = {}

    @property
    def F0(self) -> int:
        """Number of distinct items seen (zeroth frequency moment)."""
        return len(self._counts)

    @property
    def F1(self) -> int:
        """Total number of items seen (first frequency moment = stream length)."""
        return sum(self._counts.values())

    @property
    def F2(self) -> int:
        """Sum of squared frequencies (second frequency moment)."""
        return sum(v * v for v in self._counts.values())

    def memory_bytes(self) -> int:
        """Return approximate memory usage of the frequency dict in bytes.

        Sums sys.getsizeof over the dict and all its keys and values.
        For reference only — GroundTruth is not memory-constrained.
        """
        import sys
        size = sys.getsizeof(self._counts)
        for k, v in self._counts.items():
            size += sys.getsizeof(k) + sys.getsizeof(v)
        return size
