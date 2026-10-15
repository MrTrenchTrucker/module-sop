# skills_shared: the shared pack

**What it does.** Holds skills any agent class may carry, on top of its class pack.

**How it works.**
- `skills_shared_subagent_plan_file` (`subagent-plan-file/`): the plan-file skill for any agent that hands work to
  sub-agents.
- A shared skill stands alone, like a class skill, but it is not written from a class SOP and it names no class skill.
- To install, copy the skill folder's `SKILL.md` into the agent's skill folder, in a folder named after the skill.
