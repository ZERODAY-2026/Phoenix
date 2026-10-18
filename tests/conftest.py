# tests/conftest.py
import os
import sys
from pathlib import Path

# Ensure repo root is importable for `from src.config import ...`
sys.path.insert(0, str(Path(__file__).parent.parent))

# Offline mode for all tests — PRIV-03 / PRIV-04 guardrails
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")