# React Performance Patterns for Real-Time Chat

**Date**: 2026-03-28
**Source**: Session 8 — ChatOverlay/DMs performance fixes

## Patterns

1. **Memoize ReactMarkdown components at module level** — inline `components={{ img: ... }}` creates new component types every render, causing React to unmount/remount DOM elements (triggering image re-downloads).

2. **Memoize message list items with React.memo** — parent state changes (typing in textarea) shouldn't re-render every message. Extract messages as `memo()` components.

3. **Stable remarkPlugins array** — `remarkPlugins={[remarkGfm]}` creates a new array each render. Move to module-level constant.

4. **WS handlers should skip updates while typing** — check `document.activeElement?.tagName !== 'TEXTAREA'` before triggering state updates that cause re-renders.

5. **Append-only message updates** — WS handler should append new messages to existing array, not replace the whole array. Return same reference if no new messages (React skips re-render).

6. **CSP sandbox breaks image caching** — `Content-Security-Policy: sandbox` on inline image responses causes browsers to bypass disk cache. Only apply to non-image file downloads.

7. **Replace polling with WS + visibilitychange** — WebSocket for real-time, `visibilitychange` event to catch up when tab regains focus. No setInterval needed.
