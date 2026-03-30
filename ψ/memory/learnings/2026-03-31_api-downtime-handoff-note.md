# Learning: Note API downtime in handoff

**Date**: 2026-03-31
**Source**: Session 45 — forum/DM APIs unreachable during standing orders
**Context**: Standing order checks for forum mentions and DMs failed silently. No retry within session.

## Pattern

When an API is down during standing orders, the check is simply skipped. If work was assigned via that channel, it gets missed until the next session when the API recovers.

## Lesson

When standing order checks fail due to API downtime, note it explicitly in the handoff so the next session knows to retry those specific checks first.

## Tags

operations, standing-orders, api-reliability, handoff
