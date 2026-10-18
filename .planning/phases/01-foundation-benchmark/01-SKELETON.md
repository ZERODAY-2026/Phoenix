# Walking Skeleton — ClauseGuard

**Phase:** 1
**Generated:** 2026-10-18

## Capability Proven End-to-End

A developer can run `STUB_LLM=1 python -c "from src.llm import generate; print(generate('sys', 'prompt'))"` and receive a valid Answer-dict JSON without any network calls or model runtime — proving the LLM client contract, config singleton, and test harness are wired correctly.

## Architectural Decisions

| Decision | Choice | Rationale |
|---|---|---|
| **Framework** | Streamlit 1.38.0 (UI, Phase 4) + raw Python stack (no orchestration framework) | All hard constraints (local-only, MIT-compatible, no hidden network calls, Python-only) eliminate provider SDKs and multi-agent frameworks; retrieval is NumPy cosine over <500 clauses |
| **Data layer** | In-memory only (no database) | Privacy guarantee: nothing persists to disk; embeddings and indexes live only in RAM during a session |
| **Auth** | None (single-user, single-laptop) | No multi-user requirement; Delete Session button clears in-memory state |
| **Deployment target** | Single laptop, `ollama serve` on 127.0.0.1:11434 + `streamlit run app.py` | Hackathon demo runs entirely offline; judges verify zero external connections |
| **Directory layout** | `src/` (config, llm, future pipeline), `scripts/` (setup + benchmark), `tests/` (pytest), `sample_documents/` (fixtures), `models/` (gitignored embeddings), `docs/` (evidence) | Enforces `src/llm.py` as sole network importer; `models/` gitignored; `scripts/benchmark.py` independent of app code |
| **LLM runtime** | Ollama 0.20+ HTTP API on loopback only | MIT license, single binary, built-in timing stats (`eval_count`/`eval_duration`), `format: "json"` constrained decoding |
| **Model selection** | Benchmark-driven, locked in `src/config.py::MODEL_NAME` (D-04), overridable by `CLAUSEGUARD_MODEL` | Single source of truth in code; evidence in `docs/benchmarks.md`; decision recorded in `PROJECT_MASTER.md` §7.3 |
| **Embedding model** | all-MiniLM-L6-v2 via sentence-transformers 3.0.1, saved to `models/all-MiniLM-L6-v2/` | 384-dim, 256 token limit matches clause chunks; `save_pretrained`/`load` same code path; offline load with `HF_HUB_OFFLINE=1` |
| **Vector search** | NumPy cosine similarity (dot product on normalized vectors) | <500 clauses → no FAISS needed; removes C++ dependency; ~1ms latency |
| **PDF extraction** | pdfplumber 0.11.4 (MIT) | Extracts text with page numbers; works on in-memory bytes; no system deps |
| **Clause splitting** | Custom regex on legal numbering (1., 1.1, §1, Article 1) | LangChain char-split breaks MiniLM's 256 token window; full control, no hidden behavior |
| **Privacy enforcement** | Code-enforced: `OLLAMA_URL` hardcoded to 127.0.0.1, `HF_HUB_OFFLINE=1`/`TRANSFORMERS_OFFLINE=1` in tests, `netstat` evidence | No policy — architecture makes leakage impossible; verified by static test + capture |

## Stack Touched in Phase 1

- [x] Project scaffold: `src/__init__.py`, `pytest.ini`, `requirements.txt` (pinned), `.gitignore` (verify), `.streamlit/config.toml` (verify)
- [ ] Routing — N/A (no HTTP routes in Phase 1; Ollama daemon is external process)
- [ ] Database — N/A (in-memory only by design)
- [ ] UI — N/A (Streamlit UI is Phase 4)
- [ ] Deployment — `ollama serve` with pinned env + `scripts/download_embedding_model.py` + venv creation documented in README
- [ ] **LLM client contract** — `src/llm.py` with `check_model_ready()`, `generate()`, `ModelUnavailable`, `STUB_LLM=1` backend (D-02)
- [ ] **Config singleton** — `src/config.py` with all constants, `MODEL_NAME` from benchmark (D-03, D-04)
- [ ] **Embedding offline proof** — `scripts/download_embedding_model.py` + `tests/test_embedding_offline.py` (D-10, D-11, PRIV-03)
- [ ] **Loopback proof** — `tests/test_config.py` + `netstat` capture in `docs/evidence/` (D-12, PRIV-04)
- [ ] **Benchmark harness** — `scripts/benchmark.py` measuring 6 BENCH-02 metrics using Ollama's own stats (BENCH-01, BENCH-02)
- [ ] **Model selection** — Apply BENCH-03 criteria on CPU-only numbers, commit `config.py`, prune losers (BENCH-03, D-09)
- [ ] **Benchmark fixture** — `sample_documents/D1_clean_lease.pdf` (6-10 pages, 7 lease topics, fictional landlord) (D-05)

## Out of Scope (Deferred to Later Slices)

- PDF ingestion pipeline (`ingest.py`, `retrieval.py`) — Phase 2
- Guardrails and answer pipeline (`guardrails.py`, `answer.py`) — Phase 3
- Streamlit UI (`app.py`) — Phase 4
- Missing Promise Detector, injection banner polish, README benchmark table — Phase 5
- Offline demonstration recording, submission checklist, evidence pack assembly — Phase 6
- Reconciling `docs/GIT_WORKFLOW.md` with direct-to-main push (D-13) — Phase 6
- Scanned PDF support, employment/service agreements, cross-examiner, version comparison — v2 (out of scope)

## Subsequent Slice Plan

Each later phase adds one vertical slice on top of this skeleton without altering its architectural decisions:

- **Phase 2 (Ingestion & Retrieval):** User uploads text PDF → extracts pages with page numbers → splits into clauses by legal numbering → builds in-memory vector index → question returns top-3 passages with verbatim text, page numbers, similarity scores
- **Phase 3 (Guardrails & Answer Pipeline):** Question classifier routes normal/legal-verdict/out-of-scope → silence threshold triggers "document does not state this" → every model quote verified as exact substring → prompt injection warning banner → Gemma returns valid JSON with all Answer fields → "Summarise key terms" covers 6 predefined topics
- **Phase 4 (UI Integration):** Streamlit app launches on 127.0.0.1 → upload → question → answer → delete session works → two-pane layout (explanation | source passages | concerns | uncertainty | disclaimer) → model-unavailable error shown gracefully → full pipeline runs offline (Wi-Fi off)
- **Phase 5 (Should-Haves & Polish):** Missing Promise Detector checks 6 lease topics → injection banner visible and accurate → README includes benchmark table + honest scope statement → fictional sample lease included
- **Phase 6 (Evidence & Submission):** Offline demonstration recorded (Wi-Fi off, connection monitor) → temp file audit → code audit (only network call is 127.0.0.1:11434) → all gates evidenced → README complete → requirements.txt pinned → test suite passes → submission checklist 100%