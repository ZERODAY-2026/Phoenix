# Requirements: ClauseGuard

**Defined:** 2026-10-18
**Core Value:** On-device document understanding with provable privacy guarantees — every explanation is grounded in verbatim citations from the user's document, runs entirely locally with zero network calls, and honestly admits when the document doesn't contain the answer.

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Ingestion

- [ ] **INGEST-01**: User can upload a text-based PDF and receive clear errors for scanned, encrypted, corrupt, or oversized files
- [ ] **INGEST-02**: System extracts text from PDF preserving page numbers using pdfplumber
- [ ] **INGEST-03**: System splits document into clauses by legal numbering patterns (1., 1.1, §1, Article 1) using custom regex splitter
- [ ] **INGEST-04**: System builds in-memory vector index from clauses using local MiniLM embeddings (no FAISS, no disk persistence)

### Retrieval

- [ ] **RETRIEVE-01**: System returns top-3 passages by cosine similarity for a given question
- [ ] **RETRIEVE-02**: Retrieved passages include verbatim text, page numbers, and similarity scores

### Guardrails

- [ ] **GUARD-01**: System classifies questions as normal / legal verdict / out of scope via rule-based classifier
- [ ] **GUARD-02**: System triggers "The document does not state this" via code-enforced similarity threshold before model call
- [ ] **GUARD-03**: System verifies every model quote as exact substring of source passage; drops failures silently
- [ ] **GUARD-04**: System refuses verdict-style questions ("is this legal/enforceable/should I sign?") with specific escalation text
- [ ] **GUARD-05**: System shows prompt injection warning banner when document contains instruction-like text
- [ ] **GUARD-06**: System displays permanent fixed disclaimer in UI (not model-generated): "This tool is for preliminary document understanding. It is not a lawyer and does not give legal advice. Please consult a qualified legal professional for decisions that matter."

### Answer Generation

- [ ] **ANSWER-01**: Gemma returns structured JSON: category, plain_language, quote, page, kind (explicit/interpretation/concern), uncertainty
- [ ] **ANSWER-02**: User can click "Summarise key terms" covering rent, deposit, notice period, termination, penalties, repairs
- [ ] **ANSWER-03**: Missing Promise Detector — fixed checklist of lease topics (deposit return, repairs, rent increase, early termination, notice period, late fees); shows "No clear condition found in the analysed text" when absent

### UI

- [ ] **UI-01**: Streamlit UI bound to 127.0.0.1, telemetry disabled, Delete Session button clears in-memory document/index/chat
- [ ] **UI-02**: Two-pane layout showing: explanation | source passages | concerns | uncertainty | disclaimer
- [ ] **UI-03**: Model-unavailable error message with no fake analysis shown

### Privacy

- [ ] **PRIV-01**: Offline demonstration — Wi-Fi off, connection monitor shows no external calls
- [ ] **PRIV-02**: No temporary files — in-memory processing only, no document text or embeddings written to disk
- [x] **PRIV-03**: Local embedding model loaded from disk with HF_HUB_OFFLINE=1 and TRANSFORMERS_OFFLINE=1
- [x] **PRIV-04**: Ollama bound to 127.0.0.1 only; no LAN serving in submitted demo

### Benchmarking

- [x] **BENCH-01**: Benchmark Gemma candidates (3n E2B, 4 E2B, 4 E2B-QAT) on same fictional lease with network disabled
- [x] **BENCH-02**: Record model size, peak RAM/VRAM, TTFT, tokens/sec, JSON validity %, quote accuracy %
- [ ] **BENCH-03**: Choose model meeting criteria: loads on 16GB CPU laptop, <2 min response, >90% JSON validity

### Documentation

- [ ] **DOCS-01**: README with scope, license, benchmark table, minimum specs, fictional sample lease
- [ ] **DOCS-02**: Submission checklist complete — all gates ticked, evidence pack recorded

### Testing

- [ ] **TEST-01**: Test suite covering T1-T7 (ingestion, retrieval, citations, silence, refusal, injection, ambiguity)

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Scanned PDF Support

- **SCAN-01**: Local OCR for scanned/image-only PDFs
- **SCAN-02**: Clear "needs OCR, not supported" message with graceful degradation

### Extended Document Types

- **EMP-01**: Employment contract support with own topic checklist and test set
- **SVC-01**: Service agreement support with own topic checklist and test set

### Advanced Features

- **ADV-01**: Contract Cross-Examiner — flag clauses that may conflict (e.g., deposit returned in 7 days vs 30 days); show both passages with "possible inconsistency, needs review"
- **ADV-02**: Two-version comparison — diff between two lease versions

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Legal verdicts (legal/illegal/valid/void/enforceable) | Gate L8 requirement; caps PS2 at 40 if violated; safety critical |
| Scanned/image-only PDFs (v1) | OCR adds complexity, Tesseract deps, accuracy issues; stretch only |
| Non-English documents | English only for v1; MiniLM is English-centric |
| Multi-document comparison | Out of scope per guide "state scope honestly"; stretch item |
| Cloud sync / multi-device | Violates on-device privacy guarantee |
| Auto document type detection | User must select type; "app never silently guesses it" |
| Model-generated disclaimer | Disclaimer must be fixed UI text, not model output |
| LangChain / FAISS / PyMuPDF | License, dependency, hidden network call risks |
| Remote LLM API fallback | Track requires fully on-device; any external call = privacy failure |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| INGEST-01 | Phase 2 | Pending |
| INGEST-02 | Phase 2 | Pending |
| INGEST-03 | Phase 2 | Pending |
| INGEST-04 | Phase 2 | Pending |
| RETRIEVE-01 | Phase 2 | Pending |
| RETRIEVE-02 | Phase 2 | Pending |
| GUARD-01 | Phase 3 | Pending |
| GUARD-02 | Phase 3 | Pending |
| GUARD-03 | Phase 3 | Pending |
| GUARD-04 | Phase 3 | Pending |
| GUARD-05 | Phase 3 | Pending |
| GUARD-06 | Phase 4 | Pending |
| ANSWER-01 | Phase 3 | Pending |
| ANSWER-02 | Phase 3 | Pending |
| ANSWER-03 | Phase 5 | Pending |
| UI-01 | Phase 4 | Pending |
| UI-02 | Phase 4 | Pending |
| UI-03 | Phase 4 | Pending |
| PRIV-01 | Phase 6 | Pending |
| PRIV-02 | Phase 2, 4, 6 | Pending |
| PRIV-03 | Phase 1 | Complete |
| PRIV-04 | Phase 1, 4 | Complete |
| BENCH-01 | Phase 1 | Complete |
| BENCH-02 | Phase 1 | Complete |
| BENCH-03 | Phase 1 | Pending |
| DOCS-01 | Phase 5, 6 | Pending |
| DOCS-02 | Phase 6 | Pending |
| TEST-01 | Phase 2, 3, 6 | Pending |

**Coverage:**

- v1 requirements: 27 total
- Mapped to phases: 27
- Unmapped: 0 ✓

---
*Requirements defined: 2026-10-18*
*Last updated: 2026-10-18 after Plan 04 completion*
