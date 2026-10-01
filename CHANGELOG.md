# Changelog

## [1.2.1] — 2026-09-24 (PR for the Commander's review — IT manager findings on 1.2.0)
- **SOP follow-up, lands only on the Commander's merge.** Versions: MODULE SOP 1.8.1, PROJECT LEADER 1.4.1, IT MANAGER 1.3.1, WORKER 1.3.1; COMMANDER unchanged. The IT manager's findings on 1.2.0:
  - a worker permitted to set up a sub-module has every file the setup writes in its write-scope: the contract test stub, the line in the parent's README that names it, the import contracts, `MODULE_MAP.md` and the function index, not only `modules.toml` and the folder;
  - a *package* folder is one that holds code, not a folder of only test fixtures or data, defined in MODULE SOP 5.2; the IT manager's gate calls a new one a sub-module;
  - carving a sub-module out of a parent moves part of the parent's Owns: stated as an explicit exception to the card rule, recorded on the parent's card and README in the same commit, covered by the project leader's ADR, with the part the checks do not catch checked by hand at the gate; the handoff form gets a "Parent Owns moved" line (the project leader's recommendation; the Commander keeps or strikes it on merge);
  - the docs-current check's base is the commit each work order started from.
- The three `module-sop-<class>` skills mirror it. WO-001 records project setup; the module-nesting-and-docs work (v1.2.0 below) landed with the Commander's merge of PR #1.

## [1.2.0] — 2026-09-24 (same PR, for the Commander's review — module nesting and per-module docs)
- **SOP amendment, lands only on the Commander's merge.** Versions: MODULE SOP 1.8.0, PROJECT LEADER 1.4.0, IT MANAGER 1.3.0, WORKER 1.3.0; COMMANDER unchanged. Implements his rulings:
  - modules nest to any depth on a folder tree;
  - IT managers create sub-modules at any depth, with notification, setup in the same commit;
  - workers create a sub-module inside an existing sub-module only with IT manager permission;
  - names say what a module does;
  - every module at every level has `AGENTS.md` + `README.md`, read before work and kept current;
  - a docs-current check fails loudly when a README falls behind its code;
  - a `docs_pending` grace mark keeps existing projects from a big-bang failure.
  - Four independent reviewer passes: v1 3/10, v2 3/10 and 5/10, v3 6/10. Every finding folded into v3.1.
- **Class skills** mirror the amendment; the Quick Reference and One-Paragraph Version stay verbatim.
- **New gate `tools/doc_check.py`** (ADR-009):
  - every module has a card and a README;
  - each card matches the registry and the code (`public` = the whole interface);
  - each parent README names its sub-modules;
  - the docs-current check runs in the test suite.
  - Evidence: 11/11 mutants killed, with control and inert arms.
- **Structure check:** a sub-module must name its direct parent in `depends_on`, at any depth.
- **This repo meets its own rules:** a README in all 12 module folders, registry `public` lists corrected, internal helpers made private.

## [1.1.0] — 2026-09-24 (PR for the Commander's review)
- **Standalone class skills** (ADR-007 supersedes ADR-001). Each `module-sop-<class>` skill is one self-contained `SKILL.md`:
  - it carries every rule and form its class needs, in the SOP's own words, with no pointers to other documents;
  - its only outside reference is its readback skill;
  - the Quick Reference and One-Paragraph Version stay verbatim.
- **Class packs:** `skills/<class>/` holds `module-sop-<class>` + `parrot-protocol-<class>` (vendored byte-for-byte from `parrot-protocol`, sha256-pinned; ADR-008).
- **New gate:** `tools/skill_lint.py` (every rule red-armed). Retired: `build_skills.py`, `verify_skills.py`.
- **Module system completed:**
  - skill folders registered as sub-sub-modules with cards;
  - ADR-005 (module boundaries), ADR-006 (section 9 checks implemented/deferred);
  - per-module contract tests;
  - WO-001 in the full work-order form.

## [1.0.0] — 2026-09-24
- Initial import of the Commander's SOP set:
  - MODULE SOP 1.7.0;
  - COMMANDER SOP 1.3.0;
  - PROJECT LEADER SOP 1.3.3;
  - IT MANAGER SOP 1.2.0;
  - WORKER SOP 1.2.0.
- Class skills `module-sop-project-leader`, `module-sop-itm`, `module-sop-worker` (verbatim Quick Reference + One-Paragraph Version; full SOPs as references).
- `tools/verify_skills.py` fidelity check.
- Built on the Commander's word: "launch a fresh repo on the git host for the SOP's I shared and turn them into skills there".
