# skills: the class packs

**What it does.** Holds the skills each agent class carries: one class pack per class, each with exactly two skills.

**How it works.**
- `skills_project_leader` (`project-leader/`), `skills_itm` (`itm/`) and `skills_worker` (`worker/`) are the class packs.
  Each holds that class's `module-sop-<class>` skill and its `parrot-protocol-<class>` skill.
- `module-sop-<class>` is written here from the class SOP in `docs`; it stands alone, pointing only at its Parrot skill.
- `parrot-protocol-<class>` is vendored byte for byte from `parrot-protocol`. `PARROT_PIN.toml` records the
  source commit and the sha256 of each copy, and a test fails if a copy drifts.
- Agents get only the `SKILL.md` files, installed read-only; this folder's cards and READMEs stay in the repo.
