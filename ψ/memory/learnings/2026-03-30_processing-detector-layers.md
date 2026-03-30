# Processing Detector — Two-Layer Detection

**Date**: 2026-03-30
**Source**: oracle-v2/src/server.ts (lines ~1471-1490)
**Context**: Gorn asked if "Cackling" is detected in the processing indicator

## Pattern

The oracle-v2 processing detector uses two layers to detect whether a Beast's Claude Code session is processing:

1. **Generic regex**: `/[✻✽·]\s+\w+\u2026|esc to interrupt/` — catches any spinner symbol followed by a single word and ellipsis character (✻ Cackling…)
2. **Custom verb fallback**: `loadAllSpinnerVerbs()` reads every Beast's `.claude/settings.local.json`, extracts `spinnerVerbs`, caches with 5-min TTL. Checks for `verb + "…"` or `verb + "..."` in the tmux pane content above the prompt line.

## Why Two Layers

- Generic regex handles standard Claude Code spinner verbs (Crafting, Brewing, etc.) and most custom single-word verbs
- Custom loader handles edge cases like multi-word verbs that `\w+` wouldn't catch
- Together they provide robust detection across all Beast configurations

## API

- `GET /api/pack/spinner-verbs` — returns all configured verbs per Beast and unique totals
