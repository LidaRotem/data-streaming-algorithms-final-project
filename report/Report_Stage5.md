# Final Project Report — Algorithms for Real-Time Data Stream Analysis

## Title Page
- **Project title:** Under a fixed memory budget, which approach identifies Heavy Hitters (Top-k) more reliably — hash-based sketches or counter-based summaries — and how does performance change with stream skew and across real datasets?
- **Course:** Algorithms for Real-Time Data Stream Analysis
- **Submission date:** 2026-03-03
- **Repo:** attached zip / see `README.md`

---

## Abstract

Identifying the top-k most frequent items ("heavy hitters") in a high-speed data stream is hard:
the key space may be enormous, the stream cannot be rewound, and memory is strictly bounded.
We compare two algorithm families across 6 datasets and 3 memory budgets:
hash-based sketches (Count-Min Sketch, CMS with Conservative Update, Count-Sketch)
and counter-based summaries (Misra–Gries, Space-Saving).
Algorithms were evaluated on Top-k quality (Precision@k, Overlap@k),
point-query error (MAE and relative error for heavy/mid/rare frequency buckets),
and throughput (updates/sec, query latency).
On high-skew streams, MG and SS dominate: on Zipf α=1.3 (skew=0.094), both achieve Precision@k=1.000
at every budget, while the best sketch (CMS-CU) reaches only 0.523 at M=500.
CMS-CU is the best sketch for point-query accuracy and improves substantially over plain CMS
on moderately skewed streams (up to Δ=0.28 Precision@k on Kosarak at M=2000).
Practical rule: for high-skew streams or real-world clickstream data, use MG (highest throughput,
~1.96M updates/sec) or SS (best point-query MAE on heavy items); for low-skew streams
or when point-query accuracy on all buckets is critical, use CMS-CU.

---

## 0. Executive Summary

### 0.1 Primary Research Question

Given the same memory budget, how does **Top-k heavy hitters** identification compare between
**hash-based sketches** (CMS / CMS-CU / Count-Sketch) and **counter-based summaries** (Misra–Gries / Space-Saving),
and how do results change with **stream skew** and across **different real datasets**?

### 0.2 What We Did

We implemented 5 algorithms (CMS, CMS-CU, CS, MG, SS) with a reproducible experiment pipeline.
For each of 6 datasets (4 synthetic: Uniform, Zipf α=1.1, Zipf α=1.3, Mixture; 2 real: Kosarak, Retail)
we characterized skew (F0, F1, F2, skew = F2/F1², rank-frequency log-log plots).
We ran a full 210-run experiment grid over 3 memory budgets (M = 500, 2000, 8000),
3 seeds for synthetic datasets (1 seed for real), measuring Top-k quality,
point-query error by frequency bucket, and performance metrics.

### 0.3 Key Results

- **Result 1:** On Zipf α=1.3 (skew=0.094), MG and SS achieved Precision@k=**1.000** at all three budgets,
  versus CMS-CU (best sketch) at Precision@k=**0.523** at M=500 (Δ=0.477) and **0.947** at M=2000 (Δ=0.053).
  The gap narrows at M=8000 where all algorithms converge to 1.000.

- **Result 2:** CMS-CU improved over plain CMS by an average of **+0.064** Precision@k across all datasets
  and budgets. The improvement was largest on **Kosarak at M=2000** (Δ=**+0.280**, from CMS=0.600 to CMS-CU=0.880),
  and second-largest on **Retail at M=2000** (Δ=**+0.190**, from 0.640 to 0.830). On low-skew streams
  (Uniform, Mixture at M=2000), CMS-CU showed negligible or no improvement.

- **Result 3:** MG throughput (**1.96M updates/sec**) was **15.0×** faster than CMS (130K/s) and **28.4×**
  faster than CMS-CU (69K/s). CMS-CU was **1.9×** slower than CMS, the cost of its conditional update logic.
  For point queries, MG and SS have sub-2ms latency vs 71–82ms for sketch algorithms.

### 0.4 Bottom-Line Recommendation

- **High skew (skew > 0.01) + tight memory** → use **MG**: perfect or near-perfect Precision@k at M=500,
  15× faster than any sketch, with minimal memory overhead.
- **High skew + need low point-query MAE on heavy items** → use **SS**: best MAE on heavy items
  (grand mean 120.2 at M=500 vs MG 590.1), near-perfect Top-k recall.
- **Moderate skew + need accurate point queries across all buckets** → use **CMS-CU**:
  best relative error among sketches, largest CMS improvement on moderately skewed streams.
- **Low skew (uniform-like, skew < 0.001)** → all algorithms struggle equally;
  no algorithm exceeds ~6% Precision@k at M=500; use **CMS** for implementation simplicity.
- **Real datasets with natural skew (Kosarak, Retail)** → MG/SS clearly superior at M≤2000.

### 0.5 Quick Definitions

- **Heavy hitters / Top-k:** the k items with the highest true stream frequencies.
- **Point query:** estimating the frequency value `f(i)` for a specified item i.
- **Skew:** frequency concentration; we use `skew = F2/F1²` (ranges from near-0 for uniform to ~0.1 for Zipf α=1.3) plus a rank-frequency log-log plot.

---

## 1. Introduction & Motivation

### 1.1 Real-World Framing

Modern data systems routinely process streams of hundreds of thousands to millions of events per
second: web clickstreams, network flow logs, retail transaction logs, recommendation system events.
In all these settings there is a common operational need: identify the "hot items" — the top-k
most frequent keys — in real time, with bounded memory, so that capacity planning, fraud detection,
A/B testing, or content ranking can react without waiting for a full batch scan.

### 1.2 Why Exact Counting Is Hard

Maintaining an exact frequency dictionary has three fundamental costs:
1. **Key space (F0):** In our datasets, F0 ranges from 9,547 distinct items (Zipf α=1.3) to 25,343
   (Kosarak). A full dictionary at 1M-item scale is feasible, but at internet scale (billions of
   distinct IP addresses, URLs, or user IDs) it is not.
2. **Stream length (F1):** Our benchmark uses N=1,000,000 items, requiring high update throughput.
   Real systems operate at 10⁸–10⁹ items/sec; latency per update must be sub-microsecond.
3. **One pass:** Streams cannot be rewound. An algorithm must maintain its summary structure
   incrementally, with no random access to historical items.

### 1.3 Research Questions

- **RQ1 (Primary):** Under the same memory budget M, which algorithm family identifies the
  top-k heavy hitters more accurately across varying skew regimes (synthetic) and real datasets?
- **RQ2 (Secondary):** How does point-query accuracy (estimating `f(i)`) compare across families,
  and what are the throughput and latency tradeoffs?

### 1.4 Contributions

1. Head-to-head comparison of two algorithm families (sketches vs summaries) under a fair memory definition.
2. Five-algorithm benchmark including MG and SS, which go beyond typical homework baselines.
3. Controlled synthetic regimes (Uniform / Zipf α=1.1 / Zipf α=1.3 / Mixture) plus two real-world
   datasets (Kosarak, Retail) with different natural skew characteristics.
4. Quantitative decision rules derived directly from the experiment data.

---

## 2. Background

### 2.1 Stream Model & Notation

We use the **insert-only** (cash register) stream model. Each item in the stream is a key
from a vocabulary V. The frequency vector **f** records how many times each key has appeared:
`f(i) = number of occurrences of item i`.

Key quantities:
- **F0** = |{i : f(i) > 0}| — number of distinct items seen
- **F1** = Σ f(i) — total stream length
- **F2** = Σ f(i)² — second frequency moment (sum of squared frequencies)
- **Top-k:** the k items with the highest f(i) values

### 2.2 Skew Metric We Use (and Why)

We define:

```
skew = F2 / F1²
```

This is the normalized second moment. Under a uniform distribution over F0 distinct items,
skew ≈ 1/F0 (near zero). Under a highly concentrated distribution (most mass on a few items),
F2 is large relative to F1², so skew increases. It is a scalar summary of how "peaky" the
frequency distribution is — higher skew means heavier hitters and easier top-k identification.

Complementary visualization: rank-frequency log-log plots. A straight line indicates a power-law
(Zipf-like) distribution; curvature indicates deviation from pure Zipf.

### 2.3 Algorithms

#### Count-Min Sketch (CMS)
**Intuition:** Maintain a 2D array of d×w integer counters. For each incoming item, hash it
with d independent hash functions to d columns (one per row) and increment those counters.
To query `f(i)`, take the minimum of the d corresponding counters. Hash collisions always
push counters up, so CMS systematically overestimates. The error is bounded by ε·F1 with
probability 1-δ where w=⌈e/ε⌉ and d=⌈ln(1/δ)⌉.

**Pseudocode:**
```
init(d, w):
    table[d][w] = 0

update(item):
    for j in 0..d:
        table[j][hash_j(item) mod w] += 1

query(item):
    return min(table[j][hash_j(item) mod w] for j in 0..d)

topk(k):
    return top-k from candidate Counter (updated in parallel)
```

**Parameters:** d=5 (depth/rows), w=⌊M/d⌋ (width/columns). Memory: O(d·w) counters.

#### CMS with Conservative Update (CMS-CU)
**Intuition:** Same structure as CMS, but when updating item i, only increment cells that
currently hold the minimum estimate. This reduces overcounting from unrelated hash collisions,
improving accuracy — but requires reading before writing, halving throughput relative to plain CMS.

**Error behavior:** CMS-CU's estimates are always ≤ CMS estimates (since fewer increments are made),
so it reduces the overestimation bias, especially when heavy items share hash slots.

#### Count-Sketch (CS)
**Intuition:** A signed variant: each counter is incremented by +1 or -1 depending on a second
sign hash `ξ(item) ∈ {-1, +1}`. Query returns the **median** of signed estimates across rows,
not the minimum. The sign randomization makes errors zero-mean, enabling cancellation across
collisions. Estimates can be negative; we clamp to 0.

**Error behavior:** CS estimates are unbiased (zero-mean error), but the median estimator has
higher variance than CMS's minimum estimator, especially in the presence of heavy items.

#### Misra–Gries (MG)
**Intuition:** Maintain at most m key-count pairs. On each new item: (1) if it exists, increment;
(2) if a free slot exists, add with count 1; (3) otherwise, decrement all counts by 1 and remove
all zero-count entries. This guarantees that any item with frequency > N/(m+1) is in the summary.

**Pseudocode:**
```
update(item):
    if item in counters:
        counters[item] += 1
    elif len(counters) < m:
        counters[item] = 1
    else:
        for key in counters:
            counters[key] -= 1
        counters = {k: v for k, v in counters.items() if v > 0}

query(item):
    return float(counters.get(item, 0))  # missing key → 0
```

**Memory:** O(m) key-count pairs. m = M in this experiment. Key overhead scales with key size.

#### Space-Saving (SS)
**Intuition:** Maintain exactly m key-count pairs (no free slots). When a new unseen item arrives
and the structure is full, evict the item with the minimum count and replace it with the new item,
inheriting the minimum count + 1. This never underestimates any frequency — all estimates
overcount by at most the minimum count in the structure.

**Implementation:** lazy min-heap alongside a dict for O(log m) updates.

**Memory:** O(m) key-count pairs. Like MG, memory scales with key object size (string keys make
memory_bytes grow much larger than sketches).

### 2.4 Prior Expectations

Before running experiments, we expected:
- On heavy-tail (Zipf) streams: MG/SS should dominate on Top-k with small m, since their
  counters track true heavies directly.
- On low-skew streams: all algorithms struggle; MG/SS may churn (evicting legitimate candidates);
  sketches suffer hash collisions evenly.
- CS should have higher variance than CMS due to median estimator.
- CMS-CU should improve over CMS when heavy items share hash slots (moderate-to-high skew).

---

## 3. Experimental Setup

### 3.1 Environment & Reproducibility

- **Hardware:** Windows 11, standard laptop CPU
- **Software:** Python 3.10+, NumPy, Pandas, Matplotlib, PyYAML
- **Seeds:** global seed=42; per-run seeds 0,1,2 for synthetic; seed=0 for real datasets
- **How to run:**
  ```bash
  source .venv/bin/activate
  python experiments/smoke_test.py --config configs/main.yaml
  python experiments/run_all.py --config configs/main.yaml
  python experiments/make_plots.py --config configs/main.yaml
  ```

### 3.2 Fairness: Defining "Same Memory Budget"

M is defined uniformly as a **number of counters or entries**:
- **Sketches (CMS, CMS-CU, CS):** M = d × w. With fixed d=5, w=⌊M/d⌋. At M=500: w=100; at M=2000: w=400; at M=8000: w=1600.
- **Summaries (MG, SS):** M = m entries (key-count pairs).

This ensures all algorithms receive the same number of "slots." A secondary comparison by actual
`memory_bytes` is shown in Fig. 5 — sketches use fixed numpy arrays (~1MB at all budgets);
SS uses Python dict entries with string keys and grows to >30MB at M=8000 due to key overhead.

### 3.3 Data

#### 3.3.1 Synthetic Streams

| Name | Generator | Parameters |
|---|---|---|
| Uniform | `numpy.random.integers` | vocab=10,000, N=1,000,000 |
| Zipf α=1.1 | Zipf PMF via `numpy.random.choice` | α=1.1, N=1,000,000 |
| Zipf α=1.3 | Zipf PMF via `numpy.random.choice` | α=1.3, N=1,000,000 |
| Mixture | 50 "heavy" items with 50% total mass, uniform background | k_heavy=50, p_heavy=0.5, N=1,000,000 |

#### 3.3.2 Real Datasets

- **Kosarak:** anonymized clickstream of Hungarian news portal. Parsed by flattening transaction lists to a stream of integer item IDs. Gzip-compressed; auto-detected. Truncated at N_max=1,000,000.
- **Retail:** retail transaction dataset. Same parsing and truncation logic. N=908,576 (no truncation needed).

#### 3.3.3 Dataset Characterization

See §4.0 for the full stats table. Rank-frequency log-log plots are in `plots/skew_loglog_*.png`.

### 3.4 Metrics

**Top-k quality (primary):**
- `Precision@k = |T_true ∩ T_hat| / k` — fraction of predicted top-k that are truly top-k
- `Overlap@k = |T_true ∩ T_hat| / k` — identical formula; both = precision when |T_hat|=k, which is always the case here (noted in §5.3)

**Point-query accuracy (secondary):**
- Query set Q is built from the true frequency distribution: 100 heavy items (top-100), 100 mid items (around rank 500), 100 rare items (random from bottom 20%).
- `MAE = mean |f(i) - f_hat(i)|` per bucket
- `Relative error = mean |f(i) - f_hat(i)| / f(i)` per bucket
- Missing key policy: MG and SS return f_hat=0 for items not in their summary.

**Performance:**
- `updates_per_sec`: measured via `measure_throughput()`, iterating the full stream once
- `query_ms`: mean time for a single query over Q (milliseconds)

### 3.5 Experiment Matrix

| Factor | Values | Count |
|---|---|---|
| Datasets (synthetic) | uniform, zipf_1_1, zipf_1_3, mixture | 4 |
| Datasets (real) | kosarak, retail | 2 |
| Algorithms | CMS, CMS-CU, CS, MG, SS | 5 |
| Memory budgets M | 500, 2000, 8000 | 3 |
| Seeds (synthetic) | 0, 1, 2 | 3 |
| Seeds (real) | 0 | 1 |
| **Total rows** | | **210** |

Sketch width: w = ⌊M/d⌋ with d=5. At M=500: w=100; M=2000: w=400; M=8000: w=1600.
k=100 for all runs. One row per run appended to `results/results_full.csv`.

---

## 4. Results

### 4.0 Dataset Stats Table

| Dataset | N | F0 | F1 | F2 | Skew | Description |
|---|---|---|---|---|---|---|
| uniform | 1,000,000 | 10,000 | 1,000,000 | 100,987,506 | 0.000101 | Each key equally likely; no heavy hitters |
| zipf_1_1 | 1,000,000 | 9,997 | 1,000,000 | 34,016,622,264 | 0.034017 | Moderate power-law; top items significantly more frequent |
| zipf_1_3 | 1,000,000 | 9,547 | 1,000,000 | 94,042,924,048 | 0.094043 | Strong power-law; top items dominate the stream |
| mixture | 1,000,000 | 10,000 | 1,000,000 | 5,015,827,892 | 0.005016 | 50 engineered heavy items (50% total mass) + uniform background |
| kosarak | 1,000,000 | 25,343 | 1,000,000 | 12,806,120,190 | 0.012806 | Real clickstream; natural moderate skew |
| retail | 908,576 | 16,470 | 908,576 | 5,364,936,090 | 0.006499 | Real retail transactions; mild skew |

Skew ordering (ascending): uniform (0.0001) < retail (0.0065) < mixture (0.0050) < kosarak (0.0128) < zipf_1_1 (0.034) < zipf_1_3 (0.094).

Note: mixture and retail have similar skew values (~0.005–0.007), but mixture has engineered
heavy items while retail has natural distribution, leading to different algorithm behavior.

### 4.1 Figure Descriptions

**Fig. 1 — Precision@k vs Memory Budget** (`plots/fig_1_precision.png`)

Six panels (one per dataset) show mean Precision@k (y-axis, [0,1]) vs M on a log scale (x-axis).
Error bars show std across seeds for synthetic datasets.

*Takeaway:* The separation between MG/SS and sketches is stark at low budgets.
On Zipf α=1.3, MG/SS remain at 1.000 across all M values, while CMS-CU rises from 0.523 (M=500)
to 1.000 (M=8000). On Uniform, no algorithm exceeds 5% at M=500, and even at M=8000 only MG
and SS break 35%, highlighting that precision is fundamentally limited by skew, not just budget.

**Fig. 2 — Overlap@k vs Memory Budget** (`plots/fig_2_overlap.png`)

Structurally identical to Fig. 1 (overlap@k = precision@k when |T̂|=k, which is always the case
here). Generated as a separate figure per template requirements. See note in figure caption.

**Fig. 3 — Point Query MAE by Frequency Bucket** (`plots/fig_3_mae.png`)

Three panels: heavy (top-100), mid (~rank 500), rare (bottom 20%) items. y-axis is log-scale MAE,
averaged across all datasets and seeds. x-axis is M on log scale.

*Takeaway:* SS achieves the lowest heavy-item MAE at M=8000 (mean=1.0), followed closely by MG (44.8).
CMS has catastrophically high MAE at small M (heavy: 5,059 at M=500) due to collision-driven
overestimation. CS is surprisingly competitive on rare items (MAE=40.1 at M=8000) despite weaker
Top-k quality, because its zero-mean estimator avoids the systematic bias of CMS.

**Fig. 4 — Throughput vs Memory Budget** (`plots/fig_4_throughput.png`)

Six panels showing updates/sec (log scale) vs M (log scale). MG consistently reaches 1.2M–2.6M
updates/sec across all datasets; sketches plateau around 65K–150K/s. SS is intermediate at
~450K–1M/s depending on the dataset (faster on Zipf, slower on Kosarak due to larger key object size).

*Takeaway:* MG throughput is **15× CMS** and **28× CMS-CU** on average. The throughput gap grows
slightly with budget (more counters to hash for sketches). CS is slower than expected (~80K/s)
due to per-update Counter management for candidate tracking.

**Fig. 5 — Actual Memory Usage vs Budget M** (`plots/fig_5_memory_bytes.png`)

A single panel showing mean memory_bytes vs M for each algorithm.

*Takeaway:* Sketches (CMS, CMS-CU, CS) use ~1.03–1.09 MB regardless of M (fixed numpy array
plus a small Counter for candidates). MG scales linearly from 47K to 1.01MB bytes (key-count pairs).
SS grows from ~27MB to ~42MB — the large footprint comes from Python string objects stored per key.
In terms of raw bytes, SS is the most memory-intensive algorithm despite only holding M key-count entries.

### 4.2 Main Result

**MG and SS dominate on skewed streams.** Across all non-uniform datasets, MG and SS achieve
Precision@k equal to or greater than any sketch at every budget:

| Dataset | Skew | MG@500 | SS@500 | Best sketch@500 |
|---|---|---|---|---|
| uniform | 0.0001 | 0.013 | 0.013 | 0.030 (CMS-CU) |
| retail | 0.0065 | 0.560 | 0.560 | 0.270 (CMS-CU) |
| mixture | 0.0050 | 0.507 | 0.510 | 0.440 (CMS-CU) |
| kosarak | 0.0128 | 0.780 | 0.790 | 0.350 (CMS-CU) |
| zipf_1_1 | 0.034 | 0.997 | 0.997 | 0.510 (CMS-CU) |
| zipf_1_3 | 0.094 | 1.000 | 1.000 | 0.523 (CMS-CU) |

**The skew threshold effect.** Sketches become competitive with MG/SS only at M=8000 on the
most skewed datasets. On Zipf α=1.3: CMS reaches 1.000 at M=8000, matching MG/SS — but only
because the budget is large enough that collisions become negligible. The critical observation
is that MG/SS are already perfect at M=500 on this dataset, while CMS needs 16× more memory.

**Budget sensitivity.** All algorithms benefit from larger M, but the gains are asymmetric:
sketches show steep improvement (CMS: +0.394, CS: +0.458 from M=500 to M=8000), while MG/SS
show more modest gains (+0.181 and +0.179), because they already perform well at M=500 on
any dataset with meaningful skew. The implication: for a given quality target, MG/SS reach it
at much smaller M.

### 4.3 Sensitivity / Ablations

**Skew effect.** Precision@k increases monotonically with skew across all algorithms and budgets,
but the rate differs. For MG at M=500: 0.013 (uniform) → 0.507 (mixture) → 0.780 (kosarak) →
0.997 (zipf_1_1) → 1.000 (zipf_1_3). For CMS-CU at M=500: 0.030 → 0.440 → 0.350 → 0.510 → 0.523.
Note that CMS-CU's trajectory is non-monotonic (kosarak has lower CMS-CU precision at M=500 than
mixture), reflecting that kosarak's larger F0 (25,343 vs 10,000) causes more hash collisions.

**CU effect.** CMS-CU improves over CMS on moderately and highly skewed datasets:
- Kosarak M=2000: +0.280 (most dramatic improvement)
- Retail M=2000: +0.190
- Zipf α=1.1 M=500: +0.130
- Zipf α=1.3 M=500: +0.120
- Kosarak M=500: +0.100

On Uniform and Mixture at M=2000, CMS-CU shows ≤0 improvement — conservative updates do
not help when there are no heavy items generating beneficial counter-reservation.
CMS-CU costs 1.9× the per-update time of CMS; this cost is worthwhile only on skewed streams.

**Budget effect.** From M=500 to M=8000 (16× more memory), mean Precision@k improvement:
CMS: +0.394, CS: +0.458, CMS-CU: +0.321, MG: +0.181, SS: +0.179. Sketches gain more from
budget scaling because their error is inversely proportional to w (the sketch width), while
MG/SS degrade gracefully even at M=500 on skewed data.

### 4.4 Decision Rules

The following rules are derived directly from the data:

1. **If skew > 0.01, use MG:** MG achieves Precision@k ≥ 0.780 at M=500 on all datasets with
   skew > 0.01 (kosarak: 0.780, zipf_1_1: 0.997, zipf_1_3: 1.000). No sketch exceeds 0.523 at M=500.

2. **If heavy-item point-query accuracy matters, use SS:** SS achieves the lowest heavy-item MAE
   (grand mean: 120.2 at M=500, 51.7 at M=2000, **1.0 at M=8000**) due to its overcount-bounding
   guarantee. MG is second-best for heavy MAE (590.1 at M=500, improving to 44.8 at M=8000).

3. **CMS-CU is the best sketch when skew > 0.01 and M is moderate:** At M=2000 on kosarak, CMS-CU
   improves over CMS by 28 percentage points. The cost is ~2× slower updates (69K vs 130K/s).
   Do not use CMS-CU on low-skew data — the overhead is not justified.

4. **On uniform or near-uniform streams, no algorithm is reliable at M=500 or M=2000:**
   Maximum Precision@k at M=2000 is 0.088 (MG). Even at M=8000, MG reaches only 35.7%.
   In this regime, default to CMS (simplest implementation, 130K/s throughput).

5. **For maximum throughput, use MG:** 1.96M updates/sec vs 692K (SS), 130K (CMS), 69K (CMS-CU).
   MG is the only algorithm that combines near-perfect Top-k quality on skewed data with
   extremely high update throughput. The tradeoff is pure Top-k (no unbiased point-query guarantee).

---

## 5. Discussion

### 5.1 Expectations vs Surprises

**Confirmed expectations:**

- MG and SS dominate Zipf streams — confirmed strongly and at all budgets. On Zipf α=1.3 at M=500,
  both achieve perfect Precision@k, while sketches are stuck at ≤52%. The theoretical guarantee
  (MG identifies all items with frequency > N/(m+1)) translates cleanly to practice.

- Higher skew → better precision for all algorithms — confirmed monotonically. The rank-frequency
  plots and skew values predict the difficulty ordering exactly: uniform is hardest, Zipf α=1.3 is easiest.

- Higher M → better precision — confirmed for all algorithms. The improvement rate is steeper
  for sketches (error ∝ 1/w) than for summaries (already good at small M on skewed data).

**Surprises:**

1. **The mixture dataset:** Despite being engineered with 50 heavy items collectively holding 50%
   of total stream mass, MG and SS achieved only ~51% Precision@k at M=500 and ~78–78% at M=8000
   — substantially below Kosarak (78% and 100% at the same budgets), which has lower or similar skew
   (mixture: 0.005, kosarak: 0.013). Intuitively, the mixture dataset has a hard boundary: its 50 heavy
   items are all close in frequency (~1% each), making them difficult to reliably distinguish from
   the uniform background (which has ~0.01% per item each). In contrast, Kosarak's natural heavy-tail
   distribution creates a sharper separation between the true top-100 and the rest, even though
   its aggregate skew value is moderate. This reveals a limitation of using F2/F1² as the sole
   predictor of difficulty: skew captures total concentration but not the sharpness of the
   heavy/background boundary.

2. **MG throughput gap:** MG is **15× faster than CMS** and **28× faster than CMS-CU**. We
   expected MG to be faster (no hashing, simple dict operations), but this magnitude surprised us.
   The likely explanation is cache locality: MG's dictionary of ≤M key-count pairs fits in L2/L3
   cache at M=500 (47KB) and M=2000 (182KB), while CMS's 2D numpy array of d×w counters requires
   sequential hash-indexed accesses across a potentially cache-cold 1MB+ array. This effect
   dominates even though numpy operations are individually faster than Python dict lookups.

3. **Uniform precision at M=8000 — MG reaches only 35.7%:** The theoretical guarantee for MG
   (all items with frequency > N/(m+1)) at M=8000 is items with frequency > 1,000,000/8001 ≈ 125.
   Under uniform distribution over 10,000 items, each item has expected frequency ~100, which is
   below this threshold. MG therefore sees constant churn in its counter table, and its top-k
   list becomes essentially random. This confirms that MG's guarantee is tightly coupled to
   the stream being skewed.

### 5.2 Failure Modes

- **All algorithms fail on uniform streams:** This is expected — there are no genuine heavy
  hitters to detect. Even with perfect precision the "top-k" labels would change across random seeds.
  Precision is fundamentally limited by the signal (skew), not the algorithm quality.

- **Count-Sketch: highest variance, weakest Top-k quality:** CS is consistently the weakest
  sketch across all datasets. Despite CS's theoretical advantage (unbiased estimator, handles
  negative frequency updates), in practice the median estimator has higher variance than CMS's
  minimum estimator, particularly for moderate-frequency items that partially collide with heavy
  items. CS is never the winner in our experiment and is only marginally competitive with CMS at M=8000.

- **MG/SS point-query errors on rare items:** The missing-key policy (f_hat=0) inflates
  relative error for items not in the MG/SS summary. MG's grand-mean relative error on rare
  items is 0.974 (97.4%), nearly as bad as plain guessing. This is not a bug — it reflects
  that rare items are frequently evicted from the summary, and returning 0 is the only
  conservative estimate available. Users who need reliable rare-item frequency estimates
  should use a sketch (CS relative error on rare items: 43.5%).

- **CMS catastrophic overestimation at M=500:** CMS MAE on heavy items at M=500 is 5,059 —
  larger than typical heavy-item true frequencies. With w=100 counters per row and F0=10,000
  items, each counter is shared by ~100 items on average, causing enormous collision-driven
  overcounting. This reinforces why CMS-CU's conservative update is so valuable at small budgets.

### 5.3 Threats to Validity

- **Single machine benchmark:** throughput results are hardware-specific. The 15× MG vs CMS
  advantage will vary on different cache architectures or with JIT-compiled implementations.

- **Synthetic Zipf uses precomputed PMF:** numpy's choice with a power-law PMF approximates
  an idealized Zipf distribution. Real-world power-law streams may have deviations (truncated
  distributions, non-stationary heavy items) not captured here.

- **overlap@k ≡ precision@k in this experiment:** Both metrics reduce to |T_true ∩ T_hat|/k
  when |T_hat|=k (guaranteed by our `topk(k)` interface). The two metrics are not independently
  informative in this setup. We include both per the template requirement and note this explicitly.

- **Real datasets use 1 seed:** We have no variance estimate for Kosarak or Retail. The
  precision values reported are from a single run (seed=0) and may not represent the expected
  value across stream orderings.

- **MG/SS missing key policy:** the choice f_hat=0 maximally penalizes relative error for rare
  items. An alternative policy (f_hat = min_counter in the summary) would reduce relative error
  but violate the "no overestimate" property expected by some use cases.

- **memory_bytes is approximate:** our implementation measures numpy array `.nbytes` plus
  Python `sys.getsizeof` over counters, but does not account for Python object headers or
  memory allocator overhead. SS memory footprints (>30MB) are dominated by Python string objects
  and are genuinely larger than sketch memory, but the exact values are platform-dependent.

---

## 6. Conclusions & Future Work

### 6.1 Conclusions

This study provides a comprehensive head-to-head comparison of two algorithm families for
top-k heavy hitter identification in data streams under a fair memory budget definition.

The key finding is unambiguous: **counter-based summaries (MG, SS) substantially outperform
hash-based sketches (CMS, CMS-CU, CS) for Top-k identification on skewed streams**, achieving
Precision@k = 1.000 at M=500 on Zipf α=1.3 and ≥0.78 on Kosarak, while the best sketch
(CMS-CU) requires M=8000 to match this on Zipf α=1.3, and still falls short on Kosarak.

Additionally, **MG delivers this quality at 15× the throughput of CMS and 28× the throughput
of CMS-CU**, making it the Pareto-dominant choice on skewed streams — both faster and more accurate.

The mixture dataset result reveals an important nuance: **skew (F2/F1²) alone does not fully
predict Top-k difficulty**. The sharpness of the boundary between heavy items and background
matters, and this is not captured by a single scalar metric.

For practitioners: the decision between algorithm families should be driven primarily by stream
skew. On any dataset with skew > 0.01, MG or SS is the correct choice. On low-skew streams,
the choice of algorithm is secondary — the signal is simply too weak for any algorithm to reliably
identify the top-k.

### 6.2 Future Work

- **Non-stationary streams:** all experiments use static distributions. Real streams exhibit
  concept drift (heavy items change over time); sliding-window or decay-based variants of MG/SS
  would be needed.
- **Parallelism:** sketches are more naturally parallelizable (counter arrays can be sharded);
  MG/SS require coordination. Benchmarking in a multi-core or distributed setting would
  change the throughput comparison.
- **Alternative skew metrics:** the mixture surprise suggests that F2/F1² is insufficient.
  Exploring metrics that capture the "gap" between rank-k and rank-(k+1) frequencies would
  improve per-dataset difficulty prediction.
- **Adaptive algorithms:** hybrid approaches that switch between sketch and summary modes
  based on observed skew could capture the best of both families.

---

## Appendix A — How to Run

```bash
# 1. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate          # Linux/macOS
.venv\Scripts\Activate.ps1         # Windows PowerShell

# 2. Install dependencies
pip install -r requirements.txt

# 3. Place raw data files in data/raw/
#    kosarak.dat, retail.dat (gzip-compressed)

# 4. Run smoke test (15 runs, ~30s)
python experiments/smoke_test.py --config configs/main.yaml

# 5. Run full experiment grid (210 runs)
python experiments/run_all.py --config configs/main.yaml

# 6. Generate plots
python experiments/make_plots.py --config configs/main.yaml

# 7. Run tests
pytest tests/
```

All parameters are in `configs/main.yaml`. No hardcoded values in source code.

---

## Appendix B — Full Parameter Table

| Parameter | Value | Location |
|---|---|---|
| k (Top-k) | 100 | configs/main.yaml |
| M_small | 500 | configs/main.yaml |
| M_med | 2000 | configs/main.yaml |
| M_large | 8000 | configs/main.yaml |
| Sketch depth d | 5 | configs/main.yaml |
| Sketch width w | ⌊M/d⌋ | computed at runtime |
| Summary size m | M entries | computed at runtime |
| N_max | 1,000,000 | configs/main.yaml |
| Global seed | 42 | configs/main.yaml |
| Synthetic seeds | [0, 1, 2] | configs/main.yaml |
| Real seeds | [0] | configs/main.yaml |
| Zipf α (1) | 1.1 | configs/main.yaml |
| Zipf α (2) | 1.3 | configs/main.yaml |
| Mixture k_heavy | 50 | configs/main.yaml |
| Mixture p_heavy | 0.5 | configs/main.yaml |
| Uniform vocab_size | 10,000 | configs/main.yaml |
| MG/SS missing key | f_hat = 0 | configs/main.yaml |
| Skew metric | F2 / F1² | configs/main.yaml |