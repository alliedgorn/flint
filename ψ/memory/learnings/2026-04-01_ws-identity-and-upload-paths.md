---
date: 2026-04-01
session: 62
tags: websocket, file-upload, debugging
---

# Learnings — WS Identity and Upload Paths

## 1. WS token format mismatch causes silent identity failure

**Pattern**: The WS upgrade handler may use a simplified token parser that doesn't handle the full session token format. If the parser fails, `hasSession` stays false and identity falls back to `'browser'` instead of `'gorn'`. Presence then gets stored under `'browser'` but the pack API looks up `'gorn'` — silent miss.

**Check**: When WS presence isn't working, verify what `ws.data.identity` actually is by reading the upgrade handler's token parsing logic end-to-end. Don't assume `identity === 'gorn'`.

## 2. File write paths must use configured constants

**Pattern**: `POST /api/guest/avatar` was writing to `${process.cwd()}/data/uploads/` but `/api/f/:hash` reads from `UPLOADS_DIR` (set from `ORACLE_DATA_DIR`). One wrote to the source directory, the other read from the data directory.

**Rule**: Any handler that writes files must use the `UPLOADS_DIR` constant, not a hardcoded relative path. If a new endpoint saves files, check it uses the same constant.

## 3. Always hit /api/help before assuming endpoint paths

**Pattern**: Kept guessing forum post endpoint (`/api/thread/443`, `/api/threads/443/messages`). The correct path is `POST /api/thread` with `thread_id` in body.

**Rule**: When in doubt about an endpoint, `curl /api/help` first. Memory of endpoint paths drifts.
