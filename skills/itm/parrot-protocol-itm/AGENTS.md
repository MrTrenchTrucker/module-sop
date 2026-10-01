# Module: skills_itm_parrot_protocol (sub-module of skills_itm)

## Purpose
The `parrot-protocol-itm` skill for the IT Manager class: one `SKILL.md`, installed on every IT Manager agent as a locked, always-on skill.

## Owns
- `SKILL.md`: vendored byte-for-byte from `parrot-protocol` at the commit in `skills/PARROT_PIN.toml`.

## Does Not Own
- Any edit (fixes go to the parrot repo), the module-standard rules (sibling skill).

## Public Interface
- Skill name `parrot-protocol-itm` (frontmatter `name`).

## Depends On
- skills_itm (the class pack)

## Invariants
- sha256 equals the pin in `skills/PARROT_PIN.toml`; never edited here.

## Test Locations
- Contract: `tests/contract/test_parrot_pin_contract.py`

## Known Gotchas
- Install only `SKILL.md`, into a folder named `parrot-protocol-itm`; never this card.
