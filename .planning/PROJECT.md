# ClauseGuard

## What This Is

ClauseGuard is a **fully on-device** assistant that reads a **rental agreement (PDF)**, explains clauses in plain language, points to the exact passage and page behind every statement, separates "what the document says" from "what might be a concern", says **"the document does not state this"** when it is silent, and **declines to give legal verdicts** (it recommends a qualified legal professional). Nothing about the document or the user's questions ever leaves the laptop.

**What we are not building:** a lawyer, a legality checker, a cloud chatbot, or a multi-document-type platform.

Target: ZeroDay OSS Hacktoberfest 2026, IIIT Dharwad — Track PS2, Agentic AI: Private Legal Document Triage Agent.

## Core Value

**On-device document understanding with provable privacy guarantees** — every explanation is grounded in verbatim citations from the user's document, runs entirely locally with zero network calls, and honestly admits when the document doesn't contain the answer.

## Business Context

- **Customer**: Hackathon judges and tenants reviewing rental agreements
- **Revenue model**: N/A (hackathon project, open source)
- **Success metric**: Pass all mandatory gates (L1-L10), achieve competitive PS2 score
- **Strategy notes**: See docs/PROJECT_MASTER.md for full scoring strategy

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] **INGEST-01**: Upload text-based PDF; clear errors for scanned/encrypted/corrupt/oversized files
- [ ] **INGEST-02**: Extract pages with page numbers preserved using pdfplumber (MIT licensed)
- [ ] **INGEST-03**: Split into clauses by heading/numbering regex (custom splitter, no LangChain)
- [ ] **INGEST-04**: Build in-memory vector index with local MiniLM embeddings (no FAISS required)
- [ ] **RETRIEVE-01**: Search top-3 passages by cosine similarity for a given question
- [ ] **RETRIEVE-02**: Return passages with verbatim text, page numbers, and similarity scores
- [ ] **GUARD-01**: Classify questions (normal / legal verdict / out of scope) via rule-based classifier
- [ ] **GUARD-02**: Silence threshold triggers "The document does not state this" before model call
- [ ] **GUARD-03**: Model output quotes verified as exact substrings of source passages; failures dropped
- [ ] **GUARD-04**: Verdict-style questions refused with specific escalation text (not generic)
- [ ] **GUARD-05**: Prompt injection warning banner when document contains instruction-like text
- [ ] **GUARD-06**: Fixed disclaimer shown permanently in UI (not model-generated)
- [ ] **ANSWER-01**: Structured JSON output from Gemma: category, plain_language, quote, page, kind, uncertainty
- [ ] **ANSWER-02**: "Summarise key terms" one-click action covering rent, deposit, notice, termination, penalties, repairs
- [ ] **ANSWER-03**: Missing Promise Detector — checklist of lease topics showing "No clear condition found" when absent
- [ ] **UI-01**: Streamlit UI bound to 127.0.0.1, telemetry disabled, Delete Session button clears memory
- [ ] **UI-02**: Two-pane layout: explanation | source passages | concerns | uncertainty | disclaimer
- [ ] **UI-03**: Model-unavailable error message with no fake analysis
- [ ] **PRIV-01**: Offline demonstration — Wi-Fi off, connection monitor shows no external calls
- [ ] **PRIV-02**: No temporary files — in-memory processing, no document text or embeddings written to disk
- [ ] **PRIV-03**: Local embedding model loaded from disk with HF_HUB_OFFLINE=1 and TRANSFORMERS_OFFLINE=1
- [ ] **PRIV-04**: Ollama bound to 127.0.0.1 only; no LAN serving in submitted demo
- [ ] **BENCH-01**: Benchmark Gemma candidates (3n E2B, 4 E2B, 4 E2B-QAT) on same fictional lease
- [ ] **BENCH-02**: Record model size, peak RAM/VRAM, TTFT, tokens/sec, JSON validity, quote accuracy
- [ ] **BENCH-03**: Choose model meeting criteria: loads on 16GB CPU laptop, <2 min response, >90% JSON validity
- [ ] **DOCS-01**: README with scope, license, benchmark table, minimum specs, fictional sample lease
- [ ] **DOCS-02**: Submission checklist complete — all gates ticked, evidence pack recorded
- [ ] **TEST-01**: Test suite covering T1-T7 (ingestion, retrieval, citations, silence, refusal, injection, ambiguity)

### Out of Scope

- **Scanned/image-only PDFs** — Show clear "needs OCR, not supported" message (stretch only)
- **Legal verdicts** — Never decide if clause is legal/valid/enforceable (gate requirement)
- **Non-English documents** — English only for v1
- **Multi-document comparison** — Stretch only (item 14)
- **Local OCR for scanned PDFs** — Stretch only (item 13)
- **Two-version comparison** — Stretch only (item 14)
- **Employment contracts / Service agreements** — Planned for post-hackathon (section 4A)
- **Loan/credit/purchase agreements, Terms of Service** — Not planned
- **LangChain dependency** — Rejected (character-based splitting, hidden network calls, AGPL risk from PyMuPDF)
- **FAISS dependency** — Optional; NumPy cosine similarity sufficient for few hundred chunks
- **Remote API fallback** — Explicitly forbidden by track requirements

## Context

- **Technical environment**: Python 3.10+, Streamlit, Ollama, sentence-transformers, pdfplumber, NumPy
- **Team**: 4 members (3 CPU-only laptops, 1 RTX 2050 4GB) — parallel role ownership (R1-R4)
- **Prior work**: Comprehensive planning in docs/PROJECT_MASTER.md, ARCHITECTURE.md, PRIVACY.md, TEST_PLAN.md, TEAM_ROLES_AND_CONTRACTS.md, VIBE_CODING_PROMPTS.md
- **Known issues**: Gemma 3n/4 E2B may exceed 4GB VRAM on RTX 2050 — expect partial GPU offload; benchmark to pick demo machine

## Constraints

- **Timeline**: 10-hour hackathon window (confirm exact deadline with organizers)
- **Tech stack**: Streamlit + Python only (no React/FastAPI/TypeScript)
- **License**: MIT compatible — pdfplumber (MIT) over PyMuPDF (AGPL-3.0)
- **Privacy**: Zero network calls during demo; all processing on single laptop
- **Model**: Must use Gemma 3n E2B or Gemma 4 E2B class (guide requirement)
- **Hardware**: Must run on CPU-only 16GB RAM laptop; benchmark on team laptops
- **Dependencies**: Pin all versions in requirements.txt; no hidden network calls (HF_HUB_OFFLINE=1)
- **Git**: Entry file is `app.py`; .gitignore excludes *.pdf except sample_documents/; PR-based workflow

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Streamlit + Python only (no React/FastAPI) | Team cannot debug complex stack in 10h; vibe-coding friendly | ✓ Good |
| pdfplumber over PyMuPDF | MIT license vs AGPL-3.0; gate G1 and rubric C4 judge license quality | ✓ Good |
| Custom clause splitter (regex) over LangChain | LangChain splits by chars not tokens; MiniLM truncates at 256 WP; legal clauses need sentence boundaries | ✓ Good |
| NumPy cosine similarity over FAISS | Few hundred chunks don't need FAISS; removes dependency | ✓ Good |
| Code-enforced citations (substring check) not model | 2B model will invent quotes; gate requires "no systematic fabrication" | ✓ Good |
| Rule-based verdict refusal + silence threshold | Model cannot reliably refuse; code decides, model explains | ✓ Good |
| Single-machine demo (no LAN Ollama) | Guide requires on-device; judges monitor connections; Ollama has no auth | ✓ Good |
| In-memory processing only (no temp files) | Judges check temp files; leftover embeddings = privacy finding | ✓ Good |
| Embedding model downloaded at setup, loaded locally | sentence-transformers fetches from HF on first use; breaks offline requirement | ✓ Good |
| Rental agreements only for v1 (supported) | Narrow scope is strength; guide says "state scope honestly and test within it" | ✓ Good |
| Employment/Service types planned but not started | Midpoint check (hour 5) decides; rental must pass tests first | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-10-18 after initialization*