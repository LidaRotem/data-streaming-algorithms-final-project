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
- Real datasets: Kosarak + Retail. Downloaded manually into data/raw/.
- Zipf alpha: two separate named datasets — zipf_1_1 (alpha=1.1) and zipf_1_3 (alpha=1.3).
- Seeds: synthetic uses 3 seeds [0,1,2], real uses 1 seed [0]. Global seed = 42.

---

### Professor feedback — incorporated
`[2026-03-02] [PM] Professor approved project direction. 4 required amendments follow.`

**Amendment 1 — Top-k metrics:** Add `recall@k` explicitly alongside `precision@k` and `overlap@k`. All three must appear as separate columns in `results.csv` and separate lines in the report Results section.

**Amendment 2 — Point queries:** Reporting separately by bucket (heavy / mid / rare) is now a hard requirement. Both MAE and relative error must be broken out per bucket. No aggregated-only reporting accepted.

**Amendment 3 — Memory fairness:** Must report actual bytes used per algorithm including auxiliary structures. Add `memory_bytes` column to `results.csv`. Add Fig 5 comparing actual bytes vs M across algorithms. Hard requirement.

**Amendment 4 — Skew visualization:** Both a frequency histogram AND a log-log rank-frequency plot required per dataset. Outputs: `skew_hist_<dataset>.png` and `skew_loglog_<dataset>.png`.

### Report writing schedule
`[2026-03-01] [PM] Integrated report writing across stages — never leave it all to Stage 6.`

- Stage 3 triggers: §2.1, §2.2, §3.3.
- Stage 4 triggers: §3 full, §4.0.
- Stage 5 triggers: §4, §5, Abstract, Executive Summary.
- Stage 6: polish, gap-fill, Hebrew translation only.

---

## Open questions

| # | Question | Raised by | Status |
|---|---|---|---|
| 1 | Kosarak and Retail download sources | PM | ✅ Resolved — downloaded from http://www.cs.rpi.edu/~zaki/Workshops/FIMI/data/ — placed in `data/raw/` |
| 2 | Zipf alpha: two separate datasets or two alpha runs? | PM | ✅ Resolved — two separate named datasets: `zipf_1_1` (alpha=1.1) and `zipf_1_3` (alpha=1.3) |
| 3 | Key overhead for MG/SS: Threats to Validity only, or bytes comparison? | PM | ✅ Resolved — hard requirement per professor. `memory_bytes` column + Fig 5. |

---

## Stage handbacks

### Stage 1 handback
`[2026-03-01] [Coding Agent] Stage 1 complete. All DoD items confirmed ✅. No deviations.`

**Decisions made (PM approved):**
- Added `__init__.py` to all `src/` subdirs — correct, enables clean imports.
- `smoke_test.py` inserts `PROJECT_ROOT` into `sys.path` — acceptable for robustness.
- `measure_throughput()` added to `timing.py` alongside `set_seed()` — same responsibility boundary.
- Ground truth excluded from `updates_per_sec` timing — correct, we measure only the algorithm under test.
- `.venv` created per user request — run with `.venv/Scripts/python` (Windows) or `.venv/bin/python` (Unix).

### Professor Feedback Patch handback
`[2026-03-02] [Coding Agent] All 10 patch DoD items confirmed ✅. Tests: 10 passed, 0 failed.`

**Flag raised by agent — PM confirmed:**
- Patch document states "Total: 23 columns" but canonical list has 25. Agent implemented all 25 correctly. "23" is a PM typo — documentation only, no code impact.

### Stage 2 handback
`[2026-03-02] [Coding Agent] Stage 2 complete. 50/50 tests pass, smoke test clean.`

**What was built:**
- `HashFamily` — Carter-Wegman family, sign hash for CS
- All 5 algorithms fully implemented with real logic
- 50 tests across 5 files, all passing
- Soft threshold test: all 5 algos passed `precision@10 > 0.5` on Zipf

**Decisions made (PM approved):**
- `seed=0` default kwarg on CMS/CMS-CU/CS — smoke_test.py calls AlgoClass(M) with no seed. Stage 4 run_all.py must pass `seed=run_seed` explicitly.
- `CountSketch.query()` returns `max(0, median)` — clips negative estimates. Acceptable.
- SpaceSaving uses lazy min-heap for O(log M) amortized eviction.
- `import sys` deferred inside `memory_bytes()` in ground_truth.py — unconventional but functional. Accepted.
- smoke_test.py computes skew inline — Stage 4 run_all.py must use `compute_skew()` from skew.py.

`[2026-03-02] [QA] Stage 2 QA — PASS. All DoD items verified against source and live execution.`

**QA findings (non-blocking):**
- F1 (resolved): NOTES.md had duplicate Stage 2 handback entry — PM cleaned up.
- F2 (informational): results.csv has 45 rows from 3 smoke test runs — expected append-only behaviour. Production CSV starts clean in Stage 4.
- F3 (confirmed deliberate): `precision_at_k` and `recall_at_k` produce identical values when |T_hat|=k. Both defined as |T∩T̂|/k. They diverge only if an algorithm returns fewer than k candidates. Keep both. Note in Threats to Validity.
- F4 (informational): smoke_test.py computes skew inline — Stage 4 must use compute_skew().

### Git setup handback
`[2026-03-02] [Coding Agent] Git initialized. 7 commits, clean working tree.`

**Log:**
```
a24dca8 docs(plan): log Stages 1-2 complete, professor patch, decisions
25fe0fc test(stage2): 50 tests across algorithms, ground truth, metrics, quality
0d2aa5c feat(stage2): implement topk, point_query, skew metrics with professor amendments
9a8f349 feat(stage2): implement all 5 algorithms and HashFamily
70a4014 feat(stage1): repo skeleton, results logger, seed handling, smoke test
6b3c896 config(stage0): lock all experiment parameters in main.yaml
b586faa chore: add gitignore, commit conventions, CLAUDE.md
```

**Decisions made (PM approved):**
- PM briefing/QA docs not committed — management artefacts, not source code.
- `run_all.py`, `make_plots.py` not committed — unimplemented stubs belong to Stage 4/5.
- `.claude/` not committed — Claude Code internal memory, not project source.
- `hashing.py` landed in commit 3 instead of 4 — minor ordering issue, no functional impact.
- `data/raw/` gitignored — raw files are large, download sources documented in `data/raw/README.md`.

### Stage 3 handback
`[pending]`

### Stage 4 handback
`[pending]`

### Stage 5 handback
`[pending]`

### Stage 6 handback
`[pending]`

### Stage 7 handback
`[pending]`

---

## Deviations from original task plan

| Stage | Deviation | Reason | PM approval |
|---|---|---|---|
| 0 | Zipf split into zipf_1_1 and zipf_1_3 | Captures mild and strong heavy-tail separately — better experimental coverage | ✅ |
| 0 | Row count updated 165 → 210 | Direct consequence of Zipf split (4 synthetic datasets × 3 × 5 × 3 = 180) | ✅ |

---

## Architectural decisions

| Decision | Value | Rationale | Stage |
|---|---|---|---|
| Config loading | pyyaml, loaded once at entry point, passed down explicitly | Avoid re-loading config inside module functions | 0 |
| Results file | Append-only CSV, one row per run | Simple, inspectable, no database dependency | 0 |
| Algorithm API | Common interface: update/query/topk/reset | Enables uniform experiment runner | 0 |
| Stub approach | Stage 1 uses stubs for all algos except GroundTruth | Proves pipeline works before real implementation | 1 |
| seed=0 default kwarg | CMS/CMS-CU/CS accept seed as kwarg defaulting to 0 | smoke_test.py calls AlgoClass(M) with no seed — Stage 4 must pass seed explicitly | 2 |
| CountSketch negative clamp | query() returns max(0, median) | Negative estimates are artefacts of sign collisions — clamping is standard practice | 2 |
| SpaceSaving min-heap | Lazy min-heap alongside dict for O(log M) eviction | Avoids O(M) scan on every update | 2 |
| precision==recall when \|T_hat\|=k | Both metrics defined as \|T∩T̂\|/k | Deliberate per spec — diverge only if algo returns <k candidates | 2 |
| data/raw/ gitignored | Raw files not committed | Large files with documented download sources in data/raw/README.md | 2 |

---

### PM amendments — architecture [2026-03-03]
`[2026-03-03] [PM] Three architecture amendments locked before Stage 3 completes.`

**Amendment A — Streaming (no full load into memory)**
- `generate_stream()` and all parsers must be generators (`yield` one item at a time).
- No function may accept or return `stream: list`.
- `compute_stats()` in skew.py accepts a `freq_dict`, not a stream.
- Processed `.txt` files still written for reproducibility, but read back line-by-line.

**Amendment B — Parallel execution**
- `run_all.py` uses `ProcessPoolExecutor` — one process per (dataset, algo, M, seed) run.
- `run_single()` must be a top-level function (not nested) — required for pickle.
- Ground truth computed inside each worker, not shared.
- Results collected in main process, then written to CSV (not written from workers).
- `configs/main.yaml` gets `execution.max_workers: null` (null = cpu_count - 1).

**Amendment C — Progress display**
- `tqdm` bar over total runs with elapsed + ETA + avg seconds/run as postfix.
- End-of-run summary: total elapsed, avg per run.
- `characterize_data.py` also gets tqdm over datasets.
- `run_time_sec` tracked per run (update loop wall time only, not file I/O).

### Stage 3 QA report
`[2026-03-03] [QA] Stage 3 QA — FAIL on Amendment 1. Rest of stage PASS.`

**DoD: PASS on all 8 items except Amendment 1.**
- 50/50 tests pass, 12 plots, dataset_stats.csv correct, characterize_data.py clean.
- Stats verified: all 6 datasets match reported values exactly.
- retail N=908,576 confirmed correct — file has fewer than N_max items, all retained.

**Amendment 1 FAIL — briefing discrepancy, not coding error:**
- Stage 3 briefing explicitly specified `-> list`. No generator amendment appeared in NOTES.md or the Stage 3 briefing. Coding agent implemented exactly what was specified.
- PM ruling: generators are required. Fix applied in Stage 4 as Part A.

**Non-blocking findings:**
- `characterize_data.py` lines 72–73: `plots_dir` and `stats_csv_path` hardcoded — fix in Stage 4.
- `_generate_mixture()` hardcodes `vocab_size=10000` — fix in Stage 4.

**QA flags resolved by PM:**
- Duplicate `datasets:` block in main.yaml: remove flat block, `data.datasets` is canonical.
- `execution.max_workers` absent from main.yaml: add before Stage 4.
- Cache seed risk: `load_dataset()` cache was generated with global_seed=42. Stage 4 `run_single()` must call `generate_stream()` directly with per-run seed — never use cached files for experiment runs.