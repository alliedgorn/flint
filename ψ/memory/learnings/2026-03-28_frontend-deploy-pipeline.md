# Learning: Frontend Deploy Pipeline

**Date**: 2026-03-28
**Source**: Forge redesign session — Gorn couldn't see changes

## Pattern
Committing frontend code to the oracle-v2 repo does NOT deploy it. The server serves static files from `frontend/dist/`, which is a built artifact.

## Deploy Steps
1. Code changes in `frontend/src/`
2. `cd frontend && bun run build` — compiles TypeScript + Vite bundle into `dist/`
3. Server automatically serves new dist files (no restart needed for frontend)
4. Backend changes (server.ts) require server restart: `kill $(lsof -ti :47778) && bun run src/server.ts &`

## Key Insight
Multiple beasts rebuilding simultaneously is wasteful. One beast should own the deploy after coordinating that all changes are committed.

## WebSocket Timing
WS events (`dm_read`) can arrive at the client before the HTTP response that triggered them completes. If the client fetches data on WS event, add a small delay (500ms) to ensure the DB write has committed.
