# Module: skills

## Purpose
The packaged agent skills, one sub-module per agent class. Installed on agents as locked, always-on skills.

## Owns
- `project-leader/`, `itm/`, `worker/` (sub-modules): one class pack each, holding the class's two skills.
- `PARROT_PIN.toml`: the source commit and sha256 of every vendored Parrot skill (ADR-008).

## Does Not Own
- The rules' source text (module `docs`).
- The gates (module `tools`).
- The Parrot Protocol text itself (canonical in `parrot-protocol`; vendored here byte-for-byte).
- Hand edits: none are allowed.

## Public Interface
- Skills `module-sop-project-leader`, `parrot-protocol-project-leader`, `module-sop-itm`, `parrot-protocol-itm`, `module-sop-worker`, `parrot-protocol-worker` (frontmatter `name`).

## Depends On
- docs (the source the skills are authored from), tools (the gate)

## Invariants
- Each `module-sop-*` skill is standalone and faithful (`tools/skill_lint.py`); each `parrot-protocol-*` skill matches its pin.
- Every change gets two independent reviewer passes (fidelity, standalone usability) before commit.

## Test Locations
- Contract: `tests/contract/test_skills_contract.py`, `tests/contract/test_parrot_pin_contract.py`

## Known Gotchas
- **Install only `SKILL.md`**, never the folder's `AGENTS.md` card. The card is for agents working on this repo, not for the agent running the skill.
- The folder name (`itm`) differs from the skill name (`module-sop-itm`). Install into a folder named after the skill name.
