"""Real dataset order-sensitivity ablation.

Runs all 5 algorithms on 3 randomly shuffled permutations of Kosarak and
Retail (shuffle seeds 1, 2, 3). Original order (seed=0) already in
results_full.csv. Appends 90 rows.

Grid:
  datasets:      kosarak, retail
  algorithms:    CMS, CMS-CU, CS, MG, SS
  budgets:       M_small, M_med, M_large
  shuffle_seeds: [1, 2, 3]
  Total:         2 x 5 x 3 x 3 = 90

Usage:
    python experiments/run_shuffle_ablation.py --config configs/main.yaml
"""

import argparse
import os
import sys
import time
import uuid
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone

import numpy as np
import yaml
from tqdm import tqdm

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from src.algorithms.cms import CountMinSketch
from src.algorithms.cms_cu import CountMinSketchCU
from src.algorithms.count_sketch import CountSketch
from src.algorithms.ground_truth import GroundTruth
from src.algorithms.misra_gries import MisraGries
from src.algorithms.space_saving import SpaceSaving
from src.data.parsers import _stream_from_file
from src.metrics.point_queries import build_query_set, mae, relative_error
from src.metrics.topk import precision_at_k, recall_at_k, overlap_at_k
from src.utils.io import log_result
from src.utils.timing import set_seed

RESULTS_PATH = "results/results_full.csv"

ALGORITHM_CLASSES = {
    "CMS":    CountMinSketch,
    "CMS-CU": CountMinSketchCU,
    "CS":     CountSketch,
    "MG":     MisraGries,
    "SS":     SpaceSaving,
}

REAL_DATASETS = ["kosarak", "retail"]
SHUFFLE_SEEDS = [1, 2, 3]


def run_single(run_config: dict) -> dict:
    """Execute one (dataset, algo, M, shuffle_seed) combination.

    TOP-LEVEL function — must not be nested. Required for multiprocessing pickle.
    """
    dataset = run_config["dataset"]
    algo_name = run_config["algo_name"]
    M = run_config["M"]
    budget_label = run_config["budget_label"]
    seed = run_config["seed"]   # shuffle_seed stored in seed column
    k = run_config["k"]
    items_arr = run_config["items_arr"]  # numpy int64 array (shuffled)

    set_seed(seed)

    AlgoClass = ALGORITHM_CLASSES[algo_name]

    # Pass 1 — Ground truth (iterate over shuffled array)
    gt = GroundTruth(M)
    for item in items_arr:
        gt.update(int(item))

    # Pass 2 — Algorithm (timed, iterate over shuffled array)
    algo = AlgoClass(M, seed=seed)
    t0 = time.perf_counter()
    for item in items_arr:
        algo.update(int(item))
    run_time_sec = time.perf_counter() - t0

    N = gt.F1
    updates_per_sec = N / run_time_sec if run_time_sec > 0 else 0.0

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
    f1 = gt.F1
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
        "dataset":         dataset,
        "algorithm":       algo_name,
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
        "run_time_sec":    run_time_sec,   # not written to CSV
    }


def build_run_configs(cfg: dict) -> list:
    """Build all 90 shuffle run configurations.

    For each dataset: load file into memory once, then create shuffled copies.
    Each run_config includes the pre-shuffled items_arr (numpy int64).
    """
    processed_dir = cfg["data"]["processed_dir"]
    budgets = {
        "M_small": cfg["memory_budgets"]["M_small"],
        "M_med":   cfg["memory_budgets"]["M_med"],
        "M_large": cfg["memory_budgets"]["M_large"],
    }
    k = cfg["topk"]["k"]

    runs = []
    for dataset in REAL_DATASETS:
        processed_path = os.path.join(processed_dir, f"{dataset}.txt")
        # Load full dataset into memory once
        items = list(_stream_from_file(processed_path))
        items_base = np.array(items, dtype=np.int64)

        for shuffle_seed in SHUFFLE_SEEDS:
            # Create shuffled copy for this seed
            rng = np.random.default_rng(shuffle_seed)
            items_arr = items_base.copy()
            rng.shuffle(items_arr)

            for budget_label, M in budgets.items():
                for algo_name in ALGORITHM_CLASSES:
                    runs.append(dict(
                        dataset=dataset,
                        algo_name=algo_name,
                        M=M,
                        budget_label=budget_label,
                        seed=shuffle_seed,   # shuffle_seed stored in seed column
                        k=k,
                        items_arr=items_arr,
                    ))
    return runs


def run_shuffle_ablation(config_path: str):
    cfg = yaml.safe_load(open(config_path, encoding="utf-8"))
    max_workers_cfg = cfg.get("execution", {}).get("max_workers")

    os.makedirs("results", exist_ok=True)

    print("Loading datasets and building run configs...")
    runs = build_run_configs(cfg)
    print(f"Built {len(runs)} run configs.")

    from multiprocessing import cpu_count
    available = cpu_count()
    if max_workers_cfg is not None:
        max_workers = max(1, min(available - 1, len(runs), max_workers_cfg))
    else:
        max_workers = max(1, min(available - 1, len(runs)))

    completed = 0
    total_run_time = 0.0
    wall_start = time.time()

    print(f"Starting {len(runs)} runs on {max_workers} workers...")

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(run_single, r): r for r in runs}
        with tqdm(total=len(runs), desc="Shuffle ablation", unit="run",
                  bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} "
                             "[{elapsed}<{remaining}, {rate_fmt}]") as pbar:
            for future in as_completed(futures):
                result = future.result()
                total_run_time += result.pop("run_time_sec", 0)
                completed += 1
                pbar.set_postfix(avg_s=f"{total_run_time/completed:.2f}")
                pbar.update(1)
                log_result(result, RESULTS_PATH)

    elapsed = time.time() - wall_start
    print(f"\n{'='*60}")
    print(f"COMPLETED  {completed}/{len(runs)} runs")
    print(f"Wall time  {elapsed:.1f}s  ({elapsed/60:.1f} min)")
    print(f"Avg/run    {elapsed/completed:.2f}s")
    print(f"Workers    {max_workers}")
    print(f"{'='*60}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Real dataset order-sensitivity ablation.")
    parser.add_argument("--config", required=True, help="Path to configs/main.yaml")
    args = parser.parse_args()
    run_shuffle_ablation(args.config)
