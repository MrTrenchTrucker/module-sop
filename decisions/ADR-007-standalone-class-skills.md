# ADR-007: Standalone class skills (supersedes ADR-001)

**Status:** accepted
**Date:** 2026-09-24
**Approved by:** Commander (2026-09-24 ~19:2xZ): "every agent needs a clean stand allone skill that does not reference anything else except the other skills that are needed ... the original SOP's just say 'Work Order' which is fine" and "so workers, IT Managers, and Project Leaders ... can just load a skill, they know what to do without reading anything else."

## Context
ADR-001 shipped each skill as the SOP's checklist plus the full SOPs as reference files. The Commander found that this points agents at documents they do not need, workers in particular.

## Decision
- Each class skill is one self-contained `SKILL.md`, and no `references/` folder ships.
- It carries the class SOP's rules in the SOP's own words. Every pointer to another document is replaced by the rule or form it pointed at.
- The class SOP's Quick Reference and One-Paragraph Version stay byte-for-byte verbatim (the fidelity anchor).
- The only outside reference is the class's readback skill `parrot-protocol-<class>`.
- "Work order" stays generic.
- `docs/` stays verbatim as the source of truth and never ships to agents.

## Reasons
An agent loads one skill and knows what to do, and the Commander's modularisation goal (fewer tokens, less to read) applies to the skills themselves.

## Consequences
- The skills are authored, not generated.
- Fidelity is guarded by `tools/skill_lint.py`, with each rule watched failing:
  - verbatim anchors;
  - no document pointers;
  - no private identifiers (each user lists their own in `.sop/private_names.txt`);
  - pairing with the Parrot skill.
- Also by two independent reviewer passes per change (fidelity and standalone usability).
- Any `docs/` change requires re-authoring the affected skill and re-running both.
