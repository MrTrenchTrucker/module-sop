# ADR-010: A shared skills pack, starting with the sub-agent plan-file skill

**Status:** accepted, amended 2026-10-15 (the plan file gains a reading certificate before the first change, and only the sub-agent marks its own reading)
**Date:** 2026-10-08
**Approved by:** Commander (2026-10-08)

## Context
- Some working practices apply to every class that hands work to sub-agents, not to one class.
- ADR-002 and ADR-007 give each class exactly two skills, both about that class. A practice every class shares does not
  belong inside one class's skill, and copying it into three skills would let the copies drift.
- The first such practice is the plan file. A side-by-side trial on one task compared sub-agents with and without a plan
  file. Both runs passed the same gate. The run with plan files found a defect in a shared file that the other run skimmed
  past, asked all its questions up front, and every quote it recorded was real. It also spent more tokens.
- The Commander made the plan file the standard and asked for it as a skill that works with any model.

## Decision
- A new sub-module of `skills`: `skills_shared` (`skills/shared/`), holding skills any class may carry next to its class pack.
  Each shared skill is its own sub-module.
- Its first skill is `subagent-plan-file`.
- A shared skill is one standalone `SKILL.md`. `tools/skill_lint.py` gates it with the class rules that apply: no pointers to
  other documents, no internal names, frontmatter name, no `references/` folder. It has no class SOP behind it, so there is
  no fidelity check, and it must not name a class skill.
- A shared skill names no model, model vendor or agent harness; `tools/skill_lint.py` checks a list of known names, and
  review catches the rest. It names no internal tool either.
- The class skills do not change. Whether they point at a shared skill is a later decision.

## Reasons
- One copy of a shared practice cannot drift.
- Keeping class skills unchanged keeps their installed copies and pins valid.

## Consequences
- An agent that hands work to sub-agents carries its two class skills plus the shared skills it uses.
- Rule 7 of `ARCHITECTURE.md` now covers shared skills.
- A shared skill's accuracy rests on its reviewer passes, since no script compares it with a source text.
- Installing a shared skill on agents belongs to each deployment's own operations (ADR-004).
