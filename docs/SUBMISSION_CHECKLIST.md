# Submission Checklist

Tick every box before submitting. A failed **gate** means the team is not ranked, whatever the score. Deadlines and the portal are announced separately by the organisers; confirm them.

## A. Compliance gates (pass/fail)

| Gate | Requirement | Done | Evidence |
|---|---|---|---|
| G1 | Public repo with an open-source licence file in the root | [ ] | Repo URL, `LICENSE` visible in a private browser window |
| G2 | A judge can run the core demo without undisclosed credentials or paid services | [ ] | README setup steps tested on a clean machine |
| G3 | The demo shows the real system, no mock-ups or hard-coded outputs | [ ] | Recording; `STUB_LLM` is off in the demo |
| G4 | Dataset sources and licences disclosed; no private or non-redistributable data committed | [ ] | `sample_documents/README.md`, README data section |
| G5 | No keys, tokens or passwords in the repo | [ ] | `git log -p` scan; grep for `key`, `token`, `password` |
| L1-L4 (PS2) | Gemma used and run locally | [ ] | Benchmark file, README model section |
| | No private content leaves the device | [ ] | `docs/evidence/` |
| | No systematic fabrication of clauses or citations | [ ] | T3 results |
| | Not presented as legal advice; safe escalation shown | [ ] | Screenshots of refusal and disclaimer |

## B. PS2 mandatory features

| ID | Feature | Done |
|---|---|---|
| L1 | Local ingestion of PDF or plain text | [ ] |
| L2 | On-device extraction and interpretation | [ ] |
| L3 | Plain-language summaries and explanations | [ ] |
| L4 | Obligations, rights, deadlines, penalties, termination identified | [ ] |
| L5 | Responses supported by identifiable passages | [ ] |
| L6 | Explicit statements distinguished from interpretations and concerns | [ ] |
| L7 | Ambiguity, insufficient evidence and jurisdiction issues recognised | [ ] |
| L8 | Unsupported conclusions refused; qualified professional recommended | [ ] |
| L9 | Demonstrable privacy | [ ] |
| L10 | Meaningful Gemma use; reproducible open-source implementation | [ ] |

## C. Deliverables S1-S10 (both tracks)

| ID | Deliverable | Where | Done |
|---|---|---|---|
| S1 | Public repo with licence | repo root | [ ] |
| S2 | README: overview, setup, how to run, configuration, troubleshooting | `README.md` | [ ] |
| S3 | Dependencies and environment: pinned requirements, tool versions, OS and hardware tested, model file sizes | `requirements.txt`, README table | [ ] |
| S4 | Architecture diagram or explanation | `docs/ARCHITECTURE.md` | [ ] |
| S5 | Dataset sources, licences, preparation steps, attributions | README + `sample_documents/README.md` | [ ] |
| S6 | How Gemma is used | README + architecture | [ ] |
| S7 | Working demonstration (recording of up to about 5 minutes recommended) including limits | video link in README | [ ] |
| S8 | Testing results and known limitations, honestly stated | `docs/TEST_RESULTS.md` | [ ] |
| S9 | Instructions to reproduce the demonstration | README | [ ] |
| S10 | Short statement of main technical contribution | README | [ ] |

## D. Extra for PS2

| Item | Done |
|---|---|
| Evidence of local processing: recording or log of a full analysis with the network disabled, plus connection-monitoring output | [ ] |
| Explanation of how transmission of private documents is prevented, and **every** remaining network call | [ ] |
| Model acquisition instructions: weights, licence to accept, variant, quantisation, runtime | [ ] |
| Sample outputs showing cited passages beside the source, and a "document is silent" case | [ ] |
| Recommended: refusal and escalation examples | [ ] |
| Recommended: adversarial and prompt-injection test results | [ ] |

## E. Common rubric (30%): quick self-check

| Criterion | Pts | Check |
|---|---|---|
| C1 Problem understanding | 10 | README states users, problem and scope clearly |
| C2 Functional completeness | 20 | All mandatory features work on the unscripted lease (D9) |
| C3 Technical design | 15 | Architecture explained; decisions justified (for example why in-memory, why no LangChain) |
| C4 Open-source quality | 15 | Licence, structure, `CONTRIBUTING.md`, `SECURITY.md`, issue and PR templates |
| C5 Reproducibility | 15 | A newcomer follows the README from zero to demo; pinned dependencies |
| C6 UX and accessibility | 10 | Clear flow, readable text, labelled inputs, helpful errors |
| C7 Testing and reliability | 10 | `pytest` passes; bad input handled; limitations honest |
| C8 Demo and rationale | 5 | Everyone can explain their file and trade-offs |

## F. Last-hour technical checks (R1 + R4)

- [ ] Fresh clone on a different laptop: README setup works end to end
- [ ] `requirements.txt` pinned; Python version stated
- [ ] `MODEL_NAME` in `config.py` matches the model in the README
- [ ] `OLLAMA_URL` is `http://127.0.0.1:11434`; no LAN IP anywhere (`grep -rn "192.168\|10\.\|0.0.0.0" .`)
- [ ] No `gemma2` string anywhere (`grep -rni gemma2 .`)
- [ ] `models/`, `.venv/`, `.env` are not tracked (`git ls-files`)
- [ ] `.streamlit/config.toml` sets `gatherUsageStats = false`
- [ ] Offline run recorded on the final demo laptop with monitoring visible
- [ ] Temp-file search done before and after Delete session
- [ ] Recording link works in a private browser window
- [ ] Repo is public; tag `v1.0` pushed
- [ ] Name check: project name not clashing with an existing GitHub project

## G. Final honesty read-through (everyone, 10 minutes)

Read the README aloud. For each sentence, ask: "Do we have evidence for this?" Remove or soften any claim we cannot show. Replace "secure", "100% private" and "accurate" with what we actually tested.

## H. Multiple document types

| Item | Done |
|---|---|
| README lists each type with an honest status (Supported / Planned) | [ ] |
| Every Supported type has a section in `docs/TEST_RESULTS.md` with its own pass/fail table | [ ] |
| No result for one type is presented as evidence for another | [ ] |
| Planned types refuse analysis with a clear message (test X2) | [ ] |
| Cross-type checks X1 to X3 run | [ ] |
| Midpoint decision on second type recorded in `PROJECT_MASTER.md` section 4A | [ ] |
| Datasets section in README matches `docs/DATASETS.md`; no dataset files committed | [ ] |
