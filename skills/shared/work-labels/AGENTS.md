# Module: skills_shared_work_labels (sub-module of skills_shared)

## Purpose
The `work-labels` skill: one `SKILL.md` that any agent moving work orders or opening issues and pull requests can carry.

## Owns
- `SKILL.md`: the four label families (`status/*`, `lane/*`, `module/<name>`, `from/<who>`), the rule that the label moves with the work order in the same step, the rule that a label is never an approval, the set-up list for a new repository and the check before handing up.

## Does Not Own
- The work order status values (module `docs`; this skill repeats the twelve words and a contract test compares them).
- How a class gates its own work (the class skills).
- Creating the labels on a given forge or installing the skill on agents (project operations, ADR-004).

## Public Interface
- Skill name `work-labels` (frontmatter `name`).

## Depends On
- skills_shared (the shared pack)

## Invariants
- `tools/skill_lint.py` passes it as a shared skill.
- No named model, agent harness, tool or forge product.
- The twelve `status/*` words equal the status values in `docs/MODULE_SOP.md`, in the same order.
- A label is never an approval, and nothing is started, merged, closed or deployed because of one; approval is what the level above wrote into the work order.
- Exactly one `status/*` and exactly one `lane/*`; the lane is proposed by the worker and confirmed by the manager, by a decision order whose first step is "in doubt, A".
- `from/*` only on a private repository.

## Test Locations
- Contract: `tests/contract/test_skills_shared_contract.py`

## Known Gotchas
- If the status values in `docs/MODULE_SOP.md` change, this skill changes in the same commit; the contract test fails until it does.
- Install only `SKILL.md`, into a folder named `work-labels`; never this card.
