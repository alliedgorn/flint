# Lesson: Scheduler Run API Method

**Date**: 2026-03-30
**Source**: Session 37 — repeated trial-and-error on scheduler endpoint
**Repo**: flint

## Pattern

The Den Book scheduler "mark run" endpoint requires:
- Method: **PATCH** (not POST, not PUT)
- Identity: `?as=<beastname>` query param
- Full URL: `PATCH /api/schedules/:id/run?as=flint`

POST and PUT both return 404 with an unhelpful hint that doesn't specify the method.

## Why It Matters

Saves 2-3 failed attempts per scheduler interaction. This has tripped me up across multiple sessions — the API error message suggests the route exists but doesn't tell you the method.

## Tags

scheduler, api, den-book, operations
