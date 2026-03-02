"""Results logging utilities.

Provides log_result() to append one row per experiment run to results/results.csv.
"""

import csv
import os

COLUMNS = [
    "run_id",
    "dataset",
    "algorithm",
    "M",
    "budget_label",
    "seed",
    "k",
    "precision_at_k",
    "recall_at_k",
    "overlap_at_k",
    "mae_heavy",
    "mae_mid",
    "mae_rare",
    "rel_err_heavy",
    "rel_err_mid",
    "rel_err_rare",
    "updates_per_sec",
    "query_ms",
    "memory_counters",
    "memory_bytes",
    "F0",
    "F1",
    "F2",
    "skew",
    "timestamp",
]


def log_result(row: dict, path: str) -> None:
    """Append one result row to a CSV file.

    Creates the file with a header if it does not yet exist.
    Missing columns in row are written as empty strings.

    Parameters
    ----------
    row:
        Dict mapping column names to values. Must contain at least all COLUMNS keys.
    path:
        Path to the CSV file (relative to project root).
    """
    dir_name = os.path.dirname(path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)

    file_exists = os.path.isfile(path)

    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)
