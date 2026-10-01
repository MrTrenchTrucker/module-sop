# skills_itm: the IT Manager class pack

**What it does.** The two skills every IT Manager agent carries, both locked and always-on.

**How it works.**
- `skills_itm_module_sop` (`module-sop-itm/`): the IT Manager MODULE-standard skill. It stands alone: an agent that loads it
  knows the whole job without reading anything else.
- `skills_itm_parrot_protocol` (`parrot-protocol-itm/`): the IT Manager Parrot Protocol skill, the readback exchange the first
  skill relies on.
- To install, copy each folder's `SKILL.md` into the agent's skill folder and lock it.
