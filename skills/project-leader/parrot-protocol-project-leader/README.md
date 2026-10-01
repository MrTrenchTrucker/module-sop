# skills_project_leader_parrot_protocol: the Project Leader Parrot Protocol skill

**What it does.** `SKILL.md` is the skill `parrot-protocol-project-leader`: how a Project Leader reads orders back and confirms readbacks before
any work starts.

**How it works.**
- It is vendored byte for byte from `parrot-protocol` (ADR-008), never edited here. A fix goes to that repo,
  and the new copy is vendored with its pin updated.
- `skills/PARROT_PIN.toml` records the source commit and this file's sha256; `tests/contract/test_parrot_pin_contract.py`
  fails if the copy drifts.
- Only `SKILL.md` is installed on agents.
