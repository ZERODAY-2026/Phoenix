# Project Research — Stack

**Domain:** On-device legal document triage (rental agreements)
**Date:** 2026-10-18
**Context:** Greenfield — ZeroDay OSS Hacktoberfest 2026, 10-hour window, 4-person team

---

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

---

## Explicitly Rejected

| Rejected | Reason |
|----------|--------|
| **PyMuPDF (fitz)** | AGPL-3.0 — license friction with MIT repo; Gate G1 and rubric C4 judge license quality |
| **LangChain** | Character-based splitter (not tokens); MiniLM truncates at 256 WP so 500-token chunks silently cut; hidden network calls; adds many dependencies |
| **FAISS** | Overkill for <500 chunks; NumPy cosine is simpler, no C++ deps, no install issues on Windows |
| **Remote LLM API** | Track requires fully on-device; any external call = privacy failure |
| **React + FastAPI + TypeScript** | Team cannot debug complex stack in 10h; vibe-coding friendly means Python-only |
| **Ollama on 0.0.0.0 (LAN)** | No auth; content-carrying connection violates "on-device" rule; judges monitor connections |

---

## Version Pinning Strategy

After stack validation, run `pip freeze > requirements.txt` to pin every transitive dependency. Key direct deps to pin:
- `streamlit==1.38.0`
- `pdfplumber==0.11.4`
- `sentence-transformers==3.0.1`
- `numpy==1.26.4`
- `requests==2.32.3`
- `pydantic==2.8.2`
- `pytest==8.3.2`

---

## Confidence Summary

- **High confidence** (9/10): Streamlit, pdfplumber, NumPy search, requests, pytest — well-established, match constraints exactly
- **Medium-high** (8/10): sentence-transformers + MiniLM — standard for local embeddings, but must verify offline loading works
- **Medium** (7/10): Gemma 3n/4 E2B via Ollama — guide requirement, but model availability/performance on team laptops needs benchmark validation (hour 0-1.5)
- **Custom code** (9/10): Clause splitter — simple regex on legal numbering patterns; full control, no hidden behavior