# Lesson: Batch reaction lookups during pack cycle transitions

**Date**: 2026-03-31
**Source**: Session 46 — monitoring 12+ pack check-ins in thread #58

## Pattern

During pack rest/wake transitions, thread #58 gets 10-15 messages in quick succession. Looking up each message ID individually (fetch thread, find author+keyword, get ID, react) is slow and repetitive.

## Insight

Could fetch the thread once, extract all new message IDs in one pass, then fire reactions in batch. The current one-at-a-time approach works but adds unnecessary latency during high-traffic periods.

## Application

When monitoring a high-traffic thread during pack transitions, consider fetching once and processing multiple messages from a single API response rather than re-fetching per message.
