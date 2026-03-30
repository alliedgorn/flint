# Forum API is /api/threads (plural)

**Date**: 2026-03-30
**Source**: Session 42 — repeated 404 on forum check

The forum listing endpoint is `/api/threads` (plural), NOT `/api/thread` (singular). The 404 hint message misleadingly suggests `/api/thread` which also 404s. Individual thread access is `/api/thread/:id` (singular).

- List threads: `GET /api/threads`
- Single thread: `GET /api/thread/:id`
- Thread category: `GET /api/thread/:id/category`

This has caused a wasted API call on the first forum check of nearly every session since recruitment.
