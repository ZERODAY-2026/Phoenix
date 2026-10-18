# Contributing to ClauseGuard

Thanks for helping. ClauseGuard is a privacy-first tool, so a few rules matter more than usual.

## Ground rules

1. **No network calls** in application code other than to the local Ollama server on `127.0.0.1`. No telemetry, analytics, cloud APIs or runtime model downloads.
2. **No real or private documents** in issues, tests, screenshots or commits. Use the fictional files in `sample_documents/`.
3. **No secrets** in the repository.
4. **Never output legal verdicts.** Contributions must not make ClauseGuard say a clause is legal, illegal, valid, void or enforceable.
5. **Every quote shown to a user must be verifiable** against the document text.

## Getting started

```
git clone <repo_url>
cd clauseguard
python -m venv .venv && .venv\Scripts\activate   # or: source .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

## Workflow

1. Open an issue describing the change (use the templates if provided).
2. Create a branch: `git checkout -b feature/short-description`.
3. Make a small, focused change with tests.
4. Run `pytest -q` and, for anything touching I/O or dependencies, the network audit in `docs/PRIVACY.md`.
5. Open a Pull Request using the template; describe what changed and how you tested it.

## Style

- Python 3.11+, type hints, short functions, comments for non-obvious logic
- Plain-language user-facing text; avoid legal jargon without explanation
- New dependency? State its purpose, licence and whether it can make network calls

## Good first contributions

- More lease layouts and fictional test documents
- Better clause splitting for unusual numbering
- Local OCR for scanned PDFs (offline only)
- Translations of the interface and explanations (offline only)
- Additional adversarial tests (misleading clauses, injection attempts)
