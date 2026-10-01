# Module: skills_worker_parrot_protocol (sub-module of skills_worker)

## Purpose
The `parrot-protocol-worker` skill for the Worker class: one `SKILL.md`, installed on every Worker agent as a locked, always-on skill.

## Owns
- `SKILL.md`: vendored byte-for-byte from `parrot-protocol` at the commit in `skills/PARROT_PIN.toml`.

## Does Not Own
- Any edit (fixes go to the parrot repo), the module-standard rules (sibling skill).

## Public Interface
- Skill name `parrot-protocol-worker` (frontmatter `name`).

## Depends On
- skills_worker (the class pack)

## Invariants
- sha256 equals the pin in `skills/PARROT_PIN.toml`; never edited here.

## Test Locations
- Contract: `tests/contract/test_parrot_pin_contract.py`

## Known Gotchas
- Install only `SKILL.md`, into a folder named `parrot-protocol-worker`; never this card.
