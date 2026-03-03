# Final Project Report Template (EN)
Course: **Algorithms for Real-Time Data Stream Analysis**

## Title Page
- **Project title (one sentence / core question):**  
  *[Fill]* Under a fixed memory budget, which approach identifies Heavy Hitters (Top-k) more reliably—hash-based sketches or counter-based summaries—and how does performance change with stream skew and across real datasets?
- **Course / semester**
- **Name**
- **Submission date**
- **Repo link / attached zip:** *[Fill]*

---

## Abstract (5–7 lines)
- **Problem:** *[1–2 lines]* Why heavy hitters in large streams is hard (memory / one pass / speed).
- **Approach:** Compare two families: hash-based sketches vs counter-based heavy-hitter summaries.
- **Algorithms:** CMS, CMS-CU, Count-Sketch, Misra–Gries, Space-Saving.
- **Data:** 3 synthetic regimes (Uniform / Zipf / Mixture) + 2 real datasets (e.g., Kosarak + Retail).
- **Metrics:** Precision@k / Overlap@k, point-query error for `f(i)`, throughput/latency.
- **Main result:** *[1 line]* who wins where.
- **Practical rule-of-thumb:** *[1 line]* when to use what.

---

## 0. Executive Summary (≤ 1/2 page)

### 0.1 Primary research question (paste-ready)
Given the same memory budget, how does **Top-k heavy hitters** identification compare between  
**hash-based sketches** (CMS / CMS-CU / Count-Sketch) and **counter-based summaries** (Misra–Gries / Space-Saving),  
and how do results change with **stream skew** and across **different real datasets**?

### 0.2 What we did (one short paragraph)
*[Fill]* We implemented 5 algorithms with a reproducible experiment pipeline. For each dataset we characterized skew (F0,F1,F2, skew = F2/F1², and rank–frequency log-log plot). We ran an experiment grid over 3 memory budgets, measured Top-k quality, point-query error, and performance, and derived practical decision rules.

### 0.3 Key results (3 bullets — must be specific)
- Result 1: On **[dataset/regime]**, **[algorithm]** achieved the best Precision@k under **[budget]** (Δ=__ vs __).
- Result 2: Conservative Update improved/did not improve CMS mainly when **[condition]** (see Fig __).
- Result 3: Performance tradeoff: **[fastest algo]** was fastest but less accurate on __; **[best algo]** improved accuracy at the cost of __.

### 0.4 Bottom-line recommendation (rule-of-thumb)
*[Fill]* If the stream is **high-skew** (high F2/F1²) and memory is tight → use __.  
If skew is moderate / memory is larger → __ is sufficient.  
If you only need Top-k → __. If you also need point queries → __.

### 0.5 Quick definitions (2–3 lines)
- **Heavy hitters / Top-k:** the k items with highest true frequencies.
- **Point query:** estimating the value `f(i)` for a given item i.
- **Skew:** frequency concentration; we use `F2/F1²` + rank–frequency plot.

---

## 1. Introduction & Motivation (1–1.5 pages)

### 1.1 Real-world framing
- Examples: clickstream, logs, transactions, network flows.
- Practical goal: detect “hot items” (Top-k) in real time with tiny memory.

### 1.2 Why exact counting is hard
- Massive key space (large F0) → full dictionary is expensive.
- Long streams (large F1) → high update rate, needs throughput.
- One pass: no rewinds.

### 1.3 Research questions
- **RQ1 (Primary):** Under the same memory budget, who identifies Top-k better across skew regimes (synthetic + real)?
- **RQ2 (Secondary):** What happens to point-query accuracy (`f(i)`) and performance (updates/sec, latency)?

### 1.4 Contributions
- Family-level comparison: sketches vs summaries.
- 5-algorithm benchmark (including MG+SS beyond the homework baseline).
- Synthetic regimes + at least two real datasets with different characteristics.
- Practical decision rules + explanation tied to skew.

---

## 2. Background (2–4 pages)

### 2.1 Stream model & notation
- Frequency vector `f`, value `f(i)` for key i.
- Moments: `F0 = #distinct`, `F1 = Σ f(i)`, `F2 = Σ f(i)^2`.
- Definition of Top-k and heavy hitters.

### 2.2 Skew metric we use (and why)
- Main metric: `skew = F2 / (F1^2)` (higher → more mass on heavy items).
- Visualization: rank–frequency plot (log-log).
- We use skew to explain “when” each algorithm wins.

### 2.3 Algorithms (write each in the same mini-structure)
For each algorithm include:
- **Intuition (3–6 sentences)**
- **Short pseudocode (6–12 lines)**
- **Informal guarantee / error behavior**
- **Parameters and what they control**
- **Complexity:** update / query / memory
- **Practical notes:** hashing, constants, pitfalls

Algorithms:
1) **Count-Min Sketch (CMS)**  
2) **CMS + Conservative Update (CMS-CU)**  
3) **Count-Sketch (CS)**  
4) **Misra–Gries (MG)**  
5) **Space-Saving (SS)**

### 2.4 What we expect before experiments
- In heavy-tail: summaries (MG/SS) may excel on Top-k with small m.
- In low-skew: everyone struggles; MG/SS may churn; sketches suffer collisions.
- CS should correlate better with high `F2`; CMS tends to overestimate.
- CMS-CU should reduce overestimation when collisions are common with heavy items.

---

## 3. Experimental Setup (1.5–2.5 pages)

### 3.1 Environment & reproducibility
- Hardware: CPU, RAM (32GB), etc.
- Software: OS, Python version, libraries.
- Seeds: global seed + per-run seed.
- How to run: scripts + config files.

### 3.2 Fairness: defining “same memory budget”
- Define `M` in **#counters / entries**.
- **Sketches:** `M = d*w`, default `d=5`, `w=floor(M/d)`.
- **Summaries:** `M = m` entries `(key,count)`.
- Validity note: key overhead in MG/SS.
- (Optional) secondary comparison by bytes.

### 3.3 Data (operational details)
#### 3.3.1 Synthetic streams
- Uniform / Zipf(alpha=__) / Mixture(k_heavy=__, p_heavy=__)

#### 3.3.2 Real datasets
- Kosarak: parsing + flattening
- Retail: parsing + flattening
- Truncation: `N_max = __` if needed

#### 3.3.3 Dataset characterization (required)
- compute `F0,F1,F2`, `skew = F2/F1²`
- rank–frequency plot (log-log)
- dataset stats table at the start of Results

### 3.4 Metrics (precise definitions)
#### 3.4.1 Top-k metrics (Primary)
- Precision@k, Overlap@k

#### 3.4.2 Point-query metrics (Secondary)
- fixed query set `Q` split into heavy/mid/rare
- MAE + relative error
- MG/SS policy: missing key → `f_hat = 0` (or unknown)

#### 3.4.3 Performance metrics
- updates/sec, query_ms
- warmup + mean/std across seeds

### 3.5 Experiment matrix (MUST be a table)
Include datasets, N/U/N_max, k, budgets, d,w,m, repetitions.

---

## 4. Results (2–5 pages)
### 4.0 Dataset stats table (must come first)
Table: `F0,F1,F2,skew` + one-line description.

### 4.1 Figure plan
- Fig1 Precision@k vs M
- Fig2 Overlap@k vs M
- Fig3 MAE buckets vs M
- Fig4 updates/sec vs M
- Fig5 optional: CMS vs CMS-CU

### 4.2 Main result
Explain Fig1 across datasets; connect to skew; give one clear takeaway.

### 4.3 Sensitivity / ablations
- skew regime effect
- CU effect
- optional: depth vs width

### 4.4 Decision rules
2–5 concrete selection rules.

---

## 5. Discussion (1–2 pages)
### 5.1 Expectations vs surprises
### 5.2 Failure modes
### 5.3 Threats to validity (bullets)

---

## 6. Conclusions & Future Work (≤ 1 page)
### 6.1 Conclusions
### 6.2 Future work

---

## Appendix A — How to run (required)
## Appendix B — Full parameter table (required)
