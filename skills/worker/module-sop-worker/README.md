# skills_worker_module_sop: the Worker MODULE-standard skill

**What it does.** `SKILL.md` is the skill `module-sop-worker`: everything a Worker needs to work under the MODULE SOP, in one
file, so it can do the job without reading any other document.

**How it works.**
- It is written from `docs/WORKER_SOP.md` and the rules it inherits from `docs/MODULE_SOP.md`.
  Its Quick Reference and One-Paragraph Version are copied from the SOP word for word.
- The only outside skill it names is `parrot-protocol-worker`.
- `tools/skill_lint.py` gates it. Every change also gets two reviewer passes (fidelity, and reading it as the Worker who
  will use it) before it is committed.
- Only `SKILL.md` is installed on agents.
