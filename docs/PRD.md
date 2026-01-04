# PRD: NoScroll Inbox

## Overview
NoScroll Inbox lets users learn from X without opening X. Users DM a bot with links, then receive a clean inbox and digest.

## MVP Contract
- Product: Learn from X without opening X.
- Capture: user DMs links to a bot X account (primary).
- Launch: invite-only.
- Auth: Flow 2 (DM-first with email + magic link).
  - User sends DM: start user@email.com
  - System links X handle to email and sends magic link
- Dashboard (MVP): Inbox + Search. Categories + Digest are MVP-later (Phase 1.1).
- Non-goals for MVP: no For You replication, no auto-scrape 500-1500 per day, no teams, no mobile app, no billing.

## Auth Flow 2 Contract
- Invite-only allowlist (email allowlist for MVP).
- DM command: `start user@email.com`.
- Validations: email format; allowlist check.
- Outcomes:
  - If allowed: link sender handle to email, send magic link email, DM confirmation.
  - If not allowed: DM invite-only / request access message.
  - If invalid email: DM error + example.
- Link messages can arrive anytime; if user not linked yet, reply "send start email first".

## Goals
- Zero-open X learning flow
- Simple onboarding via DM
- Clear, low-noise inbox

## Users
- Knowledge workers who want to keep up with X without doomscrolling

## User Flow (MVP)
1) User DMs bot link from X
2) Bot acknowledges and stores
3) User DMs start user@email.com
4) System emails magic link
5) User lands in inbox

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
