# Module: skills_project_leader_parrot_protocol (sub-module of skills_project_leader)

## Purpose
The `parrot-protocol-project-leader` skill for the Project Leader class: one `SKILL.md`, installed on every Project Leader agent as a locked, always-on skill.

## Owns
- `SKILL.md`: vendored byte-for-byte from `parrot-protocol` at the commit in `skills/PARROT_PIN.toml`.

## Does Not Own
- Any edit (fixes go to the parrot repo), the module-standard rules (sibling skill).

## Public Interface
- Skill name `parrot-protocol-project-leader` (frontmatter `name`).

## Depends On
- skills_project_leader (the class pack)

## Invariants
- sha256 equals the pin in `skills/PARROT_PIN.toml`; never edited here.

## Test Locations
- Contract: `tests/contract/test_parrot_pin_contract.py`

## Known Gotchas
- Install only `SKILL.md`, into a folder named `parrot-protocol-project-leader`; never this card.
