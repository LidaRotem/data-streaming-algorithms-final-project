"""Smoke test for the streaming algorithms pipeline.

Runs a tiny experiment grid to verify the end-to-end pipeline works:
  - 1 synthetic dataset (uniform stub)
  - 3 memory budgets (from config)
  - 5 algorithm stubs
  - 1 seed (global_seed from config)
  - N = 1000 items (hardcoded for smoke test only)

Expected output: results/results.csv with exactly 15 rows.

Usage:
    python experiments/smoke_test.py --config configs/main.yaml
"""

import argparse
import os
import sys
import time
import uuid
from datetime import datetime, timezone

import yaml

# Ensure project root is on the path when running from any directory.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from src.algorithms.cms import CountMinSketch
from src.algorithms.cms_cu import CountMinSketchCU
from src.algorithms.count_sketch import CountSketch
from src.algorithms.ground_truth import GroundTruth
from src.algorithms.misra_gries import MisraGries
from src.algorithms.space_saving import SpaceSaving
from src.data.synthetic import generate_stream
from src.metrics.topk import overlap_at_k, precision_at_k, recall_at_k
from src.utils.io import log_result
from src.utils.timing import measure_throughput, set_seed

SMOKE_N = 1000  # hardcoded for smoke test only
RESULTS_PATH = "results/results.csv"

ALGORITHM_CLASSES = {
    "CMS": CountMinSketch,
    "CMS-CU": CountMinSketchCU,
    "CS": CountSketch,
    "MG": MisraGries,
    "SS": SpaceSaving,
}


def run_smoke_test(config_path: str) -> None:
    with open(config_path, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    budgets = {
        "M_small": config["memory_budgets"]["M_small"],
        "M_med": config["memory_budgets"]["M_med"],
        "M_large": config["memory_budgets"]["M_large"],
    }
    k = config["topk"]["k"]
    seed = config["seeds"]["global_seed"]

    rows_written = 0
    errors = []

    for budget_label, M in budgets.items():
        for algo_name, AlgoClass in ALGORITHM_CLASSES.items():
            try:
                set_seed(seed)
                gt_stream = generate_stream("uniform", SMOKE_N, seed)

                # Build ground truth (not timed — baseline only).
                gt = GroundTruth(M)
                for item in gt_stream:
                    gt.update(item)

                # Build algorithm and time updates.
                algo = AlgoClass(M)
                algo_stream = generate_stream("uniform", SMOKE_N, seed)
                updates_per_sec, _ = measure_throughput(algo.update, algo_stream)

                # Time topk query.
                t_q0 = time.perf_counter()
                algo_top = algo.topk(k)
                t_q1 = time.perf_counter()
                query_ms = (t_q1 - t_q0) * 1000

                # Compute top-k metrics.
                true_top = gt.true_topk(k)
                prec = precision_at_k(true_top, algo_top, k)
                rec = recall_at_k(true_top, algo_top, k)
                overlap = overlap_at_k(true_top, algo_top, k)

                # Compute skew.
                f1 = gt.F1
                skew = gt.F2 / (f1 * f1) if f1 > 0 else None

                row = {
                    "run_id": str(uuid.uuid4()),
                    "dataset": "uniform_stub",
                    "algorithm": algo_name,
                    "M": M,
                    "budget_label": budget_label,
                    "seed": seed,
                    "k": k,
                    "precision_at_k": prec,
                    "recall_at_k": rec,
                    "overlap_at_k": overlap,
                    "mae_heavy": None,
                    "mae_mid": None,
                    "mae_rare": None,
                    "rel_err_heavy": None,
                    "rel_err_mid": None,
                    "rel_err_rare": None,
                    "updates_per_sec": updates_per_sec,
                    "query_ms": query_ms,
                    "memory_counters": M,
                    "memory_bytes": algo.memory_bytes(),
                    "F0": gt.F0,
                    "F1": gt.F1,
                    "F2": gt.F2,
                    "skew": skew,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }

                log_result(row, RESULTS_PATH)
                rows_written += 1

            except Exception as e:
                errors.append(f"{budget_label}/{algo_name}: {e}")
                print(f"ERROR {budget_label}/{algo_name}: {e}", file=sys.stderr)

    print(f"\nSmoke test complete.")
    print(f"Rows written: {rows_written}")
    if errors:
        print(f"\nErrors ({len(errors)}):", file=sys.stderr)
        for err in errors:
            print(f"  {err}", file=sys.stderr)
        sys.exit(1)
    else:
        print("No errors.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Smoke test for streaming algorithms pipeline.")
    parser.add_argument("--config", required=True, help="Path to configs/main.yaml")
    args = parser.parse_args()
    run_smoke_test(args.config)
