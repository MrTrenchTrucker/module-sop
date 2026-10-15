# Module: skills_shared_subagent_plan_file (sub-module of skills_shared)

## Purpose
The `subagent-plan-file` skill: one `SKILL.md` that any agent handing work to sub-agents can carry.

## Owns
- `SKILL.md`: one plan file per sub-agent (read gate with exact quotes, reading certificate before any change, ticked work steps, closing certificate, plan changes), the rule that only the sub-agent marks its own reading, the five instruction lines, the check before accepting the work, and a template.

## Does Not Own
- How a class gates its own work (the class skills).
- The SOP source text (module `docs`).

## Public Interface
- Skill name `subagent-plan-file` (frontmatter `name`).

## Depends On
- skills_shared (the shared pack)

## Invariants
- `tools/skill_lint.py` passes it as a shared skill.
- No named model, agent harness or tool: the quote check is "an exact text search".
- The five instruction lines and the two certificate sentences stay word for word; agents copy them.
- Only the sub-agent ticks its read gate, writes its quotes and signs its certificates; a mark by the agent that started it is void.

## Test Locations
- Contract: `tests/contract/test_skills_shared_contract.py`

## Known Gotchas
- Install only `SKILL.md`, into a folder named `subagent-plan-file`; never this card.
