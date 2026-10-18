---
phase: 1
slug: foundation-benchmark
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-10-18
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `.planning/phases/01-foundation-benchmark/01-RESEARCH.md` → `## Validation Architecture`.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (9.1.1 present on this box; 8.3.2 is the STACK pin — either works) |
| **Config file** | **None — Wave 0 gap.** Add a minimal `pytest.ini` (or `[tool.pytest.ini_options]`) with `testpaths = tests` and `pythonpath = .` so `import src.config` resolves without an install step |
| **Quick run command** | `python -m pytest -q` |
| **Full suite command** | `python -m pytest -q` |
| **Estimated runtime** | seconds — the phase has no slow/external tier; the model-dependent checks are the manual benchmark, not pytest |

---

## Sampling Rate

- **After every task commit:** Run `python -m pytest -q`
- **After every plan wave:** Run `python -m pytest -q` plus `git grep -ni gemma2` (must be empty)
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** seconds
- **Phase gate:** full suite green, `docs/benchmarks.md` complete for all 3 candidates × 2 machines, `config.MODEL_NAME` set, §7.3 record written, and the benchmark commit visible on `origin/main` — **all before any `ollama rm`** (D-09)

---

## Per-Task Verification Map

Task IDs are assigned during planning; rows below are the requirement-level
verification contract the plans must implement.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD | — | 0 | PRIV-03 | — | Local MiniLM dir is complete and loads + embeds with `HF_HUB_OFFLINE=1`/`TRANSFORMERS_OFFLINE=1` | integration (local FS) | `python -m pytest tests/test_embedding_offline.py -q` | ❌ W0 | ⬜ pending |
| TBD | — | 0 | PRIV-04 | V4 Access Control | `config.OLLAMA_URL` is loopback; `config.EMBED_MODEL_PATH` is a local relative path | unit | `python -m pytest tests/test_config.py -q` | ❌ W0 | ⬜ pending |
| TBD | — | 0 | BENCH-02 (D-02) | — | `STUB_LLM=1` returns a fixed **valid** Answer-shape JSON with **no** network call | unit | `python -m pytest tests/test_llm_stub.py -q` | ❌ W0 | ⬜ pending |
| TBD | — | 0 | D-08 / Pitfall 5 | Tampering | No banned model string anywhere in the tree | static | `git grep -ni gemma2` → must be empty | ❌ W0 | ⬜ pending |
| TBD | — | — | BENCH-02 | — | Six metrics produced; JSON validity + quote accuracy computed | **manual harness** | `python scripts/benchmark.py --model <tag> --machine <name>` → row in `docs/benchmarks.md` | ❌ W0 | ⬜ pending |
| TBD | — | — | BENCH-03 | — | Selection recorded in `config.py` + `PROJECT_MASTER.md` §7.3, committed before prune | manual/gate | `git log origin/main --stat -- docs/benchmarks.md` shows the file before `ollama rm` | ❌ W0 | ⬜ pending |
| TBD | — | — | D-05 | — | D1 lease exists, is 6–10 pages, covers rent/deposit/notice/repairs/pets/termination/late fee | manual (human read) | — | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/conftest.py` — set `HF_HUB_OFFLINE=1` / `TRANSFORMERS_OFFLINE=1` for the session and ensure the repo root is importable
- [ ] `pytest.ini` (or `pyproject.toml`) — `testpaths = tests`, `pythonpath = .`
- [ ] `tests/test_config.py` — PRIV-04 static assertions (D-12)
- [ ] `tests/test_llm_stub.py` — `STUB_LLM=1` contract, no network (D-02)
- [ ] `tests/test_embedding_offline.py` — PRIV-03 completeness + offline load (D-11)
- [ ] `src/__init__.py` — makes `from src.llm import ...` unambiguous
- [ ] `src/config.py`, `src/llm.py` — the D-01/D-02/D-03 skeleton
- [ ] `scripts/download_embedding_model.py` — D-10, closes the README step-4 dangling reference
- [ ] `scripts/benchmark.py` — BENCH-02 harness
- [ ] `docs/benchmarks.md`, `docs/evidence/` — evidence artifacts

*No existing test infrastructure exists — `tests/` is absent. All of the above is net-new.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Ollama actually bound to `127.0.0.1` (not `0.0.0.0`) | PRIV-04 | Binding is a process/OS fact, not a source assertion | Run `netstat -ano \| findstr 11434` and capture output into `docs/evidence/` (T16 draft) |
| Six benchmark metrics per model × machine | BENCH-02 | Requires the live model runtime on real hardware | Run `scripts/benchmark.py` per candidate per machine; record rows in `docs/benchmarks.md` |
| Model selection meets BENCH-03 criteria | BENCH-03 | Requires reading live CPU-only run timings | Confirm loads on 16 GB CPU laptop, <2 min response, >90% JSON validity; tie-break on quote accuracy; record in `PROJECT_MASTER.md` §7.3 |
| D1 lease content quality | D-05 | Fictional lease is human-written prose | Read the lease; confirm 6–10 pages and coverage of rent, deposit (30 days), notice (2 months), repairs, pets, termination, late fee |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
