# Progress

## Now
- ✅ TC-001: Lock Auth Flow 2 DM command spec + replies (done)
- ✅ TC-003: Add FastAPI skeleton + CI commands (code) (done)
- 🔜 TC-002: Implement Auth Flow 2 DM parsing + reply templates (code)
- 🔜 TC-002E: Persist allowlist + links + inbox to SQLite (stdlib sqlite3)
- 🔜 TC-002F: Magic link stub (SQLite token + /auth/magic)
- 🔜 TC-002H: Digest endpoint (group by tag)
- 🔜 TC-002I: Digest email preview (subject + body, no sending)
- 🔜 TC-002J: Digest send dry-run + sent-log (sqlite)
- 🔜 TC-002B: Add /simulate_dm endpoint for local contract testing

## Task Card 001
Title: TC-001: Lock Auth Flow 2 DM command spec + replies
Goal: User can onboard via DM start email (invite-only).
Scope: DM parsing + reply templates + allowlist behavior (docs-only).
Non-goals: Categories, digest, UI, scraping.
Edge cases:
- Invalid email format
- Email not on allowlist
- Link received before start email
Acceptance:
- PRD contract updated
- WORKFLOW aligned
- Edge cases listed
Rollback strategy:
- 1 commit per logical change; revert commit if needed

## Task Card 002
Title: TC-002: Implement Auth Flow 2 DM parsing + reply templates (code)
Goal: Bot enforces invite-only Auth Flow 2 and replies exactly as specified in PRD.
Scope: DM parsing (`start`, `help`, link messages), allowlist check, state handling, reply templates.
Subtask: TC-002A: Pure DM parsing + reply selection (code+tests).
Subtask: TC-002C: In-memory inbox storage + retrieval (code+tests).
Subtask: TC-002D: link x_handle->email + allowlist + route saves by handle.
Non-goals: Categories/digest, UI beyond minimal, scraping, billing.
Acceptance:
- DM `start email` works (allowlisted and non-allowlisted cases)
- Link before start triggers the exact PRD reply
- LINKED link message saves and replies `Saved ✅`
Rollback strategy:
- 1 commit per logical change; revert commit if needed

## Task Card 003
Title: TC-003: Add FastAPI skeleton + CI commands (code)
Goal: Repo can run /health and pass make ci.
Scope: app/main.py, tests, Makefile, pyproject, ruff/pytest.
Non-goals: DM parsing/auth/UI.
Acceptance:
- make ci passes
- make dev runs
- /health works
Rollback strategy:
- 1 commit per logical change; revert commit if needed

## Log
- 2026-01-04: Repo initialized
- 2026-01-04: Docs polished + TC-001 added
- 2026-01-04: TC-003 skeleton added
- 2026-01-04: TC-003 skeleton verified (make ci green) + uv.lock committed
- 2026-01-04: TC-002B /simulate_dm added
- 2026-01-04: TC-002C in-memory inbox added
- 2026-01-04: TC-002D x_handle linking + allowlist added
- 2026-01-04: TC-002E SQLite persistence added
- 2026-01-04: Queued TC-002F
- 2026-01-04: Queued TC-002H
- 2026-01-04: Queued TC-002I
- 2026-01-05: Added TC-002J
- 2026-01-04: Added make demo runner (local)
