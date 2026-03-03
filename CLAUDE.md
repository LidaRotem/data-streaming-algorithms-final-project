# CLAUDE.md — Coding Standards & Conventions
Project: **Algorithms for Real-Time Data Stream Analysis**
Maintained by: PM

> This file defines how code must be written in this project. The coding agent must read and follow this before writing any code. These standards apply to every stage.

---

## 0. Environment (read first)
- **Always activate the virtual environment before running any Python command:**
  ```powershell
  # Windows PowerShell
  .venv\Scripts\Activate.ps1

  # Windows CMD
  .venv\Scripts\activate.bat

  # macOS / Linux
  source .venv/bin/activate
  ```
- You should see `(.venv)` at the start of your prompt before proceeding.
- All `python` and `pytest` commands assume the venv is active.
- Never install packages outside the venv.

---

## 1. General principles
- **Clarity over cleverness.** This is a research project. Code must be readable by a human reviewer and reproducible by another agent.
- **No hardcoded parameters.** Every experiment parameter comes from `configs/main.yaml`. If it's not in the config, ask the PM before adding it.
- **One responsibility per file.** Don't mix algorithm logic, data loading, and metrics in the same file.
- **Fail loudly.** Raise exceptions with clear messages rather than silently returning wrong values.

---

## 2. Language & environment
- Python 3.10+
- All dependencies in `requirements.txt` — no implicit installs.
- No Jupyter notebooks in the main codebase. Notebooks are acceptable only for scratch exploration and must not be part of the reproducible pipeline.
- Run everything from the project root. All paths are relative to root.

---

## 3. Config usage
- Load config once at entry point using `pyyaml`. Pass values down explicitly — do not re-load the config inside module functions.
- Never import `configs/main.yaml` from inside `src/`. Config is the experiment layer's responsibility.
- If a function needs a parameter, it receives it as an argument — not by reading the config file itself.

```python
# CORRECT
def run_experiment(algo, stream, M, k, seed):
    ...

# WRONG
def run_experiment(algo, stream):
    config = yaml.safe_load(open("configs/main.yaml"))
    M = config["memory_budgets"]["M_small"]
    ...
```

---

## 4. Algorithm API (non-negotiable)
Every algorithm class must implement exactly this interface:

```python
class AlgorithmName:
    def __init__(self, M: int, **kwargs): ...
    def update(self, item) -> None: ...
    def query(self, item) -> float: ...
    def topk(self, k: int) -> list: ...  # returns [(item, count), ...]
    def reset(self) -> None: ...
    def memory_bytes(self) -> int: ...   # actual bytes including aux structures
```

- `M` is always the memory budget in #counters or #entries. No exceptions.
- `topk()` must always return a list of `(item, estimated_count)` tuples, sorted descending by count.
- `query()` must always return a float, never raise KeyError or similar — missing items return 0.0.
- All algorithms must be deterministic given the same seed.

---

## 5. Seeding
- Always call `set_seed(seed)` before generating data or initializing an algorithm in any experiment run.
- Store the seed used in every row of `results/results.csv`.
- Never use `random` or `numpy.random` directly without having set the seed first in that run context.

---

## 6. Results logging
- Every experiment run appends exactly one row to `results/results.csv`.
- Never overwrite `results.csv` — always append.
- All required columns must be present in every row. Use `None` or `NaN` for metrics not yet computed, but the column must exist.
- **Canonical 25-column schema (do not rename or reorder):**
  ```
  run_id, dataset, algorithm, M, budget_label, seed, k,
  precision_at_k, recall_at_k, overlap_at_k,
  mae_heavy, mae_mid, mae_rare,
  rel_err_heavy, rel_err_mid, rel_err_rare,
  updates_per_sec, query_ms,
  memory_counters, memory_bytes,
  F0, F1, F2, skew,
  timestamp
  ```

---

## 7. File & function naming
- Files: `snake_case.py`
- Classes: `PascalCase`
- Functions and variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- No abbreviations in function/variable names unless they are domain-standard (e.g., `cms`, `mae`, `topk`, `F0`, `F1`, `F2`).

```python
# CORRECT
def compute_precision_at_k(true_topk, estimated_topk, k):
    ...

# WRONG
def prec(tt, et, k):
    ...
```

---

## 8. Error handling
- Use explicit `ValueError` or `AssertionError` with messages for bad inputs.
- Do not use bare `except:` clauses.
- Log errors to stderr, not stdout.

```python
# CORRECT
if M <= 0:
    raise ValueError(f"Memory budget M must be positive, got {M}")

# WRONG
try:
    ...
except:
    pass
```

---

## 9. Testing
- Unit tests go in `tests/`.
- Use `pytest`.
- Every algorithm must have at least one test that:
  - Runs without error on a small stream (N=100)
  - Is deterministic with a fixed seed
  - Checks that `query()` returns a non-negative float
  - Checks that `topk(k)` returns a list of length ≤ k
- `GroundTruth` must have a test that verifies `F0`, `F1`, `F2` are correct on a known stream.

---

## 10. Performance expectations
- Update throughput is a measured metric — do not optimize prematurely, but do not introduce unnecessary Python-level overhead (e.g., no file I/O inside the update loop).
- The smoke test must complete in under 30 seconds.
- The full experiment grid (Stage 4) should complete in under 30 minutes on a standard laptop. Flag the PM if this looks unreachable.

---

## 11. Reproducibility checklist (before handing back any stage)
- [ ] Venv is active — `(.venv)` visible in prompt.
- [ ] `python experiments/smoke_test.py --config configs/main.yaml` runs clean.
- [ ] No hardcoded parameters outside `configs/main.yaml`.
- [ ] All new dependencies added to `requirements.txt`.
- [ ] All new files follow naming conventions.
- [ ] Seed is set and stored for every run.
- [ ] `results/results.csv` has all 25 canonical columns.
- [ ] No commented-out dead code left in files.
- [ ] `pytest tests/` passes with 0 failures.

---

## 12. Communication with PM
- When you complete a stage, report back with:
  1. DoD checklist — each item explicitly confirmed or flagged.
  2. Any deviations from the briefing and why.
  3. Any decisions you made that weren't specified — flag these so the PM can update the task plan.
  4. Any blockers or open questions for the next stage.
- Do not silently make architectural decisions. Surface them.
