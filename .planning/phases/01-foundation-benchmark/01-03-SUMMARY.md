---
phase: 01-foundation-benchmark
plan: 03
subsystem: benchmark-harness
tags: [benchmark, ollama, gemma, pdf-fixture, harness]
dependency_graph:
  requires: ["01-01"]
  provides: ["benchmark-harness", "D1-lease-fixture", "benchmarks-table"]
  affects: ["01-04", "01-05"]
tech_stack:
  added:
    - "reportlab (for D1 PDF generation)"
  patterns:
    - "Ollama HTTP API streaming for TTFT/tok-s measurement"
    - "PowerShell Get-Process for peak RAM (avoiding ollama ps SIZE double-count)"
    - "Verbatim quote accuracy via normalized substring matching"
    - "JSON validity = parse + Answer-dict schema validation (ARCHITECTURE.md §4)"
key_files:
  created:
    - "scripts/benchmark.py"
    - "sample_documents/D1_clean_lease.pdf"
    - "scripts/create_d1_lease.py"
    - "docs/benchmarks.md"
  modified:
    - "sample_documents/README.md"
decisions:
  - "Prompt set: 8 answerable prompts from TEST_PLAN.md §3 (7 fixed + 1 variable: sublet)"
  - "Quote accuracy computed pre-Verifier using ARCHITECTURE.md §3.2 algorithm (normalized substring)"
  - "JSON validity requires both parseability AND Answer-dict schema conformance"
  - "Peak RAM measured via OS process working set, not ollama ps SIZE (Pitfall 3)"
  - "Warm-up mandatory before measurement to exclude load_duration from TTFT"
  - "D1 landlord name 'Aldric Thorne' unique for Phase 6 temp-file leak search"
metrics:
  duration_seconds: 1800
  completed_date: "2026-10-18"
  task_count: 3
  file_count: 5
status: complete
---

# Phase 01 Plan 03: Benchmark Harness & D1 Fixture Summary

**One-liner:** BENCH-02 harness script with 8 verbatim prompts, D1 clean lease PDF (8 pages, 7 topics), and benchmarks.md results table scaffolded for 3 Gemma candidates × 2 machines.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Create benchmark harness script | 4726e34 | scripts/benchmark.py |
| 2 | Create D1 lease & update sample index | 9cee4d9 | sample_documents/D1_clean_lease.pdf, sample_documents/README.md, scripts/create_d1_lease.py |
| 3 | Create benchmarks.md table structure | bd7f924 | docs/benchmarks.md |

## Artifacts Produced

### scripts/benchmark.py
Complete BENCH-02 measurement harness implementing RESEARCH.md Pattern 2:
- **Imports**: json, os, sys, time, requests, subprocess, pathlib
- **BASE_URL**: From OLLAMA_HOST env (default http://127.0.0.1:11434)
- **SYSTEM_PROMPT**: From ARCHITECTURE.md §5 with passage wrapper format
- **PROMPT_SET**: 8 triples (question, passage_id, verbatim passage_text from D1)
- **warm_up()**: Loads model via empty prompt to exclude load_duration from TTFT
- **run_prompt()**: Streams with `stream: true`, captures TTFT (first non-empty chunk), accumulates text, extracts eval_count/eval_duration for tok/s
- **model_footprint()**: GET /api/tags for size_bytes/digest/quant; GET /api/ps for size_vram_bytes
- **is_valid_answer_json()**: Parses JSON AND validates Answer-dict shape (status, findings, 7 required keys per finding)
- **quote_is_verbatim()**: Normalized whitespace + casefold substring check (matches ARCHITECTURE.md §3.2 verify_findings)
- **get_peak_ram_gb()**: PowerShell Get-Process on ollama* processes (Windows)
- **Main**: Parses --model/--machine, runs warm-up + 8 prompts, computes aggregates, appends markdown row to docs/benchmarks.md

### sample_documents/D1_clean_lease.pdf
- 8 pages (within 6-10 spec), numbered clauses (1., 2., 3., etc.)
- **Rent**: §2.1 — $1,850/month due 1st of month
- **Deposit (30 days)**: §3.3 — Return within 30 days after vacating
- **Notice (2 months)**: §8.1 — 60 days written notice to terminate
- **Repairs**: §4.3 — Landlord responsible for plumbing repairs
- **Pets**: §5.1 — 1 cat or 1 dog ≤25 lbs with $200 pet fee
- **Termination**: §8.1-8.2 — Tenant/Landlord 60-day notice; early termination fee = 2 months' rent
- **Late fee**: §2.3 — $75 after 5th day, additional $75 per 5 days
- **Fictional landlord**: Aldric Thorne (unique for Phase 6 leak search)

### sample_documents/README.md (updated)
- Complete D1-D9 table per TEST_PLAN.md §1
- D1 entry includes all 7 topics + fictional landlord name
- D6 (long lease) and D8 (corrupt) and D9 (unscripted) added

### docs/benchmarks.md
- Header with recorded date, machines, fixture, Ollama env vars
- Results table: 6 rows (gemma3n:e2b, gemma4:e2b, gemma4:e2b-it-qat × 2 machines)
- Selection Record section for chosen model decision
- Request Configuration JSON block (stream=true, format=json, think=false, keep_alive=5m, temp=0, num_ctx=8192)
- Granularity note: N=8 → >90% requires 100% (8/8)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing critical functionality] Added reportlab dependency for PDF generation**
- **Found during:** Task 2 (creating D1_clean_lease.pdf)
- **Issue:** No existing PDF creation method in repo; plan said "use any PDF creation method"
- **Fix:** Used reportlab (already available) to generate well-formatted 8-page PDF with proper clause numbering and page breaks
- **Files modified:** scripts/create_d1_lease.py (new helper script)
- **Commit:** 9cee4d9

**2. [Rule 2 - Missing critical functionality] Added 8th prompt (sublet) based on D1 content**
- **Found during:** Task 1 → Task 2 integration
- **Issue:** Plan specified 8th prompt as "one of {sublet, utilities, rent increase} based on D1 content"
- **Fix:** D1 includes sublet clause (§6), so selected sublet as 8th prompt with verbatim passage
- **Files modified:** scripts/benchmark.py (PROMPT_SET updated with actual passages)
- **Commit:** 4726e34

**3. [Rule 1 - Bug] Fixed notice period keyword check**
- **Found during:** Verification of D1 content
- **Issue:** Automated check looked for "sixty days" but D1 uses "60 (sixty) days" and "sixty (60) days"
- **Fix:** Verified manually — content is correct (60 days = 2 months); check was keyword mismatch only
- **No file changes needed** — content already correct

## Verification Results

- `python scripts/benchmark.py --help` → Shows correct argument parser
- `sample_documents/D1_clean_lease.pdf` → 8 pages, all 7 topics present, fictional landlord "Aldric Thorne"
- `docs/benchmarks.md` → Correct table structure, request config, granularity note
- `git grep -ni gemma2 -- "*.py"` → Empty (no banned model in source code)

## Self-Check

**PASSED** — All deliverables exist and verified:
- ✅ scripts/benchmark.py with all required functions
- ✅ sample_documents/D1_clean_lease.pdf (8 pages, 7 topics, unique landlord)
- ✅ sample_documents/README.md updated with D1-D9 table
- ✅ docs/benchmarks.md with results table, selection record, request config
- ✅ All commits atomic with proper messages
- ✅ No banned gemma2 references in source code