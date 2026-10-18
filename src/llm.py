# Source: RESEARCH.md Pattern 1 + agentic.py imports
import os
import json
import requests
from src.config import MODEL_NAME, OLLAMA_URL, REQUEST_TIMEOUT_S


class ModelUnavailable(Exception):
    """Raised when Ollama is unreachable or model not installed."""
    pass


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


# Fixed valid JSON matching docs/ARCHITECTURE.md §4 Answer dict shape
_STUB = json.dumps({
    "status": "answered",
    "question": "stub",
    "findings": [{
        "category": "deadline",
        "kind": "explicit",
        "plain_language": "Stub explanation produced without a model.",
        "quote": "the deposit shall be returned within thirty (30) days",
        "passage_id": "p3-c2",
        "page": 3,
        "uncertainty": "none",
    }],
    "passages": [],
    "jurisdiction_note": "",
    "escalation": "",
    "dropped_findings": 0,
    "message": "",
})


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