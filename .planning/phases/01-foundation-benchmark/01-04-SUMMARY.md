---
phase: 01-foundation-benchmark
plan: 04
subsystem: testing
tags: [pytest, stub-llm, offline-testing, llm-contract]

# Dependency graph
requires:
  - phase: 01-01
    provides: src/llm.py with STUB_LLM=1 backend, src/config.py, tests/conftest.py, tests/test_config.py
  - phase: 01-02
    provides: scripts/download_embedding_model.py, tests/test_embedding_offline.py
  - phase: 01-03
    provides: sample_documents/D1_clean_lease.pdf, docs/benchmarks.md
provides:
  - tests/test_llm_stub.py - STUB_LLM=1 contract tests verifying Answer-dict JSON shape
  - Full test suite (7 tests) passing with networking disabled
affects: [01-05, phase-2-ingestion, phase-3-answering]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "STUB_LLM=1 contract test pattern (RESEARCH.md Pattern 1)"
    - "Answer-dict schema validation with 7 required keys per ARCHITECTURE.md §4"
    - "Offline test enforcement via conftest.py HF_HUB_OFFLINE/TRANSFORMERS_OFFLINE"

key-files:
  created:
    - tests/test_llm_stub.py
  modified: []

key-decisions:
  - "STUB_LLM=1 generate() returns fixed valid Answer-dict JSON with status='answered' and findings containing all 7 required keys"
  - "check_model_ready() structure test only — real check needs Ollama running"
  - "No network calls in STUB_LLM=1 mode; conftest.py enforces offline for all tests"

patterns-established:
  - "tests/test_llm_stub.py validates exact Answer-dict schema per ARCHITECTURE.md §4"
  - "json_mode=False returns non-empty string (needed for T13 invalid output test)"
  - "7 tests total: 2 config, 2 embedding offline, 3 LLM stub"

requirements-completed:
  - BENCH-02
  - PRIV-03
  - PRIV-04

# Coverage metadata
coverage:
  - id: D1
    description: "STUB_LLM=1 contract test verifying valid Answer-dict JSON with all 7 required keys"
    requirement: "BENCH-02"
    verification:
      - kind: unit
        ref: "tests/test_llm_stub.py#test_stub_returns_valid_json_without_network"
        status: pass
    human_judgment: false
  - id: D2
    description: "STUB_LLM=1 json_mode=False returns non-empty string"
    requirement: "BENCH-02"
    verification:
      - kind: unit
        ref: "tests/test_llm_stub.py#test_stub_json_mode_false_returns_string"
        status: pass
    human_judgment: false
  - id: D3
    description: "check_model_ready() returns tuple[bool, str] structure"
    requirement: "BENCH-02"
    verification:
      - kind: unit
        ref: "tests/test_llm_stub.py#test_check_model_ready_structure"
        status: pass
    human_judgment: false
  - id: D4
    description: "Full test suite (7 tests) passes with networking disabled"
    requirement: "PRIV-03, PRIV-04"
    verification:
      - kind: unit
        ref: "tests/ (all 7 tests)"
        status: pass
    human_judgment: false

# Metrics
duration: 5min
completed: 2026-10-18
status: complete
---

# Phase 01 Plan 04: STUB_LLM=1 Contract Tests and Walking Skeleton Verification Summary

**STUB_LLM=1 contract tests created and full 7-test walking skeleton verified green**

## Performance

- **Duration:** 5 min
- **Started:** 2026-10-18T20:15:00Z
- **Completed:** 2026-10-18T20:20:00Z
- **Tasks:** 2
- **Files modified:** 1 created

## Accomplishments
- Created `tests/test_llm_stub.py` with 3 tests matching RESEARCH.md Pattern 1 and PATTERNS.md lines 358-389
- Verified STUB_LLM=1 `generate()` returns valid Answer-dict JSON with status="answered" and findings containing all 7 required keys (category, kind, plain_language, quote, passage_id, page, uncertainty)
- Verified `json_mode=False` returns non-empty string
- Verified `check_model_ready()` returns tuple[bool, str] structure
- All 7 tests in the test suite pass with networking disabled via conftest.py
- Confirmed no banned `gemma2` references in Python source files (`git grep -ni gemma2 -- "*.py"` returns empty)

## Task Commits

Each task was committed atomically:

1. **Task 1: Create STUB_LLM=1 contract test** - `219c342` (test)
2. **Task 2: Run full test suite and verify walking skeleton** - (verified, no separate commit needed)

**Plan metadata:** `219c342` (test: complete plan)

## Files Created/Modified
- `tests/test_llm_stub.py` - STUB_LLM=1 contract tests (3 tests) validating Answer-dict schema per ARCHITECTURE.md §4

## Decisions Made
- Followed PATTERNS.md exactly for test structure and assertions
- Used `monkeypatch.setenv("STUB_LLM", "1")` for isolation
- Verified Answer-dict shape using `required <= set(f.keys())` pattern from RESEARCH.md `is_valid_answer_json()`
- Structure-only test for `check_model_ready()` since real check requires Ollama daemon

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None - all tests passed on first run.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Walking skeleton complete: config, llm, embedding, benchmark fixture, and full test suite (7 tests) all green
- STUB_LLM=1 contract verified and ready for R2/R3/R4 to build against at hour 1
- Ready for Phase 1 Plan 05 (benchmark execution) and Phase 2 (ingestion/retrieval)

## Self-Check

**PASSED**

- SUMMARY.md created at `.planning/phases/01-foundation-benchmark/01-04-SUMMARY.md` ✓
- tests/test_llm_stub.py exists with 3 tests ✓
- All 7 tests pass (`python -m pytest tests/ -q`) ✓
- STUB_LLM=1 generate() returns valid Answer-dict JSON with status="answered" and findings with all 7 required keys ✓
- json_mode=False returns non-empty string ✓
- check_model_ready() returns (bool, str) ✓
- git grep -ni gemma2 -- "*.py" returns empty ✓
- Commit 219c342 recorded in git log ✓

---
*Phase: 01-foundation-benchmark*
*Completed: 2026-10-18*