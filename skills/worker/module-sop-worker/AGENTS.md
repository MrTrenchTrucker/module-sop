# Module: skills_worker_module_sop (sub-module of skills_worker)

## Purpose
The `module-sop-worker` skill for the Worker class: one `SKILL.md`, installed on every Worker agent as a locked, always-on skill.

## Owns
- `SKILL.md`: authored from `docs/`, standalone, gated by `tools/skill_lint.py` and two reviewer passes.

## Does Not Own
- The parrot protocol (sibling skill), the sop source text (docs).

## Public Interface
- Skill name `module-sop-worker` (frontmatter `name`).

## Depends On
- skills_worker (the class pack)

## Invariants
- `tools/skill_lint.py` passes; only outside reference is its sibling `parrot-protocol-worker`.

## Test Locations
- Contract: `tests/contract/test_skills_worker_contract.py`

## Known Gotchas
- Install only `SKILL.md`, into a folder named `module-sop-worker`; never this card.
