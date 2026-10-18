# Phase 1: Foundation & Benchmark - Research

**Researched:** 2026-10-18
**Domain:** Local LLM runtime setup, model benchmarking, offline embedding provisioning (CPU-only 16 GB target)
**Confidence:** HIGH (stack + Ollama mechanics) / MEDIUM (Gemma 4 runtime behaviours) / HIGH (environment audit)

> **Phase 1 decision carved out for this document:** the **BENCH-02 measurement method** was deliberately left to planning by the user (`01-CONTEXT.md` line 50). The `## Standard Stack` benchmark section and `### Pattern 2: The BENCH-02 Harness` below are the recommended, prescriptive answer. Read those two sections first.

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Phase-1 deliverable boundary**
- **D-01:** Phase 1 ships the code skeleton, not just runtime artifacts. Deliverables include `src/config.py` and `src/llm.py`, plus `scripts/` and `tests/` package skeletons. This matches the hour-1 handover in `docs/TEAM_ROLES_AND_CONTRACTS.md` §5 ("Hour 1: R4 pushes the skeleton and `config.py` stub; R1 pushes `llm.py` with the stub backend") and the PROJECT_MASTER hour 0:00-1:30 exit check ("stub LLM backend ready"). The ROADMAP's five success criteria omit this; the docs pack requires it, and R2/R3/R4 cannot start their contract files without it.
- **D-02:** `src/llm.py` implements exactly the contract in `docs/TEAM_ROLES_AND_CONTRACTS.md` §3: `check_model_ready() -> tuple[bool, str]`, `generate(system, prompt, json_mode=True) -> str`, `ModelUnavailable`, and the `STUB_LLM=1` backend that returns a fixed valid JSON string without calling a model. Because of D-10 there is no pluggable-runtime abstraction — one Ollama HTTP backend plus the stub.
- **D-03:** `src/config.py` is created with the real `MODEL_NAME` from the benchmark result plus the full constant set in TEAM_ROLES §3: `OLLAMA_URL`, `EMBED_MODEL_PATH`, `TOP_K`, `SILENT_THRESHOLD` (placeholder 0.30, calibrated in Phase 2), `MAX_UPLOAD_MB`, `MIN_CHARS_PER_PAGE`, `REQUEST_TIMEOUT_S`.
- **D-04:** **`src/config.py` `MODEL_NAME` is the single source of truth for the chosen model.** It is overridable by the `CLAUSEGUARD_MODEL` environment variable, which `README.md` setup step 5 already promises. `docs/benchmarks.md` holds the measured evidence; `docs/PROJECT_MASTER.md` §7.3 gets a one-line pointer. Downstream agents must read `config.py` and must not re-decide or duplicate the model name.
- **D-05:** Phase 1 writes **D1, the clean lease**, into `sample_documents/` as the benchmark fixture, per the specification in `docs/TEST_PLAN.md` §1: 6-10 pages, numbered clauses covering rent, deposit (30 days), notice (2 months), repairs, pets, termination, late fee. It is fictional and team-written. It is reused as the Phase 2 baseline ingestion document, so it is written once. The `sample_documents/README.md` table must be updated to list it.

**Runtime, hardware and selection fallout**
- **D-06:** The benchmark runs all three candidates (`gemma3n:e2b`, `gemma4:e2b`, `gemma4:e2b-it-qat`) on the RTX 2050 laptop **and** on one nominated CPU-only 16 GB laptop. The CPU-only run is what makes BENCH-03's criterion ("loads on 16 GB CPU laptop") real evidence instead of an assumption. The winning model then gets a confirmation run on the designated demo machine. Every benchmark row must record which machine produced it. Note: the RTX 2050 has only 4 GB VRAM, so both Gemma 4 builds will partially offload to CPU regardless.
- **D-07:** Ollama runs via **`ollama serve` in a terminal**, not the desktop tray app, for both the benchmark and the demo. Environment pinned: `OLLAMA_HOST=127.0.0.1`, `OLLAMA_NUM_PARALLEL=1`, `OLLAMA_MAX_LOADED_MODELS=1`. Rationale: `docs/PRIVACY.md` §5 lists the tray app's startup update check as an unresolved item — running the daemon directly removes it. Pinning `OLLAMA_HOST` makes the loopback binding deterministic rather than defaulted. Serialising requests keeps peak-RAM measurements from being confused by a concurrent model load. The same command serves the T15 offline test and the T16 loopback test.
- **D-08:** **Strict failure rule.** If any candidate tag is missing from the registry, or no Gemma-class candidate answers usefully within the time budget, invoke the hour-3 checkpoint immediately: **cut scope to summary + clause lookup only**. Do **not** substitute `gemma2:2b` (gate L1-L4 requires the Gemma 3n/4 class; a substitution is a gate failure disguised as a workaround). Do **not** add a second runtime such as llama.cpp. Do **not** swap in any other model family. Record the trigger and the decision in `docs/benchmarks.md`.
- **D-09:** After the selection is recorded, **prune the two non-selected models with `ollama rm` on every machine.** Consequence to respect: the benchmark table must be complete and committed *before* pruning, because re-measuring a recorded figure requires re-downloading a multi-GB model mid-window.

**Embedding setup and offline proof**
- **D-10:** `scripts/download_embedding_model.py` populates `models/all-MiniLM-L6-v2/` by calling `SentenceTransformer('all-MiniLM-L6-v2')` and then `.save('models/all-MiniLM-L6-v2')`. The saver and the loader are the same code path, so the on-disk file set (including `modules.json` and the pooling config) is exactly what `retrieval.py` will look for, by construction. `torch`/`transformers` are already required by the locked stack, so this adds no new dependency. Setup runs online with no user document involved; operation runs offline.
- **D-11:** **PRIV-03 is proven by an automated test**, not by assertion: `tests/test_embedding_offline.py` must (a) assert the local directory's file set is **complete** — `config.json`, `modules.json`, tokenizer files, model weights — *before* attempting a load, then (b) load with `HF_HUB_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1` and embed a fixed sentence. The completeness check is the point: a partial download leaves a directory that exists but is incomplete, which is the most likely false pass. This complements, and does not replace, the Phase 6 Wi-Fi-off evidence run in `docs/PRIVACY.md` §7.
- **D-12:** **PRIV-04 is verified in Phase 1** by a static test in `tests/` asserting `config.OLLAMA_URL` is loopback and `config.EMBED_MODEL_PATH` is a local relative path, **plus** a Phase 1 capture of `netstat -ano | findstr 11434` showing `127.0.0.1` rather than `0.0.0.0`. The capture is an early draft of test T16. The full `tests/test_no_network.py` regex test over `src/` and `app.py` described in `docs/TEST_PLAN.md` §5 stays in Phase 2/3, where it has a real source tree to scan.

**Git and push convention**
- **D-13:** **Push directly to `main` after every commit.** The remote is already configured: `origin` → `https://github.com/ZERODAY-2026/Phoenix.git`. This intentionally overrides two existing rules: `docs/TEAM_ROLES_AND_CONTRACTS.md` §2 (R4 deliverable 1, "no direct pushes to `main`") and `docs/GIT_WORKFLOW.md` §4 (push to role branches `r1-model`/`r2-retrieval`/`r3-answer`/`r4-ui`, then open a PR merged by a teammate). Those documents should be reconciled with this decision rather than left contradicting it.
- **D-14:** Outstanding at context time: `main` is 6 commits ahead of `origin/main`. The planning commits (initialize project, config, research, requirements, roadmap, AGENTS.md) have never been pushed. This backlog must be pushed before the after-every-commit rule starts producing value.

### the agent's Discretion
- **D-10** and **D-11** above were explicitly deferred to the agent's judgement by the user and decided as written. They are locked decisions now, not open questions.
- **Not discussed — deliberately left to planning:** the **BENCH-02 measurement method**. The user chose not to open the "Benchmark harness & measurement" gray area, so nothing here specifies whether the six BENCH-02 metrics come from a scripted harness or a hand-recorded table, what the benchmark prompt set is or how large it is, how "quote accuracy %" is computed in Phase 1 before the Phase 3 substring verifier exists, or how many runs per model. `gsd-phase-researcher` and `gsd-planner` own that decision. Constraints they must respect: the six metrics in BENCH-02 are fixed deliverables; the selection criteria in `docs/PROJECT_MASTER.md` §7.3 (loads on CPU-only 16 GB, <2 min response, >90% JSON validity, tie-break on quote accuracy) are fixed; the whole phase must fit the 1.5-hour slice in `docs/PROJECT_MASTER.md` §11; and D-09 requires the table to be complete and committed before pruning.

### Deferred Ideas (OUT OF SCOPE)
- Reconciling `docs/GIT_WORKFLOW.md` §4 and `docs/TEAM_ROLES_AND_CONTRACTS.md` §2 with the direct-to-`main` push decision (D-13). The documents currently contradict the agreed workflow. Not a Phase 1 code task, but it must be corrected before the submission pack is assembled in Phase 6.
- Adding a `models/README.md` or `.gitkeep` so the gitignored `models/` directory has a documented shape. Nice-to-have, no owner yet.
- A machine-readable benchmark artifact (`docs/benchmarks.json`/`.csv`) so the Phase 5 README table is generated from data rather than retyped. Considered and not chosen for Phase 1 (D-04 records the simpler variant); revisit if the benchmark table has to be regenerated.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| BENCH-01 | Benchmark Gemma candidates (3n E2B, 4 E2B, 4 E2B-QAT) on same fictional lease with network disabled | All three tags **verified to exist** on the Ollama library with sizes (§Standard Stack → Models). D1 lease spec in `docs/TEST_PLAN.md` §1 becomes the single fixture (D-05). Harness in `### Pattern 2`. |
| BENCH-02 | Record model size, peak RAM/VRAM, TTFT, tokens/sec, JSON validity %, quote accuracy % | Exact instrumentation per metric verified against the Ollama HTTP API (`/api/tags` `size`, `/api/ps` `size_vram`, `/api/generate` `eval_count`/`eval_duration`, streaming first-chunk for TTFT). Harness design, prompt set size, and the quote-accuracy algorithm (pre-Verifier) specified in `### Pattern 2` and `## Open Questions` Q1–Q4. |
| BENCH-03 | Choose model meeting criteria: loads on 16GB CPU laptop, <2 min response, >90% JSON validity | Selection rule is fixed (`docs/PROJECT_MASTER.md` §7.3). Research supplies the decision procedure, the machine that must pass (CPU-only 16 GB, per D-06), and the granularity caveat that with a small prompt set ">90%" collapses to "all prompts valid". |
| PRIV-03 | Local embedding model loaded from disk with `HF_HUB_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1` | `SentenceTransformer(local_path)` + `save_pretrained()` verified from SBERT + Hugging Face docs. Required-file-set assertion list derived. Test design in `### Pattern 3`. |
| PRIV-04 | Ollama bound to `127.0.0.1` only; no LAN serving in submitted demo | `OLLAMA_HOST=127.0.0.1` pinned at `ollama serve` launch (D-07); evidence via `netstat -ano \| findstr 11434` and `/api/ps`. Static test in `### Pattern 3` (D-12). |
</phase_requirements>

---

## Summary

Phase 1 is overwhelmingly **execution against an already-written specification**, not design work. Nine `docs/` documents and five `.planning/research/` documents fix the stack, the contracts, the privacy model, the test plan and the timeline. The research contribution here is therefore narrow but high-leverage: (a) confirm the three Gemma tags actually exist and what they actually weigh, (b) pin down exactly how to measure the six BENCH-02 metrics from the Ollama HTTP API, and (c) surface environment facts that would otherwise derail the 1.5-hour slice.

Three findings materially change the plan:

1. **Download time, not generation time, is the scarce resource.** The three candidates total roughly **16.4 GB** on disk (`gemma3n:e2b` 7.8 GB + `gemma4:e2b` 4.6–7.5 GB + `gemma4:e2b-it-qat` 4.3 GB). On hackathon Wi-Fi that can consume most of the 1.5-hour window. The plan must fire all pulls first, in the background, on **both** D-06 machines, and do the repo/skeleton/lease/embedding work while they download.

2. **The pins in `.planning/research/STACK.md` are not installable on this machine's default Python.** `numpy==1.26.4` supports Python 3.9–3.12 only; the dev box defaults to **Python 3.14.2**. `sentence-transformers==3.0.1` dates from mid-2024. Python **3.11** is installed and is the safe venv target (README already promises "Python 3.11+"). Current upstream versions were verified this session and are recorded in `## Standard Stack`.

3. **`agentic.py` at the repo root is a submission blocker.** It contains `MODEL_NAME = "gemma2:2b"` — the model `docs/PROJECT_MASTER.md` §2 correction #1 bans — plus network code (`requests`, `urllib`, `urlsplit`). `docs/SUBMISSION_CHECKLIST.md` §F requires `grep -rni gemma2 .` to return nothing. It must be deleted (or quarantined) in Phase 1.

**Primary recommendation:** Run Phase 1 as a **pull-first, harness-driven** slice: start background `ollama pull` for all three tags on both machines as step one; build the skeleton, D1 lease and embedding download while they land; then run one **scripted** `scripts/benchmark.py` harness per model per machine that emits a markdown row directly into `docs/benchmarks.md`; then pick the model on the CPU-only machine's numbers, record it in `config.py` + `PROJECT_MASTER.md` §7.3, commit, and only then `ollama rm` the losers (D-09).

---

## Architectural Responsibility Map

Phase 1 is single-tier by nature (one laptop, one localhost daemon), so the usual browser/API/database split collapses. The meaningful mapping is **which layer owns each capability**, with the critical rule that model choice lives in code, not in prose.

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Model runtime (inference) | **Local daemon (Ollama, loopback)** | — | Only process that loads weights; bound to `127.0.0.1` (PRIV-04). |
| Model selection lock | **Config module (`src/config.py`)** | Docs (`docs/benchmarks.md` evidence, `docs/PROJECT_MASTER.md` §7.3 record) | D-04: `config.MODEL_NAME` is the single source of truth; docs are evidence, not configuration. |
| Ollama transport (HTTP) | **LLM client module (`src/llm.py`)** | — | The only file permitted to contain network code (`TEAM_ROLES` §4 rule 5). |
| Benchmark measurement | **Repo-local script (`scripts/benchmark.py`)** | Doc table (`docs/benchmarks.md`) | Reproducibility (PIT-15); script emits the table so numbers are defensible. |
| Embedding provisioning | **Setup script (`scripts/download_embedding_model.py`)** | — | Online, one-time, no user document (`PRIVACY.md` §6). |
| Embedding load (offline) | **Local filesystem (`models/all-MiniLM-L6-v2/`)** | Test (`tests/test_embedding_offline.py`) | PRIV-03 proven by asserting the on-disk file set then loading with networking off. |
| Loopback / offline policy | **Static test + captured command output** | Docs (`docs/evidence/`) | PRIV-04: a code assertion in `tests/` plus `netstat` evidence. |
| Benchmark fixture (D1 lease) | **Repo asset (`sample_documents/`)** | — | Written once, reused by Phase 2 ingestion tests (D-05). |

**Anti-misassignment to watch:** the benchmark is **not** a UI or pipeline capability. It must not import `streamlit`, `ingest.py` or `retrieval.py`, and it must not depend on `answer.py`. It talks to Ollama directly through the same HTTP shape `src/llm.py` uses. Keeping that boundary makes Phase 1 deliverable without any Phase 2/3 code existing.

---

## Standard Stack

### Core

| Library / Tool | Verified version | STACK.md pin | Purpose | Why this one |
|---------------|------------------|--------------|---------|--------------|
| Python (venv interpreter) | **3.11** available via `py -3.11`; 3.13 also present; **3.14.2 is the default** | "3.11+" | Runtime for all repo code | 3.11 satisfies the approved pins; 3.14 does not (§Pitfall 1). |
| Ollama (external daemon) | latest release; version must be recorded in README | `0.20+` (unverified) | Local Gemma runtime on `127.0.0.1:11434` | MIT, single binary, HTTP API with built-in timing stats. |
| streamlit | 1.66.0 latest (1.38.0 is the pin) | 1.38.0 | UI (Phase 4) | Telemetry off + loopback bind already configured. |
| pdfplumber | 0.11.10 latest (0.11.4 is the pin) | 0.11.4 | PDF text + page numbers (Phase 2) | MIT vs PyMuPDF AGPL. |
| sentence-transformers | 6.1.0 latest (3.0.1 is the pin) | 3.0.1 | Local MiniLM embeddings | `SentenceTransformer(local_path)` verified to load from disk. |
| numpy | 2.5.4 latest (1.26.4 is the pin) | 1.26.4 | Cosine similarity | 1.26.4 excludes Python ≥3.13. |
| requests | 2.34.2 latest (2.32.3 is the pin) | 2.32.3 | Only localhost HTTP client | Sole network code path. |
| pytest | 9.1.1 latest (8.3.2 is the pin) | 8.3.2 | Test runner | Standard. |

### Models (candidates) — **verified against `ollama.com/library` on 2026-10-18**

| Candidate | Tag | Verified size | Context | Notes |
|-----------|-----|---------------|---------|-------|
| Gemma 3n E2B | `gemma3n:e2b` | **7.8 GB** | 32 K | Updated 3 days ago. **Largest of the three.** No native `system` role. No QAT tag exists for gemma3n. |
| Gemma 4 E2B | `gemma4:e2b` | **4.6–7.5 GB** (range — actual size depends on the variant the tag resolves to; record `ollama list`) | 128 K | Updated 2 weeks ago. Native `system` role. Has a thinking mode. |
| Gemma 4 E2B QAT | `gemma4:e2b-it-qat` | **4.3 GB** | 128 K | Updated **4 months ago** — an older snapshot than `gemma4:e2b`. Smallest download. |
| *(context)* Gemma 4 E2B q4_K_M | `gemma4:e2b-it-q4_K_M` | 4.6 GB | 128 K | Same family, non-QAT quant; a legitimate extra row if a 4th point is wanted. Out of the three required. |
| *(context)* Gemma 4 E4B | `gemma4:e4b` | 6.6–9.5 GB | 128 K | Only per `PROJECT_MASTER` §7.1 if E2B quality is poor. Not a Phase 1 requirement. |

`docs/PROJECT_MASTER.md` §7.1's reported figures are now **confirmed and corrected**: `gemma4:e2b` is a 4.6–7.5 GB range (not a flat 7.2 GB), `gemma4:e2b-it-qat` is 4.3 GB, and `gemma3n:e2b` is 7.8 GB (previously "verify after pull").

### Supporting — external tools (not pip)

| Tool | Purpose | Notes |
|------|---------|-------|
| `ollama serve` (env-pinned) | Daemon with deterministic loopback binding | `OLLAMA_HOST=127.0.0.1`, `OLLAMA_NUM_PARALLEL=1`, `OLLAMA_MAX_LOADED_MODELS=1` (D-07). Must be set in the launching shell **before** `ollama serve`. |
| `netstat` / `Get-NetTCPConnection` | PRIV-04 loopback evidence | `netstat -ano \| findstr 11434` must show `127.0.0.1`. |
| `Get-Process` / Task Manager | Peak RAM measurement | Windows process working set for the Ollama runner. |
| `nvidia-smi` | VRAM cross-check on the RTX 2050 | Only on the GPU laptop. |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|-----------|-----------|----------|
| Scripted harness `scripts/benchmark.py` | Hand-recorded table with a stopwatch | Rejected: `docs/PITFALLS.md` PIT-15 explicitly lists manual stopwatch as the warning sign for non-reproducible benchmark numbers. A script is the only way "the numbers say otherwise" (PITFALLS PIT-15, rubric "Gemma integration" 10 pts) is defensible. |
| Python 3.11 venv with the approved pins | Python 3.13/3.14 venv with current upstream versions | Rejected for Phase 1: `sentence-transformers` 6.x carries documented breaking changes, and nothing needs the newer versions. Use 3.11 for the least validation surface. |
| `ollama ps SIZE` as the peak-RAM figure | `/api/ps size_vram` + OS process working set | Rejected: Ollama over-reports SIZE for mmap'd models (see Pitfall 3). `ollama ps SIZE` may be quoted for model residency but must not be the RAM number. |
| A 4th "aggregate quality score" | Report the six fixed metrics | Rejected: BENCH-02 fixes the metric list; inventing a composite muddies the decision record. |

**Installation (recommended shape — pins resolved at execution time):**

```bash
# In the repo, on each benchmark machine
py -3.11 -m venv .venv
.venv\Scripts\activate                 # Windows; source .venv/bin/activate elsewhere
python -m pip install -r requirements.txt
```

`requirements.txt` is currently an **unpinned placeholder** (it lists direct deps with no versions) and is a Phase 1 deliverable to pin (README/S3/DOCS-01). Sequence: install, verify the app imports, then `pip freeze > requirements.txt` and trim.

**Version verification (run before writing the version table):**

```bash
python -m pip index versions streamlit
python -m pip index versions pdfplumber
python -m pip index versions sentence-transformers
python -m pip index versions numpy
python -m pip index versions requests
python -m pip index versions pytest
```

Verified this session on 2026-10-18: `streamlit 1.66.0`, `pdfplumber 0.11.10`, `sentence-transformers 6.1.0`, `numpy 2.5.4` (2.4.2 already installed on the system interpreter), `requests 2.34.2` (2.33.1 installed), `pytest 9.1.1` (9.1.1 installed).

---

## Package Legitimacy Audit

> Every package below installs in Phase 1, so the gate applies.

```bash
gsd-tools query package-legitimacy check --ecosystem pypi streamlit pdfplumber sentence-transformers numpy requests pytest
```

| Package | Registry | Latest publish | Downloads signal | Source repo | Verdict | Disposition |
|---------|----------|----------------|------------------|-------------|---------|-------------|
| streamlit | PyPI | 2026-10-14 | unknown (seam) | streamlit.io | **SUS** | Approved — see note |
| pdfplumber | PyPI | 2026-06-15 | unknown (seam) | github.com/jsvine/pdfplumber | **SUS** | Approved — see note |
| sentence-transformers | PyPI | 2026-09-18 | unknown (seam) | SBERT.net | **SUS** | Approved — see note |
| numpy | PyPI | 2026-10-10 | unknown (seam) | none listed by seam | **SUS** | Approved — see note |
| requests | PyPI | 2026-05-14 | unknown (seam) | github.com/psf/requests | **SUS** | Approved — see note |
| pytest | PyPI | 2026-06-19 | unknown (seam) | github.com/pytest-dev/pytest | **SUS** | Approved — see note |

**Packages removed due to `SLOP` verdict:** none.
**Packages flagged as suspicious `SUS`:** all six — but **these are seam false positives and must be recorded as such, not converted into blocking checkpoints.**

**Why the `SUS` verdicts are not substantiated (stated so the planner can justify keeping them):**

- The seam's reasons were uniformly `unknown-downloads` (plus `too-new` for streamlit / sentence-transformers / numpy, and `no-repository` for numpy). The reason `too-new` is derived from the **latest release publish date**, not the package's age — every one of these has shipped continuously for a decade or more.
- `unknown-downloads` means the seam had **no PyPI download data**, not that downloads are low. These six are among the most-installed packages on PyPI.
- Every package is listed in the project's own pre-approved stack (`.planning/research/STACK.md`, `AGENTS.md` "Technology Stack", `docs/PROJECT_MASTER.md` §5) and has an official upstream home.

**Recommended planner treatment:** approve all six, add **no** `checkpoint:human-verify` tasks, and record this paragraph (and the raw seam output) in `docs/privacy_audit.md` under the dependency audit required by `docs/PRIVACY.md` §10. If a reviewer wants belt-and-braces, a single task "record the six packages' upstream URLs and licences in `docs/privacy_audit.md`" satisfies C4 and the S3/DOCS-01 deliverable without blocking the 1.5-hour slice.

**Not run through the gate (correctly):** `torch` and `transformers` arrive transitively via `sentence-transformers`. They are large and must be named in the dependency audit (`docs/PRIVACY.md` §10 singles out `sentence-transformers`/`transformers`/`huggingface_hub` for first-use downloads). Do not add them as direct pins unless `pip freeze` puts them there.

---

## Architecture Patterns

### System Architecture Diagram

Data flow for the whole phase. Solid arrows are Phase 1 scope; the dashed arrow is explicitly **not** built here.

```
                            SETUP (internet ON, no user document) — PRIVACY.md §6
                    ┌──────────────────────────────────────────────────────────────────┐
                    │  pip install (venv 3.11)          ollama pull x3  (≈16.4 GB)     │
                    │        │                                │                        │
                    │        v                                v                        │
                    │  .venv/ (pinned)              ~/.ollama/models/blobs  <── background, start FIRST
                    │                                       │                            │
                    │  scripts/download_embedding_model.py  │  (online, one-time)        │
                    │        │                              │                            │
                    │        v                              │                            │
                    │  models/all-MiniLM-L6-v2/  ───────────┼────────────┐               │
                    └────────────────────────────────────────┼────────────┼───────────────┘
                                                             │            │
     ─────────────────────────  OPERATION (internet OFF) ────┼────────────┼──────────────
                                                             │            │
  launch:  OLLAMA_HOST=127.0.0.1 OLLAMA_NUM_PARALLEL=1        │            │
           OLLAMA_MAX_LOADED_MODELS=1  ollama serve            │            │
                    │                                        │            │
                    v                                        v            v
        ┌───────────────────────┐              ┌──────────────────────────────┐
        │  Ollama HTTP daemon   │              │ tests/test_embedding_offline │
        │  127.0.0.1:11434      │              │  (a) assert file set complete│
        │  GET /api/tags  ──────┼── size ──┐   │  (b) HF_HUB_OFFLINE=1        │
        │  GET /api/ps   ───────┼─ size_vram │   │      TRANSFORMERS_OFFLINE=1 │
        │  POST /api/generate   │   ──┐    │   │  -> embed a fixed sentence   │
        │   stream:true         │     │    │   └──────────────────────────────┘
        │   format:"json"       │     │    │                  │
        │   think:false         │     │    │                  v
        └───────────────────────┘     │    │        PRIV-03 proven
                    ^                 │    │
                    │                 v    v
        ┌───────────┴──────────────────────────────────────┐
        │  scripts/benchmark.py   (R1)                     │
        │   warm-up (load) ──> prompt set (N answerable)   │
        │   per prompt: TTFT, eval_count/eval_duration,    │
        │     json.loads + required-keys,                  │
        │     normalised substring(quote, passage)         │
        │   per model+machine: peak RAM, size_vram, size   │
        └───────────────────┬──────────────────────────────┘
                            │  emits one markdown row per (model, machine)
                            v
                 docs/benchmarks.md  ──> decide ──> src/config.py::MODEL_NAME
                            │                              │
                            │                              v
                            │                   docs/PROJECT_MASTER.md §7.3  "Chosen model: ___"
                            v                              │
                 commit + push (D-09: BEFORE pruning) ──── ─┘
                            │
                            v
                 ollama rm <loser1> <loser2>   on EVERY machine

  ┈┈┈┈ NOT IN PHASE 1 ┈┈┈┈>  ingest.py / retrieval.py / guardrails.py / answer.py / app.py
```

### Recommended Project Structure

```
src/
├── config.py            # D-03 constants; MODEL_NAME single source of truth (D-04)
├── llm.py               # D-02: check_model_ready(), generate(), ModelUnavailable, STUB_LLM=1
└── doc_types/           # already exists (README.md only); untouched in Phase 1
scripts/
├── download_embedding_model.py   # D-10, closes the dangling README step-4 reference
└── benchmark.py                  # BENCH-02 harness (R1) — the open-decision answer
tests/
├── conftest.py                   # offline env vars + sys.path (Wave 0 gap)
├── test_config.py                # PRIV-04 static assertions (D-12)
├── test_llm_stub.py              # STUB_LLM=1 returns fixed valid JSON, no network
└── test_embedding_offline.py     # D-11 / PRIV-03
sample_documents/
├── README.md            # update the D1-D7 table (D-05)
└── D1_clean_lease.pdf   # the benchmark fixture (D-05); .gitignore excepts it
docs/
└── benchmarks.md        # BENCH-02 table + decision record (R1)
models/                  # gitignored; created by the download script
```

> `src/__init__.py` is not named in D-01 but `app.py`'s contract imports read `from src.llm import ...` (`TEAM_ROLES` §3). Namespace packages work on Python 3.11 without it, but add it for explicitness so `import src.config` is unambiguous under pytest.

### Pattern 1: `STUB_LLM=1` backend (D-02) — unblocks the whole team at hour 1

**What:** `generate()` short-circuits before any HTTP call when `os.environ.get("STUB_LLM") == "1"`, returning a fixed string that is *valid JSON in the Answer-dict shape*.
**When to use:** always available; it is the mechanism R2/R3/R4 use to work before a model is chosen, and the mechanism test T13 uses to force invalid output.
**Why the shape matters:** the stub's JSON must satisfy the same validator the benchmark harness uses for "JSON validity", otherwise T13 cannot be built on top of it.

```python
# Source: docs/TEAM_ROLES_AND_CONTRACTS.md §3 (contract) + docs/ARCHITECTURE.md §4 (schema)
import os, json, requests

class ModelUnavailable(Exception): ...

def check_model_ready() -> tuple[bool, str]:
    """(ok, message). Tries Ollama on OLLAMA_URL and checks MODEL_NAME exists."""
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=REQUEST_TIMEOUT_S)
        r.raise_for_status()
        names = {m["name"] for m in r.json().get("models", [])}
    except Exception as exc:
        return False, f"Ollama is not reachable at {OLLAMA_URL} ({exc}). Start it with: ollama serve"
    if MODEL_NAME not in names:
        return False, f"Model {MODEL_NAME!r} is not installed. Run: ollama pull {MODEL_NAME}"
    return True, "ready"

_STUB = json.dumps({
    "status": "answered",
    "question": "stub",
    "findings": [{
        "category": "deadline", "kind": "explicit",
        "plain_language": "Stub explanation produced without a model.",
        "quote": "the deposit shall be returned within thirty (30) days",
        "passage_id": "p3-c2", "page": 3, "uncertainty": "none",
    }],
    "passages": [], "jurisdiction_note": "", "escalation": "",
    "dropped_findings": 0, "message": "",
})

def generate(system: str, prompt: str, json_mode: bool = True) -> str:
    """Raises ModelUnavailable on any failure. STUB_LLM=1 returns fixed valid JSON."""
    if os.environ.get("STUB_LLM") == "1":
        return _STUB
    payload = {
        "model": MODEL_NAME, "system": system, "prompt": prompt,
        "stream": False, "format": "json" if json_mode else None,
        "think": False,                     # Gemma 4 thinking mode OFF (see Pitfall 2)
        "keep_alive": "5m",
        "options": {"temperature": 0},
    }
    ...
```

> Note: `"format": None` should be omitted from the payload rather than sent as JSON `null`. `json_mode=False` is needed by test T13 to provoke unparseable output.

### Pattern 2: The BENCH-02 Harness — **the researcher-owned decision**

**What:** one script, `scripts/benchmark.py`, that measures all six BENCH-02 metrics for one (model, machine) pair and prints/appends a markdown row to `docs/benchmarks.md`.
**When to use:** once per candidate per D-06 machine, after the model has been pulled and the harness itself is written.

**Prompt set — recommendation: the 8 answerable prompts from `docs/TEST_PLAN.md` §3.**
Rationale: BENCH-02's JSON-validity and quote-accuracy metrics only make sense for prompts that *ask the model to produce findings*. In Phase 3, silent / verdict / out-of-scope behaviour is **code-enforced before the model is called** (`docs/ARCHITECTURE.md` §3.2) — so including those questions in the Phase 1 denominator would measure a behaviour the model is never asked to deliver in production. The 8 answerable prompts are:

| # (TEST_PLAN §3) | Question | D1 clause exercised |
|---|---|---|
| 1 | How much is the monthly rent and when is it due? | rent |
| 2 | How long does the landlord have to return the deposit? | deposit (30 days) |
| 3 | How much notice do I need to give to end the lease? | notice (2 months) |
| 4 | What happens if I pay rent late? | late fee |
| 5 | Can I keep a pet? | pets |
| 6 | Who pays for repairs to the plumbing? | repairs |
| 16 | Summarise the termination conditions | termination |

That is 7 numbered above plus one of {7, 9, 10} chosen once D1's text exists (sublet / utilities / rent increase) → **N = 8**. Every D1 topic named in `docs/TEST_PLAN.md` §1 is exercised, so the set is principled rather than arbitrary.

**Each prompt is written before the run** (as `docs/TEST_PLAN.md` §3 already instructs) as a triple: `(question, passage_id, passage_text)`, where `passage_text` is a verbatim excerpt copied out of D1. The harness embeds `passage_text` into the prompt using the `<<<DOCUMENT_PASSAGE id="..." page="...">>>` wrapper from `docs/ARCHITECTURE.md` §5. This is what makes quote accuracy computable in Phase 1 without `retrieval.py`.

**Metric-by-metric instrumentation (all verified against Ollama's documented API):**

| BENCH-02 metric | How the harness gets it | Source of truth |
|---|---|---|
| Model file size on disk | `GET /api/tags` → `models[].size` (bytes) for the tag; cross-check `ollama list`. Also record `digest` and `details.quantization_level`. | Verified: `docs.ollama.com` / `docs/api.md` |
| Peak RAM | Windows: sample the Ollama runner process working set (`Get-Process` filtered to the `ollama` runner) during and immediately after generation; take the max over the run. | Windows OS; **not** `ollama ps SIZE` (Pitfall 3) |
| Peak VRAM | `GET /api/ps` → `models[].size_vram` (bytes resident in GPU memory). On the RTX 2050 cross-check with `nvidia-smi`. On a CPU-only machine expect 0. | Verified: `docs.ollama.com/api/ps` |
| Time to first token (TTFT) | `stream: true`; timestamp the request send, then timestamp the first streamed chunk whose `response` is non-empty. **Warm-up first** (see below) so model load is not counted. | `docs/api.md` streaming semantics |
| Tokens per second | Final stream object: `tok_s = eval_count / eval_duration * 1e9` (durations are nanoseconds and `/api/generate` explicitly documents this division). | Verified: `docs/api.md` |
| JSON validity % | `json.loads(response)` succeeds **and** the parsed object carries the Answer-dict shape: top-level `status` + `findings`, and each finding has `category`, `kind`, `plain_language`, `quote`, `passage_id`, `page`, `uncertainty` (from `docs/ARCHITECTURE.md` §4). | `docs/ARCHITECTURE.md` §4 defines "valid JSON" for this project |
| Quote accuracy % | For every returned finding, normalise `quote` and `passage_text` (collapse whitespace, casefold) and test `quote in passage_text`. Report `verified_findings / total_findings` **and** `prompts_with_≥1_verified_finding / N`. | `docs/ARCHITECTURE.md` §3.2 step `verify_findings` — same algorithm, 1-line scale |

**Warm-up (non-negotiable for comparable numbers):** before measuring, issue one call to load the model (the API supports an empty prompt purely to load it). `total_duration` includes `load_duration`, so an unwarmed first call inflates TTFT by seconds-to-minutes and makes the three candidates incomparable — and disk-cached models would appear artificially fast.

**Request shape (identical for every candidate except `model`):**

```json
{
  "model": "<tag>",
  "system": "<docs/ARCHITECTURE.md §5 system prompt>",
  "prompt": "<wrapped passages + question + schema instruction>",
  "stream": true,
  "format": "json",
  "think": false,
  "keep_alive": "5m",
  "options": { "temperature": 0, "num_ctx": 8192 }
}
```

**Runs per model:** 1 warm-up (excluded) + **1 measured pass** over the 8 prompts. Do not average multiple passes at 3×2×8 = 48 generations inside a 1.5-hour slice; instead report single-pass figures and state the caveat, and spend any leftover time on a **second confirmation pass of the winner on the designated demo machine** (which D-06 requires anyway).

**Granularity caveat the harness must print into `docs/benchmarks.md`:** with `N = 8`, the fixed threshold ">90% JSON validity" is only satisfiable at 8/8 = 100 % (7/8 = 87.5 % fails). Quote the exact N and say so, otherwise a reader will assume the 20-prompt figure in `docs/PROJECT_MASTER.md` §7.2. If the team wants finer resolution, raise N to 10 and accept 10/10.

**Time budget (why the order below is the recommendation):** pulls ≈ 16.4 GB dominate. 48 generations at a CPU worst case of ~60 s ≈ 48 min. Repo + skeleton + lease + embedding work ≈ 15–25 min of human time that overlaps the downloads. Hence:

| Order | Action | Runs during |
|---|---|---|
| 1 | On **both** D-06 machines: install Ollama, launch `ollama serve` with the D-07 env, fire all three `ollama pull` in the background | downloads |
| 2 | Verify `.gitignore` + `.streamlit/config.toml` (already correct — verify, do not recreate); delete/quarantine `agentic.py`; create `src/config.py`, `src/llm.py` (stub), `scripts/`, `tests/` skeletons; `py -3.11 -m venv .venv` + install | downloads |
| 3 | Write D1 lease; update `sample_documents/README.md` | downloads |
| 4 | `python scripts/download_embedding_model.py` (≈90 MB) | downloads |
| 5 | Write `scripts/benchmark.py` + the pre-written prompt set | downloads |
| 6 | Run the harness per model per machine; fill `docs/benchmarks.md` | downloads done |
| 7 | Apply §7.3 on the **CPU-only** numbers → set `config.MODEL_NAME`, write the §7.3 record line, **commit + push** | — |
| 8 | `ollama rm` the two losers on every machine (D-09) | — |

### Pattern 3: Offline-proof tests (D-11, D-12)

**What:** the two automated tests that turn PRIV-03 and PRIV-04 from claims into evidence.
**When to use:** from the first commit; they are the guard rails `docs/PITFALLS.md` PIT-03 needs.

```python
# tests/test_config.py  -- PRIV-04 (D-12), no network, no model
from urllib.parse import urlsplit
from src import config

def test_ollama_url_is_loopback():
    host = urlsplit(config.OLLAMA_URL).hostname
    assert host in {"127.0.0.1", "localhost", "::1"}, f"OLLAMA_URL is not loopback: {config.OLLAMA_URL}"

def test_embed_model_path_is_local_relative():
    p = config.EMBED_MODEL_PATH
    assert not p.startswith(("/", "\\")) and ":" not in p, f"EMBED_MODEL_PATH is not a local relative path: {p}"
```

```python
# tests/test_embedding_offline.py  -- PRIV-03 (D-11)
import os, pathlib, pytest

MODEL_DIR = pathlib.Path("models/all-MiniLM-L6-v2")
# The set that makes the directory loadable *and* complete. A partial download
# (e.g. weights without modules.json) is the most likely false pass.
REQUIRED = ["config.json", "modules.json", "model.safetensors", "tokenizer.json", "tokenizer_config.json"]

pytestmark = pytest.mark.skipif(
    not MODEL_DIR.is_dir(),
    reason="models/all-MiniLM-L6-v2/ absent - run: python scripts/download_embedding_model.py (online, one-time)",
)

def test_local_model_dir_is_complete():
    missing = [f for f in REQUIRED if not (MODEL_DIR / f).exists()]
    assert not missing, f"Embedding model directory is incomplete, missing: {missing}"

def test_loads_and_embeds_with_networking_off(monkeypatch):
    monkeypatch.setenv("HF_HUB_OFFLINE", "1")
    monkeypatch.setenv("TRANSFORMERS_OFFLINE", "1")
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(str(MODEL_DIR))     # local path => no Hub lookup
    vec = model.encode(["The deposit shall be returned within thirty days."])
    assert vec.shape[0] == 1 and vec.shape[1] == 384
```

> The `skipif` is a deliberate choice: a fresh clone has no `models/` (it is gitignored), so a hard failure would break `pytest` for a judge before setup. The **evidence** for PRIV-03 is the recorded passing run in `docs/TEST_RESULTS.md`, not the mere existence of the test. Flag this to the planner as a small explicit decision.

### Anti-Patterns to Avoid

- **Recreating `.gitignore` or `.streamlit/config.toml`.** Both already exist and already satisfy success criterion 1 (`gatherUsageStats = false`, `server.address = "127.0.0.1"`, `headless = true`). Task is *verify*, not *write* — and `docs/PROJECT_MASTER.md` §2 correction #9 is specifically about `.gitignore` being written with `echo` on Windows. Do not touch it.
- **Recording a benchmark figure from a warmed-up-vs-cold comparison.** Model load (`load_duration`) must be excluded from TTFT or the numbers are meaningless.
- **Using `ollama ps SIZE` as the RAM figure.** See Pitfall 3.
- **Measuring JSON validity with `format` unset.** With `format: "json"` the server constrains output to well-formed JSON for *every* model, which makes the metric weakly discriminating at the top end; without it the metric does not reflect production. Measure *in the production configuration* (`format: "json"` + system prompt + schema instruction) and be explicit in `docs/benchmarks.md` that the metric discriminates mainly on **schema conformance and required keys**, not on raw parseability.
- **Letting the benchmark import the app.** `scripts/benchmark.py` must not import `streamlit`, `ingest`, `retrieval`, `guardrails` or `answer` — those do not exist yet and importing them would couple Phase 1 to Phase 2/3.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Tokens/second timing | `time.time()` around the whole request | Ollama's `eval_count` / `eval_duration` | Server-side counters exclude queueing and network jitter and are the documented method. |
| JSON validity check | A regex for "does it look like JSON" | `json.loads` + required-keys assertion against `docs/ARCHITECTURE.md` §4 | `format: "json"` already guarantees parseability; the failure mode is *missing keys*, which only a schema check catches. |
| VRAM measurement | A hand-written estimate from model file size | `GET /api/ps` → `size_vram` | The daemon reports the real resident byte count. |
| Peak RAM | `ollama ps SIZE` | OS process working set | Ollama double-counts mmap'd weights (Pitfall 3). |
| Offline enforcement | An `if` that checks whether the network is up | `HF_HUB_OFFLINE=1` + `TRANSFORMERS_OFFLINE=1` + `local_files_only` | Library-native switches fail closed at the HTTP layer; a manual check fails open. |
| Embedding model packaging | Copying files out of the Hugging Face cache by hand | `SentenceTransformer(name).save_pretrained(dir)` (D-10) | Saver and loader are the same code path, so the on-disk shape is correct by construction. |
| Loopback binding proof | A comment in the README | `netstat -ano \| findstr 11434` capture + `tests/test_config.py` | Gate L9 wants evidence, not assertion (`docs/PRIVACY.md` §3, §7). |

**Key insight:** in this phase almost every "build it yourself" instinct is a correctness regression. The only genuinely custom artifact worth writing is `scripts/benchmark.py`, and even that should compose Ollama's own stats rather than reinvent timing.

---

## Common Pitfalls

### Pitfall 1: The pinned stack does not install on the machine's default Python
**What goes wrong:** `pip install -r requirements.txt` fails or resolves to a stack nobody verified, because the dev box defaults to **Python 3.14.2** while `.planning/research/STACK.md` pins `numpy==1.26.4` (Python ≤ 3.12) and `sentence-transformers==3.0.1`.
**Why it happens:** the pins were chosen from training-time knowledge and the machine was upgraded since. `torch` 2.12 does publish cp314 wheels and the torchvision matrix covers ≤ 3.14, so 3.14 is *possible* — but only with newer numpy/sentence-transformers than the approved pins name.
**How to avoid:** create the venv with the installed **3.11** (`py -3.11 -m venv .venv`). Resolve the version table once, at execution time, with `python -m pip index versions` (commands in `## Standard Stack`) and record the result in `requirements.txt` and the README requirements table (S3/DOCS-01).
**Warning signs:** `ERROR: Could not find a version that satisfies the requirement numpy==1.26.4`; `sentence-transformers` importing but `torch` failing to load a DLL.

### Pitfall 2: Gemma 4's thinking mode inflates every timing metric
**What goes wrong:** TTFT and tok/s are measured with the model emitting an internal reasoning block, so its numbers are not comparable with Gemma 3n's, and JSON parsing may see reasoning text alongside the object.
**Why it happens:** Gemma 4 enables thinking via a `<|think|>` token and exposes a `think` API parameter; the model family is explicitly "designed as highly capable reasoners, with configurable thinking modes", and the library page also asks for `temperature=1.0, top_p=0.95, top_k=64` as its recommended sampling — all of which differ from a JSON-extraction workload.
**How to avoid:** pass `"think": false` on every benchmark and production request, do not put `<|think|>` in the system prompt, and set `temperature: 0` for JSON extraction. Record the exact request options in `docs/benchmarks.md` so the numbers are reproducible. Note the deliberate divergence from Gemma 4's recommended sampling and say why.
**Warning signs:** response text beginning with `<|channel>thought`; `eval_count` far larger than the JSON payload justifies; TTFT differing by an order of magnitude between candidates with similar sizes.

### Pitfall 3: `ollama ps` over-reports memory (mmap double-count) and fakes a CPU/GPU split
**What goes wrong:** the "peak RAM" figure is roughly double the truth and the CPU/GPU split is wrong, so the benchmark under-rates a candidate or mis-assigns the demo machine.
**Why it happens:** a known, open Ollama issue (`ollama/ollama#16637`): with the default `use_mmap=true`, the runner's `size` includes both the VRAM copy and the mmap'd weights in RAM, and the reported CPU% is derived as `(size − vram) / size`. Disabling mmap collapses `size` to ≈ VRAM with identical actual placement.
**How to avoid:** take VRAM from `/api/ps` `size_vram` and RAM from the OS process working set; treat `ollama ps SIZE` as a residency indicator only. If a suspiciously large SIZE appears, re-run with `options.use_mmap=false` in the request and quote both figures with the explanation.
**Warning signs:** SIZE ≈ 2 × the value in `ollama list`; a "50%/50% CPU/GPU" split on a machine with no discrete GPU; tok/s inconsistent with the reported split (a genuine CPU offload is ~an order of magnitude slower).

### Pitfall 4: Downloads eat the 1.5-hour slice
**What goes wrong:** at hour 1:10 the third candidate is still downloading and the benchmark, the `docs/benchmarks.md` commit, and the D-09 prune all get squeezed or skipped — which then breaks the selection record the whole project depends on.
**Why it happens:** ≈16.4 GB of weights (7.8 + up to 7.5 + 4.3) on shared hackathon Wi-Fi, requested serially after the setup work.
**How to avoid:** pull first, in the background, on both machines, before anything else; do the code/lease/embedding work during the download; if the third candidate has not landed by ~hour 1:00, benchmark the two that have and record the third as "not pulled in budget" — **do not** substitute a model family (D-08).
**Warning signs:** `ollama list` showing one or two tags at 0:45; benchmark start after 1:00.

### Pitfall 5: `agentic.py` is a stale, banned, network-touching file in the repo root
**What goes wrong:** it pins `MODEL_NAME = "gemma2:2b"` — the model `docs/PROJECT_MASTER.md` §2 correction #1 disqualifies — and contains `requests`, `urllib.parse.urlsplit` and an `ipaddress` check. `docs/SUBMISSION_CHECKLIST.md` §F requires `grep -rni gemma2 .` to return nothing, and `docs/PRIVACY.md` §10's audit greps for exactly these imports.
**Why it happens:** it is a leftover from an earlier single-file plan (`rag.py`/`agent.py` were replaced by `src/ingest.py` + `src/answer.py` per `TEAM_ROLES` §1).
**How to avoid:** delete it in Phase 1 (preferred) or move it to a gitignored `tmp/` until the submission pack is assembled. Verify with `grep -rni gemma2 .`.
**Warning signs:** `git ls-files` listing `agentic.py`; the §F grep returning a hit.

### Pitfall 6: `git` and `python`/`pip` invocation traps on this Windows box
**What goes wrong:** `pip` is not on `PATH` (only `python -m pip` works), `nvidia-smi` is not on `PATH`, and `python` resolves to 3.14 unless the venv is activated.
**Why it happens:** per-user Python install (`C:\Users\samru\AppData\Local\Python\pythoncore-3.14-64`) with no `pip.exe` shim, and no NVIDIA driver tools on the CPU-only box.
**How to avoid:** always use `python -m pip`, always activate `.venv` before running, and on the GPU laptop call `nvidia-smi` from its install path (or use `/api/ps` `size_vram` alone, which needs no driver tooling). Do not put `nvidia-smi` on the critical path of a metric.
**Warning signs:** `pip : The term 'pip' is not recognized`; a VRAM column of blanks.

### Pitfall 7: Gemma 3n and Gemma 4 do not treat the system prompt identically
**What goes wrong:** the system-prompt contract in `docs/ARCHITECTURE.md` §5 (untrusted-data framing, "return only JSON", "never say enforceable") is delivered differently to the two families, so the candidates are not measured under equivalent conditions.
**Why it happens:** Gemma 4 "introduces native support for the `system` role"; Gemma 3n (Gemma-3-lineage template) does not, so Ollama injects the system string through a different template slot.
**How to avoid:** verify `check_model_ready()` plus a single JSON-mode call with a system prompt on **each** candidate before the benchmark, and record in `docs/benchmarks.md` the request shape used and whether the system prompt was honoured. If gemma3n ignores or mangles it, say so — that is a genuine reason to prefer Gemma 4, and honest reporting is worth rubric points.
**Warning signs:** gemma3n JSON validity far below the others; gemma3n emitting the system instructions back as content.

---

## Code Examples

### Measure one (model, machine) row with streaming TTFT and Ollama's own counters

```python
# Source: docs.ollama.com/api (generate) + docs.ollama.com/api/ps, verified 2026-10-18
import json, time, requests

def warm_up(base, model):
    """Load the model so load_duration does not pollute TTFT."""
    requests.post(f"{base}/api/generate", json={"model": model, "prompt": ""}, timeout=600)

def run_prompt(base, model, system, prompt, passage_text):
    payload = {
        "model": model, "system": system, "prompt": prompt,
        "stream": True, "format": "json", "think": False, "keep_alive": "5m",
        "options": {"temperature": 0, "num_ctx": 8192},
    }
    t0 = time.perf_counter()
    ttft = None
    text = ""
    stats = {}
    with requests.post(f"{base}/api/generate", json=payload, stream=True, timeout=600) as r:
        r.raise_for_status()
        for line in r.iter_lines():
            if not line:
                continue
            chunk = json.loads(line)
            piece = chunk.get("response", "")
            if piece and ttft is None:
                ttft = time.perf_counter() - t0          # first token, load excluded by warm-up
            text += piece
            if chunk.get("done"):
                stats = chunk                          # eval_count, eval_duration, total_duration, ...
    tok_s = (stats.get("eval_count", 0) / stats["eval_duration"] * 1e9) if stats.get("eval_duration") else None
    return {"text": text, "ttft_s": ttft, "tok_s": tok_s, "stats": stats}

def model_footprint(base, model):
    """VRAM from the daemon; size on disk from /api/tags."""
    ps = requests.get(f"{base}/api/ps", timeout=30).json().get("models", [])
    vram = next((m["size_vram"] for m in ps if m["model"] == model), 0)
    tags = requests.get(f"{base}/api/tags", timeout=30).json().get("models", [])
    t = next((m for m in tags if m["name"] == model), {})
    return {"size_bytes": t.get("size"), "size_vram_bytes": vram,
            "digest": t.get("digest"), "quant": t.get("details", {}).get("quantization_level")}

def is_valid_answer_json(text):
    """Valid JSON == parses AND matches docs/ARCHITECTURE.md section 4."""
    try:
        obj = json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return False
    if not isinstance(obj, dict) or "status" not in obj or "findings" not in obj:
        return False
    required = {"category", "kind", "plain_language", "quote", "passage_id", "page", "uncertainty"}
    return all(isinstance(f, dict) and required <= set(f) for f in obj["findings"])

def quote_is_verbatim(quote, passage_text):
    """The Phase-3 verify_findings algorithm at 1-line scale (docs/ARCHITECTURE.md section 3.2)."""
    norm = lambda s: " ".join(s.split()).casefold()
    return bool(quote) and norm(quote) in norm(passage_text)
```

### The D-07 launch line (pins the loopback binding deterministically)

```bash
# Windows (cmd) — must be set in the same shell that starts the daemon
set OLLAMA_HOST=127.0.0.1
set OLLAMA_NUM_PARALLEL=1
set OLLAMA_MAX_LOADED_MODELS=1
ollama serve

# verify binding before any benchmark run  (PRIV-04 / test T16 early draft)
netstat -ano | findstr 11434        # expect 127.0.0.1:11434, never 0.0.0.0:11434
```

### Provision and then load the embedding model offline (D-10 / PRIV-03)

```python
# scripts/download_embedding_model.py   -- SETUP ONLY: online, no user document
from pathlib import Path
from sentence_transformers import SentenceTransformer

TARGET = Path("models/all-MiniLM-L6-v2")
TARGET.parent.mkdir(parents=True, exist_ok=True)
SentenceTransformer("all-MiniLM-L6-v2").save_pretrained(str(TARGET))
print(f"saved -> {TARGET}")
```

```python
# operation-time load (retrieval.py, Phase 2) -- networking already off
import os
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("models/all-MiniLM-L6-v2")   # local path => no Hub call
```

> D-10 names `.save(...)`; `save_pretrained(...)` is the documented modern equivalent and `.save()` remains an alias in the 3.x line. Either satisfies the intent (saver and loader share a code path) — use `save_pretrained` if the pinned SBERT version is ≥3.1, and record which was used.

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact on Phase 1 |
|---|---|---|---|
| `gemma2:2b` as the local model | Gemma 3n E2B / Gemma 4 E2B (E2B = "effective" 2 B params) | Gemma 4 published ~weeks before this session | `docs/PROJECT_MASTER.md` §2 correction #1 is confirmed correct; `agentic.py`'s `gemma2:2b` is a live hazard (Pitfall 5). |
| Ollama docs on GitHub (`docs/api.md`) | Ollama docs have moved to `docs.ollama.com` (GitHub file now carries a "moving" banner) | current | Cite `docs.ollama.com` in `docs/benchmarks.md`; the GitHub file is still authoritative for `/api/generate` field semantics. |
| Gemma 3-lineage chat template (no native `system` role) | Gemma 4 with native `system` role + configurable thinking | Gemma 4 | Two of the three candidates share one prompt path and one does not (Pitfall 7). |
| `format: "json"` only | `format` accepts a full **JSON schema** | current | A future option: constrain the model to the Answer-dict schema server-side. Out of scope for Phase 1 (`llm.py`'s contract exposes only a `json_mode: bool`), but worth a note. |
| Manual quantisation guessing (`Q4_K_M`) | Vendor-backed **QAT** builds (`-it-qat`) | Gemma 3-era onward | Explains why `gemma4:e2b-it-qat` is a first-class candidate rather than a hack. Note it is a 4-month-old snapshot. |

**Deprecated / outdated in this repo:**
- `agentic.py` — superseded by `src/ingest.py` + `src/retrieval.py` + `src/answer.py` (`TEAM_ROLES` §1). Contains the banned `gemma2:2b`.
- `requirements.txt` placeholder — must be replaced with real pins (DOCS-01/S3).
- `.planning/research/STACK.md` version table — the **choices** hold, the **version numbers** need re-verification (Pitfall 1).

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Ollama must be ≥ ~0.20.0 for Gemma 4 support | Standard Stack, Pitfall 2 | If a current Ollama already supports Gemma 4, "install ≥0.20.0" is harmless; if a *different* floor applies, the pinned README version is wrong. Mitigation is cheap: install the latest release, record `ollama --version`, and confirm all three tags resolve before benchmarking. `[ASSUMED]` — the number was not confirmed from an authoritative source this session. |
| A2 | Gemma 4 E2B does **not** enable thinking unless `<|think|>` or `think:true` is supplied | Pitfall 2 | If thinking defaults on, TTFT/tok-s are inflated and JSON may be malformed until `think:false` is added. Mitigation: pass `think:false` unconditionally and eyeball one raw response. `[ASSUMED]` for the default; the parameter's existence is `[CITED]`. |
| A3 | The `gemma4:e2b` tag resolving to 4.6–7.5 GB means the default is a smaller quant and the `ollama list` figure is what to record | Standard Stack | If the pulled size is at the top of the range, the CPU-only 16 GB machine may be tight; the benchmark will reveal it and `gemma4:e2b-it-qat` (4.3 GB) is the fixed fallback within the allowed set. Low risk: the metric is measured, not assumed. `[CITED: ollama.com/library/gemma4/tags]` + `[ASSUMED]` on interpretation. |
| A4 | ">90% JSON validity" over N=8 means all 8 must pass | Pattern 2 | If the team wanted the 20-prompt resolution from `PROJECT_MASTER` §7.2, the harness would need ~2.5× the generation time. Mitigation: print N and the arithmetic into `docs/benchmarks.md` so the reading is unambiguous. `[ASSUMED]` — the threshold wording is fixed, the resolution is our choice. |
| A5 | The dev box (Ryzen 7 7735HS, 14.8 GB RAM, no visible dGPU) is representative of the CPU-only benchmark machine | Environment Availability | If the actual "CPU-only 16 GB laptop" is a different machine, its numbers will differ and BENCH-03 must be decided on *that* machine (D-06 already requires per-machine rows). `[ASSUMED]` — README's example spec matches this box, but machine identity was not confirmed with the team. |

---

## Open Questions

1. **Should the deployment prompt set serve the 18-question evaluation set, or the 8 answerable prompts?** *(this is the researcher's answer to the CONTEXT §"Not discussed" item)*
   - What we know: `docs/TEST_PLAN.md` §3 lists 18 questions; ~7–10 are answerable, the rest are silent / verdict / jurisdiction / out-of-scope / adversarial.
   - What is unclear: how much of the 18 the team wants exercised in Phase 1.
   - **Recommendation:** 8 answerable prompts for BENCH-02 (all D1 topic areas covered), because silent/verdict routing is code-enforced in Phase 3 and is not a model-quality signal. The full 18 belong to the Phase 3 evaluation set and are run there against the real pipeline.

2. **Harness or hand-recorded table?**
   - What we know: `docs/PROJECT_MASTER.md` §7.2 offers "stopwatch or script timer" and `docs/PITFALLS.md` PIT-15 names the manual stopwatch as the reproducibility warning sign.
   - **Recommendation:** scripted harness (`scripts/benchmark.py`, R1-owned) that emits the markdown row. The only thing recorded by hand is the machine name and the D1 prompt triples.

3. **How many runs per model?**
   - What we know: 3 models × 2 machines × N prompts must fit ~1.5 h *including* ~16.4 GB of downloads.
   - **Recommendation:** 1 warm-up + 1 measured pass over the 8 prompts per (model, machine); one extra confirmation pass only for the winner on the designated demo machine (already required by D-06). Report single-pass caveats explicitly rather than silently averaging.

4. **How is "quote accuracy %" computed before the Phase 3 verifier exists?**
   - What we know: the Phase 3 algorithm is `verify_findings()` — quote must be an exact substring after whitespace/case normalisation (`docs/ARCHITECTURE.md` §3.2, `TEAM_ROLES` §3).
   - **Recommendation:** implement that same normalisation inline in the harness (10 lines, shown in `## Code Examples`), against the *passage supplied in the prompt*. This measures the model's verbatim-copy fidelity, which is exactly what the Phase 3 verifier will measure; it deliberately does **not** measure retrieval quality, which is Phase 2's job. Report both `verified/total findings` and `prompts with ≥1 verified finding`.

5. **Is a `format: <JSON schema>` request worth using instead of `format: "json"`?**
   - What we know: Ollama accepts a full JSON schema in `format`, which would constrain output to the Answer-dict shape server-side.
   - What is unclear: whether it improves or degrades small-model output quality, and it is outside `llm.py`'s frozen `json_mode: bool` contract (D-02).
   - **Recommendation:** do not use it in Phase 1. Note it in `docs/benchmarks.md` as a future lever if JSON validity is poor — and note that changing it would require a contract change (D-02 freezes the signature).

6. **When is the D-09 prune safe?**
   - What we know: D-09 requires the table complete and committed first; re-measuring needs a fresh multi-GB download.
   - **Recommendation:** make the last two steps of the phase strictly ordered — `git push` the commit containing `docs/benchmarks.md` + `config.py` + the §7.3 record, **then** `ollama rm`. A verification step should confirm `git log origin/main --stat` shows `docs/benchmarks.md` before any `ollama rm` runs.

7. **Where do the offline/loopback evidence artifacts live?**
   - What we know: `docs/PRIVACY.md` §11 lists `docs/evidence/`; `docs/evidence/` does not exist yet; `docs/benchmarks.md` and `docs/privacy_audit.md` also do not exist.
   - **Recommendation:** Phase 1 creates `docs/benchmarks.md` (required deliverable) and drops the `netstat` capture under `docs/evidence/` as the T16 early draft. `docs/privacy_audit.md` is R1's full-phase artifact and is listed as a Phase 6 submission item — creating a stub in Phase 1 with the seam's package-legitimacy output is optional and cheap.

---

## Environment Availability

Probed on the development workstation, 2026-10-18. **Note:** the benchmark itself runs on two *other* devices (the RTX 2050 laptop and one CPU-only 16 GB laptop, D-06), so this table describes the dev/agent box, not necessarily either benchmark machine. Treat "Available ✗" items as per-machine setup tasks in the plan.

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| Python 3.11 | venv interpreter for the pinned stack | ✓ (via `py -3.11`) | 3.11 (64-bit) | 3.13 also present; **avoid 3.14.2** for the venv (Pitfall 1) |
| Python (default) | ad-hoc scripts | ✓ | 3.14.2 | — |
| pip | dependency install | ✓ via `python -m pip` | 25.3 | `python -m pip` always; bare `pip` is **not** on `PATH` |
| Ollama | model runtime (BENCH-01/02/03, PRIV-04) | ✗ | — | **None.** Must install on both benchmark machines before anything else. Direct download, MIT. |
| Git | commits/pushes (D-13) | ✓ | 2.53.0.windows.1 | — |
| Node.js | GSD tooling only | ✓ | v24.15.0 | — |
| `nvidia-smi` | VRAM cross-check | ✗ on this box | — | `/api/ps` `size_vram` needs no driver tooling — use it as the primary VRAM source |
| Docker | optional stronger isolation (`PRIVACY.md` §8) | ✗ | — | Not needed: `ollama serve` on loopback is the D-07 approach |
| GPU | faster inference on the RTX 2050 | ✗ on this box | — | CPU-only IS the pass/fail machine for BENCH-03 |
| RAM | BENCH-03 "loads on 16 GB" | ✓ | 14.85 GB physical | — (this box is marginally *under* 16 GB; relevant only as a hint about the real target machine) |
| CPU | inference | ✓ | AMD Ryzen 7 7735HS | — |
| Network (setup only) | pulls, pip, embedding download | ✓ | — | — |
| `models/all-MiniLM-L6-v2/` | PRIV-03 | ✗ (dir absent) | — | Create via `scripts/download_embedding_model.py` (D-10) |
| `scripts/` | BENCH-02, D-10 | ✗ (dir absent) | — | Create in Phase 1 |
| `tests/` | PRIV-03/04 | ✗ (dir absent) | — | Create in Phase 1 |
| `docs/benchmarks.md` | BENCH-02/03 record | ✗ (absent) | — | Create in Phase 1 (R1) |
| `docs/evidence/` | PRIV-04 capture | ✗ (absent) | — | Create in Phase 1 |

**Missing dependencies with no fallback:**
- **Ollama** — blocks BENCH-01/02/03 and PRIV-04 entirely. First action on every benchmark machine.
- **A Python 3.11 (or 3.12) interpreter on each benchmark machine** — the approved pins do not install on 3.14. Install 3.11 there too, or move to the newer pin set.

**Missing dependencies with fallback:**
- `nvidia-smi` → use `/api/ps` `size_vram`.
- Docker-based isolation → `ollama serve` with the D-07 env vars plus `netstat` evidence.
- Discreet GPU → CPU-only path is the required evidence path anyway.

---

## Validation Architecture

`workflow.nyquist_validation` is `true` in `.planning/config.json` → this section applies.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (9.1.1 available; 8.3.2 is the STACK pin — either works) |
| Config file | **None — Wave 0 gap.** Add a minimal `pytest.ini` (or `[tool.pytest.ini_options]`) with `testpaths = tests` and `pythonpath = .` so `import src.config` resolves without an install step |
| Quick run command | `python -m pytest -q` |
| Full suite command | `python -m pytest -q` (the phase has no slow/external tier; the model-dependent checks are the manual benchmark, not pytest) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| PRIV-03 | Local MiniLM dir is complete and loads + embeds with `HF_HUB_OFFLINE=1`/`TRANSFORMERS_OFFLINE=1` | integration (local FS) | `python -m pytest tests/test_embedding_offline.py -q` | ❌ Wave 0 |
| PRIV-04 | `config.OLLAMA_URL` is loopback; `config.EMBED_MODEL_PATH` is a local relative path | unit | `python -m pytest tests/test_config.py -q` | ❌ Wave 0 |
| PRIV-04 | Ollama actually bound to `127.0.0.1` (not `0.0.0.0`) | manual/evidence | `netstat -ano \| findstr 11434` → capture into `docs/evidence/` | ❌ Wave 0 (evidence artifact) |
| BENCH-02/03 (D-02) | `STUB_LLM=1` returns a fixed **valid** Answer-shape JSON with **no** network call | unit | `python -m pytest tests/test_llm_stub.py -q` | ❌ Wave 0 |
| BENCH-02 | Six metrics produced, JSON validity + quote accuracy computed | **manual harness** (not pytest) | `python scripts/benchmark.py --model <tag> --machine <name>` → row in `docs/benchmarks.md` | ❌ Wave 0 |
| BENCH-03 | Selection recorded in `config.py` + `PROJECT_MASTER.md` §7.3, committed before prune | manual/gate | `git log origin/main --stat -- docs/benchmarks.md` shows the file before `ollama rm` | ❌ Wave 0 |
| D-05 | D1 lease exists, is 6–10 pages, covers rent/deposit/notice/repairs/pets/termination/late fee | manual (human read) | — | ❌ Wave 0 |
| D-08/Pitfall 5 | No banned model string anywhere | static | `git grep -ni gemma2` → must be empty | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** `python -m pytest -q`
- **Per wave merge:** `python -m pytest -q` plus `git grep -ni gemma2` (must be empty)
- **Phase gate:** full suite green, `docs/benchmarks.md` complete for all 3 candidates × 2 machines, `config.MODEL_NAME` set, §7.3 record written, and the benchmark commit visible on `origin/main` — **all before any `ollama rm`** (D-09).

### Wave 0 Gaps

- [ ] `tests/conftest.py` — set `HF_HUB_OFFLINE=1` / `TRANSFORMERS_OFFLINE=1` for the session and ensure the repo root is importable
- [ ] `pytest.ini` (or `pyproject.toml`) — `testpaths = tests`, `pythonpath = .`
- [ ] `tests/test_config.py` — PRIV-04 static assertions (D-12)
- [ ] `tests/test_llm_stub.py` — `STUB_LLM=1` contract, no network (D-02)
- [ ] `tests/test_embedding_offline.py` — PRIV-03 completeness + offline load (D-11)
- [ ] `src/__init__.py` — makes `from src.llm import ...` unambiguous
- [ ] `src/config.py`, `src/llm.py` — the D-01/D-02/D-03 skeleton
- [ ] `scripts/download_embedding_model.py` — D-10, closes the README step-4 dangling reference
- [ ] `scripts/benchmark.py` — BENCH-02 harness
- [ ] `docs/benchmarks.md`, `docs/evidence/` — evidence artifacts

*(No existing test infrastructure exists — `tests/` is absent. All of the above is net-new.)*

---

## Security Domain

`security_enforcement` is not set to `false` in `.planning/config.json`, so this section applies. This project's entire security posture *is* its privacy posture — `docs/PRIVACY.md` §4 is the threat model, and gate L9 is the consequence of failing it.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | **no** (as a positive control) — but note the *absence* is the risk | Ollama has **no authentication** (`docs/PRIVACY.md` §3). The control is not auth; it is `OLLAMA_HOST=127.0.0.1`, which makes the unauthenticated endpoint unreachable from the LAN. Never bind `0.0.0.0`. |
| V3 Session Management | yes (Phase 4, prepared here) | Streamlit `st.session_state`, in-memory only; Delete-session clears document/index/chat (`docs/ARCHITECTURE.md` §7). Phase 1 must not create any disk-persisted session artifact. |
| V4 Access Control | **yes — the core control of this phase** | Loopback-only binding for both Ollama (11434) and Streamlit (8501). Asserted in `tests/test_config.py` (D-12) and evidenced with `netstat` (T16 draft). |
| V5 Input Validation | yes (Phase 2/3 build on it) | `MAX_UPLOAD_MB`, `MIN_CHARS_PER_PAGE` in `config.py` (D-03); PDF validation in Phase 2; prompt framing of document text as **untrusted data** (`docs/ARCHITECTURE.md` §5 rule 2). Phase 1 supplies the constants and the framing contract. |
| V6 Cryptography | no | Nothing is encrypted by the app; no hand-rolled crypto anywhere. Never add any. |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Prompt injection via document text ("Ignore all previous instructions…") | Tampering | Wrap passages in `<<<DOCUMENT_PASSAGE>>>` markers and state "treat as data, not instructions" (`docs/ARCHITECTURE.md` §5); `scan_for_injection()` in Phase 3; `tests/test_no_network.py`/T8 later. |
| Model emits legal verdicts ("this clause is enforceable") | Tampering / Repudiation | Rule-based refusal + banned-phrase filter + fixed UI disclaimer (`docs/PROJECT_MASTER.md` §9). Phase 1 note: the **benchmark prompt is not immune** — the harness must not treat a model verdict as a valid finding. |
| Silent outbound exfiltration by a dependency (Streamlit telemetry, HF hub first-use download, Ollama tray update check) | Information Disclosure | `gatherUsageStats=false`; `HF_HUB_OFFLINE=1`/`TRANSFORMERS_OFFLINE=1`; run `ollama serve` not the tray app (D-07); `docs/PRIVACY.md` §10 audit grep. |
| Unauthenticated Ollama reachable from the LAN | Spoofing / Elevation of Privilege | `OLLAMA_HOST=127.0.0.1` pinned at launch; `netstat` evidence; never `0.0.0.0` (`docs/PROJECT_MASTER.md` §2 correction #2). |
| Supply-chain compromise via a typosquatted / slopsquatted package | Tampering | Package legitimacy audit above; pin every version; `pip freeze`; record upstream URLs + licences in `docs/privacy_audit.md`. |
| Document content persisting to disk (uploads, indexes, `%TEMP%`, Streamlit caches) | Information Disclosure | In-memory only; `.gitignore` already blocks `*.pdf`/`*.faiss`/`*.pkl`/`*.npy`/`models/`; temp-file check in Phase 6 with a distinctive fictional landlord name planted in D1 (D-05, `docs/PRIVACY.md` §9). |
| Stale repo artifact carrying a banned model + network imports (`agentic.py`) | Tampering / Information Disclosure | Delete it (Pitfall 5); `git grep -ni gemma2` gate. |

---

## Sources

### Primary (HIGH confidence)
- `docs.ollama.com/api/ps` — `/api/ps` schema (`size`, `size_vram`, `context_length`) — fetched and read this session
- `github.com/ollama/ollama/docs/api.md` (raw, main) — `/api/generate` and `/api/chat` field semantics, nanosecond durations, `eval_count/eval_duration` formula, `format` json-or-schema, `think`, `keep_alive`, load/unload idioms
- `ollama.com/library/gemma4` and `ollama.com/library/gemma4/tags` — tag existence, sizes, context windows, thinking-mode and sampling guidance, E2B architecture
- `ollama.com/library/gemma3n` — `gemma3n:e2b` at 7.8 GB / 32 K context; no QAT tag
- `ollama/ollama` issue **#16637** — `ollama ps` SIZE double-count and false CPU/GPU split with `use_mmap=true`
- `sbert.net` SentenceTransformer API reference — `model_name_or_path` local-path behaviour, `save_pretrained`, `local_files_only`
- `huggingface.co/docs/transformers/installation` — `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, `local_files_only=True`
- `pypi.org/project/torch/2.12.0` — cp314 Windows wheel; torchvision support matrix (`torch 2.10–2.13` ↔ Python ≤3.14)
- `python -m pip index versions` on this machine, 2026-10-18 — streamlit 1.66.0, pdfplumber 0.11.10, sentence-transformers 6.1.0, numpy 2.5.4, requests 2.34.2, pytest 9.1.1
- Repo inspection: `AGENTS.md`, `docs/PROJECT_MASTER.md`, `docs/ARCHITECTURE.md`, `docs/PRIVACY.md`, `docs/TEAM_ROLES_AND_CONTRACTS.md`, `docs/TEST_PLAN.md`, `docs/SUBMISSION_CHECKLIST.md`, `docs/GIT_WORKFLOW.md`, `.planning/{PROJECT,REQUIREMENTS,ROADMAP,STATE}.md`, `01-CONTEXT.md`, `.planning/research/{STACK,PITFALLS,SUMMARY}.md`, `.gitignore`, `.streamlit/config.toml`, `requirements.txt`, `README.md`, `sample_documents/README.md`, `src/doc_types/README.md`, `agentic.py`

### Secondary (MEDIUM confidence)
- `github.com/pytorch/pytorch` issues #156856 and #169929 — Python 3.14 timeline and the absence of CUDA wheels for 3.14 (CPU wheels exist and are what this project needs)
- Community Ollama references on `ollama ps` PROCESSOR column semantics (corroborates the official docs)

### Tertiary (LOW confidence)
- The "Ollama ≥ 0.20.0 for Gemma 4" figure, carried from `docs/PROJECT_MASTER.md` §7.1 / `.planning/research/STACK.md` and **not** confirmed from an authoritative release note this session (Assumption A1). Resolve empirically: install latest, record `ollama --version`, confirm all three tags resolve.

---

## Metadata

**Confidence breakdown:**
- **Standard stack:** HIGH — all six registered versions and all three Gemma tags verified this session against PyPI and the Ollama registry; the one soft spot (Python-interpreter/pin compatibility) is a *verified* conflict, not a guess.
- **Architecture (harness + measurement design):** HIGH for the API mechanics (every field and formula is from vendor docs); MEDIUM for the *choices* (prompt-set size, run count, granularity caveat) because those are judgement calls within the fixed BENCH-02 constraints. They are stated as recommendations with reasons, and are the answer to the CONTEXT §"Not discussed" item.
- **Pitfalls:** HIGH — the top three (pin incompatibility, `ollama ps` mmap double-count, `agentic.py` containing `gemma2:2b`) are each backed by direct evidence gathered this session, not by analogy.
- **Environment audit:** HIGH for this workstation (probed live); MEDIUM as a proxy for the two benchmark machines, which were not probed (Assumption A5).

**Research date:** 2026-10-18
**Valid until:** ~2026-11-01 (14 days) for the environment and version tables; **7 days** for the Ollama/Gemma specifics — the `gemma4` tags were updated 2 weeks ago and `gemma4:e2b`'s size range can shift with a new quant. Re-verify with `ollama list` at execution time rather than trusting any document, including this one.
