# Phase 1: Foundation & Benchmark - Pattern Map

**Mapped:** 2026-10-18
**Files analyzed:** 15 new/modified files
**Analogs found:** 12 / 15 (3 files have no code analog — config-driven or content files)

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `src/config.py` | config | request-response | `docs/TEAM_ROLES_AND_CONTRACTS.md` §3 (contract) | exact-contract |
| `src/llm.py` | service | request-response | `agentic.py` (URL validation, Ollama call pattern) / RESEARCH.md Pattern 1 | role-match |
| `src/__init__.py` | config | N/A | Standard Python package pattern | exact |
| `scripts/download_embedding_model.py` | utility | file-I/O | RESEARCH.md Pattern 3 (D-10 code example) | exact |
| `scripts/benchmark.py` | utility | batch | RESEARCH.md Pattern 2 (harness code example) | exact |
| `tests/conftest.py` | test | N/A | Standard pytest pattern (Wave 0 gap) | exact |
| `tests/test_config.py` | test | request-response | RESEARCH.md Pattern 3 (D-12 code example) | exact |
| `tests/test_llm_stub.py` | test | request-response | RESEARCH.md Pattern 1 (STUB_LLM contract) | exact |
| `tests/test_embedding_offline.py` | test | file-I/O | RESEARCH.md Pattern 3 (D-11 code example) | exact |
| `sample_documents/D1_clean_lease.pdf` | data | file-I/O | `docs/TEST_PLAN.md` §1 (specification) | spec-match |
| `sample_documents/README.md` | config | file-I/O | Existing `sample_documents/README.md` | exact |
| `docs/benchmarks.md` | config | file-I/O | `docs/TEST_PLAN.md` §3 table format | role-match |
| `docs/evidence/` | config | file-I/O | `docs/PRIVACY.md` §11 (evidence pack inventory) | role-match |
| `requirements.txt` | config | file-I/O | RESEARCH.md `## Standard Stack` version table | exact |
| `pytest.ini` | config | N/A | Standard pytest config | exact |
| `agentic.py` (DELETE) | — | — | N/A (anti-pattern — contains banned `gemma2:2b`) | anti-pattern |

---

## Pattern Assignments

### `src/config.py` (config, request-response)

**Analog:** `docs/TEAM_ROLES_AND_CONTRACTS.md` §3 (frozen contract)

**Constants pattern** (exact signature from contract):
```python
# Source: docs/TEAM_ROLES_AND_CONTRACTS.md §3
MODEL_NAME = "TO_BE_DECIDED"          # e.g. "gemma3n:e2b" or "gemma4:e2b-it-qat"
OLLAMA_URL = "http://127.0.0.1:11434"  # NEVER a LAN address in the submitted repo
EMBED_MODEL_PATH = "models/all-MiniLM-L6-v2"
TOP_K = 3
SILENT_THRESHOLD = 0.30                # placeholder; calibrate (see TEST_PLAN)
MAX_UPLOAD_MB = 15
MIN_CHARS_PER_PAGE = 200               # below this on average => treat as scanned
REQUEST_TIMEOUT_S = 180
```

**Environment override pattern** (D-04):
```python
import os
MODEL_NAME = os.getenv("CLAUSEGUARD_MODEL", "gemma4:e2b-it-qat")  # benchmark winner filled in
```

**Key conventions from RESEARCH.md:**
- All constants are module-level, UPPER_SNAKE_CASE
- No classes, no logic — pure constants
- `OLLAMA_URL` must be loopback (tested in `tests/test_config.py`)
- `EMBED_MODEL_PATH` must be relative local path (tested in `tests/test_config.py`)

---

### `src/llm.py` (service, request-response)

**Analog:** RESEARCH.md **Pattern 1** (STUB_LLM=1 backend) + `agentic.py` lines 122-179 (URL validation) + RESEARCH.md `## Code Examples` (Ollama streaming)

**Imports pattern:**
```python
# Source: RESEARCH.md Pattern 1 + agentic.py imports
import os
import json
import requests
from src.config import MODEL_NAME, OLLAMA_URL, REQUEST_TIMEOUT_S
```

**Exception pattern** (contract line 109):
```python
class ModelUnavailable(Exception):
    """Raised when Ollama is unreachable or model not installed."""
    pass
```

**`check_model_ready()` pattern** (contract lines 111-113 + RESEARCH.md Pattern 1):
```python
def check_model_ready() -> tuple[bool, str]:
    """(ok, message). Tries Ollama on OLLAMA_URL and checks MODEL_NAME exists."""
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=REQUEST_TIMEOUT_S)
        r.raise_for_status()
        names = {m["name"] for m in r.json().get("models", [])}
    except Exception as exc:
        return False, f"Ollama is not reachable at {OLLAMA_URL} ({exc}). Start it with: ollama serve"
    if MODEL_NAME not in names:
        return False, f"Model {MODEL_NAME!r} is not installed. Run: ollama pull {MODEL_NAME}"
    return True, "ready"
```

**STUB_LLM=1 pattern** (RESEARCH.md Pattern 1 lines 312-328):
```python
# Fixed valid JSON matching docs/ARCHITECTURE.md §4 Answer dict shape
_STUB = json.dumps({
    "status": "answered",
    "question": "stub",
    "findings": [{
        "category": "deadline", "kind": "explicit",
        "plain_language": "Stub explanation produced without a model.",
        "quote": "the deposit shall be returned within thirty (30) days",
        "passage_id": "p3-c2", "page": 3, "uncertainty": "none",
    }],
    "passages": [], "jurisdiction_note": "", "escalation": "",
    "dropped_findings": 0, "message": "",
})
```

**`generate()` core pattern** (contract lines 114-116 + RESEARCH.md Pattern 1 lines 325-336):
```python
def generate(system: str, prompt: str, json_mode: bool = True) -> str:
    """Returns the raw text from the model. Raises ModelUnavailable on any failure.
    If env STUB_LLM=1, returns a fixed valid JSON string without calling a model."""
    if os.environ.get("STUB_LLM") == "1":
        return _STUB

    payload = {
        "model": MODEL_NAME,
        "system": system,
        "prompt": prompt,
        "stream": False,
        "format": "json" if json_mode else None,  # omit key entirely when False
        "think": False,                     # Gemma 4 thinking mode OFF (Pitfall 2)
        "keep_alive": "5m",
        "options": {"temperature": 0, "num_ctx": 8192},
    }
    # Remove None values (Ollama rejects format: null)
    payload = {k: v for k, v in payload.items() if v is not None}

    try:
        r = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=REQUEST_TIMEOUT_S)
        r.raise_for_status()
        data = r.json()
    except requests.RequestException as exc:
        raise ModelUnavailable(f"Ollama request failed: {exc}") from exc
    except ValueError as exc:
        raise ModelUnavailable(f"Ollama returned invalid JSON: {exc}") from exc

    text = data.get("response", "").strip()
    if not text:
        raise ModelUnavailable("Ollama returned empty response")
    return text
```

**URL validation pattern** (from `agentic.py` lines 122-179, adapted for loopback-only):
```python
# NOTE: config.py already hardcodes OLLAMA_URL = "http://127.0.0.1:11434"
# No dynamic URL validation needed in llm.py — the constant IS the validation.
# If you need a helper for tests, see tests/test_config.py pattern.
```

**Error handling pattern:**
- All network errors wrapped in `ModelUnavailable`
- No bare `except:` — always catch specific exceptions
- `format: "json"` omitted when `json_mode=False` (test T13 needs this)

---

### `src/__init__.py` (config, N/A)

**Analog:** Standard Python namespace package pattern

**Minimal pattern:**
```python
# Makes `from src.config import ...` unambiguous under pytest
# Python 3.11+ namespace packages work without this, but explicit is clearer
```

---

### `scripts/download_embedding_model.py` (utility, file-I/O)

**Analog:** RESEARCH.md **Pattern 3** (D-10 code example lines 608-615)

**Exact pattern from research:**
```python
# scripts/download_embedding_model.py   -- SETUP ONLY: online, no user document
from pathlib import Path
from sentence_transformers import SentenceTransformer

TARGET = Path("models/all-MiniLM-L6-v2")
TARGET.parent.mkdir(parents=True, exist_ok=True)
SentenceTransformer("all-MiniLM-L6-v2").save_pretrained(str(TARGET))
print(f"saved -> {TARGET}")
```

**Key points from RESEARCH.md:**
- Runs **once at setup**, online, no user document involved (PRIVACY.md §6)
- `save_pretrained` is the documented modern equivalent of `.save()` (SBERT 3.x+)
- Saver and loader share code path → on-disk shape is correct by construction
- `models/` is gitignored (already in `.gitignore`)

---

### `scripts/benchmark.py` (utility, batch)

**Analog:** RESEARCH.md **Pattern 2** (BENCH-02 harness) + `## Code Examples` (lines 531-590)

**Imports pattern:**
```python
import json
import time
import requests
import sys
from pathlib import Path
```

**Warm-up pattern** (RESEARCH.md lines 537-539):
```python
def warm_up(base: str, model: str) -> None:
    """Load the model so load_duration does not pollute TTFT."""
    requests.post(f"{base}/api/generate", json={"model": model, "prompt": ""}, timeout=600)
```

**Prompt execution pattern** (RESEARCH.md lines 541-564):
```python
def run_prompt(base: str, model: str, system: str, prompt: str, passage_text: str) -> dict:
    payload = {
        "model": model, "system": system, "prompt": prompt,
        "stream": True, "format": "json", "think": False, "keep_alive": "5m",
        "options": {"temperature": 0, "num_ctx": 8192},
    }
    t0 = time.perf_counter()
    ttft = None
    text = ""
    stats = {}
    with requests.post(f"{base}/api/generate", json=payload, stream=True, timeout=600) as r:
        r.raise_for_status()
        for line in r.iter_lines():
            if not line:
                continue
            chunk = json.loads(line)
            piece = chunk.get("response", "")
            if piece and ttft is None:
                ttft = time.perf_counter() - t0          # first token, load excluded by warm-up
            text += piece
            if chunk.get("done"):
                stats = chunk                          # eval_count, eval_duration, total_duration, ...
    tok_s = (stats.get("eval_count", 0) / stats["eval_duration"] * 1e9) if stats.get("eval_duration") else None
    return {"text": text, "ttft_s": ttft, "tok_s": tok_s, "stats": stats}
```

**Model footprint pattern** (RESEARCH.md lines 566-573):
```python
def model_footprint(base: str, model: str) -> dict:
    """VRAM from the daemon; size on disk from /api/tags."""
    ps = requests.get(f"{base}/api/ps", timeout=30).json().get("models", [])
    vram = next((m["size_vram"] for m in ps if m["model"] == model), 0)
    tags = requests.get(f"{base}/api/tags", timeout=30).json().get("models", [])
    t = next((m for m in tags if m["name"] == model), {})
    return {"size_bytes": t.get("size"), "size_vram_bytes": vram,
            "digest": t.get("digest"), "quant": t.get("details", {}).get("quantization_level")}
```

**JSON validity check** (RESEARCH.md lines 575-584) — matches `docs/ARCHITECTURE.md` §4:
```python
def is_valid_answer_json(text: str) -> bool:
    """Valid JSON == parses AND matches docs/ARCHITECTURE.md section 4."""
    try:
        obj = json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return False
    if not isinstance(obj, dict) or "status" not in obj or "findings" not in obj:
        return False
    required = {"category", "kind", "plain_language", "quote", "passage_id", "page", "uncertainty"}
    return all(isinstance(f, dict) and required <= set(f) for f in obj["findings"])
```

**Quote accuracy pattern** (RESEARCH.md lines 586-589) — matches `docs/ARCHITECTURE.md` §3.2 `verify_findings`:
```python
def quote_is_verbatim(quote: str, passage_text: str) -> bool:
    """The Phase-3 verify_findings algorithm at 1-line scale."""
    norm = lambda s: " ".join(s.split()).casefold()
    return bool(quote) and norm(quote) in norm(passage_text)
```

**Prompt set** (RESEARCH.md Pattern 2 — 8 answerable prompts from `docs/TEST_PLAN.md` §3):
```python
# Each prompt is a triple: (question, passage_id, passage_text)
# passage_text is verbatim from D1 lease, wrapped as:
# <<<DOCUMENT_PASSAGE id="p3-c2" page="3">>>...text...<<<END_PASSAGE>>>
PROMPT_SET = [
    ("How much is the monthly rent and when is it due?", "pX-cY", "verbatim rent clause..."),
    ("How long does the landlord have to return the deposit?", "pX-cY", "verbatim deposit clause..."),
    ("How much notice do I need to give to end the lease?", "pX-cY", "verbatim notice clause..."),
    ("What happens if I pay rent late?", "pX-cY", "verbatim late fee clause..."),
    ("Can I keep a pet?", "pX-cY", "verbatim pets clause..."),
    ("Who pays for repairs to the plumbing?", "pX-cY", "verbatim repairs clause..."),
    ("Summarise the termination conditions", "pX-cY", "verbatim termination clause..."),
    # 8th: one of {sublet, utilities, rent increase} once D1 text exists
]
```

**Output format** — appends one markdown row to `docs/benchmarks.md` per (model, machine):
```markdown
| Model | Machine | Size (GB) | Peak RAM (GB) | Peak VRAM (GB) | TTFT (s) | Tok/s | JSON Valid % | Quote Acc % |
|-------|---------|-----------|---------------|----------------|----------|-------|--------------|-------------|
| gemma3n:e2b | CPU-only-16GB | 7.8 | 8.2 | 0 | 3.1 | 12.4 | 100% | 87.5% |
```

---

### `tests/conftest.py` (test, N/A)

**Analog:** Standard pytest configuration (RESEARCH.md Wave 0 gap)

**Pattern:**
```python
# tests/conftest.py
import os
import sys
from pathlib import Path

# Ensure repo root is importable for `from src.config import ...`
sys.path.insert(0, str(Path(__file__).parent.parent))

# Offline mode for all tests — PRIV-03 / PRIV-04 guardrails
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
```

---

### `tests/test_config.py` (test, request-response)

**Analog:** RESEARCH.md **Pattern 3** (D-12 code example lines 415-426)

**Exact pattern from research:**
```python
# tests/test_config.py  -- PRIV-04 (D-12), no network, no model
from urllib.parse import urlsplit
from src import config

def test_ollama_url_is_loopback():
    host = urlsplit(config.OLLAMA_URL).hostname
    assert host in {"127.0.0.1", "localhost", "::1"}, f"OLLAMA_URL is not loopback: {config.OLLAMA_URL}"

def test_embed_model_path_is_local_relative():
    p = config.EMBED_MODEL_PATH
    assert not p.startswith(("/", "\\")) and ":" not in p, f"EMBED_MODEL_PATH is not a local relative path: {p}"
```

---

### `tests/test_llm_stub.py` (test, request-response)

**Analog:** RESEARCH.md **Pattern 1** (STUB_LLM contract) + `docs/TEAM_ROLES_AND_CONTRACTS.md` §3

**Pattern:**
```python
# tests/test_llm_stub.py  -- BENCH-02 (D-02), STUB_LLM=1 contract
import os
import json
import pytest
from src.llm import generate, ModelUnavailable, check_model_ready

def test_stub_returns_valid_json_without_network(monkeypatch):
    monkeypatch.setenv("STUB_LLM", "1")
    # No network call should happen — if it does, requests will fail (no Ollama)
    out = generate("system", "prompt", json_mode=True)
    obj = json.loads(out)
    assert obj["status"] == "answered"
    assert "findings" in obj
    assert isinstance(obj["findings"], list)
    # Verify Answer-dict shape (ARCHITECTURE.md §4)
    required = {"category", "kind", "plain_language", "quote", "passage_id", "page", "uncertainty"}
    for f in obj["findings"]:
        assert required <= set(f.keys())

def test_stub_json_mode_false_returns_string(monkeypatch):
    monkeypatch.setenv("STUB_LLM", "1")
    out = generate("system", "prompt", json_mode=False)
    assert isinstance(out, str)
    assert len(out) > 0

def test_check_model_ready_structure():
    # Structure test only — real check needs Ollama running
    ok, msg = check_model_ready()
    assert isinstance(ok, bool)
    assert isinstance(msg, str)
```

---

### `tests/test_embedding_offline.py` (test, file-I/O)

**Analog:** RESEARCH.md **Pattern 3** (D-11 code example lines 428-453)

**Exact pattern from research:**
```python
# tests/test_embedding_offline.py  -- PRIV-03 (D-11)
import os
import pathlib
import pytest

MODEL_DIR = pathlib.Path("models/all-MiniLM-L6-v2")
# The set that makes the directory loadable *and* complete. A partial download
# (e.g. weights without modules.json) is the most likely false pass.
REQUIRED = ["config.json", "modules.json", "model.safetensors", "tokenizer.json", "tokenizer_config.json"]

pytestmark = pytest.mark.skipif(
    not MODEL_DIR.is_dir(),
    reason="models/all-MiniLM-L6-v2/ absent - run: python scripts/download_embedding_model.py (online, one-time)",
)

def test_local_model_dir_is_complete():
    missing = [f for f in REQUIRED if not (MODEL_DIR / f).exists()]
    assert not missing, f"Embedding model directory is incomplete, missing: {missing}"

def test_loads_and_embeds_with_networking_off(monkeypatch):
    monkeypatch.setenv("HF_HUB_OFFLINE", "1")
    monkeypatch.setenv("TRANSFORMERS_OFFLINE", "1")
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(str(MODEL_DIR))     # local path => no Hub lookup
    vec = model.encode(["The deposit shall be returned within thirty days."])
    assert vec.shape[0] == 1 and vec.shape[1] == 384
```

**Key decision from RESEARCH.md line 455:** The `skipif` is deliberate — a fresh clone has no `models/` (gitignored), so a hard failure would break `pytest` for a judge before setup. The **evidence** for PRIV-03 is the recorded passing run in `docs/TEST_RESULTS.md`, not the mere existence of the test.

---

### `sample_documents/README.md` (config, file-I/O)

**Analog:** Existing `sample_documents/README.md` (lines 1-14)

**Pattern — update the D1-D7 table:**
```markdown
# Sample documents

All files here are **fictional** and written by the team for testing. They contain no real people, addresses or terms. They are released under the project licence.

| File | Purpose |
|---|---|
| `D1_clean_lease.pdf` | Baseline numbered lease |
| `D2_conflicting_lease.pdf` | Deposit return stated as 7 days and as 30 days |
| `D3_vague_lease.pdf` | Vague wording ("reasonable notice") |
| `D4_injection_lease.pdf` | Contains an instruction aimed at the AI, to test resistance |
| `D5_layout_lease.pdf` | Two columns, headers/footers, tables |
| `D7_scanned_lease.pdf` | Image-only, to test the "unsupported" message |
```

**D-05 requirement:** D1 must be 6-10 pages, numbered clauses covering rent, deposit (30 days), notice (2 months), repairs, pets, termination, late fee. Fictional landlord name (for Phase 6 temp-file leak search per `docs/PRIVACY.md` §9).

---

### `docs/benchmarks.md` (config, file-I/O)

**Analog:** `docs/TEST_PLAN.md` §3 table format + RESEARCH.md Pattern 2 output format

**Structure:**
```markdown
# Benchmark Results

**Recorded:** 2026-10-18
**Machines:** RTX-2050-laptop, CPU-only-16GB-laptop
**Fixture:** D1_clean_lease.pdf (8 answerable prompts)
**Ollama env:** OLLAMA_HOST=127.0.0.1, OLLAMA_NUM_PARALLEL=1, OLLAMA_MAX_LOADED_MODELS=1

## Results Table

| Model | Machine | Size (GB) | Peak RAM (GB) | Peak VRAM (GB) | TTFT (s) | Tok/s | JSON Valid % | Quote Acc % |
|-------|---------|-----------|---------------|----------------|----------|-------|--------------|-------------|
| gemma3n:e2b | RTX-2050-laptop | 7.8 | X.X | X.X | X.X | X.X | XX% | XX% |
| gemma3n:e2b | CPU-only-16GB | 7.8 | X.X | 0 | X.X | X.X | XX% | XX% |
| gemma4:e2b | RTX-2050-laptop | X.X | X.X | X.X | X.X | X.X | XX% | XX% |
| gemma4:e2b | CPU-only-16GB | X.X | X.X | 0 | X.X | X.X | XX% | XX% |
| gemma4:e2b-it-qat | RTX-2050-laptop | 4.3 | X.X | X.X | X.X | X.X | XX% | XX% |
| gemma4:e2b-it-qat | CPU-only-16GB | 4.3 | X.X | 0 | X.X | X.X | XX% | XX% |

## Selection Record

**Chosen model:** `gemma4:e2b-it-qat` (2026-10-18, R1, numbers: CPU-only loads, <2min, 100% JSON valid, highest quote accuracy)
**Recorded in:** `src/config.py` `MODEL_NAME` and `docs/PROJECT_MASTER.md` §7.3

## Request Configuration (for reproducibility)

```json
{
  "stream": true,
  "format": "json",
  "think": false,
  "keep_alive": "5m",
  "options": { "temperature": 0, "num_ctx": 8192 }
}
```

**Note on JSON validity granularity:** With N=8 prompts, ">90%" requires 8/8 = 100% (7/8 = 87.5% fails). This is recorded explicitly per RESEARCH.md Pattern 2 granularity caveat.
```

---

### `docs/evidence/` (config, file-I/O)

**Analog:** `docs/PRIVACY.md` §11 (evidence pack inventory)

**Pattern:** Directory created in Phase 1, receives `netstat` capture:
```bash
# Capture command (RESEARCH.md line 602)
netstat -ano | findstr 11434        # expect 127.0.0.1:11434, never 0.0.0.0:11434
```
Save output to `docs/evidence/loopback_bind_YYYYMMDD.txt`

---

### `requirements.txt` (config, file-I/O)

**Analog:** RESEARCH.md `## Standard Stack` version table (lines 103-112)

**Pinned pattern (resolve at execution time per RESEARCH.md lines 155-166):**
```text
streamlit==1.38.0
pdfplumber==0.11.4
sentence-transformers==3.0.1
numpy==1.26.4
requests==2.32.3
pytest==8.3.2
```
**Note:** `torch` and `transformers` arrive transitively — do not pin directly unless `pip freeze` includes them.

---

### `pytest.ini` (config, N/A)

**Analog:** Standard pytest config (RESEARCH.md Wave 0 gap line 738)

**Pattern:**
```ini
[pytest]
testpaths = tests
pythonpath = .
```

---

### `agentic.py` (DELETE — anti-pattern)

**Anti-pattern reference** (RESEARCH.md Pitfall 5, lines 509-513):
- Contains `MODEL_NAME = "gemma2:2b"` — **banned** by `docs/PROJECT_MASTER.md` §2 correction #1
- Contains network imports (`requests`, `urllib.parse.urlsplit`, `ipaddress`)
- `docs/SUBMISSION_CHECKLIST.md` §F requires `grep -rni gemma2 .` to return nothing
- `docs/PRIVACY.md` §10 audit greps for these exact imports

**Action:** Delete in Phase 1 (preferred) or move to gitignored `tmp/`. Verify with `git grep -ni gemma2`.

---

## Shared Patterns

### Loopback Binding Enforcement
**Source:** `docs/TEAM_ROLES_AND_CONTRACTS.md` §3 (`OLLAMA_URL = "http://127.0.0.1:11434"`), RESEARCH.md D-07, `docs/PRIVACY.md` §5
**Apply to:** `src/config.py`, `src/llm.py`, `tests/test_config.py`, `docs/evidence/` capture
```python
# Hardcoded in config.py — single source of truth
OLLAMA_URL = "http://127.0.0.1:11434"
```
**Launch command** (RESEARCH.md line 596-599):
```cmd
set OLLAMA_HOST=127.0.0.1
set OLLAMA_NUM_PARALLEL=1
set OLLAMA_MAX_LOADED_MODELS=1
ollama serve
```

### Offline Mode Enforcement
**Source:** `docs/PRIVACY.md` §6, RESEARCH.md Pattern 3
**Apply to:** `tests/conftest.py`, `tests/test_embedding_offline.py`, `scripts/download_embedding_model.py` (setup only, online)
```python
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
# Load from local path only:
SentenceTransformer("models/all-MiniLM-L6-v2")
```

### STUB_LLM=1 Contract
**Source:** `docs/TEAM_ROLES_AND_CONTRACTS.md` §3, RESEARCH.md Pattern 1
**Apply to:** `src/llm.py`, `tests/test_llm_stub.py`
```python
if os.environ.get("STUB_LLM") == "1":
    return _STUB  # Fixed valid Answer-dict JSON
```

### Answer Dict Schema Validation
**Source:** `docs/ARCHITECTURE.md` §4, RESEARCH.md `is_valid_answer_json()`
**Apply to:** `src/llm.py` (stub), `scripts/benchmark.py`, `tests/test_llm_stub.py`
```python
required = {"category", "kind", "plain_language", "quote", "passage_id", "page", "uncertainty"}
all(isinstance(f, dict) and required <= set(f) for f in obj["findings"])
```

### Quote Verification (Verbatim Substring)
**Source:** `docs/ARCHITECTURE.md` §3.2, RESEARCH.md `quote_is_verbatim()`
**Apply to:** `scripts/benchmark.py`, future `src/guardrails.py`
```python
norm = lambda s: " ".join(s.split()).casefold()
return bool(quote) and norm(quote) in norm(passage_text)
```

### Gemma 4 Thinking Mode OFF
**Source:** RESEARCH.md Pitfall 2, Pattern 1, Pattern 2
**Apply to:** `src/llm.py`, `scripts/benchmark.py`
```python
"think": False,  # Always — prevents reasoning block pollution
"options": {"temperature": 0, "num_ctx": 8192}
```

### Warm-up Before Measurement
**Source:** RESEARCH.md Pattern 2 (non-negotiable), Pitfall 2
**Apply to:** `scripts/benchmark.py`
```python
# Always warm up before measuring TTFT/tok-s
warm_up(base, model)  # Excludes load_duration from TTFT
```

### Peak RAM Measurement (OS, not Ollama)
**Source:** RESEARCH.md Pitfall 3, Pattern 2
**Apply to:** `scripts/benchmark.py`
```python
# Windows: sample Ollama runner process working set (Get-Process)
# NOT ollama ps SIZE (double-counts mmap'd weights)
# VRAM from /api/ps size_vram only
```

---

## No Analog Found

Files with no close code match in the codebase (planner should use RESEARCH.md patterns or specs directly):

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `sample_documents/D1_clean_lease.pdf` | data | file-I/O | Content file — written from `docs/TEST_PLAN.md` §1 spec, no code analog |
| `docs/evidence/` | config | file-I/O | Evidence directory — created per `docs/PRIVACY.md` §11, no code analog |
| `agentic.py` (DELETE) | — | — | Anti-pattern — contains banned model and network code; delete per Pitfall 5 |

---

## Metadata

**Analog search scope:** `agentic.py`, `docs/TEAM_ROLES_AND_CONTRACTS.md`, `docs/ARCHITECTURE.md`, `docs/PRIVACY.md`, `docs/TEST_PLAN.md`, `README.md`, `sample_documents/README.md`, `.planning/research/STACK.md`, `.planning/research/PITFALLS.md`, `.planning/research/SUMMARY.md`, RESEARCH.md (this phase)

**Files scanned:** 12 existing files + 5 research docs
**Pattern extraction date:** 2026-10-18
**Key contracts referenced:** `docs/TEAM_ROLES_AND_CONTRACTS.md` §3 (frozen signatures), `docs/ARCHITECTURE.md` §4 (Answer dict), §5 (prompt contract)

---

## Pattern Mapping Complete

**Phase:** 1 - Foundation & Benchmark
**Files classified:** 15
**Analogs found:** 12 / 15

### Coverage
- Files with exact contract analog: 5 (`src/config.py`, `src/llm.py`, `scripts/download_embedding_model.py`, `scripts/benchmark.py`, `tests/*`)
- Files with role-match analog: 4 (`sample_documents/README.md`, `docs/benchmarks.md`, `requirements.txt`, `pytest.ini`)
- Files with spec-only analog (no code): 3 (`D1_clean_lease.pdf`, `docs/evidence/`, `agentic.py` DELETE)
- Files with no analog needed (standard patterns): 3 (`src/__init__.py`, `tests/conftest.py`)

### Key Patterns Identified
1. **Contract-first constants** — `src/config.py` is the single source of truth for `MODEL_NAME`, `OLLAMA_URL`, etc. (D-04)
2. **STUB_LLM=1 unblocks the team** — `src/llm.py` returns fixed valid Answer-dict JSON without network (hour-1 handover)
3. **Loopback-only binding** — `OLLAMA_URL` hardcoded to `127.0.0.1`, enforced by test and `netstat` evidence (PRIV-04)
4. **Offline-first embeddings** — `HF_HUB_OFFLINE=1` + `TRANSFORMERS_OFFLINE=1` + local path load (PRIV-03)
5. **Benchmark harness uses Ollama's own stats** — `eval_count`/`eval_duration` for tok/s, `/api/ps` `size_vram` for VRAM, OS process for RAM
6. **Warm-up mandatory** — Model load excluded from TTFT for comparable numbers
7. **Quote accuracy = verbatim substring** — Same algorithm as Phase 3 `verify_findings()` (whitespace/case normalized)
8. **JSON validity = parse + schema** — `format: "json"` + required Answer-dict keys (not just parseability)
9. **Gemma 4 thinking mode OFF** — `think: false` on every request to prevent metric inflation
10. **Pull-first, measure-later** — 16.4 GB downloads start before any code work

### File Created
`.planning/phases/01-foundation-benchmark/01-PATTERNS.md`

### Ready for Planning
Pattern mapping complete. Planner can now reference analog patterns in PLAN.md files.