"""Correctness tests for all 5 streaming algorithm implementations.

Parametrized over CountMinSketch, CountMinSketchCU, CountSketch,
MisraGries, and SpaceSaving.
"""

import os
import random
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.algorithms.cms import CountMinSketch
from src.algorithms.cms_cu import CountMinSketchCU
from src.algorithms.count_sketch import CountSketch
from src.algorithms.misra_gries import MisraGries
from src.algorithms.space_saving import SpaceSaving

ALGORITHMS = [CountMinSketch, CountMinSketchCU, CountSketch, MisraGries, SpaceSaving]
ALGO_IDS = [cls.__name__ for cls in ALGORITHMS]

_SEED = 42
_M = 200
_N = 100
_K = 10


def _make_stream(seed=_SEED, n=_N, n_items=50):
    rng = random.Random(seed)
    return [rng.randint(0, n_items - 1) for _ in range(n)]


@pytest.mark.parametrize("AlgoClass", ALGORITHMS, ids=ALGO_IDS)
class TestAlgorithms:
    def test_no_crash(self, AlgoClass):
        stream = _make_stream()
        algo = AlgoClass(_M, seed=_SEED)
        for item in stream:
            algo.update(item)
        for item in stream[:10]:
            algo.query(item)
        algo.topk(_K)

    def test_deterministic(self, AlgoClass):
        stream = _make_stream()

        algo1 = AlgoClass(_M, seed=_SEED)
        for item in stream:
            algo1.update(item)

        algo2 = AlgoClass(_M, seed=_SEED)
        for item in stream:
            algo2.update(item)

        for item in stream[:10]:
            assert algo1.query(item) == algo2.query(item)

    def test_query_nonnegative(self, AlgoClass):
        stream = _make_stream()
        algo = AlgoClass(_M, seed=_SEED)
        for item in stream:
            algo.update(item)
        for item in stream:
            result = algo.query(item)
            assert isinstance(result, float)
            assert result >= 0.0

    def test_topk_length(self, AlgoClass):
        stream = _make_stream()
        algo = AlgoClass(_M, seed=_SEED)
        for item in stream:
            algo.update(item)
        result = algo.topk(_K)
        assert len(result) <= _K

    def test_topk_sorted(self, AlgoClass):
        stream = _make_stream()
        algo = AlgoClass(_M, seed=_SEED)
        for item in stream:
            algo.update(item)
        result = algo.topk(_K)
        counts = [count for _, count in result]
        assert counts == sorted(counts, reverse=True)

    def test_reset(self, AlgoClass):
        stream = _make_stream()
        algo = AlgoClass(_M, seed=_SEED)
        for item in stream:
            algo.update(item)
        algo.reset()
        for item in stream[:10]:
            assert algo.query(item) == 0.0
        assert algo.topk(_K) == []
