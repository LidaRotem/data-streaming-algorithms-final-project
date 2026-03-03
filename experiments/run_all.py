"""Full experiment grid runner.

Runs all 210 (dataset × algorithm × budget × seed) combinations in parallel.
Writes results to results/results_full.csv (separate from smoke test output).

Usage:
    python experiments/run_all.py --config configs/main.yaml
"""

import argparse
import os
import sys
import time
import uuid
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from multiprocessing import cpu_count

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
from src.data.synthetic import generate_stream
from src.data.parsers import _stream_from_file
from src.metrics.topk import precision_at_k, recall_at_k, overlap_at_k
from src.metrics.point_queries import build_query_set, mae, relative_error
from src.utils.io import log_result
from src.utils.timing import set_seed

RESULTS_PATH = "results/results_full.csv"   # separate from smoke test

ALGORITHM_CLASSES = {
    "CMS":    CountMinSketch,
    "CMS-CU": CountMinSketchCU,
    "CS":     CountSketch,
    "MG":     MisraGries,
    "SS":     SpaceSaving,
}


def get_optimal_workers(num_runs: int, max_workers=None) -> int:
    available = cpu_count()
    cap = max_workers if max_workers is not None else (available - 1)
    return max(1, min(available - 1, num_runs, cap))


def _get_stream(dataset_name: str, seed: int, cfg: dict):
    """Return a fresh generator for the named dataset.

    Synthetic: calls generate_stream() with the given seed.
    Real: reads from processed file (seed-independent).
    """
    data_cfg = cfg["data"]
    processed_dir = data_cfg["processed_dir"]
    N_max = cfg["stream"]["N_max"]

    if dataset_name in {"uniform", "zipf_1_1", "zipf_1_3", "mixture"}:
        syn_cfg = data_cfg["datasets"]["synthetic"][dataset_name]
        N = int(syn_cfg.get("N", N_max))
        kwargs = {k: v for k, v in syn_cfg.items() if k != "N"}
        return generate_stream(dataset_name, N, seed, **kwargs)
    else:
        processed_path = os.path.join(processed_dir, f"{dataset_name}.txt")
        return _stream_from_file(processed_path)


def run_single(run_config: dict) -> dict:
    """Execute one (dataset, algo, M, seed) combination.

    TOP-LEVEL function — must not be nested. Required for multiprocessing pickle.
    """
    dataset = run_config["dataset"]
    algo_name = run_config["algo_name"]
    M = run_config["M"]
    budget_label = run_config["budget_label"]
    seed = run_config["seed"]
    k = run_config["k"]
    cfg = run_config["cfg"]

    set_seed(seed)
    AlgoClass = ALGORITHM_CLASSES[algo_name]

    # Pass 1 — Ground truth
    gt = GroundTruth(M)
    for item in _get_stream(dataset, seed, cfg):
        gt.update(item)

    # Pass 2 — Algorithm (timed)
    algo = AlgoClass(M, seed=seed)
    t0 = time.perf_counter()
    for item in _get_stream(dataset, seed, cfg):
        algo.update(item)
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

    # Point query metrics — per bucket
    f1 = gt.F1
    skew = gt.F2 / (f1 * f1) if f1 > 0 else None
    buckets = build_query_set(gt, k=k, seed=seed)
    query_set_heavy = buckets["heavy"]
    query_set_mid   = buckets["mid"]
    query_set_rare  = buckets["rare"]

    mae_heavy = mae(gt, algo, query_set_heavy)
    mae_mid   = mae(gt, algo, query_set_mid)
    mae_rare  = mae(gt, algo, query_set_rare)
    rel_heavy = relative_error(gt, algo, query_set_heavy)
    rel_mid   = relative_error(gt, algo, query_set_mid)
    rel_rare  = relative_error(gt, algo, query_set_rare)

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


def build_run_grid(cfg: dict) -> list:
    """Build all 210 run configurations.

    Synthetic: 4 datasets × 3 budgets × 5 algos × 3 seeds = 180
    Real:      2 datasets × 3 budgets × 5 algos × 1 seed  = 30
    Total: 210
    """
    budgets = {
        "M_small": cfg["memory_budgets"]["M_small"],
        "M_med":   cfg["memory_budgets"]["M_med"],
        "M_large": cfg["memory_budgets"]["M_large"],
    }
    k = cfg["topk"]["k"]
    syn_seeds  = cfg["seeds"]["synthetic_seeds"]
    real_seeds = cfg["seeds"]["real_seeds"]
    syn_datasets  = list(cfg["data"]["datasets"]["synthetic"].keys())
    real_datasets = list(cfg["data"]["datasets"]["real"].keys())

    runs = []
    for dataset in syn_datasets:
        for budget_label, M in budgets.items():
            for algo_name in ALGORITHM_CLASSES:
                for seed in syn_seeds:
                    runs.append(dict(
                        dataset=dataset, algo_name=algo_name,
                        M=M, budget_label=budget_label,
                        seed=seed, k=k, cfg=cfg,
                    ))
    for dataset in real_datasets:
        for budget_label, M in budgets.items():
            for algo_name in ALGORITHM_CLASSES:
                for seed in real_seeds:
                    runs.append(dict(
                        dataset=dataset, algo_name=algo_name,
                        M=M, budget_label=budget_label,
                        seed=seed, k=k, cfg=cfg,
                    ))
    return runs


def run_all(config_path: str):
    cfg = yaml.safe_load(open(config_path, encoding="utf-8"))
    runs = build_run_grid(cfg)
    max_workers = get_optimal_workers(
        len(runs),
        cfg.get("execution", {}).get("max_workers"),
    )

    os.makedirs("results", exist_ok=True)
    completed = 0
    total_run_time = 0.0
    wall_start = time.time()

    print(f"Starting {len(runs)} runs on {max_workers} workers...")

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(run_single, r): r for r in runs}
        with tqdm(total=len(runs), desc="Experiments", unit="run",
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
    print(f"Throughput {completed/elapsed:.1f} runs/s")
    print(f"Workers    {max_workers}")
    print(f"{'='*60}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Full experiment grid runner.")
    parser.add_argument("--config", required=True, help="Path to configs/main.yaml")
    args = parser.parse_args()
    run_all(args.config)