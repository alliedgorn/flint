# SDD Decree — Specification-Driven Development

Source: Leonard, thread #225 (2026-03-25). Decree from Gorn.
Updated: Gorn, thread #256 (2026-03-26). Clarification on approval scope.

## Rule
Before implementing any feature, generate spec files first. Only "big" features need Gorn's approval. Smaller specs can be peer-reviewed and built.

## Flow
1. Describe — what is wanted in natural language
2. Spec — types/interfaces, schemas, test stubs, module README
3. Review — peer review for small features, Gorn approval for big ones
4. Implement — against approved/reviewed specs
5. Verify — tests pass

## What counts as "big" (needs Gorn approval)
- New projects or major features with multiple endpoints/data models
- Significant architectural decisions

## What does NOT need Gorn approval
- Smaller feature specs — peer review is sufficient
- Write the spec file in docs/specs/ but do NOT submit to /specs board
- The spec_required flag feature (T#317) was explicitly called out as not needing Gorn approval

## Applies to
- All new features
- Significant refactors
- New modules or components

## Does NOT apply to
- Bug fixes
- One-line changes
- Hotfixes
