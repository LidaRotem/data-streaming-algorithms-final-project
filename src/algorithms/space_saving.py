"""Space-Saving frequent items summary."""

import heapq
import sys


class SpaceSaving:
    """Space-Saving frequent items summary.

    Tracks at most M items. When at capacity and a new unseen item arrives,
    the item with the smallest count is evicted and the new item takes its
    slot with count min_count + 1 (error term included in the estimate).

    A lazy min-heap is maintained alongside the dict to find the minimum
    in O(log M) amortized time instead of O(M) per update.

    Missing key policy: query() returns 0.0 for items not in the summary.

    Parameters
    ----------
    M:
        Maximum number of (item, counter) entries.
    """

    def __init__(self, M: int, **kwargs):
        if M <= 0:
            raise ValueError(f"Memory budget M must be positive, got {M}")
        self._M = M
        self._counters: dict = {}
        self._heap: list = []  # min-heap of (count, item); may contain stale entries

    def update(self, item) -> None:
        """Process one item from the stream."""
        if item in self._counters:
            self._counters[item] += 1
            heapq.heappush(self._heap, (self._counters[item], item))
        elif len(self._counters) < self._M:
            self._counters[item] = 1
            heapq.heappush(self._heap, (1, item))
        else:
            # Evict the minimum-count item using lazy deletion on the heap.
            min_count, min_item = self._find_and_pop_min()
            del self._counters[min_item]
            new_count = min_count + 1
            self._counters[item] = new_count
            heapq.heappush(self._heap, (new_count, item))

    def _find_and_pop_min(self):
        """Pop and return (count, item) for the current minimum-count tracked item.

        Discards stale heap entries (where heap count != dict count or item
        is no longer tracked) via lazy deletion.
        """
        while self._heap:
            count, item = self._heap[0]
            if item in self._counters and self._counters[item] == count:
                return heapq.heappop(self._heap)
            heapq.heappop(self._heap)  # discard stale entry

        # Fallback: linear scan (only reached if heap is exhausted, which
        # should not happen during normal operation).
        min_item = min(self._counters, key=self._counters.get)
        min_count = self._counters[min_item]
        return min_count, min_item

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
        self._heap = []

    def memory_bytes(self) -> int:
        """Return approximate memory usage in bytes (counters dict + heap)."""
        size = sys.getsizeof(self._counters) + sys.getsizeof(self._heap)
        for k, v in self._counters.items():
            size += sys.getsizeof(k) + sys.getsizeof(v)
        for entry in self._heap:
            size += sys.getsizeof(entry)
        return size
