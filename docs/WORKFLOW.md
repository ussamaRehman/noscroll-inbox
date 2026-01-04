# Workflow

This repo is docs-first. Implement only the PRD and Task Cards.

## MVP Contract (must remain aligned with PRD)
- Product: Learn from X without opening X.
- Capture: user DMs links to a bot X account (primary).
- Launch: invite-only.
- Auth: Flow 2 (DM-first with email + magic link).
  - User sends DM: start user@email.com
  - System links X handle to email and sends magic link
- Dashboard (MVP): Inbox + Search. Categories + Digest are MVP-later (Phase 1.1).
- Non-goals for MVP: no For You replication, no auto-scrape 500-1500 per day, no teams, no mobile app, no billing.

## Roles
- ChatGPT = PM + Scope Guardian
- Ussama = Executioner
- Codex = Builder/Tester/Reviewer

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

## PM -> Agent Execution Loop
### Step 0 — PM Task Card (required)
PM posts a Task Card with:
- Goal (user-visible)
- Scope + explicit non-goals
- Files likely touched (3–8 max)
- Commands to run (once code exists: include `make ci`)
- Acceptance checks (3 bullets)
- Rollback strategy (1 commit per logical change)

### Step 1 — Builder (Codex)
Builder:
- Implements minimal diff
- Lists files touched
- Lists commands it expects to pass (if code exists)
- Calls out assumptions and edge cases

### Step 2 — Executioner verification (Ussama)
- Runs relevant commands (when present) and pastes outputs back to PM

### Step 3 — Reviewer + PM sign-off
- Reviewer does 2-pass review (correctness/security, then tests/contracts)
- PM confirms scope + contract alignment and signs off

## Definition of Done
- Minimal diff
- Docs updated when contract changes
- Once code exists: make ci green

## Canonical Commands
- Environment: uv-first (placeholder; no code yet)
- Quality: make ci (once added)

## Guardrails
- PRD-first, no app code until asked
- Invite-only launch
- Auth Flow 2 only
- Do not expand scope without decision entry
- Keep diffs minimal and reversible
- No new deps without approval

## Review Workflow
- Draft task card
- Review against MVP contract
- Execute smallest change
- Update docs/PROGRESS.md
