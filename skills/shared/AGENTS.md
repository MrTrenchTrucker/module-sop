# Module: skills_shared (sub-module of skills)

## Purpose
The shared pack: skills any agent class may carry, next to its class pack (ADR-010).

## Owns
- `subagent-plan-file/`: the shared sub-agent plan-file skill (sub-module).

## Does Not Own
- Any class's own rules (the class packs).
- The SOP source text (module `docs`).
- The gate (module `tools`).

## Public Interface
- Skill `subagent-plan-file` (frontmatter `name`).

## Depends On
- skills (parent)

## Invariants
- Every shared skill passes `tools/skill_lint.py` as a shared skill: standalone, no internal names, and it names no class skill.
- A shared skill depends on no model and no agent harness.

## Test Locations
- Contract: `tests/contract/test_skills_shared_contract.py` (plus the parent's `tests/contract/test_skills_contract.py`)

## Known Gotchas
- A shared skill has no class SOP behind it, so `tools/skill_lint.py` runs no fidelity check on it. Its accuracy rests on the reviewer passes.
