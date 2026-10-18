# Source: docs/TEAM_ROLES_AND_CONTRACTS.md §3
import os

MODEL_NAME = os.environ.get("CLAUSEGUARD_MODEL", "TO_BE_DECIDED")  # e.g. "gemma3n:e2b" or "gemma4:e2b-it-qat"
OLLAMA_URL = "http://127.0.0.1:11434"  # NEVER a LAN address in the submitted repo
EMBED_MODEL_PATH = "models/all-MiniLM-L6-v2"
TOP_K = 3
SILENT_THRESHOLD = 0.30  # placeholder; calibrate (see TEST_PLAN)
MAX_UPLOAD_MB = 15
MIN_CHARS_PER_PAGE = 200  # below this on average => treat as scanned
REQUEST_TIMEOUT_S = 180