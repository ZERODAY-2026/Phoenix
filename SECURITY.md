# Security Policy

ClauseGuard handles sensitive documents, so privacy and security reports are welcome.

## Reporting a vulnerability

Please **do not open a public issue** for security or privacy problems. Contact the maintainers at **[team email]** or use GitHub's private vulnerability reporting (Security tab) if enabled. Include steps to reproduce and, if possible, the version or commit. Do **not** include real private documents.

We aim to acknowledge reports within [7] days.

## What counts

- Any code path that sends document content, questions or answers off the device
- Telemetry, analytics or logging that includes document-derived text
- Files written to disk containing document text or embeddings
- Ways to make the app ignore its guardrails (for example prompt injection that yields legal verdicts or fabricated citations)
- Exposure of the local model server beyond `127.0.0.1`

## Supported versions

Only the latest release on `main` is supported.

## Out of scope

A compromised operating system, physical access to an unlocked device, and operating-system swap files.
