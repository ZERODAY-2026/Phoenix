# Phase 1: Foundation & Benchmark - Context

**Gathered:** 2026-10-18
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 1 delivers **no user-facing capability**. It delivers a provable local foundation that every later phase depends on:

1. A runnable single-machine Ollama runtime serving a Gemma class model, bound to loopback only
2. A MiniLM embedding model on disk that loads with networking off
3. A measured benchmark of three Gemma candidates with one model selected and locked in code
4. The code skeleton (`src/config.py`, `src/llm.py` with a stub backend, `scripts/`, `tests/`) that unblocks R2/R3/R4
5. The fictional benchmark lease (D1) that later phases reuse

**Requirements in scope:** BENCH-01, BENCH-02, BENCH-03, PRIV-03, PRIV-04

**Explicitly not in this phase:** PDF ingestion, clause splitting, vector search, guardrails, the answer pipeline, the Streamlit UI. Those are Phases 2-4. If a task is not one of the five deliverables above, it belongs in another phase.

</domain>

<decisions>
## Implementation Decisions

### Phase-1 deliverable boundary
- **D-01:** Phase 1 ships the code skeleton, not just runtime artifacts. Deliverables include `src/config.py` and `src/llm.py`, plus `scripts/` and `tests/` package skeletons. This matches the hour-1 handover in `docs/TEAM_ROLES_AND_CONTRACTS.md` §5 ("Hour 1: R4 pushes the skeleton and `config.py` stub; R1 pushes `llm.py` with the stub backend") and the PROJECT_MASTER hour 0:00-1:30 exit check ("stub LLM backend ready"). The ROADMAP's five success criteria omit this; the docs pack requires it, and R2/R3/R4 cannot start their contract files without it.
- **D-02:** `src/llm.py` implements exactly the contract in `docs/TEAM_ROLES_AND_CONTRACTS.md` §3: `check_model_ready() -> tuple[bool, str]`, `generate(system, prompt, json_mode=True) -> str`, `ModelUnavailable`, and the `STUB_LLM=1` backend that returns a fixed valid JSON string without calling a model. Because of D-10 there is no pluggable-runtime abstraction — one Ollama HTTP backend plus the stub.
- **D-03:** `src/config.py` is created with the real `MODEL_NAME` from the benchmark result plus the full constant set in TEAM_ROLES §3: `OLLAMA_URL`, `EMBED_MODEL_PATH`, `TOP_K`, `SILENT_THRESHOLD` (placeholder 0.30, calibrated in Phase 2), `MAX_UPLOAD_MB`, `MIN_CHARS_PER_PAGE`, `REQUEST_TIMEOUT_S`.
- **D-04:** **`src/config.py` `MODEL_NAME` is the single source of truth for the chosen model.** It is overridable by the `CLAUSEGUARD_MODEL` environment variable, which `README.md` setup step 5 already promises. `docs/benchmarks.md` holds the measured evidence; `docs/PROJECT_MASTER.md` §7.3 gets a one-line pointer. Downstream agents must read `config.py` and must not re-decide or duplicate the model name.
- **D-05:** Phase 1 writes **D1, the clean lease**, into `sample_documents/` as the benchmark fixture, per the specification in `docs/TEST_PLAN.md` §1: 6-10 pages, numbered clauses covering rent, deposit (30 days), notice (2 months), repairs, pets, termination, late fee. It is fictional and team-written. It is reused as the Phase 2 baseline ingestion document, so it is written once. The `sample_documents/README.md` table must be updated to list it.

### Runtime, hardware and selection fallout
- **D-06:** The benchmark runs all three candidates (`gemma3n:e2b`, `gemma4:e2b`, `gemma4:e2b-it-qat`) on the RTX 2050 laptop **and** on one nominated CPU-only 16 GB laptop. The CPU-only run is what makes BENCH-03's criterion ("loads on 16 GB CPU laptop") real evidence instead of an assumption. The winning model then gets a confirmation run on the designated demo machine. Every benchmark row must record which machine produced it. Note: the RTX 2050 has only 4 GB VRAM, so both Gemma 4 builds will partially offload to CPU regardless.
- **D-07:** Ollama runs via **`ollama serve` in a terminal**, not the desktop tray app, for both the benchmark and the demo. Environment pinned: `OLLAMA_HOST=127.0.0.1`, `OLLAMA_NUM_PARALLEL=1`, `OLLAMA_MAX_LOADED_MODELS=1`. Rationale: `docs/PRIVACY.md` §5 lists the tray app's startup update check as an unresolved item — running the daemon directly removes it. Pinning `OLLAMA_HOST` makes the loopback binding deterministic rather than defaulted. Serialising requests keeps peak-RAM measurements from being confused by a concurrent model load. The same command serves the T15 offline test and the T16 loopback test.
- **D-08:** **Strict failure rule.** If any candidate tag is missing from the registry, or no Gemma-class candidate answers usefully within the time budget, invoke the hour-3 checkpoint immediately: **cut scope to summary + clause lookup only**. Do **not** substitute `gemma2:2b` (gate L1-L4 requires the Gemma 3n/4 class; a substitution is a gate failure disguised as a workaround). Do **not** add a second runtime such as llama.cpp. Do **not** swap in any other model family. Record the trigger and the decision in `docs/benchmarks.md`.
- **D-09:** After the selection is recorded, **prune the two non-selected models with `ollama rm` on every machine.** Consequence to respect: the benchmark table must be complete and committed *before* pruning, because re-measuring a recorded figure requires re-downloading a multi-GB model mid-window.

### Embedding setup and offline proof
- **D-10:** `scripts/download_embedding_model.py` populates `models/all-MiniLM-L6-v2/` by calling `SentenceTransformer('all-MiniLM-L6-v2')` and then `.save('models/all-MiniLM-L6-v2')`. The saver and the loader are the same code path, so the on-disk file set (including `modules.json` and the pooling config) is exactly what `retrieval.py` will look for, by construction. `torch`/`transformers` are already required by the locked stack, so this adds no new dependency. Setup runs online with no user document involved; operation runs offline.
- **D-11:** **PRIV-03 is proven by an automated test**, not by assertion: `tests/test_embedding_offline.py` must (a) assert the local directory's file set is **complete** — `config.json`, `modules.json`, tokenizer files, model weights — *before* attempting a load, then (b) load with `HF_HUB_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1` and embed a fixed sentence. The completeness check is the point: a partial download leaves a directory that exists but is incomplete, which is the most likely false pass. This complements, and does not replace, the Phase 6 Wi-Fi-off evidence run in `docs/PRIVACY.md` §7.
- **D-12:** **PRIV-04 is verified in Phase 1** by a static test in `tests/` asserting `config.OLLAMA_URL` is loopback and `config.EMBED_MODEL_PATH` is a local relative path, **plus** a Phase 1 capture of `netstat -ano | findstr 11434` showing `127.0.0.1` rather than `0.0.0.0`. The capture is an early draft of test T16. The full `tests/test_no_network.py` regex test over `src/` and `app.py` described in `docs/TEST_PLAN.md` §5 stays in Phase 2/3, where it has a real source tree to scan.

### Git and push convention
- **D-13:** **Push directly to `main` after every commit.** The remote is already configured: `origin` → `https://github.com/ZERODAY-2026/Phoenix.git`. This intentionally overrides two existing rules: `docs/TEAM_ROLES_AND_CONTRACTS.md` §2 (R4 deliverable 1, "no direct pushes to `main`") and `docs/GIT_WORKFLOW.md` §4 (push to role branches `r1-model`/`r2-retrieval`/`r3-answer`/`r4-ui`, then open a PR merged by a teammate). Those documents should be reconciled with this decision rather than left contradicting it.
- **D-14:** Outstanding at context time: `main` is 6 commits ahead of `origin/main`. The planning commits (initialize project, config, research, requirements, roadmap, AGENTS.md) have never been pushed. This backlog must be pushed before the after-every-commit rule starts producing value.

### Agent's Discretion
- **D-10** and **D-11** above were explicitly deferred to the agent's judgement by the user and decided as written. They are locked decisions now, not open questions.
- **Not discussed — deliberately left to planning:** the **BENCH-02 measurement method**. The user chose not to open the "Benchmark harness & measurement" gray area, so nothing here specifies whether the six BENCH-02 metrics come from a scripted harness or a hand-recorded table, what the benchmark prompt set is or how large it is, how "quote accuracy %" is computed in Phase 1 before the Phase 3 substring verifier exists, or how many runs per model. `gsd-phase-researcher` and `gsd-planner` own that decision. Constraints they must respect: the six metrics in BENCH-02 are fixed deliverables; the selection criteria in `docs/PROJECT_MASTER.md` §7.3 (loads on CPU-only 16 GB, <2 min response, >90% JSON validity, tie-break on quote accuracy) are fixed; the whole phase must fit the 1.5-hour slice in `docs/PROJECT_MASTER.md` §11; and D-09 requires the table to be complete and committed before pruning.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Authoritative project decisions (read first, highest precedence)
- `docs/PROJECT_MASTER.md` — "the single source of truth. If another file disagrees with this document, this document wins." §5 final stack, §7.1 candidate models and reported sizes, §7.2 benchmark protocol, §7.3 selection criteria and the decision record line, §8 feature list, §11 timeline, §13 risk register.
- `docs/PROJECT_MASTER.md` §2 — corrections to earlier plans that would have caused gate failures (esp. #1 on the Gemma class requirement, #2 on LAN serving, #7 on hidden network calls, #8 on the RTX 2050's 4 GB).
- `docs/ARCHITECTURE.md` §4 — the Answer dict output contract, which defines what "valid JSON" means for the BENCH-02 JSON-validity measurement.
- `docs/ARCHITECTURE.md` §5 — the model prompt contract (system prompt rules and passage wrapping markers).
- `docs/TEAM_ROLES_AND_CONTRACTS.md` §3 — exact function signatures and constant names for `config.py`, `llm.py`, `ingest.py`, `retrieval.py`, `guardrails.py`, `answer.py`. The skeleton must match these.
- `docs/TEAM_ROLES_AND_CONTRACTS.md` §2 and §5 — role ownership and the hour-1/hour-3 handover checkpoints.
- `.planning/ROADMAP.md` — Phase 1 goal, five success criteria, requirement mapping and the phase dependency graph.
- `.planning/REQUIREMENTS.md` — BENCH-01..03, PRIV-03, PRIV-04 definitions; the Out of Scope table.

### Privacy and offline evidence
- `docs/PRIVACY.md` §2 — allowed vs not-allowed network behaviour; setup vs operation split.
- `docs/PRIVACY.md` §5 — known network touchpoints table, including the open item about the Ollama tray app update check (which D-07 closes).
- `docs/PRIVACY.md` §6 — the setup/operation procedure and the offline env vars (`HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`).
- `docs/PRIVACY.md` §7-9 — the reproducible offline test, connection-monitoring options, and the temp-file check.
- `docs/PRIVACY.md` §10 — the code and dependency audit grep, and the note to watch `sentence-transformers`/`transformers`/`huggingface_hub` for first-use downloads.
- `docs/PRIVACY.md` §11 — the evidence pack inventory, which lists `docs/benchmarks.md`.

### Benchmark and test definitions
- `docs/TEST_PLAN.md` §1 — the D1 clean lease specification that D-05 implements (contents, length, clause coverage).
- `docs/TEST_PLAN.md` §3 — the evaluation question set (18 starter questions with expected answers), the natural candidate for the BENCH-02 prompt set.
- `docs/TEST_PLAN.md` §4 — `SILENT_THRESHOLD` calibration procedure (Phase 2 work, but it consumes `docs/benchmarks.md`).
- `docs/TEST_PLAN.md` §5 — planned pytest files, including the `tests/test_no_network.py` shape referenced by D-12.
- `docs/TEST_PLAN.md` §2 tests T11, T12, T15, T16 — length/robustness, model-unavailable, offline run and loopback binding, which Phase 1 partially front-runs.

### Stack research and rejected alternatives
- `.planning/research/STACK.md` — the versioned stack table with confidence levels, the explicitly rejected options (PyMuPDF, LangChain, FAISS, remote APIs, React/FastAPI) and the version pinning strategy.
- `.planning/research/PITFALLS.md` — pitfall 1 (model too slow on CPU), 2 (Gemma not working in Ollama), 3 (hidden network call), each mapped to Phase 1.
- `.planning/research/SUMMARY.md` — condensed Phase 1 focus, risk mitigations and the hour-3 checkpoint rule.
- `docs/DATASETS.md` — the rule that no model is trained or fine-tuned on any dataset; relevant to how the benchmark is framed in the README.

### Repo conventions already in place
- `README.md` — setup steps already promise `scripts/download_embedding_model.py` (step 4), `src/config.py` plus the `CLAUSEGUARD_MODEL` env var (step 5), and the offline run command block.
- `docs/GIT_WORKFLOW.md` — branch names and rules; §4 conflicts with D-13 and needs reconciling.
- `sample_documents/README.md` — the fictional-documents statement and the D1-D7 table that D-05 must update.
- `src/doc_types/README.md` — the per-type config field list, which `config.py` and `rental.py` must stay compatible with (Phase 2/3 work, but the shape is already fixed).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `.gitignore` — already committed and correct: ignores `models/`, `*.gguf`, `*.safetensors`, `*.faiss`, `*.pkl`, `*.npy`, `*.index`, all `*.pdf` **except** `!sample_documents/*.pdf` and `!sample_documents/*.txt`, plus `tmp/` and `*.log`. The D1 lease in D-05 commits cleanly with no `.gitignore` change. No new ignore rules are needed for the embedding model.
- `.streamlit/config.toml` — already committed with `gatherUsageStats = false`, `server.address = "127.0.0.1"`, `headless = true`. Phase 1 success criterion 1 is therefore already satisfied; verify rather than recreate.
- `LICENSE` — MIT, in place. Consistent with the pdfplumber-over-PyMuPDF decision.
- `docs/` pack (9 documents) — the entire design is already written. Phase 1 is mostly execution against existing specs, not design work.
- `src/doc_types/README.md` — fixes the DocType field set (`NAME`, `STATUS`, `TOPICS`, `ESCALATION`, `EXAMPLE_QUESTIONS`). Relevant because `config.py` must not conflict with it.

### Established Patterns
- **"The model explains. The code guarantees."** (`docs/ARCHITECTURE.md` §1) — anything that must be true (citations, refusals, silence, disclaimers) is enforced by deterministic code. Applies to Phase 1 as: the model choice is locked in `config.py` by code, not left to a doc.
- **Setup versus operation split** (`docs/PRIVACY.md` §6) — downloads happen once, online, with no user document; everything after is offline. The embedding download script (D-10) is a setup-time artifact and must be documented as such in the README.
- **One file, one owner** (`docs/TEAM_ROLES_AND_CONTRACTS.md` §4) — `src/config.py` and `src/llm.py` are R1's; `scripts/` and `tests/` are R4's (tests) and R2's (`scripts/inspect_retrieval.py`, Phase 2). A Phase 1 plan touching both needs both owners.
- **`STUB_LLM=1`** — the stub backend lets R2/R3/R4 work before any model is ready (`docs/TEAM_ROLES_AND_CONTRACTS.md` §4 rule 8). It is also the mechanism test T13 uses to force invalid JSON.
- **Contract-first signatures** — every module's functions are frozen in `docs/TEAM_ROLES_AND_CONTRACTS.md` §3, so the skeleton can be written before the implementations without churn.

### Integration Points
- `src/config.py` is imported by every later module (`llm`, `ingest`, `retrieval`, `guardrails`, `answer`, `app`). It is the join point for the Phase 1 model lock (D-04) and the place `CLAUSEGUARD_MODEL` must be honoured.
- `src/llm.py` is the **only** file permitted to contain network code (`docs/TEAM_ROLES_AND_CONTRACTS.md` §4 rule 5, `docs/PRIVACY.md` §10). The Phase 1 static test in D-12 must hold `config.py` and `llm.py` to that from the first commit.
- `scripts/download_embedding_model.py` is referenced by `README.md` step 4 and by `README.md` troubleshooting ("Embedding model not found"). Creating it closes a dangling reference in the public docs.
- `models/all-MiniLM-L6-v2/` is gitignored, so judges reproduce it only through that script. The script's existence and correctness is a reproducibility requirement, not a convenience.
- `sample_documents/` is currently empty except `README.md`; D1 is the first committed sample and the first thing the `.gitignore` sample exception is exercised by.

</code_context>

<specifics>
## Specific Ideas

- The benchmark uses **the same fictional lease** across all three candidates and both machines (`docs/PROJECT_MASTER.md` §7.2), with the network disabled after the pulls. Same input, same conditions, so the numbers are comparable.
- The six BENCH-02 metrics are non-negotiable: model file size on disk (`ollama list`), peak RAM/VRAM, time to first token, tokens per second (Ollama's `eval_count`/`eval_duration`), JSON validity % (over the prompt set), quote accuracy %.
- Selection rule as written in `docs/PROJECT_MASTER.md` §7.3: loads on a CPU-only 16 GB laptop with other apps closed, answers a typical question in under about 2 minutes, valid JSON in at least 90% of prompts; if two candidates pass, take the higher quote-accuracy count. Record the decision in `PROJECT_MASTER.md` §7.3 as "Chosen model: `____` (date, who, numbers)".
- Ollama needs a recent version for Gemma 4 (reported v0.20.0+); both `docs/PROJECT_MASTER.md` §7.1 and `.planning/research/STACK.md` mark the Gemma 4 sizes and tags **"(verify)"**. Confirm with `ollama list` after pulling rather than trusting either document.
- The D1 lease should contain a made-up landlord name that no real person shares — `docs/PRIVACY.md` §9 uses exactly that kind of distinctive string for the temp-file leak search in Phase 6.

</specifics>

<deferred>
## Deferred Ideas

- Reconciling `docs/GIT_WORKFLOW.md` §4 and `docs/TEAM_ROLES_AND_CONTRACTS.md` §2 with the direct-to-`main` push decision (D-13). The documents currently contradict the agreed workflow. Not a Phase 1 code task, but it must be corrected before the submission pack is assembled in Phase 6.
- Adding a `models/README.md` or `.gitkeep` so the gitignored `models/` directory has a documented shape. Nice-to-have, no owner yet.
- A machine-readable benchmark artifact (`docs/benchmarks.json`/`.csv`) so the Phase 5 README table is generated from data rather than retyped. Considered and not chosen for Phase 1 (D-04 records the simpler variant); revisit if the benchmark table has to be regenerated.

</deferred>

---

*Phase: 1-Foundation & Benchmark*
*Context gathered: 2026-10-18*
