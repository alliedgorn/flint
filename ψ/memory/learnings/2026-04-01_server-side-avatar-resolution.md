# Server-Side Avatar Resolution

**Date**: 2026-04-01
**Context**: T#602 guest avatar investigation

## Pattern

When displaying user avatars across different session types (owner vs guest), resolve avatars server-side and include them in the API response rather than fetching them client-side from a separate endpoint.

Client-side avatar fetching breaks when:
- The fetch endpoint requires a different auth level than the viewer has
- The lookup key doesn't match the display name format (e.g., `gorn (guest)` vs `gorn`)
- Multiple views need the same data but have different access patterns

## Key Details

- oracle-v2 production DB is at `~/.oracle/oracle.db` (from `src/config.ts`), not `data/oracle.db`
- The server already returns `author_avatar_url` in thread message responses — frontend should use this directly
- Guest author format: `[Guest] DisplayName` — name extraction must handle suffixes like ` (Guest)` in display names
