# SDD Decree — Specification-Driven Development

Source: Leonard, thread #225 (2026-03-25). Decree from Gorn.

## Rule
Before implementing any feature, generate spec files first. Human reviews and approves specs. Then implement against specs.

## Flow
1. Describe — what is wanted in natural language
2. Spec — types/interfaces, schemas, test stubs, module README
3. Review — human approves before implementation
4. Implement — against approved specs
5. Verify — tests pass

## Applies to
- All new features
- Significant refactors
- New modules or components

## Does NOT apply to
- Bug fixes
- One-line changes
- Hotfixes
