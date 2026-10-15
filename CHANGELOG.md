# Changelog

## [1.1.0] — 2026-10-15
- **New shared skill `subagent-plan-file`** in a new shared pack, `skills/shared/` (ADR-010), for any agent that hands
  work to sub-agents. Every sub-agent gets one plan file:
  - a read gate: each file and section, proven with an exact quote;
  - a reading certificate, signed by the sub-agent before its first change;
  - work steps ticked with their evidence;
  - a closing certificate that lists what was not done;
  - a Plan Changes section, the only part the agent that started the sub-agent writes in after it starts.
  - Only the sub-agent marks its own reading. A tick, quote or signature written by anyone else is void, and the work
    goes back for the missing reading.
  - Five lines for the sub-agent's instructions, the check before accepting the work, and a copyable template.
  - It names no model, harness or tool.
- **`tools/skill_lint.py` gates shared skills too** (`lint_shared`, `shared_skill_path`): the standalone rules without the
  SOP fidelity check; a shared skill must not name a class skill, a model, a model vendor or an agent harness. Every new
  rule has a red-arm test.
- The five SOP texts and the six class and Parrot skills are unchanged, so installed skills do not need updating.

## [1.0.2] — 2026-10-04
- Removed the project's own history from the public copy: the setup work
  order, private pull request and commit references, verbatim quotes and
  review rounds in the decision records, and the pre-release history below.
  The decision records state each ruling as a plain statement instead.
- The Parrot Protocol pin (`skills/PARROT_PIN.toml`) records the source
  version instead of a commit; each file's sha256 pin is unchanged.
- The five SOP texts and the six skills are unchanged byte for byte, so
  installed skills do not need updating.

## [1.0.1] — 2026-10-04
- Wording only. References to people are gender-neutral ("the Commander",
  "the IT manager") in the README, this changelog, the smoke test, the
  decision records, the `docs/` folder card and README, and the setup work
  order.
- ADR-004 describes the install boundary without naming any particular
  agent harness.
- The five SOP texts and the six skills are unchanged byte for byte, so
  installed skills do not need updating.

## [1.0.0] — 2026-10-01 (first public release)
- First release on GitHub. Public version numbers start here; this is the
  official version from now on.
- Contents: the five SOPs (MODULE SOP 1.8.1, PROJECT LEADER SOP 1.4.1,
  IT MANAGER SOP 1.3.1, WORKER SOP 1.3.1, COMMANDER SOP 1.3.0) and the six
  class skills: `module-sop-<class>` and the vendored `parrot-protocol-<class>`
  for the project leader, IT manager and worker.
- Prepared for publication: no private names, hosts or ids anywhere.
  `tools/skill_lint.py` no longer carries a built-in list of private names;
  each user lists their own, one per line, in `.sop/private_names.txt`
  (git-ignored).

## Before the public release
Versions before 1.0.0 were internal drafts. Everything they added is part of
1.0.0.
