"""Tests for CountMinSketchBounded (CMS-B)."""

import pytest
from src.algorithms.cms_bounded import CountMinSketchBounded


def test_basic_update_and_query():
    """All query results are non-negative after 100 updates."""
    algo = CountMinSketchBounded(M=50, seed=0)
    for i in range(100):
        algo.update(i % 20)
    for i in range(20):
        assert algo.query(i) >= 0


def test_candidates_bounded():
    """len(_candidates) never exceeds M after any update."""
    M = 100
    algo = CountMinSketchBounded(M=M, seed=1)
    for i in range(10000):
        algo.update(i)
        assert len(algo._candidates) <= M


def test_topk_returns_k_items():
    """topk(10) returns exactly 10 tuples after 200 updates."""
    algo = CountMinSketchBounded(M=50, seed=2)
    for i in range(200):
        algo.update(i % 30)
    result = algo.topk(10)
    assert len(result) == 10
    for item, count in result:
        assert isinstance(count, float)


def test_heavy_hitter_recalled():
    """A dominant item (900/1000 events) appears in topk(1)."""
    algo = CountMinSketchBounded(M=200, seed=3)
    for _ in range(900):
        algo.update(42)
    for i in range(100):
        algo.update(i)
    result = algo.topk(1)
    assert len(result) == 1
    assert result[0][0] == 42


def test_memory_bytes_positive():
    """memory_bytes() returns a positive integer after updates."""
    algo = CountMinSketchBounded(M=100, seed=4)
    for i in range(50):
        algo.update(i)
    mb = algo.memory_bytes()
    assert isinstance(mb, int)
    assert mb > 0


def test_reset():
    """After reset(), _candidates is empty and table is all zeros."""
    algo = CountMinSketchBounded(M=100, seed=5)
    for i in range(200):
        algo.update(i)
    algo.reset()
    assert len(algo._candidates) == 0
    assert algo._table.sum() == 0


def test_interface_matches_cms():
    """CMS-B exposes all required algorithm API methods."""
    algo = CountMinSketchBounded(M=50, seed=6)
    assert hasattr(algo, "update")
    assert hasattr(algo, "query")
    assert hasattr(algo, "topk")
    assert hasattr(algo, "reset")
    assert hasattr(algo, "memory_bytes")
    # Smoke-check return types
    algo.update(1)
    assert isinstance(algo.query(1), float)
    assert isinstance(algo.topk(1), list)
    assert isinstance(algo.memory_bytes(), int)
