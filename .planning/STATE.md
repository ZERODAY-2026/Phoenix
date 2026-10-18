---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
current_phase: 1 (Foundation & Benchmark)
status: in-progress
stopped_at: Completed Plan 04 (STUB_LLM=1 Contract Tests)
last_updated: "2026-10-18T20:20:00.000Z"
progress:
  total_phases: 6
  completed_phases: 0
  total_plans: 5
  completed_plans: 4
  percent: 0
---

# Project State

**Project:** ClauseGuard
**Initialized:** 2026-10-18
**Current Phase:** 1 (Foundation & Benchmark)
**Mode:** mvp

---

## Project Reference

See: .planning/PROJECT.md (updated 2026-10-18 after initialization)

**Core value:** On-device document understanding with provable privacy guarantees — every explanation is grounded in verbatim citations from the user's document, runs entirely locally with zero network calls, and honestly admits when the document doesn't contain the answer.

**Current focus:** Phase 1: Foundation & Benchmark

---

## Phase Status

| Phase | Name | Status | Started | Completed |
|-------|------|--------|---------|-----------|
| 1 | Foundation & Benchmark | In Progress | 2026-10-18 | — |
| 2 | Ingestion & Retrieval | Pending | — | — |
| 3 | Guardrails & Answer Pipeline | Pending | — | — |
| 4 | UI Integration | Pending | — | — |
| 5 | Should-Haves & Polish | Pending | — | — |
| 6 | Evidence & Submission | Pending | — | — |

---

## Active Requirements (v1)

All 27 v1 requirements are Active (hypotheses until shipped and validated):

- INGEST-01 through INGEST-04
- RETRIEVE-01, RETRIEVE-02
- GUARD-01 through GUARD-06
- ANSWER-01 through ANSWER-03
- UI-01 through UI-03
- PRIV-01 through PRIV-04
- BENCH-01 through BENCH-03
- DOCS-01, DOCS-02
- TEST-01

---

## Validated Requirements

(None yet — ship to validate)

---

## Out of Scope (Confirmed)

- Legal verdicts
- Scanned/image-only PDFs (v1)
- Non-English documents
- Multi-document comparison
- Cloud sync / multi-device
- Auto document type detection
- Model-generated disclaimer
- LangChain / FAISS / PyMuPDF
- Remote LLM API fallback

---

## Key Decisions Logged

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Streamlit + Python only | Team cannot debug complex stack in 10h | ✓ Good |
| pdfplumber over PyMuPDF | MIT vs AGPL-3.0; gate G1/rubric C4 | ✓ Good |
| Custom clause splitter | LangChain char-split breaks MiniLM 256 limit | ✓ Good |
| NumPy cosine over FAISS | <500 chunks; removes C++ dep | ✓ Good |
| Code-enforced citations | 2B model hallucinates quotes | ✓ Good |
| Rule-based silence/refusal | Model unreliable at "I don't know" | ✓ Good |
| Single-machine demo | Guide requires on-device; judges monitor | ✓ Good |
| In-memory only | Judges check temp files | ✓ Good |
| Local embedding model | sentence-transformers fetches from HF | ✓ Good |
| Rental only for v1 | Narrow scope is strength | ✓ Good |
| MODEL_NAME overridable by CLAUSEGUARD_MODEL env | Benchmark decides final model; D-04 single source of truth | ✓ Good |
| OLLAMA_URL hardcoded to 127.0.0.1 | PRIV-04: loopback-only, never LAN in submitted repo | ✓ Good |
| STUB_LLM=1 backend in llm.py | Unblocks R2/R3/R4 during model benchmarking | ✓ Good |
| agentic.py deleted | Contained banned gemma2:2b; submission blocker per SUBMISSION_CHECKLIST §F | ✓ Good |
| save_pretrained() for embedding download | SBERT 3.x+ modern API; saver/loader same code path (D-10) | ✓ Good |
| 5-file completeness check before load | Partial download is most likely false pass (D-11) | ✓ Good |
| pytest skipif for gitignored models/ | Fresh clone passes CI before one-time setup (D-11) | ✓ Good |
| Static config tests for privacy boundary | Proves loopback URL + local path at code level (D-12) | ✓ Good |
| Benchmark harness uses Ollama HTTP API directly | RESEARCH.md Pattern 2; no app imports; reproducible metrics | ✓ Good |
| Quote accuracy = normalized verbatim substring | Matches ARCHITECTURE.md §3.2 verify_findings algorithm | ✓ Good |
| JSON validity = parse + Answer-dict schema | format:json + 7 required keys per finding (ARCHITECTURE.md §4) | ✓ Good |
| Peak RAM via OS process (Get-Process) | Avoids ollama ps SIZE mmap double-count (Pitfall 3) | ✓ Good |
| D1 landlord "Aldric Thorne" for Phase 6 leak search | Unique fictional name per PRIVACY.md §9 | ✓ Good |

---

## Context Updates

- **Team:** 4 members (3 CPU-only, 1 RTX 2050 4GB) — parallel roles R1-R4
- **Timeline:** 10-hour hackathon window (confirm exact deadline with organizers)
- **Model decision pending:** Benchmark in Phase 1 will select between Gemma 3n E2B, 4 E2B, 4 E2B-QAT
- **Demo machine:** To be determined by benchmark results (CPU-only vs GPU laptop)

---

## Next Actions

1. Run `/gsd-discuss-phase 1` to gather context and clarify approach for Phase 1
2. Run `/gsd-plan-phase 1` to create detailed execution plan
3. Begin Phase 1: repo setup, Ollama install, model pulls, benchmark

---

*State updated: 2026-10-18 after initialization*

## Session

**Last session:** 2026-10-18T20:20:00.000Z
**Stopped at:** Completed Plan 04 (STUB_LLM=1 Contract Tests)
**Resume file:** .planning/phases/01-foundation-benchmark/01-04-SUMMARY.md
