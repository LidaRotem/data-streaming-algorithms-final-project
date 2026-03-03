"""Stream skew computation and visualization.

Provides:
  compute_skew()             — skew = F2 / F1^2 (used inside experiment runner)
  compute_stats()            — returns F0, F1, F2, skew for a stream
  plot_rank_frequency()      — log-log rank-frequency plot
  plot_frequency_histogram() — frequency histogram (log-log axes)

Plot naming convention:
  plots/skew_loglog_<dataset>.png  — rank-frequency log-log plot
  plots/skew_hist_<dataset>.png    — frequency histogram
"""

import os
import collections

import matplotlib
matplotlib.use("Agg")  # non-interactive backend, safe for scripted use
import matplotlib.pyplot as plt
import numpy as np


# ---------------------------------------------------------------------------
# Core statistics
# ---------------------------------------------------------------------------

def compute_skew(counts: dict) -> float:
    """Compute stream skew as F2 / F1^2.

    Parameters
    ----------
    counts:
        Dict mapping item -> frequency.

    Returns
    -------
    float
        Skew value. Returns 0.0 if stream is empty.
    """
    f1 = sum(counts.values())
    if f1 == 0:
        return 0.0
    f2 = sum(v * v for v in counts.values())
    return f2 / (f1 * f1)


def compute_stats(stream: list) -> dict:
    """Compute F0, F1, F2, and skew for a stream.

    Parameters
    ----------
    stream:
        List of item IDs (integers or hashables).

    Returns
    -------
    dict with keys:
        F0   — number of distinct items
        F1   — total stream length (sum of frequencies)
        F2   — second frequency moment (sum of freq^2)
        skew — F2 / F1^2  (0.0 if stream is empty)
    """
    counts = collections.Counter(stream)
    f0 = len(counts)
    f1 = sum(counts.values())
    f2 = sum(v * v for v in counts.values())
    skew = f2 / (f1 * f1) if f1 > 0 else 0.0
    return {"F0": f0, "F1": f1, "F2": f2, "skew": skew}


# ---------------------------------------------------------------------------
# Visualizations
# ---------------------------------------------------------------------------

def plot_rank_frequency(
    freq_dict: dict,
    dataset_name: str,
    output_path: str,
) -> None:
    """Plot a rank-frequency curve on log-log axes and save as PNG.

    The most frequent item has rank 1. Zipf's law predicts a straight line
    on log-log axes with slope -alpha.

    Parameters
    ----------
    freq_dict:
        Dict mapping item -> frequency.
    dataset_name:
        Label used in the plot title.
    output_path:
        File path for the saved PNG (e.g. 'plots/skew_loglog_zipf_1_1.png').
    """
    if not freq_dict:
        raise ValueError(f"freq_dict is empty for dataset '{dataset_name}'.")

    freqs_sorted = sorted(freq_dict.values(), reverse=True)
    ranks = np.arange(1, len(freqs_sorted) + 1)
    freqs = np.array(freqs_sorted, dtype=np.float64)

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.loglog(ranks, freqs, linewidth=1.2, color="steelblue")
    ax.set_xlabel("Rank", fontsize=12)
    ax.set_ylabel("Frequency", fontsize=12)
    ax.set_title(f"Rank–Frequency (log–log) — {dataset_name}", fontsize=13)
    ax.grid(True, which="both", linestyle="--", linewidth=0.5, alpha=0.7)
    fig.tight_layout()

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def plot_frequency_histogram(
    freq_dict: dict,
    dataset_name: str,
    output_path: str,
) -> None:
    """Plot a histogram of item frequencies using log-log axes and save as PNG.

    x-axis: frequency value (log-binned)
    y-axis: number of items with that frequency (log scale)

    Parameters
    ----------
    freq_dict:
        Dict mapping item -> frequency.
    dataset_name:
        Label used in the plot title.
    output_path:
        File path for the saved PNG (e.g. 'plots/skew_hist_zipf_1_1.png').
    """
    if not freq_dict:
        raise ValueError(f"freq_dict is empty for dataset '{dataset_name}'.")

    freqs = np.array(list(freq_dict.values()), dtype=np.float64)
    min_freq = freqs.min()
    max_freq = freqs.max()

    if min_freq <= 0:
        raise ValueError("All frequencies must be positive for log-log histogram.")

    # Log-spaced bin edges covering the full frequency range
    n_bins = min(50, int(np.ceil(np.log10(max_freq / min_freq) * 10)) + 1)
    n_bins = max(n_bins, 10)
    bin_edges = np.logspace(np.log10(min_freq), np.log10(max_freq + 1), n_bins + 1)

    counts, edges = np.histogram(freqs, bins=bin_edges)
    bin_centers = np.sqrt(edges[:-1] * edges[1:])  # geometric midpoints

    # Only plot bins with at least one item
    mask = counts > 0

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar(
        bin_centers[mask],
        counts[mask],
        width=np.diff(edges)[mask],
        color="steelblue",
        edgecolor="white",
        linewidth=0.4,
        align="center",
    )
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Item frequency", fontsize=12)
    ax.set_ylabel("Number of items", fontsize=12)
    ax.set_title(f"Frequency histogram (log–log) — {dataset_name}", fontsize=13)
    ax.grid(True, which="both", linestyle="--", linewidth=0.5, alpha=0.7)
    fig.tight_layout()

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)