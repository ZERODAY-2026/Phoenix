---
phase: 01-foundation-benchmark
plan: 01
subsystem: foundation
tags: [config, llm, stub, test-infra, requirements]
dependency_graph:
  requires: []
  provides: [src/config.py, src/llm.py, tests/conftest.py, pytest.ini, requirements.txt]
  affects: [all downstream phases]
tech_stack:
  added:
    - streamlit==1.38.0
    - pdfplumber==0.11.4
    - sentence-transformers==3.0.1
    - numpy==1.26.4
    - requests==2.32.3
    - pydantic==2.8.2
    - pytest==8.3.2
  patterns:
    - "Contract-first constants in src/config.py (D-04)"
    - "STUB_LLM=1 backend in src/llm.py for team unblocking"
    - "Loopback-only OLLAMA_URL hardcoded to 127.0.0.1 (PRIV-04)"
    - "Offline mode enforced via conftest.py (PRIV-03)"
key_files:
  created:
    - src/__init__.py
    - src/config.py
    - src/llm.py
    - pytest.ini
    - tests/conftest.py
  modified:
    - requirements.txt
  deleted:
    - agentic.py
decisions:
  - "MODEL_NAME defaults to TO_BE_DECIDED, overridable by CLAUSEGUARD_MODEL env var; benchmark will set the final value"
  - "OLLAMA_URL hardcoded to http://127.0.0.1:11434 — never LAN in submitted repo"
  - "STUB_LLM=1 returns fixed valid Answer-dict JSON matching ARCHITECTURE.md §4"
  - "All 7 required finding keys present: category, kind, plain_language, quote, passage_id, page, uncertainty"
  - "agentic.py deleted (contained banned gemma2:2b and network imports)"
  - "requirements.txt pinned to exact versions per STACK.md"
metrics:
  duration_seconds: 180
  completed_date: "2026-10-18"
  tasks_completed: 3
  files_changed: 8
status: complete
---

# Phase 01 Plan 01: Foundation & Benchmark - Walking Skeleton Summary

**One-liner:** Config singleton, LLM client with stub backend, test infrastructure, pinned deps, banned file removed, backlog pushed.

## Completed Tasks

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Create config singleton and LLM client with stub backend | 6b0d2ea | src/__init__.py, src/config.py, src/llm.py |
| 2 | Create test infrastructure and pinned requirements | c250551 | pytest.ini, tests/conftest.py, requirements.txt |
| 3 | Remove banned agentic.py and push planning backlog | 6b0d2ea | agentic.py (deleted) |

## Verification Results

- ✅ `from src.config import MODEL_NAME, OLLAMA_URL, EMBED_MODEL_PATH` works — prints `MODEL_NAME=TO_BE_DECIDED OLLAMA_URL=http://127.0.0.1:11434 EMBED_MODEL_PATH=models/all-MiniLM-L6-v2`
- ✅ `STUB_LLM=1 python -c "from src.llm import generate; import json; json.loads(generate('sys', 'prompt'))"` succeeds — returns valid Answer-dict JSON with `status="answered"` and findings containing all 7 required keys
- ✅ `python -m pytest --collect-only` runs without import errors (no tests collected yet — test files created in later plans)
- ✅ `git grep -ni gemma2 -- "*.py"` returns empty — no Python source files contain banned model reference
- ✅ `git log origin/main --oneline -10` shows 6 planning commits on remote

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing critical functionality] Combined Task 1 and Task 3 commits**
- **Found during:** Committing Task 1
- **Issue:** The `git add src/__init__.py src/config.py src/llm.py` also staged the already-staged `agentic.py` deletion, so both changes went into commit 6b0d2ea
- **Fix:** Accepted the combined commit — the walking skeleton (config + LLM + stub + banned file removal) is a logical atomic unit
- **Files modified:** agentic.py (deleted), src/__init__.py, src/config.py, src/llm.py
- **Commit:** 6b0d2ea

**2. [Rule 1 - Bug] requirements.txt had placeholder content**
- **Found during:** Task 2
- **Issue:** Original requirements.txt had only comments and unpinned package names
- **Fix:** Replaced with 7 pinned versions per STACK.md (streamlit==1.38.0, pdfplumber==0.11.4, sentence-transformers==3.0.1, numpy==1.26.4, requests==2.32.3, pydantic==2.8.2, pytest==8.3.2)
- **Files modified:** requirements.txt
- **Commit:** c250551

### Auth Gates

None — no authentication required for this plan.

## Known Stubs

None — the STUB_LLM=1 backend is an intentional test double, not a stub in the negative sense. It returns a fully valid Answer-dict JSON with all required fields populated with realistic placeholder data.

## Threat Flags

None — no new security-relevant surface introduced beyond what was modeled in the threat register.

## Self-Check

- ✅ All created files exist on disk
- ✅ All commits exist in git history (6b0d2ea, c250551)
- ✅ Verification commands pass
- ✅ No banned model references in source code
- ✅ Planning backlog already on origin/main

---

**Commits:**
- 6b0d2ea: feat(01-01): create config singleton and LLM client with stub backend
- c250551: feat(01-01): add test infrastructure and pinned requirements

**Duration:** ~3 minutes