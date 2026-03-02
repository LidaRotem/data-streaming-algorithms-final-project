"""Soft correctness test: precision@10 > 0.5 on a Zipf stream (N=10000, alpha=1.3).

This is a sanity check, not a strict pass/fail gate. If an algorithm fails the
threshold, the test fails with a descriptive message so it can be flagged in the
Stage 2 handback without blocking the overall suite.
"""

import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.algorithms.cms import CountMinSketch
from src.algorithms.cms_cu import CountMinSketchCU
from src.algorithms.count_sketch import CountSketch
from src.algorithms.ground_truth import GroundTruth
from src.algorithms.misra_gries import MisraGries
from src.algorithms.space_saving import SpaceSaving
from src.metrics.topk import precision_at_k

_N = 10_000
_ALPHA = 1.3
_M = 2000
_K = 10
_SEED = 42
_N_ITEMS = 1000


def _generate_zipf_stream(n, alpha, seed, n_items=_N_ITEMS):
    rng = np.random.default_rng(seed)
    ranks = np.arange(1, n_items + 1)
    weights = 1.0 / ranks ** alpha
    weights /= weights.sum()
    return rng.choice(n_items, size=n, p=weights).tolist()


_STREAM = _generate_zipf_stream(_N, _ALPHA, _SEED)

_ALGORITHMS = [
    ("CMS", CountMinSketch),
    ("CMS-CU", CountMinSketchCU),
    ("CS", CountSketch),
    ("MG", MisraGries),
    ("SS", SpaceSaving),
]


@pytest.fixture(scope="module")
def ground_truth():
    gt = GroundTruth(_M)
    for item in _STREAM:
        gt.update(item)
    return gt


@pytest.mark.parametrize("name,AlgoClass", _ALGORITHMS, ids=[n for n, _ in _ALGORITHMS])
def test_precision_soft_threshold(name, AlgoClass, ground_truth):
    true_top = ground_truth.true_topk(_K)

    algo = AlgoClass(_M, seed=_SEED)
    for item in _STREAM:
        algo.update(item)
    algo_top = algo.topk(_K)

    prec = precision_at_k(true_top, algo_top, _K)
    assert prec > 0.5, (
        f"{name}: precision@{_K}={prec:.3f} did not exceed soft threshold 0.5. "
        "Flagged for Stage 2 handback."
    )
