<!-- GSD:project-start source:PROJECT.md -->

## Project

**ClauseGuard**

ClauseGuard is a **fully on-device** assistant that reads a **rental agreement (PDF)**, explains clauses in plain language, points to the exact passage and page behind every statement, separates "what the document says" from "what might be a concern", says **"the document does not state this"** when it is silent, and **declines to give legal verdicts** (it recommends a qualified legal professional). Nothing about the document or the user's questions ever leaves the laptop.

**What we are not building:** a lawyer, a legality checker, a cloud chatbot, or a multi-document-type platform.

Target: ZeroDay OSS Hacktoberfest 2026, IIIT Dharwad — Track PS2, Agentic AI: Private Legal Document Triage Agent.

**Core Value:** **On-device document understanding with provable privacy guarantees** — every explanation is grounded in verbatim citations from the user's document, runs entirely locally with zero network calls, and honestly admits when the document doesn't contain the answer.

### Constraints

- **Timeline**: 10-hour hackathon window (confirm exact deadline with organizers)
- **Tech stack**: Streamlit + Python only (no React/FastAPI/TypeScript)
- **License**: MIT compatible — pdfplumber (MIT) over PyMuPDF (AGPL-3.0)
- **Privacy**: Zero network calls during demo; all processing on single laptop
- **Model**: Must use Gemma 3n E2B or Gemma 4 E2B class (guide requirement)
- **Hardware**: Must run on CPU-only 16GB RAM laptop; benchmark on team laptops
- **Dependencies**: Pin all versions in requirements.txt; no hidden network calls (HF_HUB_OFFLINE=1)
- **Git**: Entry file is `app.py`; .gitignore excludes *.pdf except sample_documents/; PR-based workflow

<!-- GSD:project-end -->

<!-- GSD:stack-start source:research/STACK.md -->

## Technology Stack

## Recommended Stack

| Layer | Choice | Version | License | Confidence | Rationale |
|-------|--------|---------|---------|------------|-----------|
| **UI Framework** | Streamlit | 1.38+ | Apache-2.0 | High | Vibe-coding friendly; single-file app; built-in widgets for file upload, chat, buttons; telemetry easily disabled; binds to 127.0.0.1 |
| **PDF Text Extraction** | pdfplumber | 0.11+ | MIT | High | MIT license (vs PyMuPDF AGPL-3.0); extracts text with page numbers; works on in-memory bytes; no system dependencies |
| **Clause Splitting** | Custom regex splitter (in `ingest.py`) | — | Ours | High | Legal clauses have numbered headings (1., 1.1, §1); regex on numbering/headings preserves clause boundaries; LangChain splits by chars not tokens, MiniLM truncates at 256 WP |
| **Embeddings** | sentence-transformers + all-MiniLM-L6-v2 | 3.0+ / model card | Apache-2.0 | High | 384-dim, fast on CPU, 256 token limit matches clause-sized chunks; download once at setup to `models/`; load locally with `HF_HUB_OFFLINE=1` |
| **Vector Search** | NumPy cosine similarity | 1.26+ | BSD | High | Few hundred chunks max — no need for FAISS; removes dependency; ~1ms search latency; in-memory index |
| **LLM Runtime** | Ollama | 0.20+ | MIT | High | Runs Gemma 3n/4 locally; HTTP API on 127.0.0.1:11434; only network code in app; v0.20+ required for Gemma 4 support |
| **Model** | Gemma 3n E2B **or** Gemma 4 E2B (benchmark both) | Ollama tags: `gemma3n:e2b`, `gemma4:e2b` | Gemma ToU / Apache-2.0 (verify) | Medium | Guide names "Gemma 3n/4 class"; E2B fits 16GB RAM; QAT build (`gemma4:e2b-it-qat` ~4.3GB) for 4GB VRAM laptop; benchmark to decide |
| **HTTP Client** | requests | 2.32+ | Apache-2.0 | High | Only network call is to localhost Ollama; simple, no async complexity |
| **Testing** | pytest | 8.0+ | MIT | High | Standard, fixtures, parametrize for test cases |
| **Config** | Python dataclasses / pydantic | 3.10+ / 2.8+ | MIT | Medium | Type-safe config for document types, thresholds, model params |

## Explicitly Rejected

| Rejected | Reason |
|----------|--------|
| **PyMuPDF (fitz)** | AGPL-3.0 — license friction with MIT repo; Gate G1 and rubric C4 judge license quality |
| **LangChain** | Character-based splitter (not tokens); MiniLM truncates at 256 WP so 500-token chunks silently cut; hidden network calls; adds many dependencies |
| **FAISS** | Overkill for <500 chunks; NumPy cosine is simpler, no C++ deps, no install issues on Windows |
| **Remote LLM API** | Track requires fully on-device; any external call = privacy failure |
| **React + FastAPI + TypeScript** | Team cannot debug complex stack in 10h; vibe-coding friendly means Python-only |
| **Ollama on 0.0.0.0 (LAN)** | No auth; content-carrying connection violates "on-device" rule; judges monitor connections |

## Version Pinning Strategy

- `streamlit==1.38.0`
- `pdfplumber==0.11.4`
- `sentence-transformers==3.0.1`
- `numpy==1.26.4`
- `requests==2.32.3`
- `pydantic==2.8.2`
- `pytest==8.3.2`

## Confidence Summary

- **High confidence** (9/10): Streamlit, pdfplumber, NumPy search, requests, pytest — well-established, match constraints exactly
- **Medium-high** (8/10): sentence-transformers + MiniLM — standard for local embeddings, but must verify offline loading works
- **Medium** (7/10): Gemma 3n/4 E2B via Ollama — guide requirement, but model availability/performance on team laptops needs benchmark validation (hour 0-1.5)
- **Custom code** (9/10): Clause splitter — simple regex on legal numbering patterns; full control, no hidden behavior

<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->

## Conventions

Conventions not yet established. Will populate as patterns emerge during development.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->

## Architecture

Architecture not yet mapped. Follow existing patterns found in the codebase.
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->

## Project Skills

No project skills found. Add skills to any of: `.claude/skills/`, `.agents/skills/`, `.cursor/skills/`, `.github/skills/`, or `.codex/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->

## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:

- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->

<!-- GSD:profile-start -->

## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
