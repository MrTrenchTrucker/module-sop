# skills_itm_module_sop: the IT Manager MODULE-standard skill

**What it does.** `SKILL.md` is the skill `module-sop-itm`: everything a IT Manager needs to work under the MODULE SOP, in one
file, so it can do the job without reading any other document.

**How it works.**
- It is written from `docs/IT_MANAGER_SOP.md` and the rules it inherits from `docs/MODULE_SOP.md`.
  Its Quick Reference and One-Paragraph Version are copied from the SOP word for word.
- The only outside skill it names is `parrot-protocol-itm`.
- `tools/skill_lint.py` gates it. Every change also gets two reviewer passes (fidelity, and reading it as the IT Manager who
  will use it) before it is committed.
- Only `SKILL.md` is installed on agents.
