# Project Research — Pitfalls

**Domain:** On-device legal document triage (rental agreements)
**Date:** 2026-10-18
**Context:** Greenfield — ZeroDay OSS Hacktoberfest 2026

---

## Critical Pitfalls

### PIT-01: Model Too Slow on CPU-Only Laptops
**Warning Signs:** Time-to-first-token > 2 minutes; tokens/sec < 5; team laptops freeze during generation
**Impact:** Demo fails; judges can't evaluate; 10-hour window expires
**Prevention:**
- Benchmark in Hour 0-1.5 on ALL team laptops (section 7.2)
- Limit prompt to top-3 passages (already in design)
- Have QAT build (`gemma4:e2b-it-qat` ~4.3GB) ready as fallback
- Show retrieved passages immediately, stream explanation underneath
- **Cut scope at Hour 3 checkpoint** if no model works: summary + clause lookup only
**Phase:** Phase 1 (Benchmark) → Phase 4 (Integration)

### PIT-02: Gemma 3n/4 Not Working in Ollama on Team Laptop
**Warning Signs:** `ollama run` fails; model pulls but errors on inference; version mismatch
**Impact:** No LLM → no explanations → fail L3, L10 gates
**Prevention:**
- Test `ollama list` and `ollama run` on each laptop during setup
- Have both `gemma3n:e2b` and `gemma4:e2b` pulled
- Check Ollama version ≥ 0.20.0 for Gemma 4 support
- Fallback: llama.cpp with GGUF Gemma if Ollama fails
- Document exact working version in README
**Phase:** Phase 1 (Benchmark)

### PIT-03: Hidden Network Call in Dependency
**Warning Signs:** Connection monitor shows outbound during demo; pip install downloads at runtime; sentence-transformers fetches model; Streamlit telemetry
**Impact:** Privacy gate (L9) fails → not ranked
**Prevention:**
- `HF_HUB_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1` in env
- Download MiniLM to `models/` at setup, load from local path
- `gatherUsageStats = false` in `.streamlit/config.toml`
- Bind Streamlit to `127.0.0.1`
- Bind Ollama to `127.0.0.1` (not `0.0.0.0`)
- Full offline test + connection monitor recording in final hour
- Code audit: grep for `http`, `requests`, `httpx`, `urllib` — only `requests` to localhost allowed
**Phase:** Phase 1 (Setup) → Phase 6 (Evidence)

### PIT-04: Model Invents Quotes (Hallucination)
**Warning Signs:** Quote in output not found in source passage; citation check fails; judge spots fabricated text
**Impact:** Grounding gate (L5) fails → caps PS2 at 40
**Prevention:**
- **Code decides, not model**: substring verification in `guardrails.py`
- Every quote checked as exact substring of source passage
- Failures dropped silently; UI shows only code-extracted passages
- Test T3 (citation check) with 20 prompts — must pass
- Few-shot examples in prompt showing correct citation format
**Phase:** Phase 3 (Guardrails)

### PIT-05: Vibe-Coded Code Nobody Understands
**Warning Signs:** Owner can't explain their file in 2 minutes; AI-generated code has subtle bugs; merge conflicts from misunderstood changes
**Impact:** Bugs during demo; can't fix under time pressure; rubric "Robustness" (12pts) and "Reusability" (10pts) suffer
**Prevention:**
- Every owner explains their file in 2 minutes (standup at each phase transition)
- Ask AI to comment code with rationale, not just what
- One file, one owner — PRs for cross-file changes
- Commit often with descriptive messages
- Pair on critical paths (guardrails, quote verification)
**Phase:** All phases — continuous

### PIT-06: Merge Conflicts / Lost Work
**Warning Signs:** Divergent branches; force pushes; overwritten files; `ui.py` vs `app.py` confusion
**Impact:** Lost hours redoing work; submission deadline missed
**Prevention:**
- One file, one owner (strict)
- Branch per feature/PR; no direct commits to main
- Entry file is `app.py` — enforce in .gitignore/docs
- `.gitignore` created in text editor (not `echo "\n"`)
- Commit every 30-60 min during active coding
**Phase:** Phase 4 (Integration) → Phase 6 (Submission)

### PIT-07: 16GB RAM Exhausted During Demo
**Warning Signs:** System swap thrashing; OOM kills; demo freezes
**Impact:** Demo fails; can't recover in time
**Prevention:**
- Close all other apps before demo (browser, Slack, IDE)
- Test exact demo machine with full pipeline loaded
- Smaller model (QAT build) if RAM tight
- In-memory index only — no duplicate copies
- Monitor with Task Manager / htop during test runs
**Phase:** Phase 4 (Integration) → Phase 6 (Demo)

### PIT-08: Scanned PDFs Break the App
**Warning Signs:** pdfplumber returns empty text; no error shown; app crashes or shows blank
**Impact:** Judge tests with scanned PDF → bad UX; rubric "Robustness" (12pts)
**Prevention:**
- Detect low text extraction (e.g., < 100 chars/page)
- Show clear "This appears to be a scanned/image-only PDF. OCR is not supported in this version." message
- Test with actual scanned PDF in test suite
- Never crash — always return structured error
**Phase:** Phase 2 (Ingestion)

### PIT-09: Output Sounds Like Legal Advice
**Warning Signs:** Model says "this clause is enforceable", "you should sign", "this is legal/illegal"
**Impact:** Gate L8 fails → not ranked; critical safety issue
**Prevention:**
- Fixed disclaimer in UI (never model-generated)
- Banned-phrase filter in `guardrails.py`: "legal", "illegal", "valid", "void", "enforceable", "should sign", "binding"
- Verdict refusal: rule-based classifier catches "is this legal/enforceable/should I sign?"
- Escalation text specific: "Ask a tenant advice service or qualified lawyer to review the deposit and termination clauses"
- Review sample outputs with non-lawyer teammate for plain language
**Phase:** Phase 3 (Guardrails) → Phase 6 (Review)

### PIT-10: Demo Machine Differs from Judge Machine
**Warning Signs:** Works on RTX 2050 laptop but not on CPU-only; different Ollama version; path issues
**Impact:** Judge can't reproduce; submission fails verification
**Prevention:**
- Test on CPU-only 16GB laptop (majority of team)
- README states minimum spec: 16GB RAM, Python 3.10+, Ollama 0.20+
- Pin all versions in `requirements.txt` (`pip freeze`)
- Use relative paths only; no hardcoded absolute paths
- Provide fictional sample lease in `sample_documents/`
**Phase:** Phase 6 (Submission)

### PIT-11: Dataset / Sample License Problem
**Warning Signs:** Real lease used; copyrighted text in repo; license violation
**Impact:** Disqualification; legal risk
**Prevention:**
- Only fictional leases written by team
- Disclose in README: "Sample documents are fictional, created for testing"
- No real personal data in any test file
**Phase:** Phase 6 (Submission)

### PIT-12: Silent Threshold Too Aggressive / Too Lenient
**Warning Signs:** "Document does not state this" for answerable questions (false negative); or answers with no evidence (false positive)
**Impact:** Grounding gate (L5) or Uncertainty gate (L7) fails
**Prevention:**
- Tune threshold on sample lease test set (5-10 questions)
- Log similarity scores for analysis
- Default threshold: cosine similarity < 0.35 → silent (tune per benchmark)
- Show top passage score in debug mode for calibration
**Phase:** Phase 3 (Guardrails) → Phase 4 (Integration)

### PIT-13: Clause Splitter Breaks on Edge Cases
**Warning Signs:** Clauses merged incorrectly; split mid-sentence; headings lost; page numbers wrong
**Impact:** Retrieval returns wrong context → bad answers → grounding fails
**Prevention:**
- Test splitter on 5+ diverse lease PDFs
- Regex patterns for: `^\d+\.`, `^\d+\.\d+`, `^§\d+`, `^Article\s+\d+`, `^[A-Z][A-Z\s]+:` (ALL CAPS headings)
- Preserve heading with clause text
- Unit tests for each pattern
**Phase:** Phase 2 (Ingestion)

### PIT-14: MiniLM Truncation Loses Clause Context
**Warning Signs:** Clauses > 256 tokens truncated; key terms cut off; retrieval misses relevant passage
**Impact:** Search quality degrades; answers incomplete
**Prevention:**
- Splitter targets 120-200 words per clause (well under 256 WP)
- Size cap: if clause > 300 words, sub-split at sentence boundary
- Test with longest clauses in sample leases
**Phase:** Phase 2 (Ingestion)

### PIT-15: Benchmark Numbers Not Reproducible
**Warning Signs:** Different runs give different results; no script; manual stopwatch
**Impact:** Can't defend model choice; rubric "Gemma integration" (10pts) weakened
**Prevention:**
- Benchmark script: fixed lease, fixed prompts, automated timing
- Record: model size, peak RAM/VRAM (Task Manager/nvidia-smi), TTFT, tok/s, JSON validity %, quote accuracy %
- Run 20 prompts per candidate
- Save results to `docs/benchmarks.md`
**Phase:** Phase 1 (Benchmark)

---

## Pitfall-to-Phase Mapping

| Phase | Primary Pitfalls to Address |
|-------|----------------------------|
| **Phase 1** (Benchmark) | PIT-01, PIT-02, PIT-03, PIT-15 |
| **Phase 2** (Ingestion) | PIT-08, PIT-13, PIT-14 |
| **Phase 3** (Guardrails) | PIT-04, PIT-09, PIT-12 |
| **Phase 4** (Integration) | PIT-05, PIT-06, PIT-07 |
| **Phase 5** (Should-Haves) | PIT-09 (review), PIT-12 (calibrate) |
| **Phase 6** (Evidence) | PIT-03, PIT-10, PIT-11 |

---

## Research Sources

- PROJECT_MASTER.md (sections 7, 8, 9, 11, 13, 14)
- Hackathon guide gates L1-L10
- Rubric: Grounding (15), Uncertainty (15), Privacy (15), Gemma (10), Robustness (12), Reusability (10)
- Team retrospective from similar hackathons
- Common failure modes in on-device LLM apps