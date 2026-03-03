# Task Plan (EN) — Step-by-step execution guide
Course: **Algorithms for Real-Time Data Stream Analysis**

This file is a high-resolution checklist so another agent can execute the project end-to-end.
Each stage includes:
- Tasks
- Outputs
- Definition of Done (DoD)

---

## 🗂️ Project Status (PM Tracker)

| Stage | Status | Notes |
|---|---|---|
| 0 — Lock decisions | ✅ DONE | All decisions locked (see below) |
| 1 — Repo skeleton | ✅ DONE | Clean smoke test, 15 rows in results.csv |
| 2 — Algorithms + tests | 🔄 IN PROGRESS | See Coding_Agent_Briefing_Stage2.md — amended with professor feedback |
| 3 — Data + skew | ⬜ Not started | |
| 4 — Full experiment grid | ⬜ Not started | |
| 5 — Plot generation | ⬜ Not started | |
| 6 — Report (polish + translate) | ⬜ Not started | Writing begins in Stage 3 — see schedule below |
| 7 — Submission packaging | ⬜ Not started | |

> ⚠️ **Professor feedback incorporated [2026-03-02]:** recall@k added, point-query bucket reporting hardened, memory_bytes now required, histogram added to skew plots. See NOTES.md for full detail.

---

## 📋 Report Writing Schedule (integrated across stages)

> **Principle: write from data, not from plans. Never leave report writing to Stage 6.**

| When | What to write | Report sections |
|---|---|---|
| Stage 1–2 | Nothing yet. Focus on code correctness. | — |
| Stage 3 | Stream model + notation + skew metric definition. Dataset characterization with real F0/F1/F2/skew numbers and plots. | §2.1, §2.2, §3.3 |
| Stage 4 | Experimental setup (fairness, metrics, experiment matrix). Dataset stats table. Begin Results structure. | §3 (full), §4.0 |
| Stage 5 | Results narrative (one paragraph per figure). Discussion. Abstract + Executive Summary with real numbers. | §4.1–4.4, §5, §0, Abstract |
| Stage 6 | Polish, fill remaining sections (Intro, Background algos, Conclusions, Appendices), translate to Hebrew. | §1, §2.3–2.4, §6, Appendices |

---

## Stage 0 — Lock decisions ✅ DONE

### Locked decisions

| Parameter | Value |
|---|---|
| Stream model | insert-only |
| k (Top-k) | 100 |
| M_small / M_med / M_large | 500 / 2000 / 8000 counters |
| Sketch depth d | 5 |
| Sketch width w | floor(M / d) |
| Summary size m | M entries |
| Real datasets | Kosarak + Retail (download required) |
| N_max (truncation) | 1,000,000 |
| Skew metric | F2 / F1² + rank-frequency log-log plot + frequency histogram |
| MG/SS missing key policy | f_hat = 0 (treat as unseen) |
| Seeds (synthetic / real) | 3 / 1 |

### Outputs
- `configs/main.yaml` containing all above choices. ✅ (values locked, file to be written in Stage 1)

### DoD
- One config fully defines all experiments (no hardcoded params elsewhere). ✅

---

## Stage 1 — Repo skeleton & reproducibility
### Tasks
1. Write `configs/main.yaml` from locked Stage 0 decisions.
2. Create folders: `src/`, `experiments/`, `configs/`, `data/raw`, `data/processed`, `results/`, `plots/`, `report/`.
3. Create environment file: `requirements.txt` (or conda/poetry).
4. Implement results logger to append 1 row per run into `results/results.csv`.
5. Implement seeding: global seed + per-run seed, store seed in results.
6. Implement `experiments/smoke_test.py` to run a tiny grid.

### Outputs
- `configs/main.yaml`
- Working repository structure.
- `results/results.csv` created by smoke test.

### DoD
- `python experiments/smoke_test.py --config configs/main.yaml` runs and produces a valid CSV.

---

## Stage 2 — Implement algorithms + correctness tests
### Tasks
1. Implement common API:
   - `update(item)`
   - `query(item)`
   - `topk(k)` (or helper extracting candidates)
   - `reset()`
2. Implement algorithms:
   - CMS, CMS-CU, CS, MG, SS
3. Implement ground truth:
   - exact dict counts
   - `true_topk(k)`
4. Unit tests on a tiny stream:
   - no crashes, deterministic with fixed seed
   - `topk` overlap is reasonable under large enough M (soft threshold)

### Outputs
- `src/algorithms/*.py`
- `tests/` (or a minimal test runner script)

### DoD
- All 5 algorithms run on a small stream and produce sensible outputs.

---

## Stage 3 — Data processing + skew characterization
### Tasks (Synthetic)
1. Implement generators: Uniform, Zipf(alpha=1.1 and 1.3), Mixture(k_heavy, p_heavy).
2. Produce synthetic streams into `data/processed/`.
3. Compute `F0,F1,F2,skew` and save to `results/dataset_stats.csv`.
4. Create **both** a frequency histogram (`plots/skew_hist_<dataset>.png`) and a rank-frequency log-log plot (`plots/skew_loglog_<dataset>.png`) for every dataset. *(Professor requirement — both are mandatory.)*

### Tasks (Real)
1. Download Kosarak & Retail into `data/raw/` and document the source in README.
2. Write parsers to output a unified item stream format in `data/processed/`.
3. Apply truncation `N_max = 1,000,000` consistently.
4. Compute stats + both skew plots for each real dataset.

### Outputs
- `data/processed/{uniform,zipf,mixture,kosarak,retail}.txt` (or similar)
- `results/dataset_stats.csv`
- `plots/skew_hist_<dataset>.png` — frequency histogram per dataset
- `plots/skew_loglog_<dataset>.png` — rank-frequency log-log plot per dataset

### DoD
- All datasets parse/generate successfully, with stats and plots produced.

### 📝 Report writing triggered at this stage
- Write §2.1 (stream model + notation) and §2.2 (skew metric + why we use it).
- Fill in the dataset characterization subsection §3.3 with real F0/F1/F2/skew values and embed plots.
- Do NOT write Results yet — wait for Stage 4.

---

## Stage 4 — Full experiment grid
### Tasks
1. Generate the full grid: datasets × budgets × algos × seeds.
2. Run all experiments via `experiments/run_all.py --config configs/main.yaml`.
3. Verify row count in `results.csv`:
   - Synthetic: 3 datasets × 3 budgets × 5 algos × 3 seeds = 135
   - Real: 2 datasets × 3 budgets × 5 algos × 1 seed = 30
   - **Expected total: 165 rows**
4. Produce a winners table (pivot): best Precision@k AND Recall@k per dataset×budget. *(Both metrics required per professor feedback.)*
5. Verify `memory_bytes` column is populated correctly for all algorithms — sketches include Counter overhead, MG/SS include key storage.

### Outputs
- `results/results.csv` (165 rows)
- `results/winners.csv` (or winners table in markdown)

### DoD
- Full grid completed with no missing combinations; winners table exists.

### 📝 Report writing triggered at this stage
- Write §3 (full experimental setup): fairness definition, metrics, experiment matrix table.
- Write §4.0 (dataset stats table — now you have all numbers).
- Sketch the Results structure (one placeholder paragraph per figure).

---

## Stage 5 — Plot generation (Figure Plan)
### Tasks
1. Implement `experiments/make_plots.py` reading `results/results.csv`.
2. Generate required figures:
   - Fig1: precision@k AND recall@k vs M *(both required — professor feedback)*
   - Fig2: overlap@k vs M
   - Fig3: MAE by bucket (heavy/mid/rare) vs M — **separate lines per bucket, no aggregation** *(professor requirement)*
   - Fig3b: relative error by bucket vs M — separate lines per bucket
   - Fig4: updates/sec vs M
   - Fig5: actual memory_bytes vs M across all algorithms — **required** *(professor requirement — memory fairness)*
   - Fig6 (optional): CMS vs CMS-CU under heavy-tail to isolate CU effect
3. Generate tables for report:
   - dataset stats table (from dataset_stats.csv)
   - winners table

### Outputs
- `plots/fig_*.png`
- `results/winners.csv`

### DoD
- All required figures exist and are ready to paste into the report.

### 📝 Report writing triggered at this stage
- Write §4.1–4.4 (Results): one paragraph per figure, grounded in actual numbers.
- Write §5 (Discussion): surprises, failure modes, threats to validity.
- Write §0 (Executive Summary) and Abstract — now with 3 real numeric results.
- Decision rules §4.4: 2–5 concrete selection rules derived from plots.

---

## Stage 6 — Report writing (polish + translate)
> At this stage the report should already be ~70% written. This stage is for polish, gap-filling, and Hebrew translation only.

### Tasks
1. Fill remaining sections not yet written:
   - §1 (Introduction & Motivation)
   - §2.3–2.4 (Algorithm descriptions in standard mini-structure + expectations)
   - §6 (Conclusions + Future work)
   - Appendix A (How to run) + Appendix B (Full parameter table)
2. Polish all sections: check every claim references a figure or table.
3. Verify fairness, skew characterization, and threats to validity are explicitly addressed.
4. Translate completed English draft to Hebrew: `report/Project_Report_Template_HE_v3.md`.
5. Export to PDF if required.

### Chapter checklist
- **Abstract + Exec summary:** includes 3 numeric results + one rule-of-thumb. *(written in Stage 5)*
- **Intro:** setting + why exact is hard + primary/secondary RQs. *(write now)*
- **Background:** definitions + each algo in same mini-structure + expectations. *(write now)*
- **Experimental setup:** fairness + data + metrics + experiment matrix table. *(written in Stage 4)*
- **Results:** dataset stats table first, then figures, then decision rules. *(written in Stage 5)*
- **Discussion:** surprises, failure modes, threats to validity. *(written in Stage 5)*
- **Conclusions:** 3 direct answers to RQ1 + 1–2 secondary conclusions. *(write now)*
- **Appendix:** how to run + full parameter table. *(write now)*

### Outputs
- Completed English report: `report/Report_Template_EN.md`
- Completed Hebrew report: `report/Project_Report_Template_HE_v3.md`
- PDF export if required.

### DoD
- Every claim in Results references a figure/table.
- Fairness, skew characterization, and threats to validity are explicitly addressed.
- Hebrew translation complete and consistent with English.

---

## Stage 7 — Submission packaging
### Tasks
1. Final run end-to-end using `configs/main.yaml`.
2. Ensure code is runnable from scratch with clear instructions.
3. Confirm data submission policy: include small processed streams OR scripts to fetch.
4. Export report to PDF if required.
5. Final sanity check: row count in results.csv = 165, all plots exist, report is complete.

### Outputs
- Final report (EN + HE) + code bundle.

### DoD
- Another agent can reproduce results and figures with the provided instructions.
