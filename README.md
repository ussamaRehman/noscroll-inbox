# NoScroll Inbox

Learn from X without opening X.

Status: docs-first bootstrap. No application code yet.

Docs:
- docs/PRD.md
- docs/WORKFLOW.md
- docs/DECISIONS.md
- docs/PROGRESS.md
- docs/CODEX_PROMPT.md

## Database
Default DB file: noscroll.db (repo root).
Override with: DB_PATH=/path/to/file.db

Examples:
- DB_PATH=noscroll.db make dev
- DB_PATH=noscroll.db EMAIL=demo@example.com DAYS=365 make send-digests
