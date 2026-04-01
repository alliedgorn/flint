# Learning: Empty Watch Efficiency Ceiling

**Date**: 2026-04-02
**Source**: Sessions 86-91 — six consecutive empty watches
**Context**: Board empty, all items waiting Gorn via Sable

## Pattern

When board is empty and all pending items are blocked on external decisions, the wake-check-rest cycle has a floor cost that can't be reduced further within current architecture. Rest-sooner norm cuts the duration, but each cycle still requires: recap, standing orders (forum + DMs + board + scheduler), and N scheduler ticks before rest triggers.

## Insight

The minimum useful session in empty watch is ~20-30 minutes and ~10 tool calls. Below that, the overhead of waking exceeds the value of checking. Above that (holding watch longer), you're just burning scheduler ticks on an empty board.

## Application

- Don't fight the pattern — short empty watches are correct behavior
- The real optimization is at the scheduling layer, not the session layer
- When work lands after a dry spell, the fresh context from clean rests pays off
