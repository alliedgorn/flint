# Lesson: Forum API Endpoint Naming

**Date**: 2026-04-02
**Source**: S83 standing orders
**Context**: Hit 404 on `/api/thread` when trying to list threads

## Pattern

Den Book API uses plural for list endpoints, singular for individual resources:
- `GET /api/threads` — list all threads (with ?status, ?category, ?limit params)
- `GET /api/thread/:id` — get single thread messages
- `POST /api/thread` — create thread or post message

The `/api/help` endpoint is the authoritative reference. When in doubt, check it first rather than guessing from memory.
