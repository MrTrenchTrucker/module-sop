# ADR-001: Skills quote the SOPs verbatim; the full SOPs travel as references

**Status:** superseded by ADR-007
**Date:** 2026-09-24
**Approved by:** Commander (WO-001; the Commander's word; review ruling: "no changes")

## Context
The Commander wrote the SOPs with expert and cross-model review and ruled that they need no changes. An always-on skill loads on every task, so its body has to be small.

## Decision
`SKILL.md` = frontmatter + a short how-to + the class SOP's own **Quick Reference** and **One-Paragraph Version**, copied word for word. The full class SOP and `MODULE_SOP.md` ride in `references/`, byte-identical to `docs/`.

## Reasons
- No agent's rules can drift from the Commander's words: nothing is paraphrased.
- The Commander's own COMMANDER SOP says the checklist is the real SOP, so the checklist is what loads every time.
- The detail stays one read away, not in every context.

## Consequences
- Rules in: `tools/verify_skills.py` must pass; any wording change goes into `docs/` first.
- Rules out: summarising or "improving" an SOP inside a skill.
