# Project Research — Architecture

**Domain:** On-device legal document triage (rental agreements)
**Date:** 2026-10-18
**Context:** Greenfield — ZeroDay OSS Hacktoberfest 2026

---

## Component Boundaries

```
┌─────────────────────────────────────────────────────────────────┐
│                        app.py (Streamlit UI)                     │
│  Upload → Question → Answer Display → Delete Session            │
└─────────────────────────┬───────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│  ingest.py    │ │ retrieval.py  │ │  guardrails.py │
│  (R2)         │ │  (R2)         │ │  (R3)         │
│               │ │               │ │               │
│ - extract_pdf │ │ - build_index │ │ - classify_q  │
│ - split_clauses│ │ - search     │ │ - silence_chk │
│               │ │               │ │ - verify_quote│
└───────┬───────┘ └───────┬───────┘ └───────┬───────┘
        │                 │                 │
        ▼                 ▼                 ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│  In-Memory    │ │  In-Memory    │ │  prompts.py   │
│  Document     │ │  Vector Index │ │  (R3)         │
│  (pages,      │ │  (embeddings, │ │               │
│   clauses)    │ │   clauses)    │ │ - system_prompt│
└───────────────┘ └───────────────┘ │ - format_output│
                                    └───────┬───────┘
                                            │
                                            ▼
                                    ┌───────────────┐
                                    │   answer.py   │
                                    │   (R3)        │
                                    │               │
                                    │ - orchestrate │
                                    │ - call_llm    │
                                    │ - postprocess │
                                    └───────┬───────┘
                                            │
                                            ▼
                                    ┌───────────────┐
                                    │   llm.py      │
                                    │   (R1)        │
                                    │               │
                                    │ - Ollama HTTP │
                                    │ - Gemma call  │
                                    │ - JSON parse  │
                                    └───────┬───────┘
                                            │
                                            ▼
                                    ┌───────────────┐
                                    │  Ollama       │
                                    │  (127.0.0.1)  │
                                    │  Gemma 3n/4   │
                                    └───────────────┘
```

---

## Data Flow

### Ingestion Pipeline (R2 — `ingest.py`)
```
PDF bytes (in memory)
    → extract_pages() [pdfplumber] → List[Page{page_num, text}]
    → split_into_clauses() [regex on numbering] → List[Clause{id, text, page_num, heading}]
    → build_index() [MiniLM embeddings] → InMemoryIndex{clauses, embeddings, metadata}
```

### Query Pipeline (R2+R3 — `retrieval.py` + `answer.py` + `guardrails.py`)
```
User Question
    → classify_question() [rules: normal / legal_verdict / out_of_scope]
    → IF legal_verdict: RETURN refusal + escalation (no LLM call)
    → search() top-3 passages [cosine similarity]
    → is_silent()? [threshold in code]
        → YES: RETURN "The document does not state this" (no LLM call)
        → NO:  CALL Gemma (local Ollama) with passages wrapped as untrusted data
    → verify_findings() [quotes must be exact substrings; failures dropped]
    → RETURN structured Answer{findings[], disclaimer, uncertainty, kind}
```

### UI Data Flow (R4 — `app.py`)
```
Upload → ingest_pdf() → store Document + Index in session_state
Question → answer_question() → render Answer in two-pane layout
Delete → clear session_state
```

---

## Component Ownership (Per PROJECT_MASTER.md Section 10)

| Role | Owner | Files | Key Deliverable |
|------|-------|-------|-----------------|
| **R1** | Model & Runtime | `src/llm.py`, `src/config.py`, `docs/benchmarks.md`, privacy evidence | Local Gemma answering; benchmark; offline test recording |
| **R2** | Ingestion & Retrieval | `src/ingest.py`, `src/retrieval.py` | Pages, clauses, top-3 passages with scores |
| **R3** | Answer Pipeline & Guardrails | `src/guardrails.py`, `src/prompts.py`, `src/answer.py` | Verified structured answers; silent, refusal, injection handling |
| **R4** | UI, Git Master, Docs | `app.py`, `tests/`, `README.md`, repo files | Working UI; clean public repo; submission pack |

**Rule:** One file, one owner. Cross-file changes via PR.

---

## Build Order (Dependency-Aware)

### Phase 1: Foundation (Hours 0-1.5) — R1 leads, all support
- [ ] Repo init, .gitignore, .streamlit/config.toml (telemetry off, bind 127.0.0.1)
- [ ] Ollama install + pull candidate models (gemma3n:e2b, gemma4:e2b, gemma4:e2b-it-qat)
- [ ] Benchmark protocol on same fictional lease (network disabled)
- [ ] Download MiniLM to `models/`, verify offline loading (HF_HUB_OFFLINE=1)
- [ ] Record chosen model in PROJECT_MASTER.md

### Phase 2: Ingestion & Retrieval (Hours 1.5-3.5) — R2 leads
- [ ] `ingest.py`: extract_pages(), split_into_clauses(), build_index()
- [ ] `retrieval.py`: build_index(), search(), InMemoryIndex class
- [ ] Test: 3 correct passages with page numbers for 5 test questions on sample leases

### Phase 3: Guardrails & Answer Pipeline (Hours 3.5-6.5) — R3 leads
- [ ] `guardrails.py`: classify_question(), is_silent(), verify_quotes(), injection_scan()
- [ ] `prompts.py`: system prompt, output schema (JSON), few-shot examples
- [ ] `answer.py`: orchestrate pipeline, call_llm(), postprocess()
- [ ] Tests T3 (citation check), T4 (silence), T5 (refusal) pass

### Phase 4: UI Integration (Hours 6.5-8) — R4 leads, all integrate
- [ ] `app.py`: Streamlit UI wired to real pipeline
- [ ] Two-pane layout: explanation | source passages | concerns | uncertainty | disclaimer
- [ ] Delete Session button, error messages, model-unavailable handling
- [ ] Full flow works end-to-end on one laptop

### Phase 5: Should-Haves & Polish (Hours 8-9) — Parallel
- [ ] Missing Promise Detector (R3) — topic checklist per doc type
- [ ] Prompt injection warning banner (R3 + R4)
- [ ] Benchmark table in README (R1 + R4)

### Phase 6: Offline Evidence & Submission (Hours 9-10) — R4 leads, all contribute
- [ ] Offline run (Wi-Fi off), connection monitor recording
- [ ] Temp file audit, code audit
- [ ] README polish, submission checklist complete

---

## Key Architectural Decisions

| Decision | Rationale |
|----------|-----------|
| **In-memory only** | Privacy requirement — no document text or embeddings on disk |
| **NumPy over FAISS** | <500 chunks; removes C++ dependency; simpler deploy |
| **Custom clause splitter** | Legal numbering patterns; LangChain char-split breaks MiniLM 256-token limit |
| **Code-enforced citations** | 2B model hallucinates quotes; substring check is deterministic |
| **Rule-based silence/refusal** | Model unreliable at "I don't know" and "I can't answer that" |
| **Single entry point: app.py** | Streamlit convention; simplifies demo launch |
| **Config per document type** | Extensible to employment/service without pipeline changes (section 4A) |
| **Ollama on 127.0.0.1 only** | Zero external connections; judges verify |

---

## Build Order Implications

- **R1 (Model) can start immediately** — independent of other roles
- **R2 (Ingestion) must complete before R3 (Answer)** — retrieval is prerequisite
- **R4 (UI) can build stub UI in parallel** — integrate in Phase 4
- **Phase 3 is critical path** — guardrails + answer pipeline are most complex
- **Benchmark (Phase 1) informs model choice** — if no model works by hour 3, cut scope per checkpoint rule