# Module: skills_itm_module_sop (sub-module of skills_itm)

## Purpose
The `module-sop-itm` skill for the IT Manager class: one `SKILL.md`, installed on every IT Manager agent as a locked, always-on skill.

## Owns
- `SKILL.md`: authored from `docs/`, standalone, gated by `tools/skill_lint.py` and two reviewer passes.

## Does Not Own
- The parrot protocol (sibling skill), the sop source text (docs).

## Public Interface
- Skill name `module-sop-itm` (frontmatter `name`).

## Depends On
- skills_itm (the class pack)

## Invariants
- `tools/skill_lint.py` passes; only outside reference is its sibling `parrot-protocol-itm`.

## Test Locations
- Contract: `tests/contract/test_skills_itm_contract.py`

## Known Gotchas
- Install only `SKILL.md`, into a folder named `module-sop-itm`; never this card.
