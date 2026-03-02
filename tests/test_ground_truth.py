"""Tests for GroundTruth on a known stream."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.algorithms.ground_truth import GroundTruth

_STREAM = [1, 1, 1, 2, 2, 3]


def _build_gt():
    gt = GroundTruth(M=0)
    for item in _STREAM:
        gt.update(item)
    return gt


def test_moments():
    gt = _build_gt()
    assert gt.F0 == 3        # three distinct items
    assert gt.F1 == 6        # six total items
    assert gt.F2 == 14       # 3^2 + 2^2 + 1^2 = 9 + 4 + 1


def test_true_topk():
    gt = _build_gt()
    topk = gt.true_topk(2)
    assert len(topk) == 2
    assert topk[0][0] == 1  # item 1 is most frequent (count 3)
    assert topk[1][0] == 2  # item 2 is second (count 2)


def test_query_known_items():
    gt = _build_gt()
    assert gt.query(1) == 3.0
    assert gt.query(2) == 2.0
    assert gt.query(3) == 1.0


def test_query_unseen_item():
    gt = _build_gt()
    assert gt.query(99) == 0.0


def test_reset():
    gt = _build_gt()
    gt.reset()
    assert gt.F0 == 0
    assert gt.F1 == 0
    assert gt.query(1) == 0.0
    assert gt.topk(5) == []
