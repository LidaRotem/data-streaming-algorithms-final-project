"""CMS-B bounded-candidate ablation runner.

Runs CountMinSketchBounded (CMS-B) on zipf_1_3 across all 3 memory budgets and
all 3 synthetic seeds (9 runs total). Appends results to results/results_full.csv
with algorithm="CMS-B".

Usage:
    python experiments/run_bounded_ablation.py --config configs/main.yaml
"""

import argparse
import os
import sys
import time
import uuid
from datetime import datetime, timezone

import yaml

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from src.algorithms.cms_bounded import CountMinSketchBounded
from src.algorithms.ground_truth import GroundTruth
from src.data.synthetic import generate_stream
from src.metrics.topk import precision_at_k, recall_at_k, overlap_at_k
from src.metrics.point_queries import build_query_set, mae, relative_error
from src.utils.io import log_result
from src.utils.timing import set_seed

RESULTS_PATH = "results/results_full.csv"
DATASET = "zipf_1_3"


def run_single_cmsb(M: int, budget_label: str, seed: int, k: int, cfg: dict) -> dict:
    """Execute one CMS-B run on zipf_1_3."""
    set_seed(seed)

    syn_cfg = cfg["data"]["datasets"]["synthetic"][DATASET]
    N = int(syn_cfg.get("N", cfg["stream"]["N_max"]))
    kwargs = {key: val for key, val in syn_cfg.items() if key != "N"}

    # Pass 1 — Ground truth
    gt = GroundTruth(M)
    for item in generate_stream(DATASET, N, seed, **kwargs):
        gt.update(item)

    # Pass 2 — CMS-B (timed)
    algo = CountMinSketchBounded(M, seed=seed)
    t0 = time.perf_counter()
    for item in generate_stream(DATASET, N, seed, **kwargs):
        algo.update(item)
    run_time_sec = time.perf_counter() - t0

    f1 = gt.F1
    updates_per_sec = f1 / run_time_sec if run_time_sec > 0 else 0.0

    # Query timing
    t_q0 = time.perf_counter()
    algo_top = algo.topk(k)
    query_ms = (time.perf_counter() - t_q0) * 1000

    # Top-k metrics
    true_top = gt.true_topk(k)
    prec = precision_at_k(true_top, algo_top, k)
    rec = recall_at_k(true_top, algo_top, k)
    overlap = overlap_at_k(true_top, algo_top, k)

    # Point query metrics
    skew = gt.F2 / (f1 * f1) if f1 > 0 else None
    buckets = build_query_set(gt, k=k, seed=seed)
    mae_heavy = mae(gt, algo, buckets["heavy"])
    mae_mid   = mae(gt, algo, buckets["mid"])
    mae_rare  = mae(gt, algo, buckets["rare"])
    rel_heavy = relative_error(gt, algo, buckets["heavy"])
    rel_mid   = relative_error(gt, algo, buckets["mid"])
    rel_rare  = relative_error(gt, algo, buckets["rare"])

    return {
        "run_id":          str(uuid.uuid4()),
        "dataset":         DATASET,
        "algorithm":       "CMS-B",
        "M":               M,
        "budget_label":    budget_label,
        "seed":            seed,
        "k":               k,
        "precision_at_k":  prec,
        "recall_at_k":     rec,
        "overlap_at_k":    overlap,
        "mae_heavy":       mae_heavy,
        "mae_mid":         mae_mid,
        "mae_rare":        mae_rare,
        "rel_err_heavy":   rel_heavy,
        "rel_err_mid":     rel_mid,
        "rel_err_rare":    rel_rare,
        "updates_per_sec": updates_per_sec,
        "query_ms":        query_ms,
        "memory_counters": M,
        "memory_bytes":    algo.memory_bytes(),
        "F0":              gt.F0,
        "F1":              gt.F1,
        "F2":              gt.F2,
        "skew":            skew,
        "timestamp":       datetime.now(timezone.utc).isoformat(),
    }


def run_ablation(config_path: str):
    cfg = yaml.safe_load(open(config_path, encoding="utf-8"))
    k = cfg["topk"]["k"]
    seeds = cfg["seeds"]["synthetic_seeds"]
    budgets = {
        "M_small": cfg["memory_budgets"]["M_small"],
        "M_med":   cfg["memory_budgets"]["M_med"],
        "M_large": cfg["memory_budgets"]["M_large"],
    }

    os.makedirs("results", exist_ok=True)

    runs = [
        (budget_label, M, seed)
        for budget_label, M in budgets.items()
        for seed in seeds
    ]
    total = len(runs)
    completed = 0

    for budget_label, M, seed in runs:
        print(f"Running CMS-B {DATASET} M={M} seed={seed}...")
        result = run_single_cmsb(M, budget_label, seed, k, cfg)
        log_result(result, RESULTS_PATH)
        completed += 1

    print(f"{completed}/{total} complete. Appended to {RESULTS_PATH}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CMS-B bounded-candidate ablation runner.")
    parser.add_argument("--config", required=True, help="Path to configs/main.yaml")
    args = parser.parse_args()
    run_ablation(args.config)
