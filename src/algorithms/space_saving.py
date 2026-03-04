"""Space-Saving frequent items summary.

Uses an indexed min-heap so the heap always contains exactly the M tracked
items (no stale entries).  Memory is therefore O(M) at all times regardless
of stream length, matching the algorithm's theoretical guarantee.

Each heap node is a mutable list [count, item] so counts can be updated
in-place without re-inserting.  A position map _pos: {item -> heap index}
allows O(log M) sift operations on arbitrary nodes.
"""

import sys


class SpaceSaving:
    """Space-Saving frequent items summary.

    Tracks at most M items. When at capacity and a new unseen item arrives,
    the item with the smallest count is evicted and the new item takes its
    slot with count min_count + 1 (error term included in the estimate).

    An indexed min-heap (heap + position map) is maintained so that every
    counter update is O(log M) and the heap never accumulates stale entries.
    Total heap size is exactly min(items_seen_so_far, M) at all times.

    Missing key policy: query() returns 0.0 for items not in the summary.

    Parameters
    ----------
    M : int
        Maximum number of (item, counter) entries.
    """

    def __init__(self, M: int, **kwargs):
        if M <= 0:
            raise ValueError(f"Memory budget M must be positive, got {M}")
        self._M = M
        self._counters: dict = {}          # item -> count
        self._heap: list = []              # min-heap of [count, item] (mutable lists)
        self._pos: dict = {}               # item -> index in _heap

    # ------------------------------------------------------------------
    # Internal heap helpers
    # ------------------------------------------------------------------

    def _swap(self, i: int, j: int) -> None:
        """Swap two heap nodes and update the position map."""
        self._heap[i], self._heap[j] = self._heap[j], self._heap[i]
        self._pos[self._heap[i][1]] = i
        self._pos[self._heap[j][1]] = j

    def _sift_up(self, i: int) -> None:
        """Bubble node at index i upward until heap property is restored."""
        while i > 0:
            parent = (i - 1) // 2
            if self._heap[i][0] < self._heap[parent][0]:
                self._swap(i, parent)
                i = parent
            else:
                break

    def _sift_down(self, i: int) -> None:
        """Push node at index i downward until heap property is restored."""
        n = len(self._heap)
        while True:
            smallest = i
            left = 2 * i + 1
            right = 2 * i + 2
            if left < n and self._heap[left][0] < self._heap[smallest][0]:
                smallest = left
            if right < n and self._heap[right][0] < self._heap[smallest][0]:
                smallest = right
            if smallest == i:
                break
            self._swap(i, smallest)
            i = smallest

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def update(self, item) -> None:
        """Process one item from the stream.

        Three cases:
        1. Item already tracked: increment its counter and sift down
           (count increased → may violate min-heap property downward).
        2. Not tracked and capacity not full: insert at count=1 and sift up.
        3. Not tracked and at capacity: replace the heap root (minimum) with
           the new item at count = min_count + 1, then sift down.
        """
        if item in self._counters:
            self._counters[item] += 1
            idx = self._pos[item]
            self._heap[idx][0] = self._counters[item]
            self._sift_down(idx)          # count grew → push down in min-heap
        elif len(self._counters) < self._M:
            # Capacity available — append and sift up
            self._counters[item] = 1
            new_node = [1, item]
            idx = len(self._heap)
            self._heap.append(new_node)
            self._pos[item] = idx
            self._sift_up(idx)
        else:
            # At capacity — evict the minimum (root) and reuse its slot
            min_count = self._heap[0][0]
            min_item = self._heap[0][1]
            del self._counters[min_item]
            del self._pos[min_item]
            new_count = min_count + 1
            self._counters[item] = new_count
            self._heap[0] = [new_count, item]
            self._pos[item] = 0
            self._sift_down(0)

    def query(self, item) -> float:
        """Return estimated frequency. Returns 0.0 if item is not in summary."""
        return float(self._counters.get(item, 0))

    def topk(self, k: int) -> list:
        """Return list of (item, count) for top-k entries, sorted descending."""
        sorted_items = sorted(self._counters.items(), key=lambda x: x[1], reverse=True)
        return sorted_items[:k]

    def reset(self) -> None:
        """Reset internal state."""
        self._counters = {}
        self._heap = []
        self._pos = {}

    def memory_bytes(self) -> int:
        """Return approximate memory usage in bytes.

        Accounts for the counters dict, the indexed heap (exactly M mutable
        list nodes), and the position map.  No stale entries exist so this
        is a tight O(M) measurement.
        """
        size = (sys.getsizeof(self._counters)
                + sys.getsizeof(self._heap)
                + sys.getsizeof(self._pos))
        for k, v in self._counters.items():
            size += sys.getsizeof(k) + sys.getsizeof(v)
        for entry in self._heap:
            size += sys.getsizeof(entry)
        for k, v in self._pos.items():
            size += sys.getsizeof(k) + sys.getsizeof(v)
        return size
