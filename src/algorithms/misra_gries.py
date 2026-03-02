"""Misra-Gries frequent items summary."""

import sys


class MisraGries:
    """Misra-Gries frequent items summary.

    Guarantees that any item with true frequency > F1 / (M + 1) appears
    in the summary. Items absent from the summary may still have been
    frequent — they were pushed out by the decrement step.

    Missing key policy: query() returns 0.0 for items not in the summary.

    Parameters
    ----------
    M:
        Maximum number of (item, counter) entries in the summary.
    """

    def __init__(self, M: int, **kwargs):
        if M <= 0:
            raise ValueError(f"Memory budget M must be positive, got {M}")
        self._M = M
        self._counters: dict = {}

    def update(self, item) -> None:
        """Process one item from the stream.

        Steps:
        1. If item is tracked: increment its count.
        2. Elif there is room: add item with count 1.
        3. Else: decrement all counts by 1 and remove any entry ≤ 0.
        """
        if item in self._counters:
            self._counters[item] += 1
        elif len(self._counters) < self._M:
            self._counters[item] = 1
        else:
            to_delete = []
            for key in self._counters:
                self._counters[key] -= 1
                if self._counters[key] <= 0:
                    to_delete.append(key)
            for key in to_delete:
                del self._counters[key]

    def query(self, item) -> float:
        """Return estimated frequency. Returns 0.0 if item is not in summary."""
        return float(self._counters.get(item, 0))

    def topk(self, k: int) -> list:
        """Return list of (item, count) for top-k entries in summary, sorted descending."""
        sorted_items = sorted(self._counters.items(), key=lambda x: x[1], reverse=True)
        return sorted_items[:k]

    def reset(self) -> None:
        """Reset internal state."""
        self._counters = {}

    def memory_bytes(self) -> int:
        """Return approximate memory usage in bytes (counters dict)."""
        size = sys.getsizeof(self._counters)
        for k, v in self._counters.items():
            size += sys.getsizeof(k) + sys.getsizeof(v)
        return size
