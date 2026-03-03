"""Stage 3 — dataset characterization.

For each dataset (4 synthetic + 2 real):
  1. Load or generate the processed stream.
  2. Compute F0, F1, F2, skew.
  3. Save a row to results/dataset_stats.csv.
  4. Save two plots to plots/:
       plots/skew_loglog_<dataset>.png
       plots/skew_hist_<dataset>.png
  5. Print a summary table to stdout.

Usage:
    python experiments/characterize_data.py --config configs/main.yaml
"""

import argparse
import collections
import csv
import os
import sys

# Allow running from project root without installing the package
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import yaml

from src.data.datasets import load_dataset
from src.metrics.skew import compute_stats, plot_rank_frequency, plot_frequency_histogram
from src.utils.timing import set_seed


# ---------------------------------------------------------------------------
# CSV output
# ---------------------------------------------------------------------------

STATS_COLUMNS = ["dataset", "N", "F0", "F1", "F2", "skew"]


def _ensure_stats_csv(path: str) -> None:
    """Create dataset_stats.csv with headers if it does not exist."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=STATS_COLUMNS)
            writer.writeheader()


def _append_stats_row(path: str, row: dict) -> None:
    with open(path, "a", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=STATS_COLUMNS)
        writer.writerow(row)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Characterize datasets and generate skew plots."
    )
    parser.add_argument("--config", required=True, help="Path to configs/main.yaml")
    args = parser.parse_args()

    with open(args.config, "r", encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)

    data_cfg = cfg["data"]
    processed_dir = data_cfg["processed_dir"]
    plots_dir = cfg.get("plots_dir", "plots")
    stats_csv_path = os.path.join(cfg.get("results_dir", "results"), "dataset_stats.csv")

    # Build ordered list of datasets to process
    synthetic_names = list(data_cfg["datasets"]["synthetic"].keys())
    real_names = list(data_cfg["datasets"]["real"].keys())
    all_datasets = synthetic_names + real_names

    global_seed = cfg["seeds"]["global_seed"]

    # Wipe and re-create dataset_stats.csv for this run (idempotent script)
    os.makedirs(os.path.dirname(stats_csv_path), exist_ok=True)
    with open(stats_csv_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=STATS_COLUMNS)
        writer.writeheader()

    os.makedirs(plots_dir, exist_ok=True)

    results = []

    for name in all_datasets:
        print(f"\n[{name}] Loading stream …")
        set_seed(global_seed)
        stream = list(load_dataset(name, cfg, seed=global_seed))

        print(f"[{name}] Computing stats …")
        stats = compute_stats(stream)

        row = {
            "dataset": name,
            "N": len(stream),
            "F0": stats["F0"],
            "F1": stats["F1"],
            "F2": stats["F2"],
            "skew": round(stats["skew"], 8),
        }
        _append_stats_row(stats_csv_path, row)
        results.append(row)

        freq_dict = collections.Counter(stream)

        loglog_path = os.path.join(plots_dir, f"skew_loglog_{name}.png")
        hist_path = os.path.join(plots_dir, f"skew_hist_{name}.png")

        print(f"[{name}] Saving plots …")
        plot_rank_frequency(freq_dict, name, loglog_path)
        plot_frequency_histogram(freq_dict, name, hist_path)
        print(f"[{name}] Done — F0={stats['F0']:,}  skew={stats['skew']:.6f}")

    # ------------------------------------------------------------------
    # Summary table
    # ------------------------------------------------------------------
    print("\n" + "=" * 76)
    print(f"{'Dataset':<14}{'N':>12}{'F0':>10}{'F1':>14}{'F2':>20}{'Skew':>12}")
    print("-" * 76)
    for row in results:
        print(
            f"{row['dataset']:<14}"
            f"{row['N']:>12,}"
            f"{row['F0']:>10,}"
            f"{row['F1']:>14,}"
            f"{row['F2']:>20,}"
            f"{row['skew']:>12.6f}"
        )
    print("=" * 76)
    print(f"\nStats saved to: {stats_csv_path}")
    print(f"Plots saved to: {plots_dir}/")


if __name__ == "__main__":
    main()