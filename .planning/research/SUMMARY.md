# Project Research Summary

**Project:** ClauseGuard — On-device legal document triage for rental agreements
**Event:** ZeroDay OSS Hacktoberfest 2026, IIIT Dharwad — Track PS2
**Date:** 2026-10-18
**Milestone:** Greenfield (first release)

---

## Key Findings

### Stack (from STACK.md)

| Layer | Choice | Confidence | Key Rationale |
|-------|--------|------------|---------------|
| UI | Streamlit 1.38+ | High | Vibe-coding friendly; single-file; telemetry off; binds 127.0.0.1 |
| PDF | pdfplumber 0.11+ | High | MIT license (vs PyMuPDF AGPL); page numbers; in-memory bytes |
| Splitting | Custom regex (ingest.py) | High | Legal numbering patterns; LangChain char-split breaks MiniLM 256 limit |
| Embeddings | sentence-transformers + all-MiniLM-L6-v2 | Medium-High | 384-dim, fast CPU, 256 token limit matches clauses; offline load |
| Vector Search | NumPy cosine | High | <500 chunks; no FAISS needed; removes C++ dep |
| LLM Runtime | Ollama 0.20+ | High | Local Gemma; only network code is localhost HTTP |
| Model | Gemma 3n E2B or 4 E2B | Medium | Guide requirement; benchmark to pick; QAT build for 4GB VRAM |
| HTTP | requests | High | Only localhost call |
| Testing | pytest | High | Standard |

**Explicitly Rejected:** PyMuPDF (AGPL), LangChain (char-split, hidden calls), FAISS (overkill), Remote APIs (privacy fail), React/FastAPI (too complex for 10h).

---

### Table Stakes (from FEATURES.md) — 15 Must-Haves

| Category | Features |
|----------|----------|
| **Ingestion** | PDF upload/validation, page-aware extraction, clause segmentation, local embedding index |
| **Retrieval** | Semantic search (top-3), cosine similarity |
| **Guardrails** | Structured JSON output, citation verification (substring check), silence detection, verdict refusal, prompt injection defense |
| **UI** | Permanent disclaimer, Delete Session, model-unavailable handling, key terms summary |
| **Privacy** | Offline demo evidence (Wi-Fi off, connection monitor, no temp files) |

### Differentiators (from FEATURES.md) — 6 Competitive Advantages

1. **Missing Promise Detector** — Fixed lease topic checklist; "No clear condition found" when absent
2. **Uncertainty Field** — Jurisdiction dependence, ambiguous wording, insufficient evidence
3. **Kind Classification** — `explicit` / `interpretation` / `concern` in separate UI panes
4. **Specific Escalation** — Per-type text: "Ask tenant advice service or lawyer to review deposit/termination"
5. **Connection Monitor Evidence** — Live proof of zero external calls
6. **Benchmark Transparency** — README table: size, RAM, TTFT, tok/s, JSON%, quote%

### Anti-Features (Deliberately Not Building)

- Legal verdicts (gate failure), scanned PDFs (stretch), multi-doc comparison (stretch), non-English, cloud sync, auto type detection, model-generated disclaimer

---

### Architecture (from ARCHITECTURE.md)

**Component Ownership (4 parallel roles):**
- **R1 (Model/Runtime):** `llm.py`, `config.py`, benchmarks, privacy evidence
- **R2 (Ingestion/Retrieval):** `ingest.py`, `retrieval.py` — pages, clauses, top-3 passages
- **R3 (Answer/Guardrails):** `guardrails.py`, `prompts.py`, `answer.py` — verified answers, silence, refusal, injection
- **R4 (UI/Git/Docs):** `app.py`, `tests/`, `README.md`, submission pack

**Data Flow:**
```
PDF bytes → extract_pages → split_clauses → build_index (in-memory)
Question → classify → search top-3 → silence? → "doc silent" : Gemma → verify quotes → Answer
```

**Build Order (6 phases, 10 hours):**
1. **Phase 1 (0-1.5h):** Repo, Ollama, benchmark, MiniLM download, model selection
2. **Phase 2 (1.5-3.5h):** Ingestion + retrieval working on sample leases
3. **Phase 3 (3.5-6.5h):** Guardrails + answer pipeline; T3/T4/T5 tests pass
4. **Phase 4 (6.5-8h):** UI wired to real pipeline; end-to-end on one laptop
5. **Phase 5 (8-9h):** Missing Promise Detector, injection banner, benchmark table
6. **Phase 6 (9-10h):** Offline run, connection monitor, README, submission checklist

---

### Critical Pitfalls (from PITFALLS.md) — Top 5

| Pitfall | Impact | Prevention | Phase |
|---------|--------|------------|-------|
| **Model too slow on CPU** | Demo fails | Benchmark all laptops hour 0; QAT fallback; show passages first; cut scope at hour 3 | 1, 4 |
| **Gemma not working in Ollama** | No LLM → fail gates | Test both models; check Ollama ≥0.20; llama.cpp fallback | 1 |
| **Hidden network call** | Privacy gate fails | HF_HUB_OFFLINE=1; local MiniLM; Streamlit telemetry off; bind 127.0.0.1; offline test | 1, 6 |
| **Model invents quotes** | Grounding gate fails | Code-enforced substring check; drop failures; T3 test 20 prompts | 3 |
| **Vibe-coded code unclear** | Bugs, can't fix | Owner explains file in 2min; AI comments rationale; one file one owner; PRs | All |

---

## Implications for Roadmap

### Phase Structure (aligned to architecture build order)

| Phase | Focus | Owner | Key Requirements | Success Criteria |
|-------|-------|-------|------------------|------------------|
| **1** | Foundation & Benchmark | R1 (all support) | BENCH-01, BENCH-02, BENCH-03, PRIV-03 | Chosen model recorded; runs on CPU laptop; <2 min; >90% JSON valid |
| **2** | Ingestion & Retrieval | R2 | INGEST-01..04, RETRIEVE-01..02 | 3 correct passages + pages for 5 test questions |
| **3** | Guardrails & Answer Pipeline | R3 | GUARD-01..06, ANSWER-01 | T3 (citations), T4 (silence), T5 (refusal) pass |
| **4** | UI Integration | R4 (all integrate) | UI-01..03, ANSWER-02..03, PRIV-01..02 | Full flow works end-to-end on one laptop |
| **5** | Should-Haves | Parallel | DIFF-01 (Missing Promise), GUARD-05 (injection), DIFF-06 (benchmark table) | Optional features behave honestly |
| **6** | Evidence & Submission | R4 (all contribute) | PRIV-01..04, DOCS-01..02, TEST-01 | Every submission checklist box ticked |

### Risk Mitigations Built Into Phases

- **Phase 1 checkpoint (hour 3):** If no model works → cut to summary + clause lookup only
- **Phase 3 tests T3/T4/T5:** Must pass before UI integration — catches grounding/refusal/silence early
- **Phase 4 on single laptop:** Validates privacy architecture before evidence collection
- **Phase 6 offline run:** Final gate — Wi-Fi off, connection monitor, no temp files

### Scope Boundaries Reinforced

- **In scope:** Rental agreements only (Supported); English; text PDF + txt; free-text questions + key terms summary
- **Out of scope:** Scanned PDFs, legal verdicts, non-English, multi-doc, employment/service (planned post-hackathon)
- **License:** MIT compatible only — pdfplumber over PyMuPDF

---

## Sources

- STACK.md — Stack research with versioned recommendations and rejections
- FEATURES.md — 15 table stakes, 6 differentiators, 8 anti-features with dependencies
- ARCHITECTURE.md — Component diagram, data flows, ownership, 6-phase build order
- PITFALLS.md — 15 pitfalls with warning signs, prevention, phase mapping
- PROJECT_MASTER.md — Original hackathon planning (sections 4, 5, 7, 8, 9, 11, 12, 13, 14)
- Hackathon guide requirements L1-L10 and PS2 rubric

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack choices | High | All constraints mapped; rejections justified |
| Feature scope | High | Directly from PROJECT_MASTER.md + guide requirements |
| Architecture | High | Build order matches dependency graph; parallel roles defined |
| Pitfall coverage | High | Covers all gate failure modes + team/hackathon risks |
| Timeline feasibility | Medium | 10h is tight; Phase 3 (3h) is critical path; checkpoint rule mitigates |

---

**Next Step:** Generate REQUIREMENTS.md from table stakes + differentiators, then ROADMAP.md with 6 phases mapping every v1 requirement.