"""Tests for src/metrics/topk.py — precision_at_k, recall_at_k, overlap_at_k."""

import os
import sys

from pytest import approx

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.metrics.topk import overlap_at_k, precision_at_k, recall_at_k


def _make_topk(items: list) -> list:
    """Convert a list of item labels to (item, rank) tuples for testing."""
    return [(item, len(items) - i) for i, item in enumerate(items)]


class TestRecallAtK:
    def test_partial_overlap(self):
        true = _make_topk(["A", "B", "C", "D", "E"])
        est = _make_topk(["A", "B", "X", "Y", "Z"])
        assert recall_at_k(true, est, k=5) == approx(0.4)

    def test_full_overlap(self):
        true = _make_topk(["A", "B", "C"])
        est = _make_topk(["A", "B", "C"])
        assert recall_at_k(true, est, k=3) == approx(1.0)

    def test_no_overlap(self):
        true = _make_topk(["A", "B", "C"])
        est = _make_topk(["X", "Y", "Z"])
        assert recall_at_k(true, est, k=3) == approx(0.0)

    def test_k_zero(self):
        assert recall_at_k([], [], k=0) == 0.0


class TestPrecisionAtK:
    def test_partial_overlap(self):
        true = _make_topk(["A", "B", "C", "D", "E"])
        est = _make_topk(["A", "B", "X", "Y", "Z"])
        assert precision_at_k(true, est, k=5) == approx(0.4)

    def test_full_overlap(self):
        true = _make_topk(["A", "B", "C"])
        est = _make_topk(["A", "B", "C"])
        assert precision_at_k(true, est, k=3) == approx(1.0)

    def test_k_zero(self):
        assert precision_at_k([], [], k=0) == 0.0


class TestOverlapAtK:
    def test_partial_overlap(self):
        true = _make_topk(["A", "B", "C", "D", "E"])
        est = _make_topk(["A", "B", "X", "Y", "Z"])
        assert overlap_at_k(true, est, k=5) == approx(0.4)

    def test_full_overlap(self):
        true = _make_topk(["A", "B", "C"])
        est = _make_topk(["A", "B", "C"])
        assert overlap_at_k(true, est, k=3) == approx(1.0)

    def test_no_overlap(self):
        true = _make_topk(["A", "B", "C"])
        est = _make_topk(["X", "Y", "Z"])
        assert overlap_at_k(true, est, k=3) == approx(0.0)
