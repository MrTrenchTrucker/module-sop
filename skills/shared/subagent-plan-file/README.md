# skills_shared_subagent_plan_file: the sub-agent plan-file skill

**What it does.** `SKILL.md` is the skill `subagent-plan-file`. Every sub-agent gets one plan file with four parts: a read
gate (each file and section proven with an exact quote), a reading certificate signed before any change, work steps ticked
with their evidence, and a closing certificate that lists what was not done. Only the sub-agent marks them; the agent that
started it writes only under Plan Changes, and checks the plan file before it accepts the work.

**How it works.**
- It is written from a side-by-side trial on one task: with plan files, the sub-agents read better and found a defect the
  other run missed, at a higher token cost.
- It names no model, harness or tool, so any agent can carry it.
- `tools/skill_lint.py` gates it as a shared skill. Every change also gets two reviewer passes before it is committed.
- Only `SKILL.md` is installed on agents.
