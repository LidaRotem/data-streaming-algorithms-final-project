"""Stream skew computation and visualization.

Provides compute_skew(), plot_rank_frequency_loglog(), and plot_frequency_histogram().
Plot functions are stubs — full implementation in Stage 3.

Plot naming convention:
  plots/skew_loglog_<dataset>.png  — rank-frequency log-log plot
  plots/skew_hist_<dataset>.png    — frequency histogram
"""


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


def plot_rank_frequency_loglog(
    freq_dict: dict, dataset_name: str, output_path: str
) -> None:
    """Plot rank-frequency curve on log-log axes and save as PNG.

    Parameters
    ----------
    freq_dict:
        Dict mapping item -> frequency.
    dataset_name:
        Label used in the plot title.
    output_path:
        File path for the saved PNG (e.g. 'plots/skew_loglog_zipf.png').

    Notes
    -----
    Stub — full implementation in Stage 3.
    """
    # Stage 3: implement log-log rank-frequency plot using matplotlib.
    raise NotImplementedError("plot_rank_frequency_loglog is a Stage 3 deliverable.")


def plot_frequency_histogram(
    freq_dict: dict, dataset_name: str, output_path: str
) -> None:
    """Plot a histogram of item frequencies (log scale on both axes) and save as PNG.

    x-axis: frequency bucket (log-binned)
    y-axis: number of items with that frequency (log scale)

    Parameters
    ----------
    freq_dict:
        Dict mapping item -> frequency.
    dataset_name:
        Label used in the plot title.
    output_path:
        File path for the saved PNG (e.g. 'plots/skew_hist_zipf.png').

    Notes
    -----
    Stub — full implementation in Stage 3.
    """
    # Stage 3: implement frequency histogram using matplotlib.
    raise NotImplementedError("plot_frequency_histogram is a Stage 3 deliverable.")
