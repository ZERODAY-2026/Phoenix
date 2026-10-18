# ClauseGuard: Project Master Document

**Event:** ZeroDay OSS Hacktoberfest 2026, IIIT Dharwad
**Track:** PS2, Agentic AI: Private Legal Document Triage Agent
**Team:** 4 members (3 CPU-only laptops, 1 laptop with RTX 2050 4 GB)
**Status of this document:** v1.0, written 18 Oct 2026. Facts about models and tools were checked on this date. Re-check anything marked **(verify)** before relying on it.

> This is the single source of truth. If another file, chat message or earlier plan disagrees with this document, this document wins. If you change a decision, change it here first.

---

## 0. Document map

| File | What it is | Read it if you are |
|---|---|---|
| `docs/PROJECT_MASTER.md` (this file) | Decisions, scope, plan, risks | everyone |
| `docs/ARCHITECTURE.md` | How the system works, data flow, output format | everyone, especially R2/R3 |
| `docs/PRIVACY.md` | Threat model, offline test, evidence to record | R1, R4, and anyone touching network code |
| `docs/TEAM_ROLES_AND_CONTRACTS.md` | Who owns which file, exact function signatures | everyone |
| `docs/VIBE_CODING_PROMPTS.md` | Copy-paste prompts for your AI coding assistant | everyone |
| `docs/GIT_WORKFLOW.md` | Safe Git/GitHub steps for beginners | everyone |
| `docs/TEST_PLAN.md` | Test documents, test cases, evaluation questions | R3, R4, R1 |
| `docs/DATASETS.md` | Dataset sources, licences, use rules (evaluation only, no training) | R2, R3, R4 |
| `docs/SUBMISSION_CHECKLIST.md` | Every gate, rubric item and deliverable, tickable | R4 (Git master), all before submit |
| `README.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, `LICENSE` | Public repo files | R4 |

---

## 1. Mission in one paragraph

ClauseGuard is a **fully on-device** assistant that reads a **rental agreement (PDF)**, explains clauses in plain language, points to the exact passage and page behind every statement, separates "what the document says" from "what might be a concern", says **"the document does not state this"** when it is silent, and **declines to give legal verdicts** (it recommends a qualified legal professional). Nothing about the document or the user's questions ever leaves the laptop.

**What we are not building:** a lawyer, a legality checker, a cloud chatbot, or a multi-document-type platform.

---

## 2. Corrections to the earlier plans (read this first)

We were given three planning documents plus chat advice. They disagree with each other and with the official guide in places. Each row below is a problem we found and the decision we took. **Several of these would have caused a gate failure or a score cap if left alone.**

| # | Problem found | Where | Why it matters | Decision |
|---|---|---|---|---|
| 1 | The plan pulls `gemma2:2b` and claims it satisfies the "Gemma 3n/4 class" rule. **It does not.** Gemma 2 is an older generation, not the Gemma 3n / Gemma 4 edge family named in the guide. | Execution Plan Phase 1; Role 1 and Role 3 prompts | Gate **L1-L4** requires Gemma used and run locally. The guide names Gemma 3n-class (E2B/E4B) and accepts Gemma 4 E2B/E4B. Claiming Gemma 2 is "edge-class" would also be dishonest in the README. | Use **Gemma 3n E2B** or **Gemma 4 E2B** (benchmark both, see section 7). `gemma2:2b` may be used **only** as a throwaway plumbing test on day one and must never appear in the submission. |
| 2 | Laptop 1 serves the model to the other laptops over Wi-Fi (`OLLAMA_HOST=0.0.0.0`, `http://<LAPTOP_1_IP>:11434`). | Role 1, Role 3 prompts | The guide says the user's questions, chunks, answers and extracted text must stay **on the device**. Sending them to a second laptop over the network is a content-carrying connection. Judges monitor connections and look for their absence. Also, Ollama has **no authentication**; binding to `0.0.0.0` lets anyone on the same Wi-Fi use it. | **LAN serving is for development only, with fictional documents only.** The submitted demo, the recording and the privacy evidence must run **everything on one laptop with Ollama on `127.0.0.1`**. |
| 3 | `ingest_pdf()` saves a FAISS index to disk and the UI saves the upload to a "temporary local path". | Role 2 and Role 4 prompts | Judges check temporary files. Leftover copies of a private document or its embeddings on disk are a privacy finding. | Process the upload **in memory**. Keep the index **in memory**. Provide a **Delete session** button. Log no document text. |
| 4 | ClauseGuard blueprint recommends **PyMuPDF**. | Blueprint stack table | PyMuPDF is **AGPL-3.0**. Our repo should carry a permissive licence (MIT). Mixing creates licence friction, and Gate G1 and rubric C4 judge licence quality. | Use **pdfplumber (MIT)**. |
| 5 | "Chunk 500 tokens with 50 overlap" via LangChain; embeddings with `all-MiniLM-L6-v2`. | Execution Plan Phase 2; Role 2 prompt | LangChain's splitter counts **characters** by default, not tokens. MiniLM-L6-v2 truncates input at about 256 word pieces, so 500-token chunks would be silently cut. Legal clauses also should not be sliced mid-sentence. | **Split by clause/section headings and numbering**, targeting roughly 120-200 words per chunk, with a size cap. Write our own small splitter; drop the `langchain-community` dependency (fewer packages, fewer hidden network calls). |
| 6 | The "silent" behaviour is only a prompt instruction in one plan, and citations are "append the quote" by the model. | Role 3 prompt | A 2B-class model will sometimes invent quotes or answer from general knowledge. "No systematic fabrication of clauses or citations" is a pass/fail gate. | **Code decides, not the model.** (a) A similarity threshold triggers the silent response before the model is called. (b) Source passages shown to the user come **from the extracted text by code**. (c) Any quote the model returns is **checked as a substring** of the passage; failures are dropped. |
| 7 | Hidden network calls are not addressed in the prompts. | All | Sentence-transformers tries to fetch the model from Hugging Face on first use. Streamlit collects usage stats unless turned off. A Hugging Face or analytics call during the demo is a privacy failure. | Download the embedding model **once at setup** into `models/`, load it from the local path, set `HF_HUB_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1`. Set `gatherUsageStats = false` in `.streamlit/config.toml`. Bind Streamlit to `127.0.0.1`. |
| 8 | A 4 GB RTX 2050 cannot hold the model fully. | Role 1 | Third-party sources report `gemma4:e2b` at about 7.2 GB on disk by default and about 4.3 GB for the `-it-qat` build (verify). Both exceed 4 GB VRAM, so Ollama will split layers between GPU and CPU. | Expect **partial GPU offload**. Benchmark it; do not assume the GPU laptop is automatically fastest. Pick the final demo machine by measurement. |
| 9 | Git steps: `echo "env/\n*.pdf..." > .gitignore`; `.gitignore` excludes `*.pdf`; branch names differ between documents; `ui.py` vs `app.py`. | Merge strategy section; Role 4 | `echo "\n"` writes a literal `\n` in Windows `cmd`. Ignoring all PDFs also hides our **sample documents**, which judges need. Inconsistent names cause merge confusion. | Create `.gitignore` in a text editor (provided in this pack, with an exception for `sample_documents/`). Use Pull Requests. Entry file is **`app.py`**. See `docs/GIT_WORKFLOW.md`. |
| 10 | Three different plans: React + FastAPI + PyMuPDF for 6 people in 12 hours; Streamlit + pdfplumber + FAISS for 4 in 10 hours; mixed chat advice. | All documents | A team that is vibe-coding cannot debug a React + FastAPI + TypeScript stack. | **Streamlit + Python only.** We borrow the *ideas* from the ClauseGuard blueprint (evidence validator, Missing Promise Detector, Privacy Proof Mode, "Needs review" status) but not its stack. |
| 11 | The blueprint's `/api/delete` and Privacy Proof Mode are good ideas, but a "privacy badge" in the UI can be misleading. | Blueprint | The blueprint itself warns not to rely on a status badge. | Any in-app "private" indicator must be backed by a real check, or be removed. Evidence comes from the offline test and connection monitoring, not from a badge. |

---

## 3. How the guide's requirements map to our design

| ID | Mandatory requirement | How ClauseGuard meets it | Evidence to show |
|---|---|---|---|
| L1 | Local ingestion of PDF or text | PDF (text-based) and `.txt` via `ingest.py` | Demo, test T1 |
| L2 | On-device extraction and interpretation | pdfplumber + local Gemma | Demo, benchmark log |
| L3 | Plain-language summaries and explanations | Gemma produces `plain_language` per finding | Sample outputs |
| L4 | Identify obligations, rights, deadlines, penalties, termination | Fixed category field in the output schema | Test T6 |
| L5 | Responses supported by identifiable passages | Passage id + page + verbatim text, built by code | Test T3 (citation check) |
| L6 | Distinguish explicit statements from interpretation | `kind` field: `explicit` / `interpretation` / `concern`, shown in separate UI blocks | Screenshot |
| L7 | Recognise ambiguity, insufficient evidence, jurisdiction dependence | `uncertainty` field, jurisdiction note, silent threshold | Tests T4, T7 |
| L8 | Refuse unsupported conclusions, recommend a professional | Rule-based question classifier + hardcoded escalation text | Test T5 |
| L9 | Demonstrable privacy | Offline run, connection monitoring, code audit, temp-file check | `docs/PRIVACY.md` evidence pack |
| L10 | Meaningful Gemma use, reproducible, open source | Gemma writes all explanations; repo has pinned deps and README | README, benchmark table |

---

## 4. Scope (state this honestly in the README)

**In scope**
- Document types: **residential rental agreements (first release, fully tested)**. Employment contracts and service agreements are **planned**, and each becomes Supported only after its own test set passes (see section 4A).
- Language: **English**
- Format: **text-based PDF** and plain text
- Questions: free-text questions about the loaded document, plus a one-click "summarise key terms" action
- Platform tested: team laptops only (fill in exact specs in the README)

**Out of scope (say so in the README)**
- Scanned or image-only PDFs: show a clear "needs OCR, not supported" message
- Legal notices, loan and credit agreements, purchase agreements, terms of service (not planned)
- Deciding whether a clause is legal, valid or enforceable
- Non-English documents
- Multi-document comparison (stretch only)

**Why narrow scope is a strength:** the guide says to "state your scope honestly and test within it".

---

## 5. Technology stack (final)

| Layer | Choice | Licence | Notes |
|---|---|---|---|
| UI | Streamlit | Apache-2.0 | Telemetry disabled in `.streamlit/config.toml`; bind to `127.0.0.1` |
| PDF text | pdfplumber | MIT | Works on in-memory bytes; keeps page numbers |
| Clause splitting | Our own `ingest.py` (regex on numbering/headings) | ours | No LangChain |
| Embeddings | `sentence-transformers` with `all-MiniLM-L6-v2` loaded from a local folder | Apache-2.0 (check model card) | Downloaded once at setup |
| Vector search | NumPy cosine similarity (a few hundred chunks do not need FAISS) | BSD | FAISS is optional; skipping it removes a dependency |
| LLM runtime | Ollama on `127.0.0.1:11434` | MIT | Needs a recent version for Gemma 4 (reported v0.20.0+, verify) |
| Model | Gemma 3n E2B or Gemma 4 E2B | Gemma Terms of Use / reported Apache-2.0 for Gemma 4 (verify) | Chosen by benchmark |
| HTTP to Ollama | `requests` to localhost only | Apache-2.0 | The **only** network code in the app |
| Tests | pytest | MIT | |

Pin every version in `requirements.txt` once it works (`pip freeze`).

---

## 6. Architecture summary

Full detail is in `docs/ARCHITECTURE.md`. In short:

```
PDF bytes (in memory)
  -> extract_pages()            [pdfplumber, page numbers kept]
  -> split_into_clauses()       [our regex splitter]
  -> build_index()              [local MiniLM embeddings, in memory]

Question
  -> classify_question()        [rules: normal / legal_verdict / out_of_scope]
  -> search() top 3 passages    [cosine similarity]
  -> is_silent()?               [threshold in code]  -- yes --> "The document does not state this"
  -> Gemma (local Ollama)       [JSON output, passages wrapped as untrusted data]
  -> verify_findings()          [quotes must be exact substrings; failures dropped]
  -> UI: explanation | source passages | concerns | uncertainty | disclaimer
```

**Rule of thumb:** *the model explains, the code guarantees.* Anything that must be true (citations, refusals, disclaimers, silence) is enforced by code the model cannot override.

---

## 7. Model plan

### 7.1 Candidates (sizes reported by third-party sources on 18 Oct 2026; verify with `ollama list`)

| Candidate | Ollama tag | Reported size | Notes |
|---|---|---|---|
| Gemma 3n E2B | `gemma3n:e2b` | verify after pull | The guide's primary named class |
| Gemma 4 E2B | `gemma4:e2b` | about 7.2 GB | Accepted by the guide as same class |
| Gemma 4 E2B, QAT build | `gemma4:e2b-it-qat` | about 4.3 GB | Smaller download, fits 8 GB RAM machines better |
| Gemma 4 E4B | `gemma4:e4b` | about 9.6 GB | Heavier; try only if E2B quality is poor and RAM allows |

Reported guidance: E2B wants roughly 8 GB RAM minimum, 16 GB recommended. Reported memory for 4-bit **weights only**: E2B about 2.9 GB (Google's table, as relayed by a third party). Context length adds more.

### 7.2 Benchmark protocol (R1, hour 0-1.5)

Run each candidate on **the same 10-page fictional lease**, network **disabled** after the pull, and record in `docs/benchmarks.md`:

| Metric | How |
|---|---|
| Model file size on disk | `ollama list` |
| Peak RAM / VRAM | Task Manager (Windows) or `htop` / `nvidia-smi` |
| Time to first token for a 3-passage prompt (about 1,000-1,500 tokens) | stopwatch or script timer |
| Tokens per second | Ollama's `eval_count` / `eval_duration` fields, or timer |
| JSON validity | run 20 test prompts, count valid JSON responses |
| Quote accuracy | count quotes that pass the substring check |

### 7.3 Decision rule (our proposal, adjust if the numbers say otherwise)

Pick the candidate that: loads on a CPU-only 16 GB laptop with other apps closed; answers a typical question in **under about 2 minutes**; returns valid JSON in at least 90% of the 20 prompts. If two candidates pass, take the one with the higher quote-accuracy count. Record the decision here: **Chosen model: `______` (date, who, numbers).**

### 7.4 If the model is too slow

The design already limits prompts to the top 3 passages. Further options, in order: smaller quantisation or QAT build; shorter output schema; reduce `TOP_K` to 2; show the retrieved passages immediately and stream the explanation underneath. Do **not** fall back to a remote API; that fails the track.

---

## 8. Features

### Must have (the MVP; build and test these before anything else)
1. Upload a text PDF; clear errors for scanned, encrypted, corrupt or oversized files
2. Ask a question; get a structured answer with **category**, **plain-language explanation**, **verbatim quote**, **page number**
3. "Summarise key terms" button covering rent, deposit, notice period, termination, penalties, repairs
4. "The document does not state this" for unanswered questions (threshold in code)
5. Refusal plus escalation for verdict-style questions ("is this legal / enforceable / should I sign?")
6. Permanent disclaimer shown by the UI (not generated by the model)
7. Delete-session button that clears the in-memory document, index and chat
8. Model-unavailable error message with no fake analysis

### Should have (after the MVP passes the offline test)
9. **Missing Promise Detector:** a fixed checklist of lease topics (deposit return, repairs, rent increase, early termination, notice period, late fees). For each topic, code searches the passages; if nothing clears the threshold, show "No clear condition found in the analysed text." Absence is not illegality.
10. Prompt-injection warning banner when the document contains instruction-like text
11. Benchmark table in README

### Stretch (only if time remains; never at the cost of the above)
12. **Contract Cross-Examiner:** flag clauses that may conflict (for example deposit returned in 7 days vs 30 days). Show both passages. Use "possible inconsistency, needs review", never "contradiction proven".
13. Local OCR for scanned PDFs
14. Two-version comparison

---

## 9. Answer rules (apply to code, prompts and UI)

1. Every statement shown as "the document says" must carry a verbatim quote and page number that **passed the substring check**.
2. Interpretations and concerns are labelled as such and shown in a separate block.
3. If evidence is weak, say "Needs review" or "The document does not state this". Never guess.
4. Never say a clause is legal, illegal, valid, void or enforceable. Say that this depends on local law and a qualified professional can confirm.
5. Escalation advice should be specific (for example "ask a lawyer or a local tenants' association to review the deposit and termination clauses"), not a generic line.
6. The disclaimer text is fixed: *"This tool is for preliminary document understanding. It is not a lawyer and does not give legal advice. Please consult a qualified legal professional for decisions that matter."*
7. Document text is **untrusted data**. Instructions inside the document are never followed.

---

## 10. Team and ownership (summary)

Full detail and function signatures are in `docs/TEAM_ROLES_AND_CONTRACTS.md`.

| Role | Owner (fill in) | Laptop | Files owned | Key deliverable |
|---|---|---|---|---|
| R1 Model and runtime, privacy evidence | ______ | RTX 2050 | `src/llm.py`, `src/config.py`, `docs/benchmarks.md`, privacy evidence | Local Gemma answering; benchmark; offline test recording |
| R2 Ingestion and retrieval | ______ | CPU | `src/ingest.py`, `src/retrieval.py` | Pages, clauses, top-3 passages with scores |
| R3 Answer pipeline and guardrails | ______ | CPU | `src/guardrails.py`, `src/prompts.py`, `src/answer.py` | Verified structured answers; silent, refusal, injection handling |
| R4 UI, Git master, docs, submission | ______ | CPU | `app.py`, `tests/`, `README.md`, repo files | Working UI; clean public repo; submission pack |

**One file, one owner.** If you need a change in someone else's file, ask them or open a Pull Request they review.

---

## 11. Timeline

The execution plan assumes a **10-hour** hackathon window. The guide says deadlines and the portal are announced separately by the organisers, so **confirm the real schedule** (section 16). If you have more days, keep the same order and use the extra time on tests, the offline evidence and documentation.

| Hours | Goal | Exit check |
|---|---|---|
| 0:00-1:30 | Repo created; Ollama and candidate models pulled; benchmark; embedding model downloaded to `models/`; stub LLM backend ready | A model answers a short fictional clause locally; chosen model recorded |
| 1:30-3:30 | `ingest.py` and `retrieval.py` working on sample leases | 3 correct passages with page numbers for 5 test questions |
| 3:30-6:30 | `guardrails.py`, `prompts.py`, `answer.py`; silent, refusal and quote verification working | Tests T3, T4, T5 pass |
| 6:30-8:00 | `app.py` wired to the real pipeline; delete button; error messages | Full flow works end to end on one laptop |
| 8:00-9:00 | Missing Promise Detector (should-have); injection banner | Optional features behave honestly |
| 9:00-10:00 | Offline run, connection monitoring, recording, README, repo polish, submission checklist | Every box in `docs/SUBMISSION_CHECKLIST.md` ticked |

**Checkpoint rule:** if by hour 3 no candidate model answers usefully on any laptop, cut scope (summary and clause lookup only) rather than adding features.

---

## 12. Scoring strategy

Final score = 0.70 x track score + 0.30 x common score. A failed gate means not ranked. Poor on grounding, uncertainty or privacy caps the PS2 score at 40.

| Rubric item (PS2) | Pts | Our main lever |
|---|---|---|
| Accuracy of explanations | 15 | Narrow scope; test set; plain language checked by a non-lawyer teammate |
| Grounding and traceability | 15 | Code-built citations; substring check; "document is silent" demo |
| Uncertainty, refusal, escalation | 15 | Rule-based verdict refusal; `uncertainty` field; specific escalation lines |
| On-device privacy and isolation | 15 | Single-machine demo; offline run; connection monitor; code audit; no temp files |
| Gemma integration and deployment | 10 | Documented model, quantisation, runtime, RAM, speed |
| Robustness | 12 | Malformed PDF, scanned PDF, long doc, vague clauses, injection tests |
| Usability and clarity | 8 | Two-pane layout, priority ordering, plain words |
| Reusability and documentation | 10 | README, pinned deps, works on any lease PDF |

**Common rubric (30%):** functional completeness (20 pts) counts all mandatory features working on inputs you did not script, so test on a lease nobody on the team wrote.

---

## 13. Risk register

| Risk | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|
| Model too slow on CPU | High | High | Benchmark in hour 1; top-3 passages only; QAT build; show passages first | R1 |
| Gemma 3n or 4 not working in Ollama on a team laptop | Medium | High | Try the other candidate; check Ollama version; fall back to another local runtime (for example llama.cpp) | R1 |
| Hidden network call found in a dependency | Medium | Critical | Offline run, connection monitor, code audit, env vars | R1 + R4 |
| Model invents quotes | High | Critical | Substring check drops them; UI shows code-extracted passages | R3 |
| Vibe-coded code nobody understands | High | Medium | Every owner explains their file in 2 minutes; AI asked to comment code | all |
| Merge conflicts or lost work | Medium | Medium | One file one owner; PRs; commit often | R4 |
| 16 GB RAM exhausted during demo | Medium | High | Close other apps; smaller model; test the exact demo machine | R1 |
| Scanned PDFs break the app | Medium | Medium | Detect low text and show a clear message | R2 |
| Output sounds like legal advice | Medium | Critical | Fixed disclaimer; banned-phrase filter; verdict refusal; reviewed samples | R3 |
| Demo machine differs from judge machine | Medium | Medium | README states minimum spec; tested on a CPU-only laptop | R4 |
| Dataset or sample licence problem | Low | Medium | Only fictional leases written by the team; disclose in README | R4 |

---

## 14. Definition of done and demo script

**Done means:** all must-haves work, on one laptop, with Wi-Fi off, on a lease nobody on the team wrote, and the evidence pack exists.

**Demo script (about 5 minutes, recorded):**
1. Show the repo, licence and README (20 s)
2. Turn Wi-Fi off, show connection monitor running (20 s)
3. Upload a fictional lease; show it loaded locally (20 s)
4. Ask about deposit and notice period; show explanation, quote and page side by side (60 s)
5. Ask about something the lease does not cover; show "The document does not state this" (30 s)
6. Ask "Is this clause enforceable?"; show the refusal and escalation (30 s)
7. Open a lease with a hidden "ignore previous instructions" line; show the warning and that the answer is unaffected (40 s)
8. Upload a scanned PDF; show the clear unsupported message (20 s)
9. Press Delete session; show the app is empty (15 s)
10. Show the connection monitor: no external connections (20 s)
11. State limits honestly (20 s)

---

## 15. Glossary for the non-coders

| Term | Plain meaning |
|---|---|
| **On-device / local** | Runs on this laptop only; no internet needed to process the document |
| **LLM / Gemma** | The AI language model that writes explanations |
| **Ollama** | A program that runs the model on your laptop and answers requests on `localhost` |
| **localhost / 127.0.0.1** | "This computer only"; other devices cannot reach it |
| **Embedding** | Numbers that represent the meaning of a piece of text, used for finding similar text |
| **Retrieval / RAG** | Finding the most relevant passages first, then giving only those to the model |
| **Chunk / clause** | A small piece of the document, ideally one clause |
| **Prompt** | The instructions plus text sent to the model |
| **Hallucination** | The model stating something not supported by the text |
| **Quantisation (Q4, QAT)** | Shrinking a model so it uses less memory |
| **Prompt injection** | Text inside a document that tries to give the model new orders |
| **Gate** | A pass/fail requirement; failing one means not being ranked |
| **Vibe coding** | Writing code by asking an AI assistant; allowed, but you must still test and understand it |

---

## 16. Open questions to confirm with the organisers

1. Exact deadline, submission portal and team rules (the guide says these are announced separately)
2. Whether judges will run on their own hardware or review the recording
3. Whether Gemma 3n E2B or Gemma 4 E2B is preferred when both are available (the guide accepts both)
4. Whether Ollama as the runtime is acceptable (the guide leaves runtime to us)
5. Whether a short, clearly fictional sample lease written by the team is the expected test input

---

## 17. Change log

| Date | Who | Change |
|---|---|---|
| 18 Oct 2026 | Project pack v1.0 | Initial master; reconciled three planning documents; replaced `gemma2:2b`; made final demo single-machine |

## 4A. Multiple document types (added 18 Oct 2026)

**Principle:** one shared pipeline, one config per document type, and a type counts as Supported only with passing evidence.

| Type | Status | Config file | Owner | Enters Supported status when |
|---|---|---|---|---|
| Residential rental agreement | Supported (first release) | `src/doc_types/rental.py` | R3 | Rental test set (`docs/TEST_PLAN.md` section 7) passes and is recorded in `docs/TEST_RESULTS.md` |
| Employment contract | Planned | `src/doc_types/employment.py` | R3 | Starts only after rental is stable (midpoint check); needs its own fictional samples and test set |
| Service agreement | Planned | `src/doc_types/service.py` | R3 | As above |

Rules:
1. The user selects the document type. The app never silently guesses it.
2. Each type file defines: topic checklist (for the Missing Promise Detector), escalation wording, and example questions. Verdict-refusal rules are shared and cannot be switched off per type.
3. Results are reported per type. A result for one type is never shown as evidence for another.
4. Adding a type means adding a config file and a test set, not changing the pipeline.
5. If the midpoint check fails on rental, no second type is started. Record the decision here.

**Midpoint check (hour 5):** rental passes T1, T3, T4, T5 on the sample set? [yes / no] Decision on second type: [ ]

| 18 Oct 2026 | Project pack v1.1 | Added multi-type support (rental supported; employment and service planned); DATASETS.md; per-type tests |
