# Phase 1: Foundation & Benchmark - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-10-18
**Phase:** 1-Foundation & Benchmark
**Areas discussed:** Phase-1 deliverable boundary, Runtime/hardware/selection fallout, Embedding setup & offline proof, Git and push convention

---

## Area selection

| Option | Description | Selected |
|--------|-------------|----------|
| Benchmark harness & measurement | Scripted harness vs hand-timed table; how quote accuracy is measured before the Phase 3 verifier exists; prompt set and run count | |
| Phase-1 deliverable boundary | Whether Phase 1 ships `config.py`/`llm.py`/stub/skeleton, and whether D1 is written now | ✓ |
| Runtime, hardware & selection fallout | Ollama run mode, benchmark machines, disk footprint, fallback ladder | ✓ |
| Embedding setup & offline proof | How `models/all-MiniLM-L6-v2/` is populated and how PRIV-03/PRIV-04 are proven | ✓ |

**User's choice:** the three areas above; benchmark harness deliberately not opened.
**Notes:** The unselected area was re-offered at the final gate and the user still chose to proceed to CONTEXT.md, leaving the BENCH-02 measurement method to the researcher/planner. Recorded in CONTEXT.md under "Agent's Discretion".

---

## Phase-1 deliverable boundary

### Does Phase 1 also deliver the code skeleton?

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — config.py + llm.py + stub + skeleton | Matches the TEAM_ROLES hour-1 handover; unblocks R2/R3/R4; locks the model in code | ✓ |
| llm.py stub only, config.py in Phase 2 | Less churn if contract signatures still move | |
| No — models + benchmark + repo files only | Exactly the five ROADMAP criteria | |
| You decide | Agent picks for shortest critical path | |

**User's choice:** Yes — full skeleton.
**Notes:** Accepted the ~30 min cost inside the 1.5-hour window.

### Does Phase 1 write the D1 benchmark lease?

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — write D1 now as the benchmark fixture | 6-10 page numbered lease; reused as the Phase 2 baseline | ✓ |
| No — benchmark on a short throwaway excerpt | Faster, but numbers measured on a toy document | |
| Partial — a short but real numbered lease now | Only the clauses the prompt set needs | |
| You decide | Agent judges against the hour-3 checkpoint | |

**User's choice:** Write D1 now.
**Notes:** PROJECT_MASTER §7.2 already specified "the same 10-page fictional lease"; `sample_documents/` contained only a README.

### Where does the chosen model live as the source of truth?

| Option | Description | Selected |
|--------|-------------|----------|
| src/config.py MODEL_NAME is canonical (env-overridable) | App reads one value; `CLAUSEGUARD_MODEL` override; docs point at it | ✓ |
| PROJECT_MASTER.md §7.3 stays canonical, config.py mirrors it | Documentation-first, app depends on a markdown file | |
| All three, plus a machine-readable benchmark file | Data-driven README table in Phase 5; more sync surface | |
| You decide | Agent picks least drift-prone | |

**User's choice:** `src/config.py` `MODEL_NAME` canonical.

---

## Runtime, hardware & selection fallout

### Which laptops run the benchmark?

| Option | Description | Selected |
|--------|-------------|----------|
| GPU laptop + one nominated CPU-only laptop | Full comparison plus the machine BENCH-03 actually constrains | ✓ |
| GPU laptop for the comparison, CPU laptop to confirm | Cheapest; CPU numbers become a single confirmation point | |
| CPU-only 16GB laptop only | Strictest reading; slow iteration, discards GPU offload data | |
| You decide | Agent designs the matrix around the hour-3 checkpoint | |

**User's choice:** GPU laptop + one nominated CPU-only 16 GB laptop, then confirm on the demo machine.

### How does Ollama run?

| Option | Description | Selected |
|--------|-------------|----------|
| `ollama serve` in a terminal, env pinned | Removes the tray app update check; explicit loopback binding; serialised requests | ✓ |
| Tray app for setup, terminal serve for the evidence run | Convenient but requires documenting the update check at least once | |
| Tray app, documented in the touchpoint table | Least process change; weakest offline verification | |
| You decide | Agent picks least ambiguous for T15/T16 | |

**User's choice:** `ollama serve` in a terminal with `OLLAMA_HOST=127.0.0.1`, `OLLAMA_NUM_PARALLEL=1`, `OLLAMA_MAX_LOADED_MODELS=1`.

### Fallback if no Gemma candidate works?

| Option | Description | Selected |
|--------|-------------|----------|
| Gemma-class ladder only, then the hour-3 checkpoint | Step through the three named candidates, then cut scope | |
| Gemma ladder, then llama.cpp + Gemma GGUF | Keeps Gemma requirement if Ollama itself fails | |
| Any failure → cut scope immediately | No substitution, no second runtime, no alternative model | ✓ |
| You decide | Agent protects gate L1-L4 and records triggers | |

**User's choice:** Any failure → cut scope immediately.
**Notes:** Strictest option. Explicitly rejects `gemma2:2b` substitution and a llama.cpp fallback. Consequence captured in CONTEXT.md D-02: `src/llm.py` needs no pluggable-runtime abstraction.

### What happens to the two non-selected models on disk?

| Option | Description | Selected |
|--------|-------------|----------|
| Keep all three on the bench laptop, prune the demo machine | Keeps re-measurement possible until Phase 6 | |
| Prune losers everywhere right after selection | Frees ~8-10 GB; numbers survive in docs/benchmarks.md | ✓ |
| Keep all three everywhere | Simplest; demo laptop carries ~15 GB of unused models | |
| You decide | Agent balances re-measurement safety vs disk pressure | |

**User's choice:** Prune everywhere right after selection.
**Notes:** Creates a hard ordering constraint — the benchmark table must be committed before pruning.

---

## Embedding setup & offline proof

### How is `models/all-MiniLM-L6-v2/` populated?

| Option | Description | Selected |
|--------|-------------|----------|
| SentenceTransformer(...).save() in the script | Saver and loader share one code path | ✓ (agent discretion) |
| huggingface_hub.snapshot_download into local_dir | Lighter; loader depends on local_dir resolution | |
| git clone the HF repo | Transparent; needs git-lfs, brings `.git` into `models/` | |
| You decide | Agent picks the least likely to fail on a fresh machine | ✓ |

**User's choice:** "You decide".
**Notes:** Agent chose `SentenceTransformer('all-MiniLM-L6-v2').save('models/all-MiniLM-L6-v2')`. Rationale: the downloader and loader are the same code path, so `modules.json` and the pooling config are correct by construction. `torch`/`transformers` are already in the locked stack.

### How is PRIV-03's offline load proven?

| Option | Description | Selected |
|--------|-------------|----------|
| pytest test asserting the offline load | Automated, regression guard, complements the Phase 6 run | |
| Documented manual check with Wi-Fi off | Fastest; no regression guard | |
| pytest test, plus a local-file-set completeness check | Also catches the partial-download false pass | ✓ (agent discretion) |
| You decide | Agent picks what a judge can check without re-running the demo | ✓ |

**User's choice:** "You decide".
**Notes:** Agent chose the completeness check plus the offline load test, because a partial download leaves a directory that exists but is incomplete — the most likely false pass for PRIV-03. The manual Wi-Fi-off run stays as Phase 6 evidence.

### How is PRIV-04 verified in Phase 1?

| Option | Description | Selected |
|--------|-------------|----------|
| Static test + a Phase 1 netstat capture | Loopback/local-path assertion plus `netstat` evidence; early T16 draft | ✓ |
| netstat capture only, test later | Keeps Phase 1 lean; no guard on `llm.py` from its first commit | |
| Write the full no-network test now | Front-loads Phase 2/3 work into a 1.5-hour window | |

**User's choice:** Static test + Phase 1 netstat capture.
**Notes:** Full `tests/test_no_network.py` regex over `src/` and `app.py` (TEST_PLAN §5) stays in Phase 2/3.

---

## Git and push convention

Free-text instruction from the user, not a gray-area option: *"after each commit push to https://github.com/ZERODAY-2026/Phoenix.git"*.

| Option | Description | Selected |
|--------|-------------|----------|
| Push directly to `main` after every commit | Fastest; overrides the PR rule and the branch-protection line in TEAM_ROLES §2 | ✓ |
| Push the current branch after every commit | Keeps the PR model intact | |
| `main` during the hackathon, PRs for final polish | Matches how teams work under time pressure | |

**User's choice:** Push directly to `main` after every commit.
**Notes:** `origin` already points at `https://github.com/ZERODAY-2026/Phoenix.git`. Two conflicts with existing docs were flagged (`docs/TEAM_ROLES_AND_CONTRACTS.md` §2 "no direct pushes to main", `docs/GIT_WORKFLOW.md` §4 branch-plus-PR flow); reconciling those documents is recorded as a deferred idea. Also flagged: `main` was 6 commits ahead of `origin/main` at context time.

---

## Agent's Discretion

- **Embedding model download method** — chose `SentenceTransformer(...).save()` (D-10) over `snapshot_download` and `git clone`.
- **PRIV-03 offline proof** — chose the pytest test *with* a local file-set completeness check (D-11), not the test alone and not the manual check alone.
- **BENCH-02 measurement method** — not discussed at the user's direction. Left to `gsd-phase-researcher` and `gsd-planner`: scripted harness vs hand-recorded table, prompt set and size, quote-accuracy computation before the Phase 3 verifier exists, runs per model. Fixed constraints: the six BENCH-02 metrics, the PROJECT_MASTER §7.3 selection criteria, the 1.5-hour phase budget, and the D-09 commit-before-prune ordering.

## Deferred Ideas

- Reconcile `docs/GIT_WORKFLOW.md` §4 and `docs/TEAM_ROLES_AND_CONTRACTS.md` §2 with the direct-to-`main` push decision.
- Add `models/README.md` or `.gitkeep` to document the gitignored `models/` shape.
- Optional machine-readable benchmark artifact (`docs/benchmarks.json`/`.csv`) so the Phase 5 README table is generated rather than retyped.
