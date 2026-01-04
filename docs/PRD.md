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
- Dashboard (future): Inbox + Categories (per-user enabled) + Search + Daily Digest.
- Non-goals for MVP: no For You replication, no auto-scrape 500-1500 per day, no teams, no mobile app, no billing.

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
- Basic inbox view (internal prototype)

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
