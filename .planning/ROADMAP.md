# Roadmap: ClauseGuard

**Created:** 2026-10-18
**Mode:** mvp
**Granularity:** standard
**Phases:** 6
**v1 Requirements:** 27

---

### Phase 1: Foundation & Benchmark

**Goal:** Repo initialized, Ollama running, embedding model local, Gemma candidate benchmarked and selected
**Mode:** mvp
**Success Criteria**:

1. Repository created with .gitignore, .streamlit/config.toml (telemetry off, bind 127.0.0.1)
2. Ollama installed and 3 candidate models pulled (gemma3n:e2b, gemma4:e2b, gemma4:e2b-it-qat)
3. MiniLM embedding model downloaded to models/ and loads offline (HF_HUB_OFFLINE=1)
4. Benchmark completed on same fictional lease: model size, peak RAM/VRAM, TTFT, tok/s, JSON validity %, quote accuracy % recorded
5. Chosen model documented in PROJECT_MASTER.md meeting criteria: loads on 16GB CPU laptop, <2 min response, >90% JSON validity

**Requirements:** BENCH-01, BENCH-02, BENCH-03, PRIV-03, PRIV-04

**Plans:** 2/5 plans executed

Plans:
**Wave 1**

- [x] 01-01-PLAN.md — Walking skeleton: config singleton, LLM client with STUB_LLM=1 backend, test infrastructure, pinned requirements, remove banned agentic.py, push backlog

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 01-02-PLAN.md — Embedding setup: download all-MiniLM-L6-v2 to models/, PRIV-03 offline test (completeness + load), PRIV-04 static config tests (loopback URL + local path)
- [ ] 01-03-PLAN.md — Benchmark harness: scripts/benchmark.py with 6 metrics via Ollama API, D1_clean_lease.pdf fixture (6-10 pages, 7 topics), sample_documents/README.md update, docs/benchmarks.md scaffold

**Wave 3** *(blocked on Wave 2 completion)*

- [ ] 01-04-PLAN.md — Contract tests: STUB_LLM=1 test (Answer-dict JSON validity, json_mode=False, check_model_ready structure), full test suite verification (7 tests green)

**Wave 4** *(blocked on Wave 3 completion)*

- [ ] 01-05-PLAN.md — Benchmark execution + selection: run on both machines (3×2=6 rows), apply CPU-only selection criteria, lock MODEL_NAME in config.py, record in PROJECT_MASTER.md §7.3, commit before prune, netstat loopback capture, ollama rm losers

---

### Phase 2: Ingestion & Retrieval

**Goal:** PDF ingestion pipeline and semantic retrieval working on sample leases
**Mode:** mvp
**Success Criteria**:

1. User uploads text PDF → extracts pages with page numbers preserved (INGEST-01, INGEST-02)
2. Document split into clauses by legal numbering; headings preserved; page numbers correct (INGEST-03)
3. In-memory vector index built from clauses using local MiniLM embeddings (INGEST-04)
4. Question returns top-3 passages with verbatim text, page numbers, similarity scores (RETRIEVE-01, RETRIEVE-02)
5. Test suite: 5 test questions on sample leases return 3 correct passages with accurate page numbers

**Requirements:** INGEST-01, INGEST-02, INGEST-03, INGEST-04, RETRIEVE-01, RETRIEVE-02, PRIV-02, TEST-01

---

### Phase 3: Guardrails & Answer Pipeline

**Goal:** All guardrails enforced by code; structured answers with verified citations; silence/refusal/injection handling working
**Mode:** mvp
**Success Criteria**:

1. Question classifier routes: normal → pipeline, legal verdict → hardcoded refusal + specific escalation, out of scope → polite decline (GUARD-01, GUARD-04)
2. Silence threshold triggers "The document does not state this" before any model call; no fake answers (GUARD-02)
3. Every model quote verified as exact substring of source passage; failures dropped; UI shows only verified passages (GUARD-03)
4. Prompt injection detector shows warning banner when document contains instruction-like text; answer unaffected (GUARD-05)
5. Gemma returns valid JSON with all fields: category, plain_language, quote, page, kind, uncertainty (ANSWER-01)
6. "Summarise key terms" returns structured summary covering all 6 predefined topics (ANSWER-02)
7. Tests T3 (citation check), T4 (silence), T5 (refusal) pass on 20 prompts each

**Requirements:** GUARD-01, GUARD-02, GUARD-03, GUARD-04, GUARD-05, ANSWER-01, ANSWER-02, TEST-01

---

### Phase 4: UI Integration

**Goal:** Full end-to-end flow working on single laptop with Streamlit UI wired to real pipeline
**Mode:** mvp
**Success Criteria**:

1. Streamlit app launches on 127.0.0.1; upload → question → answer → delete session works (UI-01, UI-03)
2. Two-pane layout displays: explanation | source passages | concerns | uncertainty | disclaimer (UI-02, GUARD-06)
3. Delete Session button clears all in-memory state (document, index, chat) (UI-01)
4. Model-unavailable error shows gracefully with no fake analysis (UI-03)
5. Full pipeline runs offline: Wi-Fi off, connection monitor shows zero external calls (PRIV-01, PRIV-04)
6. No temporary files created during any operation (PRIV-02)

**Requirements:** UI-01, UI-02, UI-03, GUARD-06, PRIV-01, PRIV-02, PRIV-04, TEST-01

---

### Phase 5: Should-Haves & Polish

**Goal:** Missing Promise Detector, injection banner polish, benchmark table in README
**Mode:** mvp
**Success Criteria**:

1. Missing Promise Detector runs on answer: checks 6 lease topics; shows "No clear condition found" for absent topics (ANSWER-03)
2. Prompt injection warning banner visible and accurate; doesn't block legitimate answers (GUARD-05)
3. README includes benchmark table: model, size, RAM/VRAM, TTFT, tok/s, JSON validity %, quote accuracy % (DOCS-01)
4. README states scope honestly: rental only, English, text PDF, no legal verdicts (DOCS-01)
5. Fictional sample lease included in sample_documents/ for judge testing (DOCS-01)

**Requirements:** ANSWER-03, GUARD-05, DOCS-01

---

### Phase 6: Evidence & Submission

**Goal:** Complete offline evidence pack, submission checklist 100% ticked, repo polished for public submission
**Mode:** mvp
**Success Criteria**:

1. Offline demonstration recorded: Wi-Fi off, connection monitor running, full flow works (PRIV-01)
2. Temp file audit: no document text, embeddings, or indexes written to disk (PRIV-02)
3. Code audit: only network call is requests to 127.0.0.1:11434; no hidden calls (PRIV-01, PRIV-04)
4. All gates L1-L10 evidenced in submission checklist (DOCS-02)
5. README complete: setup instructions, minimum specs, benchmark table, scope, license, sample lease (DOCS-01)
6. requirements.txt pinned with pip freeze; all versions locked (DOCS-01)
7. Test suite T1-T7 passes; runnable by judges (TEST-01)
8. Submission checklist every box ticked; evidence pack organized (DOCS-02)

**Requirements:** PRIV-01, PRIV-02, PRIV-04, DOCS-01, DOCS-02, TEST-01, BENCH-01, BENCH-02, BENCH-03

---

## Phase Dependency Graph

```
Phase 1 (Foundation) ──┬──→ Phase 2 (Ingestion)
                       │
                       ├──→ Phase 3 (Guardrails) ←── Phase 2
                       │
                       └──→ Phase 4 (UI) ←───────── Phase 2 + Phase 3
                                                      ↓
Phase 5 (Should-Haves) ←────────────────────────────┘
                                                      ↓
Phase 6 (Evidence) ←────────────────────────────────┘
```

**Critical Path:** Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 6
**Parallel Work:** Phase 1 (R1) independent; Phase 5 can start after Phase 4 integration begins

---

## Checkpoint Rules

- **Hour 3 Checkpoint:** If no candidate model answers usefully on any laptop → cut scope to summary + clause lookup only
- **Hour 5 Midpoint:** Rental passes T1, T3, T4, T5 on sample set? → Decision on second document type
- **Hour 8 Checkpoint:** Full flow works end-to-end on one laptop? → If not, prioritize Phase 4 over Phase 5

---

## Requirement Coverage

| Phase | Requirements | Count |
|-------|--------------|-------|
| Phase 1 | BENCH-01, BENCH-02, BENCH-03, PRIV-03, PRIV-04 | 5 |
| Phase 2 | INGEST-01..04, RETRIEVE-01..02, PRIV-02, TEST-01 | 8 |
| Phase 3 | GUARD-01..05, ANSWER-01..02, TEST-01 | 8 |
| Phase 4 | UI-01..03, GUARD-06, PRIV-01, PRIV-02, PRIV-04, TEST-01 | 7 |
| Phase 5 | ANSWER-03, GUARD-05, DOCS-01 | 3 |
| Phase 6 | PRIV-01, PRIV-02, PRIV-04, DOCS-01, DOCS-02, TEST-01, BENCH-01..03 | 10 |

**Total v1 requirements mapped:** 27/27 ✓
