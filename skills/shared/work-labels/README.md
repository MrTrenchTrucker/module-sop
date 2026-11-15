# skills_shared_work_labels: the work-labels skill

**What it does.** `SKILL.md` is the skill `work-labels`. It mirrors a work order on the forge as labels: one `status/*` label
(the twelve work-order status values), a `lane/A|B|C` label for how the delivery is tested, one `module/<name>` label per
registered module touched, and optionally `from/<who>` on a private repository. The label changes in the same step as the
work order, and a label is never an approval. The worker proposes the lane and the manager confirms it.

**How it works.**
- A status label per work order makes "what is waiting for review" one filter instead of a search through files.
- It names no model, harness, tool or forge product, so any agent on any forge can carry it.
- `tools/skill_lint.py` gates it as a shared skill, and a contract test checks that its status words equal the SOP's.
- Only `SKILL.md` is installed on agents.
