# Scope Fidelity in Task Routing

**Date**: 2026-03-27
**Source**: Session 7 — PWA built then reverted same day

## Pattern

When tasks are routed through intermediaries (Gorn → Gnarl → Flint), scope can lose fidelity. "Make Den Book installable on iPhone" was interpreted as PWA, but Gorn meant native app (Capacitor) for Apple Health integration.

## Lesson

When a task description is ambiguous about technical approach, confirm scope with the source before building. Especially when there are multiple valid interpretations (PWA vs native app, REST vs WebSocket, etc.).

## Applied

- Before building, ask: "Is this PWA or native?" rather than assuming
- If the intermediary says "directly approved," still verify the technical approach if it's ambiguous
- The cost of a 2-minute clarification is less than the cost of building and reverting
