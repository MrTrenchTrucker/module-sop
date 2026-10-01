# ADR-006: Which MODULE SOP section 9 checks this repo runs, and which it defers (and why)

**Status:** accepted
**Date:** 2026-09-24
**Approved by:** Commander (WO-001)

## Context
MODULE SOP section 9 lists the automated checks. This repo is small: four stdlib Python scripts, and no third-party packages by design. Not every named tool fits.

## Decision
| SOP check | Here |
|---|---|
| 9.1 structure | **Implemented**: `tools/sop_check.py` (registry, cards, line caps, word budget, generated files fresh) |
| 9.2 import contracts | **Implemented, hand-rolled**: `sop_check.py` derives the rule from `depends_on` and walks imports with `ast`. Import Linter is not used, to keep the repo stdlib-only. |
| 9.3 write-scope | **Deferred**: needs a work-order diff runner; so far the only WO is whole-repo scope. |
| 9.4 duplicate detection | **Deferred**: 4 small scripts. Reuse was handled manually (one shared `sections.py` for build + verify). |
| 9.5 test run | **Implemented**: `python3 -m unittest discover -s tests -t .` |
| 9.6 mutation | **Manual**: hand-made mutants recorded in the work order (WO-001: M1 and M2, each killed by its guard test). mutmut is not used (stdlib-only). |
| 9.7 test integrity | **Deferred**: needs a WO diff runner (same as 9.3). |
| CI (12.1) | **Deferred**: no CI runner configured on the git host for this repo; the checks run from the command line (allowed by 12.3). |

## Reasons
- The checks that matter most for this repo (fidelity to the Commander's text, structure) are implemented and each has a watched red arm.
- The deferred ones need a work-order runner that does not exist yet.

## Consequences
- Deferred items are known, not hidden.
- When a shared `.sop` toolkit exists, this repo adopts it and this ADR is superseded.
