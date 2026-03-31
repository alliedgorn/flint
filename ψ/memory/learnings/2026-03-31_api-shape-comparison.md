# Lesson: Compare API response shapes before building frontend

**Date**: 2026-03-31
**Source**: Session 50 — Guest Mode build
**Context**: Guest API endpoints returned different response shapes than private API (missing reactions, reply_to_id). This caused crashes that required multiple fix cycles.

## Pattern

When building frontend code that talks to two different API surfaces (private vs guest, v1 vs v2), always:

1. `curl` both endpoints and compare the JSON keys
2. Handle missing fields with optional chaining or defaults
3. Test the actual guest flow before submitting for review

## Anti-pattern

Building the entire frontend against the private API shape, then swapping to guest endpoints and discovering mismatches through production crashes.

## Cost

3 extra fix-commit cycles, each requiring rebuild + push + Gorn re-test. Could have been zero with 5 minutes of upfront API comparison.
