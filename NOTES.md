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

**Amendment 2 — Point queries:** Reporting separately by bucket (heavy / mid / rare) is now a hard requirement, not just recommended. Both MAE and relative error must be broken out per bucket. No aggregated-only reporting accepted.

**Amendment 3 — Memory fairness:** Must report actual bytes used per algorithm including auxiliary structures (keys stored in MG/SS dicts, candidate Counter in CMS/CS). Add `memory_bytes` column to `results.csv`. Add a figure (Fig 5) comparing actual bytes vs M across algorithms. This resolves open question #3 — it is now a hard requirement, not optional.

**Amendment 4 — Skew visualization:** Both a frequency histogram AND a log-log rank-frequency plot are required per dataset. Previously only log-log was specified. Rename plot outputs to `skew_hist_<dataset>.png` and `skew_loglog_<dataset>.png` for clarity.

- Principle: write from data, not from plans.
- Stage 3 triggers: §2.1, §2.2, §3.3.
- Stage 4 triggers: §3 full, §4.0.
- Stage 5 triggers: §4, §5, Abstract, Executive Summary.
- Stage 6: polish, gap-fill, Hebrew translation only.

---

## Open questions

| # | Question | Raised by | Status |
|---|---|---|---|
| 1 | Kosarak and Retail download sources — need to confirm URLs and license. | PM | ✅ Resolved — Kosarak: http://fimi.uantwerpen.be/data/kosarak.dat — Retail: http://fimi.uantwerpen.be/data/retail.dat — both public, free for research use. Place in `data/raw/`. |
| 2 | Zipf alpha: use 1.1 and 1.3 as two separate datasets, or one dataset with two alpha runs? | PM | ✅ Resolved — treat as two separate named datasets: `zipf_low` (alpha=1.1) and `zipf_high` (alpha=1.3). Each gets its own row in dataset_stats.csv and its own plots. |
| 3 | Key overhead for MG/SS: mention in Threats to Validity only, or add a bytes-based secondary comparison? | PM | ✅ Resolved — now a hard requirement per professor. Add memory_bytes column and Fig 5. |

---

## Stage handbacks

*(Coding agent appends here after each stage is complete)*

### Stage 1 handback
`[2026-03-01] [Coding Agent] Stage 1 complete. All DoD items confirmed ✅. No deviations.`

**Decisions made (PM approved):**
- Added `__init__.py` to all `src/` subdirs — correct, enables clean imports.
- `smoke_test.py` inserts `PROJECT_ROOT` into `sys.path` — acceptable for robustness.
- `measure_throughput()` added to `timing.py` alongside `set_seed()` — approved, same responsibility boundary.
- Ground truth excluded from `updates_per_sec` timing — correct, we measure only the algorithm under test.
- `.venv` created per user request — run with `.venv/Scripts/python` (Windows) or `.venv/bin/python` (Unix).

**Open question resolved:**
- `tests/` structure will be specified in the Stage 2 briefing. ✅

### Professor Feedback Patch handback
`[2026-03-02] [Coding Agent] All 10 patch DoD items confirmed ✅. Tests: 10 passed, 0 failed.`

**Flag raised by agent — PM confirmed:**
- Patch document (`Coding_Agent_Professor_Patch.md`) states "Total: 23 columns" but the canonical list has 25. Agent implemented all 25 correctly. The "23" is a PM typo in the patch document only.
- **Action assigned to coding agent:** correct the typo in `Coding_Agent_Professor_Patch.md` line reading "Total: 23 columns" → "Total: 25 columns". No code changes required — documentation fix only.

### Stage 2 handback
`[2026-03-02] [Coding Agent] Stage 2 complete. 50/50 tests pass, smoke test clean.`

**What was built:**
- `HashFamily` — Carter-Wegman family, sign hash for CS
- All 5 algorithms fully implemented with real logic
- 50 tests across 5 files, all passing
- Soft threshold test: all 5 algos passed `precision@10 > 0.5` on Zipf

**Decisions made (PM approved):**
- `seed=0` default kwarg on CMS/CMS-CU/CS to handle `AlgoClass(M)` calls with no seed arg. Experiment runner (Stage 4) must pass `seed=run_seed` explicitly.
- `CountSketch.query()` returns `max(0, median)` — clips negative estimates. Acceptable.
- SpaceSaving uses lazy min-heap for O(log M) amortized eviction — good call.

**Open question — resolved:**
- Kosarak/Retail raw file paths: place in `data/raw/kosarak.dat` and `data/raw/retail.dat`. Configurable via `configs/main.yaml` under `data.raw_dir`. Specified in Stage 3 briefing.

**Documentation fix still pending:**
- `Coding_Agent_Professor_Patch.md` line "Total: 23 columns" → "Total: 25 columns". Assigned to coding agent to fix in next session.

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
| — | None yet | — | — |

---

## Architectural decisions

| Decision | Value | Rationale | Stage |
|---|---|---|---|
| Config loading | pyyaml, loaded once at entry point, passed down explicitly | Avoid re-loading config inside module functions | 0 |
| Results file | Append-only CSV, one row per run | Simple, inspectable, no database dependency | 0 |
| Algorithm API | Common interface: update/query/topk/reset | Enables uniform experiment runner | 0 |
| Stub approach | Stage 1 uses stubs for all algos except GroundTruth | Proves pipeline works before real implementation | 1 |
