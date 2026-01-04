# Workflow

This repo is docs-first. Implement only the PRD and Task Cards.

## MVP Contract (must remain aligned with PRD)
- Product: Learn from X without opening X.
- Capture: user DMs links to a bot X account (primary).
- Launch: invite-only.
- Auth: Flow 2 (DM-first with email + magic link).
  - User sends DM: start user@email.com
  - System links X handle to email and sends magic link
- Dashboard (future): Inbox + Categories (per-user enabled) + Search + Daily Digest.
- Non-goals for MVP: no For You replication, no auto-scrape 500-1500 per day, no teams, no mobile app, no billing.

## Roles
- Product: defines scope, priorities, and acceptance criteria.
- Engineering: proposes tasks, estimates, and execution.
- Design: defines UX copy and flows if needed.

## Task Cards
Each task card lives in docs/PROGRESS.md and includes:
- Title
- Context
- Requirements
- Acceptance
- Out of Scope
- Risks
- Dependencies
- Test notes

## Definition of Done
- Requirements met with minimal diff
- No new deps without approval
- Tests added once code exists
- Docs updated as needed

## Guardrails
- PRD-first, no app code until asked
- Invite-only launch
- Auth Flow 2 only
- Do not expand scope without decision entry
- Keep diffs minimal and reversible

## Review Workflow
- Draft task card
- Review against MVP contract
- Execute smallest change
- Update docs/PROGRESS.md
