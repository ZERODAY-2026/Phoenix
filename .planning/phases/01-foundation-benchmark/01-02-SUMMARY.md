---
phase: "01-foundation-benchmark"
plan: "02"
subsystem: "embedding-offline-tests"
tags: ["embedding", "privacy", "offline", "tests"]
dependency_graph:
  requires: ["01-01"]
  provides: ["PRIV-03", "PRIV-04"]
  affects: []
tech_stack:
  added:
    - "sentence-transformers==3.0.1"
    - "torch==2.14.1"
    - "transformers==4.57.6"
  patterns:
    - "HF_HUB_OFFLINE=1 + TRANSFORMERS_OFFLINE=1 for offline loading"
    - "save_pretrained() for embedding model provisioning"
    - "pytest skipif for gitignored model directory"
key_files:
  created:
    - "scripts/download_embedding_model.py"
    - "tests/test_embedding_offline.py"
    - "tests/test_config.py"
  modified: []
decisions:
  - "Used save_pretrained() instead of .save() per SBERT 3.x+ modern API (D-10)"
  - "Completeness check on 5 required files before load attempt prevents false pass from partial download (D-11)"
  - "pytest skipif allows fresh clones to pass CI before one-time setup (D-11)"
  - "Static config tests prove privacy boundary at code level, not just documentation (D-12)"
metrics:
  duration_seconds: 420
  completed_date: "2026-10-18"
  tasks_completed: 3
  files_created: 3
status: "complete"
---

# Phase 01 Plan 02: Embedding Offline Tests Summary

**One-liner:** Embedding model download script + PRIV-03 offline load test + PRIV-04 static config tests, all verified with networking disabled.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Create embedding download script and download model | b0f861a | scripts/download_embedding_model.py |
| 2 | Create PRIV-03 offline embedding test | 9b68b20 | tests/test_embedding_offline.py |
| 3 | Create PRIV-04 static config tests | f8b7973 | tests/test_config.py |

## Verification Results

**Embedding model download:**
```
$ python scripts/download_embedding_model.py
saved -> models\all-MiniLM-L6-v2
```

**Model directory completeness (5/5 required files):**
- config.json ✓
- modules.json ✓
- model.safetensors ✓ (90.9 MB)
- tokenizer.json ✓
- tokenizer_config.json ✓

**Test suite (all passing with networking disabled):**
```
$ python -m pytest tests/test_embedding_offline.py tests/test_config.py -q
....                                                                     [100%]
4 passed in 7.95s
```

**Test details:**
- `test_local_model_dir_is_complete` — asserts all 5 required files exist
- `test_loads_and_embeds_with_networking_off` — loads with `HF_HUB_OFFLINE=1` + `TRANSFORMERS_OFFLINE=1`, embeds test sentence, asserts shape (1, 384)
- `test_ollama_url_is_loopback` — asserts `config.OLLAMA_URL` hostname is loopback (127.0.0.1)
- `test_embed_model_path_is_local_relative` — asserts `config.EMBED_MODEL_PATH` is relative local path

## Deviations from Plan

### Auto-fixed Issues

None — plan executed exactly as written.

## Auth Gates

None encountered.

## Known Stubs

None.

## Threat Flags

None — all threat mitigations from the plan's threat model are implemented:
- T-02-01 (partial download) → mitigated by completeness check in `test_embedding_offline.py`
- T-02-02 (OLLAMA_URL LAN) → mitigated by static test + hardcoded 127.0.0.1 in config
- T-02-03 (EMBED_MODEL_PATH outside repo) → mitigated by static test + download script writes to models/
- T-02-SC (compromised package) → all 6 packages approved per RESEARCH.md Package Legitimacy Audit

## Self-Check

- [x] scripts/download_embedding_model.py exists with exact pattern from PATTERNS.md
- [x] Running script creates models/all-MiniLM-L6-v2/ with all 5 required files
- [x] tests/test_embedding_offline.py exists with exact pattern from PATTERNS.md
- [x] test_local_model_dir_is_complete passes (all 5 files present)
- [x] test_loads_and_embeds_with_networking_off passes (loads model, embeds sentence, shape (1, 384))
- [x] tests/test_config.py exists with exact pattern from PATTERNS.md
- [x] Both config tests pass
- [x] All tests run with HF_HUB_OFFLINE=1 and TRANSFORMERS_OFFLINE=1 enforced by conftest.py
- [x] Commits created: b0f861a, 9b68b20, f8b7973
- [x] SUMMARY.md created at .planning/phases/01-foundation-benchmark/01-02-SUMMARY.md