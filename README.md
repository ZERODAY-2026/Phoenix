# ClauseGuard

A private, on-device assistant that helps you understand a legal document. It explains clauses in plain language, shows the exact passage and page behind each quoted explanation, says so when the document is silent, and declines to give legal verdicts.

> **Not legal advice.** ClauseGuard is for preliminary document understanding. It is not a lawyer and does not give legal advice. It cannot decide whether a clause is legal, valid or enforceable. Please consult a qualified legal professional for decisions that matter.

Built for ZeroDay OSS Hacktoberfest 2026 (IIIT Dharwad), Problem Statement 2: Private Legal Document Triage Agent.

<!-- INTERNAL: replace every [bracketed] item and delete this comment before submitting. -->

---

## What it does

- Reads a text-based PDF or `.txt` document on your own laptop
- Answers questions with a plain-language explanation, a verbatim quote and a page number
- Separates "stated in the document" from "possible interpretation" and "possible concern"
- Says "The document does not state this." when the document does not address a question
- Declines questions that ask for a legal verdict, and suggests who to ask instead
- Warns when a document contains text that tries to instruct the AI, and ignores that text
- Keeps document content in memory and can clear the session with one click

## Supported document types

Each type is a separate, explicitly scoped feature. A type is listed as **Supported** only when it has a passing test set in `docs/TEST_RESULTS.md`.

| Document type | Status | Scope | Test evidence |
|---|---|---|---|
| Residential rental agreement | **Supported** (first release) | English; text-based PDF or `.txt`; residential leases only | `docs/TEST_RESULTS.md`, rental section |
| Employment contract | Planned | Not yet supported. Added only after the rental tests pass. | Not yet available |
| Service agreement (freelance or consulting) | Planned | Not yet supported. Added only after the rental tests pass. | Not yet available |

**Not supported in any version:** scanned or image-only PDFs (a clear message is shown), non-English documents, legal notices, loan or credit agreements, and any question about whether a clause is legal, valid or enforceable.

### How multiple types are organised

- **One shared pipeline.** Text extraction, clause splitting, retrieval, the local model call and quote verification are the same for every type.
- **Per-type configuration.** Each type has its own file under `src/doc_types/` (planned layout: `rental.py`, `employment.py`, `service.py`). Each file defines the topic checklist, the escalation wording and the question examples for that type.
- **User chooses the type.** The user selects the document type before asking questions. The app does not guess the type silently.
- **Per-type evaluation.** Results are reported separately for each type. A result for one type is never presented as evidence for another.

## Privacy

Documents are processed locally. The AI model runs on your machine through Ollama, which listens only on `127.0.0.1`. The application makes no network calls during document processing. Setup downloads the model and packages; that step involves no user documents.

Privacy testing: [describe the evidence, for example "We ran the full demo with networking disabled and monitored connections during processing. Evidence: `docs/evidence/`."]. Until that evidence exists, do not describe the tool as fully private.

Full threat model, offline test procedure and network inventory: [`docs/PRIVACY.md`](docs/PRIVACY.md).

What ClauseGuard cannot protect against: a compromised device, physical access to an unlocked laptop, operating-system swap files, or screenshots you take yourself.

## Requirements

| Item | Tested value |
|---|---|
| Operating system | [for example Windows 11] |
| CPU / RAM | [for example Ryzen 7 7735HS, 16 GB] |
| GPU | [none, or RTX 2050 4 GB] |
| Python | [3.11.x] |
| Ollama | [version] |
| Model | [model tag], [size] GB on disk |
| Speed | [tokens per second; seconds per answer] (see `docs/benchmarks.md`) |
| Peak RAM | [GB] |

Minimum recommended: 16 GB RAM. No GPU is required.

## Setup (needs internet; no user documents involved)

1. Install [Python 3.11+](https://www.python.org/), [Git](https://git-scm.com/) and [Ollama](https://ollama.com/).
2. Download the model:
   ```
   ollama pull [MODEL_TAG]
   ```
   Accept the model's licence on its official page if required.
3. Clone the repository and install dependencies:
   ```
   git clone [REPO_URL]
   cd clauseguard
   python -m venv .venv
   .venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
   pip install -r requirements.txt
   ```
4. Download the embedding model once:
   ```
   python scripts/download_embedding_model.py
   ```
5. Check `src/config.py` for the model name, or set the environment variable `CLAUSEGUARD_MODEL`.

## Run (works offline after setup)

```
set HF_HUB_OFFLINE=1
set TRANSFORMERS_OFFLINE=1
streamlit run app.py --server.address 127.0.0.1
```

On macOS or Linux, use `export` instead of `set`. Make sure Ollama is running and bound to `127.0.0.1`.

Try the fictional samples in `sample_documents/`.

## How it works

```
document -> text extraction (pdfplumber) -> clause splitter -> local embeddings -> top passages
         -> local Gemma (Ollama) -> code checks (quotes must match the document) -> answer
```

The model explains. Code guarantees. Citations, silence, refusals and the disclaimer are enforced by code, not left to the model. Details: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## How Gemma is used

[Gemma variant] runs locally through Ollama. It rewrites retrieved passages in plain language and classifies each finding (obligation, right, penalty, deadline, termination or other). It does not decide what the document says, whether evidence exists, or whether to refuse. Code makes those decisions.

The model is used as released. **It is not fine-tuned or trained on CUAD, India Code, Open India Law or any other dataset.**

## Datasets and evaluation

| Dataset | Use in ClauseGuard | Status |
|---|---|---|
| Team-written fictional leases (`sample_documents/`) | Main test set for the rental type | Used |
| CUAD (commercial contracts) | Evaluation of clause finding only. Results are not proof for consumer documents. | [Used / not used] |
| India Code, Open India Law | Not used in the first release | Not used |

No dataset is redistributed in this repository. Each dataset is downloaded from its source and used under its own licence. Attribution, licence and download steps are in [`docs/DATASETS.md`](docs/DATASETS.md).

## Testing

```
pytest -q
```

Results, metrics and known limitations for each supported type: [`docs/TEST_RESULTS.md`](docs/TEST_RESULTS.md).

## Known limitations

- Supports residential rental agreements only, in the first release
- Text-based PDFs only; scanned documents are not processed
- Explanations are preliminary and can be incomplete or wrong; always check the quoted passage
- Results on commercial contracts (CUAD) do not show performance on consumer documents
- [Add results-based limits from `docs/TEST_RESULTS.md`]

## Troubleshooting

| Problem | Fix |
|---|---|
| "Model not ready" | Start Ollama; run `ollama list`; run `ollama pull [MODEL_TAG]` |
| "Embedding model not found" | Run `python scripts/download_embedding_model.py` once while online |
| Very slow answers | Close other applications; try a smaller model; see `docs/benchmarks.md` |
| "Looks like a scanned document" | Scanned documents are not supported; use a text-based PDF |
| Port already in use | Close other Streamlit or Ollama instances |

## Contributing, security and conduct

See [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). New document types should follow the process in CONTRIBUTING.md and need their own test set before being marked Supported.

## Our main technical contribution

[Two or three sentences. For example: a citation pipeline in which every quote shown to the user is checked against the extracted text, and a repeatable offline test for a document-processing tool.]

## Licence

MIT. See [LICENSE](LICENSE).
