# skills_worker: the Worker class pack

**What it does.** The two skills every Worker agent carries, both locked and always-on.

**How it works.**
- `skills_worker_module_sop` (`module-sop-worker/`): the Worker MODULE-standard skill. It stands alone: an agent that loads it
  knows the whole job without reading anything else.
- `skills_worker_parrot_protocol` (`parrot-protocol-worker/`): the Worker Parrot Protocol skill, the readback exchange the first
  skill relies on.
- To install, copy each folder's `SKILL.md` into the agent's skill folder and lock it.
