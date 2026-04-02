# Learning: Empty Watch Token Efficiency

**Date**: 2026-04-02
**Source**: Sessions 89-98, extended empty board watch
**Context**: Ten consecutive sessions with no board assignments

## Pattern

When the board is empty for multiple consecutive sessions, each session follows an identical pattern: recap → standing orders → schedule checks → rest. The information yield per session approaches zero after the first confirmation that the board is empty.

## Insight

The rest-sooner norm correctly shortens individual sessions, but doesn't address the cycle frequency. A graduated rest interval — longer sleeps after consecutive empty checks — would reduce total token cost while maintaining responsiveness. The current pattern burns ~40 min of context per session for essentially one API call's worth of new information.

## Application

- When board has been empty for 3+ consecutive sessions, consider suggesting longer rest intervals
- A "quiet mode" schedule adjustment could extend 368 from 10m to 30m during confirmed quiet periods
- The wolf stays ready, but doesn't need to pace the same circle every hour
