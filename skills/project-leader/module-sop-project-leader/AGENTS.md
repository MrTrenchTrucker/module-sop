# Module: skills_project_leader_module_sop (sub-module of skills_project_leader)

## Purpose
The `module-sop-project-leader` skill for the Project Leader class: one `SKILL.md`, installed on every Project Leader agent as a locked, always-on skill.

## Owns
- `SKILL.md`: authored from `docs/`, standalone, gated by `tools/skill_lint.py` and two reviewer passes.

## Does Not Own
- The parrot protocol (sibling skill), the sop source text (docs).

## Public Interface
- Skill name `module-sop-project-leader` (frontmatter `name`).

## Depends On
- skills_project_leader (the class pack)

## Invariants
- `tools/skill_lint.py` passes; only outside reference is its sibling `parrot-protocol-project-leader`.

## Test Locations
- Contract: `tests/contract/test_skills_project_leader_contract.py`

## Known Gotchas
- Install only `SKILL.md`, into a folder named `module-sop-project-leader`; never this card.
