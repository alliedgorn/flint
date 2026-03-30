# Lesson: Scheduler Overhead During Extended Idle

**Date**: 2026-03-30
**Source**: Session 27, 17th consecutive empty-board session
**Context**: Scheduler #368 fires every 10 minutes to check PM Board tasks. During 17+ sessions of empty board, every ping returns the same result.

## Pattern

Recurring schedulers designed for active work periods create noise during extended idle. The check becomes mechanical — no new information, just ceremony.

## Insight

Schedulers should either adapt their interval based on consecutive empty results, or Beasts should be empowered to pause non-critical schedules during confirmed idle stretches (with auto-resume when board state changes).

## Application

- When board has been empty for 5+ consecutive checks, consider proposing a longer interval or pause to Gorn
- Don't let mechanical overhead mask the signal — if every check returns empty, the check itself has become the noise
