# Lesson: Fixed-interval scheduling wastes tokens during sustained empty watch

**Date**: 2026-04-02
**Source**: Sessions 88-96 — eight consecutive empty watch cycles
**Context**: Schedule 368 (board check every 10m) fires repeatedly with no changes

## Pattern

When the board has been empty for multiple consecutive sessions, a fixed 10-minute check interval generates noise without value. Each check costs tokens for the same "nothing new" result.

## Insight

Scheduling should be adaptive — short intervals during active work, longer intervals during sustained quiet. A simple heuristic: if N consecutive checks return empty, extend the interval (e.g., 10m → 30m → 1h). Reset to short interval when a new task appears.

## Application

Next time discussing scheduler improvements with the pack, propose adaptive intervals as a feature. Until then, the current fixed interval is fine — it's a small cost, and responsiveness matters more than efficiency when work does arrive.
