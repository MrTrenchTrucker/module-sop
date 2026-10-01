# Module: skills_itm (sub-module of skills)

## Purpose
The IT Manager class pack: the two skills every IT Manager agent carries, both locked and always-on.

## Owns
- `module-sop-itm/`: the standalone MODULE-standard skill (sub-module).
- `parrot-protocol-itm/`: the vendored Parrot Protocol skill (sub-module).

## Does Not Own
- Any other class's skill.
- The SOP source text (module `docs`).
- The gate (module `tools`).

## Public Interface
- Skills `module-sop-itm` and `parrot-protocol-itm`.

## Depends On
- skills (parent)

## Invariants
- Exactly two skills.
- `module-sop-itm` passes `tools/skill_lint.py` and names `parrot-protocol-itm` as its readback skill.
- `parrot-protocol-itm` matches its sha256 pin.

## Test Locations
- Contract: `tests/contract/test_skills_itm_contract.py` (plus the parent's `tests/contract/test_skills_contract.py`)

## Known Gotchas
- Install each skill's `SKILL.md` into a folder named after the skill (`module-sop-itm`, `parrot-protocol-itm`). Never install the cards.
