"""Unified dataset loader.

Provides load_dataset() which dispatches to:
  - synthetic generators (src.data.synthetic) for uniform / zipf_* / mixture
  - real dataset parsers  (src.data.parsers)   for kosarak / retail

Processed streams are cached to data/processed/<name>.txt.
If a processed file already exists it is read directly (no re-generation).

Each call to load_dataset() returns a fresh independent generator.

Usage
-----
Config is loaded once at the experiment entry point and passed explicitly::

    cfg = yaml.safe_load(open("configs/main.yaml"))
    stream = load_dataset("zipf_1_1", cfg, seed=0)

NOTE: For experiment runs, call generate_stream() directly with the per-run
seed to ensure correct seed isolation. load_dataset() is intended for
dataset characterization (characterize_data.py) which uses the cached files.
"""

import os
import sys

from src.data.synthetic import generate_stream
from src.data.parsers import parse_and_save, _stream_from_file
from src.utils.timing import set_seed


SYNTHETIC_TYPES = {"uniform", "zipf_1_1", "zipf_1_3", "mixture"}
REAL_TYPES = {"kosarak", "retail"}


def _processed_path(dataset_name: str, processed_dir: str) -> str:
    return os.path.join(processed_dir, f"{dataset_name}.txt")


def _read_processed(path: str):
    """Generator — yields one integer item at a time from a processed file."""
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                yield int(line)


def load_dataset(dataset_name: str, cfg: dict, seed: int):
    """Load (or generate) a dataset, returning a fresh generator.

    Parameters
    ----------
    dataset_name:
        One of 'uniform', 'zipf_1_1', 'zipf_1_3', 'mixture',
        'kosarak', 'retail'.
    cfg:
        Full config dict loaded from configs/main.yaml.
    seed:
        Random seed for synthetic generators.

    Returns
    -------
    generator
        Fresh generator of integer item IDs, yielding at most N_max items.

    Raises
    ------
    ValueError
        If dataset_name is not recognised.
    """
    data_cfg = cfg["data"]
    processed_dir = data_cfg["processed_dir"]
    N_max = cfg["stream"]["N_max"]

    processed_file = _processed_path(dataset_name, processed_dir)

    # ------------------------------------------------------------------
    # Synthetic datasets
    # ------------------------------------------------------------------
    if dataset_name in SYNTHETIC_TYPES:
        syn_cfg = data_cfg["datasets"]["synthetic"][dataset_name]
        N = int(syn_cfg.get("N", N_max))

        if os.path.exists(processed_file):
            print(
                f"  [{dataset_name}] reading from cache.",
                file=sys.stderr,
            )
            return _read_processed(processed_file)

        # Generate fresh stream and write to cache
        set_seed(seed)
        kwargs = {k: v for k, v in syn_cfg.items() if k != "N"}
        os.makedirs(processed_dir, exist_ok=True)
        count = 0
        with open(processed_file, "w", encoding="utf-8") as fh:
            for item in generate_stream(dataset_name, N, seed, **kwargs):
                fh.write(f"{item}\n")
                count += 1
        print(
            f"  [{dataset_name}] generated {count:,} items → {processed_file}",
            file=sys.stderr,
        )
        return _read_processed(processed_file)

    # ------------------------------------------------------------------
    # Real datasets
    # ------------------------------------------------------------------
    if dataset_name in REAL_TYPES:
        real_cfg = data_cfg["datasets"]["real"][dataset_name]
        raw_dir = data_cfg["raw_dir"]
        raw_file = real_cfg["raw_file"]
        raw_path = os.path.join(raw_dir, raw_file)

        if os.path.exists(processed_file):
            print(
                f"  [{dataset_name}] reading from cache.",
                file=sys.stderr,
            )
            return _read_processed(processed_file)

        return parse_and_save(raw_path, processed_file, N_max)

    raise ValueError(
        f"Unknown dataset_name '{dataset_name}'. "
        f"Expected one of: {sorted(SYNTHETIC_TYPES | REAL_TYPES)}."
    )