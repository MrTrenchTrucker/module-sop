# ADR-003: docs/ is exempt from the line caps

**Status:** accepted
**Date:** 2026-09-24
**Approved by:** Commander (WO-001)

## Context
MODULE SOP 9.1 caps files at 500 lines. `docs/MODULE_SOP.md` is 775 lines.

## Decision
`docs` is registered with `line_cap_exempt = true`. The caps apply to code (`.py`, `.sh`) in every other module.

## Reasons
- The SOPs are the Commander's verbatim text. Splitting one changes it, and only he changes it.
- The caps exist to keep code slices small for agents, not to reshape human-authored standards.

## Consequences
The exemption is visible in the registry and checked by `sop_check.py`. No other module may use it without its own ADR.
