# Changelog

## Unreleased
- New `adapters/` module: harness adapter packs mapping the SOP chain onto
  concrete agent harnesses. First pack: `hermes-bot-mode.md` (Hermes Bot
  Mode: orchestrator, delegated task workers, reviewer role, kanban
  work-order form, lazy skill loading). Docs-only; no SOP or skill changes.

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
