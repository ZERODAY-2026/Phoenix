# tests/test_config.py  -- PRIV-04 (D-12), no network, no model
from urllib.parse import urlsplit
from src import config

def test_ollama_url_is_loopback():
    host = urlsplit(config.OLLAMA_URL).hostname
    assert host in {"127.0.0.1", "localhost", "::1"}, f"OLLAMA_URL is not loopback: {config.OLLAMA_URL}"

def test_embed_model_path_is_local_relative():
    p = config.EMBED_MODEL_PATH
    assert not p.startswith(("/", "\\")) and ":" not in p, f"EMBED_MODEL_PATH is not a local relative path: {p}"