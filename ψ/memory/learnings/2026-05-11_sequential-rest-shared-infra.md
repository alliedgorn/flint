# Lesson: Sequential Rest on Shared Infrastructure

**Date**: 2026-05-11
**Source**: Pack-wide rest cycle for kernel reboot (CVE-2026-31431)
**Context**: 13 Beasts running pre-rest ceremony simultaneously crashed the server

## Pattern

When multiple Beasts share a machine and all run heavy I/O operations simultaneously (gzip session archives + RAG embedding reindex + git operations), the combined load overwhelms RAM and CPU. Most processes die mid-execution.

## Solution

Pack-wide ceremonies must be sequential — one Beast at a time, each confirming completion before the next starts. Leonard's sequence order worked clean once established. Cost ~30 minutes of coordination but zero failures.

## Generalization

Any pack-wide operation that involves per-Beast heavy I/O should default to sequential execution, not simultaneous. The coordination overhead is cheaper than the crash recovery.
