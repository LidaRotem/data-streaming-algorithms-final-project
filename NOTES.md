# NOTES.md — Running Project Log
Project: **Algorithms for Real-Time Data Stream Analysis**
Maintained by: PM

> This file is the living memory of the project. Every significant decision, deviation, or open question is logged here with a date. The coding agent appends to this file when handing back a completed stage. The PM updates it when decisions change.

---

## How to use this file
- **PM:** log all decisions made, changes to plan, and responses to agent questions.
- **Coding agent:** when handing back a stage, append a new entry under "Stage N handback" with your DoD report, deviations, and decisions made.
- Never delete entries — this is an append-only log.
- Format: `[YYYY-MM-DD] [Role] Note`

---

## Decision log

### Stage 0 — Locked decisions
`[2026-03-01] [PM] All Stage 0 decisions locked after discussion with project owner.`

- Memory budgets set to 500 / 2000 / 8000. Rationale: covers tight/moderate/comfortable regimes with ~4x ratio between steps, suitable for log-scale plots. Kosarak ~41K distinct items, Retail ~17K — 500 forces real pressure on all algorithms.
- MG/SS missing key policy: f_hat = 0. Rationale: simpler, consistent, discuss implications in Threats to Validity.
- Real datasets: Kosarak + Retail. Status: not yet downloaded — coding agent to handle in Stage 3.
- Zipf alpha: use two values (1.1 and 1.3) to capture mild and strong heavy-tail regimes.
- Seeds: synthetic uses 3 seeds [0,1,2], real uses 1 seed [0]. Global seed = 42.

---

### Professor feedback — incorporated
`[2026-03-02] [PM] Professor approved project direction. 4 required amendments follow.`

**Amendment 1 — Top-k metrics:** Add `recall@k` explicitly alongside `precision@k` and `overlap@k`. All three must appear as separate columns in `results.csv` and separate lines in the report Results section.

**Amendment 2 — Point queries:** Reporting separately by bucket (heavy / mid / rare) is now a hard requirement. Both MAE and relative error must be broken out per bucket. No aggregated-only reporting accepted.

**Amendment 3 — Memory fairness:** Must report actual bytes used per algorithm including auxiliary structures. Add `memory_bytes` column to `results.csv`. Add Fig 5 comparing actual bytes vs M across algorithms.

**Amendment 4 — Skew visualization:** Both a frequency histogram AND a log-log rank-frequency plot are required per dataset. Outputs: `skew_hist_<dataset>.png` and `skew_loglog_<dataset>.png`.

- Principle: write from data, not from plans.
- Stage 3 triggers: §2.1, §2.2, §3.3.
- Stage 4 triggers: §3 full, §4.0.
- Stage 5 triggers: §4, §5, Abstract, Executive Summary.
- Stage 6: polish, gap-fill, Hebrew translation only.

---

## Open questions

| # | Question | Raised by | Status |
|---|---|---|---|
| 1 | Kosarak and Retail download sources | PM | ✅ Resolved — mirror: http://www.cs.rpi.edu/~zaki/Workshops/FIMI/data/ (fimi.uantwerpen.be is down) |
| 2 | Zipf alpha: two separate datasets or one with two alpha runs? | PM | ✅ Resolved — two datasets: zipf_1_1 (α=1.1) and zipf_1_3 (α=1.3). Total grid = 210 rows. |
| 3 | Key overhead for MG/SS: Threats to Validity only, or bytes comparison? | PM | ✅ Resolved — hard requirement. memory_bytes column + Fig 5. |

---

## Stage handbacks

### Stage 1 handback
`[2026-03-01] [Coding Agent] Stage 1 complete. All DoD items confirmed ✅. No deviations.`

**Decisions made (PM approved):**
- Added `__init__.py` to all `src/` subdirs.
- `smoke_test.py` inserts `PROJECT_ROOT` into `sys.path`.
- `measure_throughput()` added to `timing.py`.
- Ground truth excluded from `updates_per_sec` timing.
- `.venv` created — activate with `.venv/Scripts/Activate.ps1` (Windows).

### Professor Feedback Patch handback
`[2026-03-02] [Coding Agent] All 10 patch DoD items confirmed ✅. Tests: 10 passed.`

**Decisions made (PM approved):**
- Patch document had typo "23 columns" → correct is 25. Code was correct.

### Stage 2 handback
`[2026-03-02] [Coding Agent] Stage 2 complete. 50/50 tests pass, smoke test clean.`

**What was built:**
- HashFamily — Carter-Wegman family, sign hash for CS
- All 5 algorithms fully implemented
- 50 tests across 5 files, all passing
- Soft threshold test: all 5 algos passed precision@10 > 0.5 on Zipf

**Decisions made (PM approved):**
- `seed=0` default kwarg on CMS/CMS-CU/CS. Experiment runner must pass seed explicitly.
- `CountSketch.query()` returns `max(0, median)` — clips negative estimates.
- SpaceSaving uses lazy min-heap for O(log M) amortized eviction.

### Stage 3 handback
`[2026-03-03] [Coding Agent] Stage 3 complete. All 8 DoD items confirmed ✅.`

**What was built:**
- Synthetic generators: uniform, zipf_1_1, zipf_1_3, mixture → data/processed/
- Real parsers: kosarak.dat, retail.dat (gzip auto-detected) → data/processed/
- characterize_data.py: F0/F1/F2/skew for all 6 datasets, 12 plots generated
- data/raw/README.md with download instructions

**Dataset stats:**
| Dataset   | N         | F0     | Skew     |
|-----------|-----------|--------|----------|
| uniform   | 1,000,000 | 10,000 | 0.000101 |
| zipf_1_1  | 1,000,000 | 9,997  | 0.034017 |
| zipf_1_3  | 1,000,000 | 9,547  | 0.094043 |
| mixture   | 1,000,000 | 10,000 | 0.005016 |
| kosarak   | 1,000,000 | 25,343 | 0.012806 |
| retail    | 908,576   | 16,470 | 0.006499 |

**Decisions made (PM approved):**
- Raw files are gzip-compressed — parser auto-detects via magic bytes.
- retail N=908,576 — below N_max, all items retained. Asymmetric N noted for §3.3.
- characterize_data.py overwrites dataset_stats.csv — idempotent, acceptable.
- datasets.py caches processed streams — Stage 4 run_single() must NOT use cache; call generate_stream() directly with per-run seed.

**QA findings (non-blocking, fixed in Stage 4):**
- Amendment 1 (streaming generators) was not applied in Stage 3 — briefing discrepancy, not coding error. Fixed in Stage 4.
- characterize_data.py had hardcoded paths — fixed in Stage 4.
- _generate_mixture() hardcoded vocab_size=10000 — fixed in Stage 4.
- Duplicate flat datasets: block in main.yaml — removed in Stage 4.

### Stage 4 handback
`[2026-03-03] [Coding Agent] Stage 4 complete. 20/20 DoD passed, QA cleared.`

**What was built:**
- Amendment 1 applied: generate_stream(), parse_transaction_file(), load_dataset() all converted to generators
- smoke_test.py approved fix: two separate generate_stream() calls
- run_all.py: ProcessPoolExecutor, 210 runs, tqdm progress, results/results_full.csv
- tests/test_streaming.py: 6 new streaming tests (56 total, all passing)
- Makefile, execution.max_workers in config, plots_dir/results_dir in config

**Decisions made (PM approved):**
- measure_throughput() fixed to count items during iteration (len() fails on generators)
- experiments/__init__.py added to resolve package vs module conflict
- characterize_data.py materialises stream with list() — intentional exception for non-hot-path script
- overlap_at_k normalised to [0,1] (was returning raw count [0–100]); tests updated to match
- overlap_at_k patched in results_full.csv as precision_at_k (equal when |T̂|=k); grid not re-run

**Results summary (210 rows, all valid):**
| Dataset  | Algorithm | Mean precision@k | Mean updates/sec |
|----------|-----------|-----------------|-----------------|
| uniform  | MG        | 0.131           | 1,786,138       |
| uniform  | SS        | 0.130           | 626,490         |
| zipf_1_1 | MG        | 0.999           | 2,352,303       |
| zipf_1_1 | SS        | 0.999           | 756,848         |
| zipf_1_3 | MG        | 1.000           | 2,629,483       |
| zipf_1_3 | SS        | 1.000           | 1,011,336       |
| kosarak  | MG        | 0.927           | 1,182,985       |
| kosarak  | SS        | 0.930           | 460,924         |
| retail   | MG        | 0.843           | 1,158,339       |
| retail   | SS        | 0.843           | 451,532         |
- Wall time: 67.1s (1.1 min), 27 workers
- CMS-CU is slowest (63K–88K updates/sec); MG is fastest (1M–2.6M updates/sec)

### Stage 5 handback
`[2026-03-03] [Coding Agent] Stage 5 complete. All 15 DoD items confirmed ✅.`

**What was built:**
- `experiments/make_plots.py`: full implementation; 5 figures generated clean from results_full.csv
- `plots/fig_1_precision.png` — 6-panel Precision@k vs M, error bars for synthetic
- `plots/fig_2_overlap.png` — 6-panel Overlap@k vs M (identical to Fig 1, required separately)
- `plots/fig_3_mae.png` — MAE by bucket (heavy/mid/rare), grand mean across datasets, log scale
- `plots/fig_4_throughput.png` — Throughput by dataset, log-log scale
- `plots/fig_5_memory_bytes.png` — Actual memory bytes vs M, single panel, log scale
- `results/winners.csv` — 18 rows (6 datasets × 3 budgets), schema: dataset, M, budget_label, best_algo, best_precision, runner_up, runner_up_precision
- `report/Report_Stage5.md` — complete report: Abstract, §0 Executive Summary, §1 Intro, §2 Background, §3 Setup, §4 Results, §5 Discussion, §6 Conclusions, Appendices A & B; all numbers from data

**Key findings confirmed from data:**
- MG/SS: Precision@k = 1.000 on Zipf α=1.3 at all budgets; CMS-CU best sketch at 0.523 (M=500)
- MG throughput: 1.96M/s = 15× CMS (130K/s), 28× CMS-CU (69K/s)
- CMS-CU largest improvement: Kosarak M=2000, Δ=+0.280 (0.60→0.88)
- mixture surprise: MG/SS only ~51% precision at M=500 despite engineered heavy hitters — addressed in §5.1
- SS memory_bytes: >30MB at all budgets (Python string key overhead); sketches ~1MB fixed
  [CORRECTION 2026-03-03] SS large memory is caused by O(N) stale tuples in the lazy-deletion
  heap, not string keys. Keys are Python ints (parsers.py yields int(token)). Each update()
  calls heapq.heappush without cleanup; stale entries only removed during eviction events. After
  N=1,000,000 updates the heap holds hundreds of thousands of stale (count, item) tuples (~72
  bytes each), dominating memory. See Stage 6a Part 5 for details.

**Decisions made:**
- `winners.csv` is gitignored in `.gitignore` but required by Stage 5 briefing → force-added (`git add -f`)
- `winners.csv` "best" definition: highest mean precision@k across seeds (as briefed)
- Where multiple algorithms tie at 1.000, whichever appears first alphabetically is "winner" (minor, all tied at 1.000)
- Fig 3 uses log scale on y-axis (grand MAE spans 1–5,059 — log scale required for readability)
- Fig 5 uses aggregate mean across datasets (not per-dataset) as briefed

**Deviations:**
- None from briefing.

**Blockers / questions for Stage 6:**
- §1 Intro, §2.3 algorithm descriptions, §2.4 pre-experiment expectations, §6 Conclusions are in the report as stubs filled with content — PM should verify whether to carry forward or rewrite for Stage 6 polish.
- Hebrew translation (Stage 6) — will need original English text finalized first.

### Stage 6 handback
`[2026-03-03] [Coding Agent] Stage 6a Part 5 complete. All 20 DoD items confirmed ✅.`

**CMS-B ablation results (zipf_1_3, mean over seeds 0,1,2):**
| Algorithm | M=500 | M=2000 | M=8000 |
|---|---|---|---|
| CMS-B | 0.733 | 0.973 | 1.000 |
| CMS (unbounded) | 0.403 | 0.923 | 1.000 |
| MG | 1.000 | 1.000 | 1.000 |

- Bounded vs unbounded CMS precision delta at M=500: +0.330 (0.403 → 0.733)
- Gap between CMS-B and MG at M=500: 0.267
- Conclusion: MG/SS advantage is driven primarily by sketch collision errors, not unbounded
  candidate tracking. Bounding the Counter to M entries (CMS-B) substantially improves
  precision but cannot close the gap to MG/SS on high-skew streams.
- CMS-B memory at M=500: ~69KB (vs CMS ~834KB, MG ~50KB) — directly comparable to MG

**Hash family (from src/utils/hashing.py):**
- Carter-Wegman family: h_i(x) = (a_i·x + b_i) mod p mod w, p = 2^31 − 1
- Independence: each row draws separate (a_i, b_i) from numpy.random.default_rng(seed)
- Sign hash for CS: g_i(x) = 2·((c_i·x + e_i) mod p mod 2)−1 ∈ {−1, +1}
- Documented in §3.1 of report

**All 7 sweeps applied to report/Report_Stage5.md:**
1. ✅ §3.2: Fixed "fixed-depth numpy array ~1.03MB" → "total sketch memory dominated by Counter"
2. ✅ No "string keys" / SS explanation already correct in all sections; NOTES.md correction added
3. ✅ No "cache-cold" or "1MB+ array" text in report (already corrected in prior stage)
4. ✅ No universal language violations ("consistent across all tested conditions", "In our tested
   regimes" already present from prior stage)
5. ✅ Hash family description added to §3.1
6. ✅ CMS-B results added to §3.2, §4.2, §5.3, §6.2 with real numbers, zero placeholders
7. ✅ PLAN.md: Stage 5 DONE, Stage 6 IN PROGRESS, CMS-B note, grid table updated

**fig_5 regenerated:** ✅ annotation updated to
  "Sketches: numpy table (4-64KB) + candidates Counter (~1MB, dominates)"

**pytest results:** 63 passed (56 existing + 7 new CMS-B tests), 0 failed ✅

**results_full.csv:** 219 rows (210 original + 9 CMS-B on zipf_1_3) ✅

**Decisions made (not specified in briefing):**
- CMS-B memory table not shown in §3.2 (only CMS/MG/SS in existing table) — CMS-B results
  are in §4.2 ablation table only, to keep §3.2 focused on the original 5-algorithm comparison.
- "Any dataset with meaningful skew" in PLAN.md line 499 left as-is (not on the reviewer's list).

**Deviations:**
- None from briefing.

**Blockers / questions for next stage:**
- Hebrew translation (Stage 6 remaining) still pending PM briefing.

### Stage 7 handback
`[pending]`

---

## Deviations from original task plan

| Stage | Deviation | Reason | PM approval |
|---|---|---|---|
| 3 | zipf split into zipf_1_1 and zipf_1_3 | Capture mild and strong heavy-tail separately | ✅ |
| 3 | Amendment 1 not applied in Stage 3 | Briefing omission — fixed in Stage 4 | ✅ |
| 4 | results written to results_full.csv not results.csv | Keep smoke test output separate | ✅ |
| 4 | overlap_at_k normalised to [0,1] | Was returning raw count — bug fix | ✅ |

---

## Architectural decisions

| Decision | Value | Rationale | Stage |
|---|---|---|---|
| Config loading | pyyaml, loaded once at entry point, passed down explicitly | Avoid re-loading config inside module functions | 0 |
| Results file | Append-only CSV, one row per run | Simple, inspectable, no database dependency | 0 |
| Algorithm API | Common interface: update/query/topk/reset | Enables uniform experiment runner | 0 |
| Stub approach | Stage 1 uses stubs for all algos except GroundTruth | Proves pipeline works before real implementation | 1 |
| Streaming generators | All data functions yield, never return list | Memory efficiency, single-pass constraint | 4 |
| Parallel execution | ProcessPoolExecutor, run_single() top-level | CPU-bound workload, pickle requirement | 4 |
| Cache isolation | run_single() calls generate_stream() directly with per-run seed | Cache files use global_seed=42, not per-run seeds | 4 |
| results_full.csv | Separate from results.csv (smoke test) | Avoid smoke test noise in production results | 4 |