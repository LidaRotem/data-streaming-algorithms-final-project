# Final Project — Real-Time Data Stream Algorithms (README)
Course: **Algorithms for Real-Time Data Stream Analysis**  
(אלגוריתמים לניתוח זרם נתונים בזמן אמת)

This README is written so that **another agent** can pick up the project and execute it end-to-end (code + experiments + report) using the **report skeleton** and the **task plan**.

---

## 0) One-liner
We compare **hash-based frequency sketches** vs **counter-based heavy-hitter summaries** under the **same memory budget**, across **different skew regimes** (synthetic + real datasets), focusing primarily on **Top-k heavy hitters** quality.

---

## 1) Research Question (Primary)
**Given the same memory budget, how does Top-k heavy hitters identification compare between:**
- **Hash-based frequency sketches:** Count-Min (CMS), Count-Min + Conservative Update (CMS-CU), Count-Sketch (CS)
and
- **Counter-based heavy-hitter summaries:** Misra–Gries (MG), Space-Saving (SS)

**and how do results change with stream skew and across different real datasets?**

### Secondary objectives
- Point queries: accuracy of estimating `f(i)` for a fixed query set (heavy/mid/rare buckets).
- Performance: `updates/sec`, `query latency`.

---

## 2) Deliverables
1. **Hebrew report** (Markdown, then export to PDF if required):  
   `report/Project_Report_Template_HE_v3.md`
2. **English report draft** (optional but recommended for collaboration):  
   `report/Report_Template_EN.md`
3. **Code** (Python project) + reproducible experiment runner.
4. **Results file**: `results/results.csv` with all metrics for all runs.
5. **Plots**: `plots/fig_*.png` + summary tables (winners, dataset stats).
6. **"How to run" appendix** inside the report.

---

## 3) Algorithms (must include all)
### Hash-based sketches
- CMS — Count-Min Sketch  
- CMS-CU — Count-Min with Conservative Update  
- CS — Count-Sketch

### Counter-based summaries
- MG — Misra–Gries  
- SS — Space-Saving

### Baseline (ground truth)
Exact counting with a hashmap/dict to compute:
- true `Top-k`
- true `f(i)`
- `F0, F1, F2`

---

## 4) Data
### 4.1 Synthetic streams (3 regimes)
1. **Uniform**
2. **Zipf / heavy-tail** (choose `alpha` = 1 or two values like 1.1 and 1.3)
3. **Mixture** (few heavy hitters + many singletons; controlled by `k_heavy` and `p_heavy`)

### 4.2 Real datasets (at least two)
Recommended:
- **Kosarak**
- **Retail**
If unavailable, replace with two transaction/clickstream-like datasets and update the report accordingly.

### 4.3 Skew characterization (required for every dataset)
Compute and report:
- `F0, F1, F2`
- `skew = F2 / (F1^2)`
- rank–frequency plot (log-log)

Output:
- `results/dataset_stats.csv`
- `plots/skew_<dataset>.png`

---

## 5) Fairness: “same memory budget”
Define a budget `M` in units of **#counters / entries**:

- **Sketches:** `M = d * w` table cells  
  Default: `d = 5`, `w = floor(M / d)`
- **Summaries:** `M = m` entries (`(key, count)`)

⚠️ Validity note: MG/SS store keys, adding overhead not reflected in “#entries”. Mention this in *Threats to validity*.  
(Optional) If time allows: also compare by approximate bytes.

---

## 6) Metrics
### 6.1 Primary — Top-k quality
- `precision@k = |T_true ∩ T_hat| / k`
- `overlap@k = |T_true ∩ T_hat|`

### 6.2 Secondary — Point queries (`f(i)`)
Query set `Q` split into buckets:
- heavy (from true Top-k)
- mid
- rare (including singletons)

Compute:
- `MAE = avg(|f_hat(i) - f(i)|)`
- `relative error = |f_hat - f| / max(1, f)`

**Policy for MG/SS:** if item not in summary → define `f_hat = 0` (or “unknown”). Pick one and stay consistent, then discuss implications.

### 6.3 Performance
- update throughput: `updates/sec`
- query latency: `query_ms` (avg over Q)

---

## 7) Experiment Grid (must be explicit)
Run over:
- datasets: 3 synthetic + 2 real = 5
- algorithms: 5
- memory budgets: 3 (`small/med/large`)
- seeds: synthetic 3 seeds; real 1 seed (or 2 if time)

### Expected number of rows in results
- Synthetic: `3 datasets * 3 budgets * 5 algos * 3 seeds = 135`
- Real: `2 datasets * 3 budgets * 5 algos * 1 seed = 30`
- **Total expected:** `165` rows in `results/results.csv`

Use this as a sanity check.

---

## 8) Figure Plan (required plots)
1. **Fig1:** `precision@k` vs `M` (at least Zipf + both real datasets)
2. **Fig2:** `overlap@k` vs `M`
3. **Fig3:** point-query `MAE` by bucket (heavy/mid/rare) vs `M`
4. **Fig4:** `updates/sec` vs `M` (optionally also `query_ms`)
5. **Fig5 (optional):** CMS vs CMS-CU under heavy-tail (to isolate CU effect)

Also include:
- table: dataset stats (`F0,F1,F2,skew`)
- table: winners (“which algorithm wins where”) by dataset × budget

---

## 9) Recommended repo structure
```text
project/
  README.md
  requirements.txt
  configs/
    main.yaml
  src/
    algorithms/
      cms.py
      cms_cu.py
      count_sketch.py
      misra_gries.py
      space_saving.py
      ground_truth.py
    data/
      synthetic.py
      parsers.py
      datasets.py
    metrics/
      topk.py
      point_queries.py
      skew.py
    utils/
      hashing.py
      timing.py
      io.py
  experiments/
    run_all.py
    make_plots.py
    smoke_test.py
  data/
    raw/
    processed/
  results/
    results.csv
    dataset_stats.csv
  plots/
    fig_1_precision.png
    ...
  report/
    Project_Report_Template_HE_v3.md
    Project_Step_by_Step_Plan_HE_v3.md
    Report_Template_EN.md
    Task_Plan_EN.md
```
---

## 10) Execution Workflow (for another agent)

### Stage 0 — Lock decisions (before coding)
- choose `k` (recommended 100)
- choose `M_small/M_med/M_large`
- set `d=5`
- choose real datasets + `N_max` (if truncation needed)
- choose MG/SS point-query policy (0 vs unknown)
- put everything into `configs/main.yaml`

**DoD:** one config file fully defines all experiments.

### Stage 1 — Project infrastructure & reproducibility
- implement `experiments/run_all.py --config ...`
- ensure it writes `results/results.csv` with consistent columns
- add seed handling and metadata logging

**DoD:** a small smoke run produces a valid `results.csv`.

### Stage 2 — Implement algorithms + correctness tests
- unify API: `update(item)`, `query(item)`, `topk(k)` (or helper)
- create unit tests on a small stream with ground truth
- confirm outputs are reasonable and reproducible under same seed

**DoD:** all 5 algorithms run without errors; tests pass.

### Stage 3 — Data processing + skew characterization
- generate 3 synthetic streams (uniform/zipf/mixture)
- parse 2 real datasets into `data/processed/*.txt` stream format
- compute dataset stats and rank-frequency plots

**DoD:** `dataset_stats.csv` exists + `plots/skew_*.png` exist.

### Stage 4 — Full experiment grid
- run all datasets × budgets × algorithms × seeds
- verify `results.csv` row count ≈ 165
- produce a winners pivot table

**DoD:** complete `results.csv` + winners table.

### Stage 5 — Plot generation
- implement `experiments/make_plots.py`
- generate required figures (Fig1–Fig4) + tables for report

**DoD:** all plots saved and ready for report inclusion.

### Stage 6 — Report writing (high resolution)
Write in:
- `report/Report_Template_EN.md` (English drafting), then
- translate to Hebrew in `report/Project_Report_Template_HE_v3.md` if required.

Every claim in Results must reference a figure/table.

**DoD:** full report with fairness, skew characterization, threats to validity, decision rules, and how-to-run appendix.

---

## 11) Threats to validity (must include in report)
- memory fairness: MG/SS key overhead not captured by “#entries”
- hash independence assumptions not fully met in practice
- dataset truncation (`N_max`) may affect Top-k
- performance depends on implementation (Python, dict/heap) and machine

---

## 12) Definition of Done (project completion)
- `results/results.csv` complete (≈165 rows)
- `results/dataset_stats.csv` + `plots/skew_*.png`
- `plots/fig_1..fig_4` (and optional fig_5)
- report fully filled and consistent with figures/tables
- another agent can run:
  - `run_all.py` → results
  - `make_plots.py` → plots
  - and reproduce the report claims
