# Team Roles and Function Contracts

Four people, four roles, **one owner per file**. Everyone codes against the same function signatures ("contracts") below so the pieces fit when merged. If you must change a signature, tell the whole team and update this file first.

## 1. Mapping from the old plans

| Old name (uploaded plans) | New name | Why it changed |
|---|---|---|
| `rag.py` with `ingest_pdf(file_path) -> bool` and `search_clauses(query)` | `src/ingest.py` + `src/retrieval.py` | Old version saved the index to disk and read from a file path; new version works in memory |
| `agent.py` with `get_legal_answer(query, chunks) -> str` | `src/answer.py` with `answer_question(question, index) -> dict` | Returns a structured, verified dict, not free text |
| `app.py` / `ui.py` | `app.py` | One entry file name everywhere |
| Ollama at `http://<LAPTOP_1_IP>:11434` | `http://127.0.0.1:11434` | Final demo must be single-machine |
| `gemma2:2b` | chosen Gemma 3n / Gemma 4 E2B | Gemma 2 is not the edge class named in the guide |

## 2. Roles

### R1: Model, runtime and privacy evidence (laptop with RTX 2050)

**Owns:** `src/llm.py`, `src/config.py`, `docs/benchmarks.md`, `docs/privacy_audit.md`, `docs/evidence/`

**Deliverables**
1. Ollama installed; candidate models pulled; `ollama list` screenshot
2. Benchmark table for each candidate (size, RAM/VRAM, time to first token, tokens per second, JSON validity, quote accuracy)
3. `llm.py` with `generate()` and `check_model_ready()`, plus a **stub backend** (`STUB_LLM=1`) that returns a fixed valid JSON so the other three can work without a model
4. Written recommendation of the final model, with numbers, recorded in `PROJECT_MASTER.md` section 7.3
5. Offline test, connection monitoring, temp-file check and the evidence pack (with R4 filming)

**Done when:** a teammate on a CPU-only laptop can run the stub; the real model answers locally with Wi-Fi off; benchmark and evidence files exist.

### R2: Ingestion and retrieval (CPU laptop)

**Owns:** `src/ingest.py`, `src/retrieval.py`, `sample_documents/` (with R4)

**Deliverables**
1. `extract_pages()` and `split_into_clauses()` working on 3 sample leases plus one awkward layout
2. Clear failure modes: not a PDF, encrypted, scanned/low text, too large
3. `build_index()` and `search()` using the local embedding model, in memory only
4. A small script `scripts/inspect_retrieval.py` that prints the top 3 passages and scores for a question, used to calibrate the silent threshold

**Done when:** for 10 test questions, the correct clause is in the top 3 in at least 8 cases; the scanned sample is rejected cleanly.

### R3: Answer pipeline and guardrails (CPU laptop)

**Owns:** `src/guardrails.py`, `src/prompts.py`, `src/answer.py`

**Deliverables**
1. `classify_question()` for verdict-style questions ("is this legal/enforceable/valid", "should I sign", "can they do this")
2. `is_silent()` using the calibrated threshold
3. `scan_for_injection()` for instruction-like text inside documents
4. `verify_findings()` with substring check and banned-phrase filter
5. `prompts.py` and `answer_question()` tying it together
6. Unit tests for every guardrail

**Done when:** tests T3, T4, T5, T7 in `docs/TEST_PLAN.md` pass with the real model and with the stub.

### R4: UI, Git master, documentation and submission (CPU laptop)

**Owns:** `app.py`, `tests/`, `README.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, `LICENSE`, `.gitignore`, `.streamlit/config.toml`, `docs/SUBMISSION_CHECKLIST.md`

**Deliverables**
1. Repo created, licence added, branch protection (at least: no direct pushes to `main`), team invited
2. Skeleton files pushed in the first hour so everyone has a file to work in
3. Streamlit two-column UI: upload and loaded-document view on the left; chat on the right; evidence shown beside the explanation
4. Delete-session button; clear error messages; permanent disclaimer
5. README with setup, run, scope, limits, benchmarks, privacy summary
6. Submission checklist fully ticked; demo recording assembled

**Done when:** a stranger can follow the README on a clean laptop and reach a working demo.

## 3. Contracts (exact signatures)

```python
# src/config.py
MODEL_NAME = "TO_BE_DECIDED"          # e.g. "gemma3n:e2b" or "gemma4:e2b-it-qat"
OLLAMA_URL = "http://127.0.0.1:11434"  # NEVER a LAN address in the submitted repo
EMBED_MODEL_PATH = "models/all-MiniLM-L6-v2"
TOP_K = 3
SILENT_THRESHOLD = 0.30                # placeholder; calibrate (see TEST_PLAN)
MAX_UPLOAD_MB = 15
MIN_CHARS_PER_PAGE = 200               # below this on average => treat as scanned
REQUEST_TIMEOUT_S = 180
```

```python
# src/ingest.py
class UnsupportedDocument(Exception): ...

def extract_pages(file_bytes: bytes, filename: str = "") -> list[dict]:
    """[{"page": 1, "text": "..."}, ...]. Raises UnsupportedDocument with a
    user-friendly message for non-PDF, encrypted, corrupt, scanned or oversized input.
    Never writes to disk."""

def split_into_clauses(pages: list[dict]) -> list[dict]:
    """[{"id": "p3-c2", "page": 3, "heading": "4. Deposit" or None, "text": "..."}, ...]
    Ids are unique and stable for a given document."""
```

```python
# src/retrieval.py
def build_index(clauses: list[dict]) -> dict:
    """In-memory index: {"clauses": [...], "embeddings": ndarray}. No disk writes."""

def search(index: dict, query: str, top_k: int = 3) -> list[dict]:
    """Best first. Each item: {"id","page","heading","text","score"} with score in [0, 1]."""
```

```python
# src/llm.py
class ModelUnavailable(Exception): ...

def check_model_ready() -> tuple[bool, str]:
    """(ok, message). Tries Ollama on OLLAMA_URL and checks MODEL_NAME exists."""

def generate(system: str, prompt: str, json_mode: bool = True) -> str:
    """Returns the raw text from the model. Raises ModelUnavailable on any failure.
    If env STUB_LLM=1, returns a fixed valid JSON string without calling a model."""
```

```python
# src/guardrails.py
def classify_question(question: str) -> str:
    """'normal' | 'legal_verdict' | 'out_of_scope'"""

def is_silent(passages: list[dict], threshold: float | None = None) -> bool: ...

def scan_for_injection(text: str) -> list[str]:
    """Returns suspicious lines (for a UI warning). Never executes or follows them."""

def verify_findings(findings: list[dict], passages: list[dict]) -> tuple[list[dict], list[dict]]:
    """(kept, dropped). Kept findings have page and passage text attached by code."""
```

```python
# src/answer.py
DISCLAIMER = ("This tool is for preliminary document understanding. It is not a lawyer "
              "and does not give legal advice. Please consult a qualified legal "
              "professional for decisions that matter.")

def answer_question(question: str, index: dict, doc_type: str = "rental") -> dict:
    """Returns the Answer dict defined in docs/ARCHITECTURE.md section 4."""
```

```python
# app.py (Streamlit)
# imports: from src.ingest import extract_pages, split_into_clauses, UnsupportedDocument
#          from src.retrieval import build_index
#          from src.answer import answer_question, DISCLAIMER
#          from src.llm import check_model_ready
#          from src.guardrails import scan_for_injection
```

## 4. Working agreements

1. **One file, one owner.** Need a change elsewhere? Message the owner or open a Pull Request they review.
2. **Small steps.** Ask your AI assistant for one function at a time; run it; commit it.
3. **Test before you push.** Run `pytest` and the stub run. Never push code you have not run.
4. **No secrets, no real documents, no model files in Git.** Ever.
5. **No network code** outside `src/llm.py` (localhost only). If your AI assistant adds an import you do not recognise, ask it what it does.
6. **Explain your file.** Each owner should be able to explain their file in two minutes for the demo (rubric C8).
7. **Daily 10-minute sync:** what is done, what is blocked, what is next.
8. **Use the stub.** R2, R3 and R4 should not wait for the real model.
9. **Fictional documents only** while developing.

## 5. Handover checkpoints

| When | Who hands what to whom |
|---|---|
| Hour 1 | R4 pushes the skeleton and `config.py` stub; R1 pushes `llm.py` with the stub backend |
| Hour 3 | R2 pushes `ingest.py` and `retrieval.py`; R3 starts using real passages instead of canned ones |
| Hour 6.5 | R3 pushes `answer.py`; R4 wires the UI to it |
| Hour 8 | Everyone stops adding features; R1 and R4 begin the offline evidence run |

## 6. Multiple document types: ownership and contract

- `src/doc_types/rental.py` is written by R3 in the first release. It must match the `DocType` fields in `docs/ARCHITECTURE.md` section 10.
- Employment and service configs start only after the midpoint check in `docs/PROJECT_MASTER.md` section 4A.
- `answer_question` now takes `doc_type` (default `"rental"`). Any caller that does not pass it gets rental behaviour; R4's UI always passes the user's selection.
- A type's `status` in its config must not say `supported` until `docs/TEST_RESULTS.md` has a passing section for it. Changing the status is a PR reviewed by R4.
