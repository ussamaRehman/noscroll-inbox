# Progress

## Now
- ✅ TC-001: Lock Auth Flow 2 DM command spec + replies (done)
- 🔜 TC-002: Implement Auth Flow 2 DM parsing + reply templates (code)

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
Non-goals: Categories/digest, UI beyond minimal, scraping, billing.
Acceptance:
- DM `start email` works (allowlisted and non-allowlisted cases)
- Link before start triggers the exact PRD reply
- LINKED link message saves and replies `Saved ✅`
Rollback strategy:
- 1 commit per logical change; revert commit if needed

## Log
- 2026-01-04: Repo initialized
- 2026-01-04: Docs polished + TC-001 added
