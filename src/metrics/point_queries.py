"""Point query accuracy metrics.

Provides mae(), relative_error(), and build_query_set() for per-bucket
frequency estimation evaluation (heavy / mid / rare).
"""

import random


def mae(ground_truth, algo, query_set: list) -> float:
    """Mean absolute error of frequency estimates over a list of items.

    MAE = avg(|f_hat(i) - f(i)|) for i in query_set

    Parameters
    ----------
    ground_truth:
        GroundTruth instance with a .query(item) method.
    algo:
        Algorithm instance with a .query(item) method.
    query_set:
        List of items to evaluate.
    """
    if not query_set:
        return 0.0
    errors = [abs(algo.query(item) - ground_truth.query(item)) for item in query_set]
    return sum(errors) / len(errors)


def relative_error(ground_truth, algo, query_set: list) -> float:
    """Mean relative error of frequency estimates over a list of items.

    rel_err = avg(|f_hat(i) - f(i)| / max(1, f(i))) for i in query_set

    Parameters
    ----------
    ground_truth:
        GroundTruth instance with a .query(item) method.
    algo:
        Algorithm instance with a .query(item) method.
    query_set:
        List of items to evaluate.
    """
    if not query_set:
        return 0.0
    errors = [
        abs(algo.query(item) - ground_truth.query(item)) / max(1.0, ground_truth.query(item))
        for item in query_set
    ]
    return sum(errors) / len(errors)


def build_query_set(
    ground_truth, k: int, n_mid: int = 100, n_rare: int = 100, seed: int = 0
) -> dict:
    """Build a stratified query set split into heavy, mid, and rare buckets.

    Parameters
    ----------
    ground_truth:
        GroundTruth instance after processing the full stream.
    k:
        Number of top items; these form the 'heavy' bucket.
    n_mid:
        Number of items to sample from the middle-frequency tier.
    n_rare:
        Number of items to sample from the low-frequency tier.
    seed:
        Seed for sampling mid and rare items (independent of run seed).

    Returns
    -------
    dict
        {'heavy': [item, ...], 'mid': [item, ...], 'rare': [item, ...]}
    """
    rng = random.Random(seed)

    # All items sorted by frequency descending — uses public topk API with large k.
    all_sorted = ground_truth.topk(k=10 ** 9)

    heavy = [item for item, _ in all_sorted[:k]]

    remaining = all_sorted[k:]
    boundary = len(remaining) // 2
    mid_candidates = [item for item, _ in remaining[:boundary]]
    rare_candidates = [item for item, _ in remaining[boundary:]]

    mid = rng.sample(mid_candidates, min(n_mid, len(mid_candidates)))
    rare = rng.sample(rare_candidates, min(n_rare, len(rare_candidates)))

    return {"heavy": heavy, "mid": mid, "rare": rare}
