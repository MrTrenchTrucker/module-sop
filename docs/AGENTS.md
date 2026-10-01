# Module: docs

## Purpose
Holds the Commander's SOP set exactly as he wrote it. Everything else in this repo is derived from these files.

## Owns
- `MODULE_SOP.md` (master), `COMMANDER_SOP.md`, `PROJECT_LEADER_SOP.md`, `IT_MANAGER_SOP.md`, `WORKER_SOP.md`

## Does Not Own
- Skills (module `skills`), tooling (module `tools`), and any summary, paraphrase or "improvement" of an SOP. There is no such thing here.

## Public Interface
- `MODULE_SOP.md`, `COMMANDER_SOP.md`, `PROJECT_LEADER_SOP.md`, `IT_MANAGER_SOP.md`, `WORKER_SOP.md`: the source the skills are authored from, and what `tools/skill_lint.py` checks the verbatim anchors against.
- Each carries a `**Version:** x.y.z` line and, for the class SOPs, `## Quick Reference` and `## One-Paragraph Version` sections.

## Depends On
- nothing

## Invariants
- The text is the Commander's, byte for byte. Only he changes it, and every change bumps its version.
- The class SOPs keep the `## Quick Reference` and `## One-Paragraph Version` headings. The skills quote them verbatim; renaming one fails the gate loudly.

## Test Locations
- Contract: `tests/contract/test_docs_contract.py`

## Known Gotchas
- Line caps do not apply here (ADR-003): splitting an SOP would change it.
- After any change: re-author the affected skill, then `tools/skill_lint.py`, `tools/sop_check.py --write`, two reviewer passes, and the tests.
