# Project Research — Features

**Domain:** On-device legal document triage (rental agreements)
**Date:** 2026-10-18
**Context:** Greenfield — ZeroDay OSS Hacktoberfest 2026, Track PS2

---

## Feature Categories

### Table Stakes (Must Have — users expect these or the product fails)

| ID | Feature | Description | Complexity | Dependencies |
|----|---------|-------------|------------|--------------|
| TS-01 | **PDF Upload & Validation** | Accept text-based PDF; reject scanned/encrypted/corrupt/oversized with clear messages | Low | pdfplumber |
| TS-02 | **Page-Aware Text Extraction** | Extract text preserving page numbers for citations | Low | pdfplumber |
| TS-03 | **Clause Segmentation** | Split document into clauses by legal numbering (1., 1.1, §1, Article 1) | Medium | Custom regex |
| TS-04 | **Local Embedding Index** | Build in-memory vector index from clauses using MiniLM | Medium | sentence-transformers, NumPy |
| TS-05 | **Semantic Search** | Top-3 passage retrieval by cosine similarity for a question | Medium | NumPy index |
| TS-06 | **Structured LLM Output** | Gemma returns JSON: category, plain_language, quote, page, kind, uncertainty | High | Ollama + Gemma, prompt engineering |
| TS-07 | **Citation Verification** | Code checks every model quote is exact substring of source passage; drops failures | High | Custom verification logic |
| TS-08 | **Silence Detection** | Threshold in code triggers "The document does not state this" before model call | Medium | Similarity threshold config |
| TS-09 | **Verdict Refusal** | Rule-based classifier detects "is this legal/enforceable/should I sign?" → hardcoded refusal + specific escalation | Medium | Keyword/pattern classifier |
| TS-10 | **Prompt Injection Defense** | Detect instruction-like text in document; show warning banner; answer unaffected | Medium | Heuristic scanner |
| TS-11 | **Permanent Disclaimer** | Fixed disclaimer in UI (not model-generated): "This tool is for preliminary document understanding..." | Low | Streamlit UI |
| TS-12 | **Delete Session** | Button clears in-memory document, index, chat history | Low | Streamlit session state |
| TS-13 | **Model Unavailable Handling** | Graceful error when Ollama/Gemma not responding; no fake analysis | Low | Requests timeout handling |
| TS-14 | **Key Terms Summary** | One-click "Summarise key terms" covering rent, deposit, notice, termination, penalties, repairs | Medium | Predefined topic list + retrieval |
| TS-15 | **Offline Demo Evidence** | Wi-Fi off, connection monitor running, no external calls, no temp files | Low | OS tools, code audit |

---

### Differentiators (Competitive Advantage — judge scoring levers)

| ID | Feature | Description | Complexity | Dependencies |
|----|---------|-------------|------------|--------------|
| DIFF-01 | **Missing Promise Detector** | Fixed checklist of lease topics (deposit return, repairs, rent increase, early termination, notice period, late fees). For each: search passages; if nothing clears threshold → "No clear condition found in the analysed text." Absence ≠ illegality. | Medium | TS-05, topic list config |
| DIFF-02 | **Uncertainty Field** | Structured `uncertainty` field in output: jurisdiction dependence, ambiguous wording, insufficient evidence. Shown in separate UI block. | Medium | TS-06 schema |
| DIFF-03 | **Kind Classification** | Every finding tagged `explicit` / `interpretation` / `concern` — shown in separate UI panes. Code-enforced, not model-decided. | Medium | TS-06, TS-07 |
| DIFF-04 | **Specific Escalation Text** | Not generic "consult a lawyer" but "Ask a tenant advice service or qualified lawyer to review the deposit and termination clauses." Per document type. | Low | Config per type |
| DIFF-05 | **Connection Monitor Evidence** | Live connection monitoring during demo (netstat/Resource Monitor) proving zero external calls | Low | OS tools |
| DIFF-06 | **Benchmark Transparency** | README table: model size, RAM/VRAM, TTFT, tok/s, JSON validity %, quote accuracy % — reproducible | Low | Benchmark script |

---

### Anti-Features (Deliberately NOT Building)

| ID | Feature | Reason |
|----|---------|--------|
| AF-01 | **Legal Verdicts** | "Never say a clause is legal, illegal, valid, void or enforceable" — gate requirement; caps PS2 at 40 if violated |
| AF-02 | **Scanned PDF Support (v1)** | OCR adds complexity, Tesseract deps, accuracy issues; show clear "needs OCR, not supported" message; stretch only |
| AF-03 | **Multi-Document Comparison** | Out of scope per guide "state scope honestly"; stretch item 14 |
| AF-04 | **Non-English Documents** | English only for v1; MiniLM is English-centric |
| AF-05 | **Cloud Sync / Multi-Device** | Violates on-device privacy guarantee |
| AF-06 | **LangChain / FAISS / PyMuPDF** | License, dependency, hidden network call risks |
| AF-07 | **Auto Document Type Detection** | User must select type; "app never silently guesses it" (section 4A) |
| AF-08 | **Model-Generated Disclaimer** | Disclaimer must be fixed UI text, not model output |

---

## Feature Dependencies

```
TS-01 (Upload) → TS-02 (Extract) → TS-03 (Split) → TS-04 (Index) → TS-05 (Search)
                                                                    ↓
TS-06 (LLM Output) ← TS-08 (Silence) ← TS-05 (Search) ← TS-04 (Index)
      ↓
TS-07 (Verify Quotes) → TS-09 (Refusal) → TS-10 (Injection)
      ↓
TS-14 (Summary) ← TS-05 (Search)
      ↓
DIFF-01 (Missing Promise) ← TS-05 (Search) + topic config
DIFF-02/03 (Uncertainty/Kind) ← TS-06 schema
```

---

## Complexity Notes

- **High complexity**: TS-06 (structured JSON from 2B model), TS-07 (quote verification), TS-08 (silence threshold tuning)
- **Medium complexity**: TS-03 (clause splitting edge cases), TS-04/05 (embedding + search), TS-09 (refusal classifier), TS-10 (injection detection), DIFF-01 (missing promise)
- **Low complexity**: TS-01, TS-02, TS-11, TS-12, TS-13, TS-15, DIFF-04, DIFF-05, DIFF-06

---

## Research Sources

- PROJECT_MASTER.md (sections 4, 5, 8, 9, 12, 14)
- Hackathon guide requirements L1-L10
- Rubric items: Grounding (15pts), Uncertainty (15pts), Privacy (15pts), Gemma (10pts)
- Team constraints: 10h, 4 people, 3 CPU + 1 GPU laptop