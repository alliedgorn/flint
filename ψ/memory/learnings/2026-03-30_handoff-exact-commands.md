# Lesson: Include Exact API Commands in Handoffs

**Date**: 2026-03-30
**Source**: Session 40 — repeated scheduler endpoint friction
**Tags**: handoff, api, efficiency, rest-cycle

## Pattern

When writing handoff files, include the exact curl commands (with HTTP method, full URL, and query params) for any API calls the next session will need to make. Fresh context means the next session has zero memory of past API friction — it will re-discover endpoint quirks every time unless the handoff spells them out.

## Example

Instead of: "Mark schedule 368 as run"
Write: `curl -s -X PATCH 'http://localhost:47778/api/schedules/368/run?as=flint'`

## Why

Over 33+ sessions, the same small friction points recur: wrong HTTP method for scheduler, wrong endpoint path for forum mentions. Each costs a failed request and a retry. The handoff is the only bridge between sessions — make it load-bearing.
