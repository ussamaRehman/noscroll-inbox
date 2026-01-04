# PRD: NoScroll Inbox

## Overview
NoScroll Inbox lets users learn from X without opening X. Users DM a bot with links, then receive a clean inbox (and later a digest).

## MVP Contract
- Product: Learn from X without opening X.
- Capture: user DMs links to a bot X account (primary).
- Launch: invite-only.
- Auth: Flow 2 (DM-first with email + magic link).
  - User sends DM: start user@email.com
  - System links X handle to email and sends magic link
- Dashboard (MVP): Inbox + Search. Categories + Digest are MVP-later (Phase 1.1).
- Non-goals for MVP: no For You replication, no auto-scrape 500-1500 per day, no teams, no mobile app, no billing.

## Auth Flow 2 Contract (DM-first with email + magic link) — MVP

### Purpose
Link an X DM sender (x_handle) to an email so they can access their saved Inbox via a magic login link.

### Invite-only rule (MVP)
- Access is invite-only via **email allowlist**.
- A user is eligible only if the email used in `start <email>` is on the allowlist.

### States
- **UNLINKED**: sender is not linked to any user account yet.
- **LINKED**: sender is linked to exactly one user account (email).
- **BLOCKED**: sender attempted to start with a non-allowlisted email.

### DM Commands (exact)
1) Start (required):
- `start user@email.com`

2) Help (optional):
- `help`

### Validation rules
- Email must match basic format: `local@domain.tld` (strict enough to catch obvious mistakes).
- `start` is case-insensitive, but canonical form is lowercase.

### Outcomes + bot replies (exact)

#### A) UNLINKED + valid allowlisted email
Action:
- Create/lookup User(email)
- Link sender x_handle ↔ User(email)
- Send magic link email
Reply:
- `✅ Linked. Check your email for a sign-in link.`

#### B) UNLINKED + invalid email format
Reply:
- `❌ Invalid email. Send: start your@email.com`

#### C) UNLINKED + email not allowlisted
Action:
- Do not link
Reply:
- `🚫 Invite-only right now. You're not on the allowlist. Reply with: start your@email.com and we'll notify you if approved.`

#### D) LINKED + start called again with same email
Action:
- Re-send magic link (idempotent)
Reply:
- `✅ You're already linked. I just sent a new sign-in link to your email.`

#### E) LINKED + start called with different email
Action:
- Do not change link in MVP
Reply:
- `⚠️ This X account is already linked to a different email. Reply: help`

#### F) Any state + help
Reply:
- `Send: start your@email.com (invite-only MVP). Then DM me any X post link to save it.`

### Link capture rules (MVP)
A “link message” is any DM containing at least one URL.

#### If sender is UNLINKED and sends a link
Reply:
- `👋 To save links, first link your account: start your@email.com`

#### If sender is BLOCKED and sends a link
Reply:
- `🚫 Invite-only right now. You're not approved yet. Reply with: start your@email.com`

#### If sender is LINKED and sends a link
Action:
- Save item(s) to that user’s Inbox
Reply:
- `Saved ✅`

### Multiple links in one message
- Save up to N links per message (MVP: N=5).
- Reply stays: `Saved ✅`

### Notes/tags in link messages (MVP parsing)
Supported optional hints:
- `#tag` (store as tag hint; no category logic required in MVP)
- `note: ...` (store as user_note)

Examples:
- `https://x.com/... #tools`
- `https://x.com/... note: new eval framework`

## Goals
- Zero-open X learning flow
- Simple onboarding via DM
- Clear, low-noise inbox

## Users
- Knowledge workers who want to keep up with X without doomscrolling

## User Flow (MVP)
Happy path:
1) User DMs: start user@email.com
2) Bot links account and emails magic link
3) User DMs bot a post link to save it
4) Bot replies: Saved ✅
5) User uses magic link to open dashboard (Inbox + Search)

Edge case:
- If the user sends a link before `start`, bot replies asking them to run `start user@email.com` first.

## MVP Scope
- Bot DM intake
- Link capture and storage
- Email capture and magic link
- Dashboard (MVP): inbox + search

## Capture Message Formats
- link-only
- link + #tag
- link + note: ...
- For MVP: store raw + parse URLs; categorize later

## Out of Scope
See Non-goals in MVP Contract.

## Success Metrics
- Percent of invited users who complete DM auth
- Links captured per user per week
- Weekly active inbox readers

## Risks
- X API limits or policy changes
- Email deliverability

## Open Questions
- What inbox information density is right for MVP?
- Should categories be default-on or opt-in?
