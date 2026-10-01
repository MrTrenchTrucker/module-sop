# skills_project_leader: the Project Leader class pack

**What it does.** The two skills every Project Leader agent carries, both locked and always-on.

**How it works.**
- `skills_project_leader_module_sop` (`module-sop-project-leader/`): the Project Leader MODULE-standard skill. It stands alone: an agent that loads it
  knows the whole job without reading anything else.
- `skills_project_leader_parrot_protocol` (`parrot-protocol-project-leader/`): the Project Leader Parrot Protocol skill, the readback exchange the first
  skill relies on.
- To install, copy each folder's `SKILL.md` into the agent's skill folder and lock it.
