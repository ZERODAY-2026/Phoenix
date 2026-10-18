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