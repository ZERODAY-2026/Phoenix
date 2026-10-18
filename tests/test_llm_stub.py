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