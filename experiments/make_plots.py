"""Generate all experiment figures from results/results_full.csv.

Usage:
    python experiments/make_plots.py --config configs/main.yaml
"""

import argparse
import os

import matplotlib
matplotlib.use('Agg')  # non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml

ALGO_COLORS = {
    'CMS':    '#1f77b4',  # blue
    'CMS-CU': '#ff7f0e',  # orange
    'CS':     '#2ca02c',  # green
    'MG':     '#d62728',  # red
    'SS':     '#9467bd',  # purple
}
ALGO_ORDER = ['CMS', 'CMS-CU', 'CS', 'MG', 'SS']
BUDGETS = [500, 2000, 8000]
DATASETS_ORDER = ['uniform', 'zipf_1_1', 'zipf_1_3', 'mixture', 'kosarak', 'retail']
DATASET_LABELS = {
    'uniform': 'Uniform',
    'zipf_1_1': 'Zipf α=1.1',
    'zipf_1_3': 'Zipf α=1.3',
    'mixture': 'Mixture',
    'kosarak': 'Kosarak',
    'retail': 'Retail',
}
REAL_DATASETS = {'kosarak', 'retail'}


def load_data(results_path, stats_path):
    df = pd.read_csv(results_path)
    stats = pd.read_csv(stats_path).set_index('dataset')
    return df, stats


def _agg_metric(df, metric, group_cols):
    """Return mean ± std of metric grouped by group_cols."""
    grouped = df.groupby(group_cols)[metric]
    return grouped.mean(), grouped.std()


def _draw_6panel(fig, axes, df, stats, metric, ylabel, title):
    """Helper: draw 6-panel grid (2×3) for a per-dataset metric."""
    for idx, dataset in enumerate(DATASETS_ORDER):
        ax = axes[idx // 3][idx % 3]
        sub = df[df['dataset'] == dataset]
        skew_val = stats.loc[dataset, 'skew'] if dataset in stats.index else 0.0
        is_real = dataset in REAL_DATASETS

        for algo in ALGO_ORDER:
            sub_algo = sub[sub['algorithm'] == algo]
            means = sub_algo.groupby('M')[metric].mean().reindex(BUDGETS)
            stds = sub_algo.groupby('M')[metric].std().reindex(BUDGETS)

            ax.plot(
                BUDGETS,
                means.values,
                marker='o',
                color=ALGO_COLORS[algo],
                label=algo,
                linewidth=1.8,
                markersize=5,
            )
            # Error bars only for synthetic (real datasets have 1 seed)
            if not is_real:
                ax.errorbar(
                    BUDGETS,
                    means.values,
                    yerr=stds.values,
                    fmt='none',
                    ecolor=ALGO_COLORS[algo],
                    alpha=0.4,
                    capsize=3,
                )

        ax.set_xscale('log')
        ax.set_xticks(BUDGETS)
        ax.set_xticklabels([str(b) for b in BUDGETS], fontsize=8)
        ax.set_ylabel(ylabel, fontsize=9)
        ax.set_xlabel('M (budget)', fontsize=9)
        ax.set_title(f'{DATASET_LABELS[dataset]} (skew={skew_val:.4f})', fontsize=9)
        ax.set_ylim(0, 1.05)
        ax.grid(True, alpha=0.3)

        if idx == 0:
            ax.legend(fontsize=7, loc='upper left')

    fig.suptitle(title, fontsize=13, fontweight='bold')
    fig.tight_layout(rect=[0, 0, 1, 0.96])


def plot_precision(df, stats, plots_dir):
    fig, axes = plt.subplots(2, 3, figsize=(13, 8))
    _draw_6panel(fig, axes, df, stats, 'precision_at_k', 'Precision@k', 'Precision@k vs Memory Budget')
    path = os.path.join(plots_dir, 'fig_1_precision.png')
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f'  Saved {path}')


def plot_overlap(df, stats, plots_dir):
    fig, axes = plt.subplots(2, 3, figsize=(13, 8))
    _draw_6panel(fig, axes, df, stats, 'overlap_at_k', 'Overlap@k', 'Overlap@k vs Memory Budget')
    # Add note to figure
    fig.text(
        0.5, 0.01,
        'Note: overlap@k = precision@k when |T̂| = k (all runs in this experiment)',
        ha='center', fontsize=8, style='italic', color='#555555',
    )
    path = os.path.join(plots_dir, 'fig_2_overlap.png')
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f'  Saved {path}')


def plot_mae(df, plots_dir):
    fig, axes = plt.subplots(1, 3, figsize=(13, 5))
    buckets = [('mae_heavy', 'Heavy items'), ('mae_mid', 'Mid items'), ('mae_rare', 'Rare items')]

    for col_idx, (metric, bucket_label) in enumerate(buckets):
        ax = axes[col_idx]
        for algo in ALGO_ORDER:
            sub_algo = df[df['algorithm'] == algo]
            # Grand mean across all datasets and seeds
            means = sub_algo.groupby('M')[metric].mean().reindex(BUDGETS)
            ax.plot(
                BUDGETS,
                means.values,
                marker='o',
                color=ALGO_COLORS[algo],
                label=algo,
                linewidth=1.8,
                markersize=5,
            )

        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_xticks(BUDGETS)
        ax.set_xticklabels([str(b) for b in BUDGETS], fontsize=8)
        ax.set_ylabel('Mean Absolute Error (log scale)', fontsize=9)
        ax.set_xlabel('M (budget)', fontsize=9)
        ax.set_title(bucket_label, fontsize=10)
        ax.grid(True, alpha=0.3, which='both')

        if col_idx == 2:
            ax.legend(fontsize=8, loc='upper right')

    fig.suptitle('Point Query MAE by Frequency Bucket (grand mean across datasets)', fontsize=12, fontweight='bold')
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    path = os.path.join(plots_dir, 'fig_3_mae.png')
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f'  Saved {path}')


def plot_throughput(df, stats, plots_dir):
    fig, axes = plt.subplots(2, 3, figsize=(13, 8))

    for idx, dataset in enumerate(DATASETS_ORDER):
        ax = axes[idx // 3][idx % 3]
        sub = df[df['dataset'] == dataset]
        skew_val = stats.loc[dataset, 'skew'] if dataset in stats.index else 0.0
        is_real = dataset in REAL_DATASETS

        for algo in ALGO_ORDER:
            sub_algo = sub[sub['algorithm'] == algo]
            means = sub_algo.groupby('M')['updates_per_sec'].mean().reindex(BUDGETS)

            ax.plot(
                BUDGETS,
                means.values,
                marker='o',
                color=ALGO_COLORS[algo],
                label=algo,
                linewidth=1.8,
                markersize=5,
            )

        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_xticks(BUDGETS)
        ax.set_xticklabels([str(b) for b in BUDGETS], fontsize=8)
        ax.set_ylabel('Updates / sec (log scale)', fontsize=9)
        ax.set_xlabel('M (budget)', fontsize=9)
        ax.set_title(f'{DATASET_LABELS[dataset]} (skew={skew_val:.4f})', fontsize=9)
        ax.grid(True, alpha=0.3, which='both')

        if idx == 0:
            ax.legend(fontsize=7, loc='upper right')

    fig.suptitle('Throughput (updates/sec) vs Memory Budget', fontsize=13, fontweight='bold')
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    path = os.path.join(plots_dir, 'fig_4_throughput.png')
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f'  Saved {path}')


def plot_memory(df, plots_dir):
    fig, ax = plt.subplots(figsize=(8, 5))

    for algo in ALGO_ORDER:
        sub_algo = df[df['algorithm'] == algo]
        means = sub_algo.groupby('M')['memory_bytes'].mean().reindex(BUDGETS)
        ax.plot(
            BUDGETS,
            means.values,
            marker='o',
            color=ALGO_COLORS[algo],
            label=algo,
            linewidth=2,
            markersize=7,
        )

    ax.set_yscale('log')
    ax.set_xticks(BUDGETS)
    ax.set_xticklabels([str(b) for b in BUDGETS], fontsize=9)
    ax.set_xlabel('M (budget)', fontsize=10)
    ax.set_ylabel('Memory bytes (log scale)', fontsize=10)
    ax.set_title('Actual Memory Usage vs Budget M', fontsize=12, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3, which='both')
    ax.text(
        0.02, 0.02,
        'MG grows with distinct items tracked; SS stores key strings\nSketches use fixed numpy arrays',
        transform=ax.transAxes, fontsize=8, color='#555555',
        verticalalignment='bottom',
    )
    fig.tight_layout()
    path = os.path.join(plots_dir, 'fig_5_memory_bytes.png')
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f'  Saved {path}')


def main(config_path):
    cfg = yaml.safe_load(open(config_path))
    plots_dir = cfg.get('plots_dir', 'plots')
    results_dir = cfg.get('results_dir', 'results')
    results_path = os.path.join(results_dir, 'results_full.csv')
    stats_path = os.path.join(results_dir, 'dataset_stats.csv')
    os.makedirs(plots_dir, exist_ok=True)

    print(f'Loading data from {results_path}')
    df, stats = load_data(results_path, stats_path)
    print(f'  {len(df)} rows loaded')

    print('Generating figures...')
    plot_precision(df, stats, plots_dir)
    plot_overlap(df, stats, plots_dir)
    plot_mae(df, plots_dir)
    plot_throughput(df, stats, plots_dir)
    plot_memory(df, plots_dir)
    print(f'All figures saved to {plots_dir}/')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate experiment figures')
    parser.add_argument('--config', required=True, help='Path to configs/main.yaml')
    args = parser.parse_args()
    main(args.config)