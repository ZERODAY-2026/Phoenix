# Document type configurations

Each supported document type has one file here. The shared pipeline reads these files; it does not contain type-specific rules.

| File | Status | Notes |
|---|---|---|
| `rental.py` | Supported (first release) | Written first; the only type in the first release |
| `employment.py` | Planned | Only after the midpoint check and its own test set |
| `service.py` | Planned | Only after the midpoint check and its own test set |

## Required fields (see `docs/ARCHITECTURE.md` section 10)

```python
# src/doc_types/rental.py  (illustrative; the owner writes the real file)
NAME = "Residential rental agreement"
STATUS = "supported"          # must match docs/TEST_RESULTS.md; do not set "supported" without a passing test section
TOPICS = ["deposit return", "repairs", "rent increase", "early termination", "notice period", "late fees"]
ESCALATION = "Ask a tenant advice service or a qualified lawyer to review the deposit and termination clauses."
EXAMPLE_QUESTIONS = ["How much notice do I need to give?", "When is the deposit returned?"]
```

Rules:
- Verdict refusal, silence checks and quote verification are shared and cannot be disabled per type.
- Escalation text must be specific to the type and must not claim the clause is legal or illegal.
- Keep `STATUS` honest. A type is "supported" only with passing evidence.
