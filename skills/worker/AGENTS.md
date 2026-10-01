# Module: skills_worker (sub-module of skills)

## Purpose
The Worker class pack: the two skills every Worker agent carries, both locked and always-on.

## Owns
- `module-sop-worker/`: the standalone MODULE-standard skill (sub-module).
- `parrot-protocol-worker/`: the vendored Parrot Protocol skill (sub-module).

## Does Not Own
- Any other class's skill.
- The SOP source text (module `docs`).
- The gate (module `tools`).

## Public Interface
- Skills `module-sop-worker` and `parrot-protocol-worker`.

## Depends On
- skills (parent)

## Invariants
- Exactly two skills.
- `module-sop-worker` passes `tools/skill_lint.py` and names `parrot-protocol-worker` as its readback skill.
- `parrot-protocol-worker` matches its sha256 pin.

## Test Locations
- Contract: `tests/contract/test_skills_worker_contract.py` (plus the parent's `tests/contract/test_skills_contract.py`)

## Known Gotchas
- Install each skill's `SKILL.md` into a folder named after the skill (`module-sop-worker`, `parrot-protocol-worker`). Never install the cards.
