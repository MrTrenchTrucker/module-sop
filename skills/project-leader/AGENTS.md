# Module: skills_project_leader (sub-module of skills)

## Purpose
The Project Leader class pack: the two skills every Project Leader agent carries, both locked and always-on.

## Owns
- `module-sop-project-leader/`: the standalone MODULE-standard skill (sub-module).
- `parrot-protocol-project-leader/`: the vendored Parrot Protocol skill (sub-module).

## Does Not Own
- Any other class's skill.
- The SOP source text (module `docs`).
- The gate (module `tools`).

## Public Interface
- Skills `module-sop-project-leader` and `parrot-protocol-project-leader`.

## Depends On
- skills (parent)

## Invariants
- Exactly two skills.
- `module-sop-project-leader` passes `tools/skill_lint.py` and names `parrot-protocol-project-leader` as its readback skill.
- `parrot-protocol-project-leader` matches its sha256 pin.

## Test Locations
- Contract: `tests/contract/test_skills_project_leader_contract.py` (plus the parent's `tests/contract/test_skills_contract.py`)

## Known Gotchas
- Install each skill's `SKILL.md` into a folder named after the skill (`module-sop-project-leader`, `parrot-protocol-project-leader`). Never install the cards.
