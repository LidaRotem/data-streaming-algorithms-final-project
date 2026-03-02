"""Pairwise-independent hash function families for sketch algorithms.

Provides HashFamily, used by CountMinSketch, CountMinSketchCU, and CountSketch.
Hash functions follow h(x) = (a*x + b) mod p mod w (Carter-Wegman family).
Sign functions follow g(x) = 2 * ((c*x + e) mod p mod 2) - 1 → {-1, +1}.
"""

import numpy as np

_LARGE_PRIME = (1 << 31) - 1  # Mersenne prime 2^31 − 1


class HashFamily:
    """Family of d pairwise-independent hash functions mapping items to [0, w).

    Parameters
    ----------
    d:
        Number of hash functions (one per sketch row).
    w:
        Width of each sketch row; hash outputs land in [0, w).
    seed:
        Integer seed for reproducible parameter generation.
    """

    def __init__(self, d: int, w: int, seed: int):
        if d <= 0:
            raise ValueError(f"d must be positive, got {d}")
        if w <= 0:
            raise ValueError(f"w must be positive, got {w}")
        rng = np.random.default_rng(seed)
        p = _LARGE_PRIME
        # Parameters for h_i(x) = (a_i*x + b_i) mod p mod w
        self._a = rng.integers(1, p, size=d)
        self._b = rng.integers(0, p, size=d)
        # Parameters for g_i(x) = 2 * ((c_i*x + e_i) mod p mod 2) - 1
        self._c = rng.integers(1, p, size=d)
        self._e = rng.integers(0, p, size=d)
        self._p = p
        self._w = w
        self._d = d

    def hash(self, row: int, item) -> int:
        """Return hash of item for sketch row, result in [0, w).

        Accepts integer or string items. Strings are converted via Python's
        built-in hash() before applying the hash function.
        """
        x = hash(item) % self._p
        return int((int(self._a[row]) * x + int(self._b[row])) % self._p % self._w)

    def sign(self, row: int, item) -> int:
        """Return sign hash of item for sketch row, result in {-1, +1}.

        Used by CountSketch only.
        """
        x = hash(item) % self._p
        bit = int((int(self._c[row]) * x + int(self._e[row])) % self._p % 2)
        return 2 * bit - 1
