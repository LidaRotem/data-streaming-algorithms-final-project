"""Top-k quality metrics.

Provides precision_at_k(), recall_at_k(), and overlap_at_k().
Both precision and recall are reported separately as required by the project spec,
even though they are numerically equal when |T_hat| = k.
"""


def precision_at_k(true_topk: list, estimated_topk: list, k: int) -> float:
    """Fraction of estimated top-k items that are in the true top-k.

    precision@k = |T_true ∩ T_hat| / k

    Parameters
    ----------
    true_topk:
        List of (item, count) from ground truth, sorted descending.
    estimated_topk:
        List of (item, estimated_count) from algorithm, sorted descending.
    k:
        Number of top items to consider.
    """
    if k <= 0:
        return 0.0
    true_set = {item for item, _ in true_topk[:k]}
    est_set = {item for item, _ in estimated_topk[:k]}
    return len(true_set & est_set) / k


def recall_at_k(true_topk: list, estimated_topk: list, k: int) -> float:
    """Fraction of true top-k items that appear in estimated top-k.

    recall@k = |T_true ∩ T_hat| / k

    Parameters
    ----------
    true_topk:
        List of (item, count) from ground truth, sorted descending.
    estimated_topk:
        List of (item, estimated_count) from algorithm, sorted descending.
    k:
        Number of top items to consider.
    """
    if k <= 0:
        return 0.0
    true_set = {item for item, _ in true_topk[:k]}
    est_set = {item for item, _ in estimated_topk[:k]}
    return len(true_set & est_set) / k


def overlap_at_k(true_topk: list, estimated_topk: list, k: int) -> int:
    """Number of items in common between true top-k and estimated top-k.

    overlap@k = |T_true ∩ T_hat|

    Parameters
    ----------
    true_topk:
        List of (item, count) from ground truth, sorted descending.
    estimated_topk:
        List of (item, estimated_count) from algorithm, sorted descending.
    k:
        Number of top items to consider.
    """
    true_set = {item for item, _ in true_topk[:k]}
    est_set = {item for item, _ in estimated_topk[:k]}
    return len(true_set & est_set)
