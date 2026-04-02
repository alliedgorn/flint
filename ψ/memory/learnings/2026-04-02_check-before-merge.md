# Check Before Creating a Merge PR

**Date**: 2026-04-02
**Source**: S99 — T#575 "please merge" from Gorn

## Pattern

When someone asks to "merge" a task, do not assume there is an open PR. Check:
1. Was the commit shipped directly to main?
2. Is there an actual open PR to merge?
3. If already on main, confirm it — no action needed.

## Context

Gorn asked to merge T#575. Karo had committed directly to main (8318644). Three Beasts independently confirmed no PR existed. The correct response was verification, not action.

## Tags

git, workflow, merge, verification
