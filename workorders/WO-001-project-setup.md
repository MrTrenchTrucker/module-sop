# WO-001: Project setup: import the SOP set, build the class skills, apply the module system

**Status:** signed_off
**Issued by:** the project leader (no IT manager on this repo)
**Assigned to:** the project leader
**Authorized by:**
- Commander, chat (2026-09-24 18:53Z): "launch a fresh repo on the git host for the SOP's I shared and turn them into skills there".
- Commander, the work-order record (2026-09-24 ~19:0xZ): "Needs to follow the module system in the SOP's for good practice".
- Commander, chat (2026-09-24 ~19:2xZ): "every agent needs a clean stand allone skill that does not reference anything else except the other skills that are needed".

**Project plan reference:** this work order (single-order project)
**Check-in interval:** n/a (single sitting)
**Reply path:** chat (Commander)

## Intent (Commander, verbatim)

*[Square brackets] mark words replaced for this public copy.*

> "ok so basically, we replace the old parrot protocol skill with the new one on [the git host] as it was all verified. You get the Project Leader skills should be 2 skills total. [Both IT managers] get the ITM skills 2 skills total. all workers get worker skills 2 skills total. ALL skills for the SOp into skills we were working on get locked always on. Also, might as well launch a fresh repo on [the git host] for the SOP's I shared and turn them into skills there."
>
> "ok so basically, when we roll this out, every agent needs a clean stand allone skill that does not reference anything else except the other skills that are needed such as [a work-order workflow skill] or Parrot Protocol is what it calls for in particular since I specifically left out [that work-order workflow] and the original SOP's just say "Work Order" which is fine."
>
> "Load clean release skill with that in mind so workers, IT Managers, and Project Leaders like you can just load a skill, they know what to do without reading anything else."

## Task
Create `module-sop` with:
- the SOP set, verbatim, as the source (`docs/`);
- one standalone skill per agent class;
- the MODULE SOP foundation: registry, cards, ARCHITECTURE, ADRs, approvals, smoke test, generated map and index, structure checks and tests.

## Module
docs, tools, skills (+ sub-modules skills_project_leader, skills_itm, skills_worker). New project: all created here.

## Write-Scope
- Whole repo (new project).

## Acceptance Criteria
- [ ] `docs/` byte-identical to the Commander's zip (md5 2abede1b)
- [ ] Each class skill is ONE standalone `SKILL.md`:
  - no pointer to another document;
  - only outside reference is `parrot-protocol-<class>`;
  - no internal team names;
  - "work order" generic;
  - Quick Reference + One-Paragraph Version verbatim.
- [ ] `tools/skill_lint.py`, `tools/sop_check.py` and the unittest suite all pass, and every lint rule has a watched red arm
- [ ] Two independent reviewer passes per skill (fidelity, standalone usability), findings applied or rejected with reasons
- [ ] Every folder registered, every card complete, ARCHITECTURE ≤ 1500 words
- [ ] Non-author confirmation by the IT manager (Commander: "NOT [the second IT manager]") before the skills are installed on agents

## Constraints
- Only the Commander changes `docs/`.
- This repo produces and verifies the skills; it is not the install or distribution path (ADR-004).
- No token stored in the repo config.

## Conversion Step (existing projects only)
n/a (new project)

---
## Readback Rounds
**None before the first build. That is a process gap, recorded here, not hidden.** The project leader built directly from the Commander's intent instead of parroting a plan back first. The Commander's review (Bounce-Backs below) caught what a readback would have: the skills pointed at other documents. The rework was read back to the Commander by voice before building (2026-09-24 ~19:2xZ): "every class skill will stand on its own ... work order stays work order ... your checklist and your one paragraph version stay word for word". He confirmed with the clean-release instruction.

## Advisor Consults
| # | Asked by | Question | Advisor answer | Action taken |
|---|---|---|---|---|
| (none) | | | | |

## Approvals
- 2026-09-24 18:53Z: Commander: create the repo, turn the SOPs into skills.
- 2026-09-24 ~19:0xZ: Commander, the work-order record: follow the module system.
- 2026-09-24 ~19:2xZ: Commander, chat: standalone class skills; load clean-release.
- 2026-09-24 ~19:1xZ: Commander, chat: "NOT [the second IT manager]" (the non-author confirmation goes to the IT manager).

## Handoff Report
**Worker:** the project leader  **WO:** WO-001  **Against readback round:** the voiced rework readback (see above)
- **Files touched:** the whole repo (new).
  - Round 1: the initial draft (superseded; see Bounce-Backs).
  - Round 2 (this PR):
    - the standalone class skills;
    - class packs with the vendored Parrot skills (ADR-008, sha256-pinned to `parrot-protocol`);
    - ADR-005..008;
    - the `skill_lint` gate;
    - per-module contract tests.
  - Skill sizes: worker 32 KB, IT manager 49 KB, project leader 48 KB.
- **Reviewer passes:** two per class (fidelity + standalone usability), then a fixer per class:
  - worker: 8 applied, 8 rejected;
  - IT manager: 6 applied, 2 rejected;
  - project leader: see the workflow log.

  Rejected findings asked for detail the SOPs never specify (thresholds, timeouts, tool names) or for pointers back to the SOPs; adding either would invent rules or break standalone.
- **Interface changes:** skills went from `SKILL.md` + `references/` to one standalone `SKILL.md` (ADR-007 supersedes ADR-001).
- **Function index search:** one shared `tools/sections.py`, reused by the lint gate and the tests. No duplicate helpers.
- **Tests added (38 in total, all passing):**
  - `tests/unit/tools/test_skill_lint.py`: a clean skill passes; every rule has a red arm.
  - `test_sop_check.py`: every structure rule red-armed.
  - Per-module contract tests.
  - `test_parrot_pin_contract.py`: vendored Parrot skills match their sha256 pin; a local edit is caught.
- **Proof of loud failure:** every lint and structure rule has a planted-fault test. Tool mutants: see Mutation Results.
- **Mutation results:** manual (ADR-006):
  - `skill_lint.py` with the fidelity check disabled → `test_edited_checklist_breaks_fidelity` FAILS;
  - with the pairing check disabled → `test_missing_pairing` FAILS;
  - earlier `sop_check.py` card-section mutant → `test_card_missing_section_fails` FAILS.

  Each mutant is caught by exactly its guard test.
- **Collateral breaks:** none (new project).
- **Line cap warnings:** none; all code is under the 300-line soft cap.
- **Memory log entry:** written (the project leader's memory).

## Bounce-Backs
- **2026-09-24, Commander (live review):** "I allready spotted some things wrong in the skills... It references other documents workers in particular do not need to be aware of." → Required action: standalone skills (ADR-007).
- **2026-09-24, adversarial conformance review (review #13):**
  - MUST: this work order lacked the full form, readback rounds and strike log.
  - SHOULD:
    - the section 9 deviations were undeclared;
    - the sub-module contract tests had no per-module files;
    - there was no ADR for the top-level split.
  - Required action: this rewritten WO, ADR-005, ADR-006, per-class contract tests.

## Strike Log
| # | Class (minor/major) | Response (reprompt/compaction) | Reason | Outcome |
|---|---|---|---|---|
| 1 | minor | reprompt | Skills pointed at documents the class does not need (one contained issue class); no readback before the first build | Reworked to standalone skills under two reviewer passes + a lint gate |

## Sign-Off
- **The IT manager, non-author, 2026-09-24 ~20:17Z: CONFIRMED 5/5 at the pre-merge revision.**
  - Legs: docs byte-identical to her own SOP copy; the ITM skill standalone when read as the consumer; the fidelity gate watched failing twice; the vendored Parrot skills against her own clone at the pinned revision; 38 tests.
  - Observations:
    - O1: the `docs/AGENTS.md` note is added to the README.
    - O3: the fidelity gate's scope is noted in `tools/AGENTS.md`.
    - O2: the ITM clock overlap goes to the Commander as a rollout decision.
- **Commander merged PR #1 to main**: "Looks good. I merged to main." The IT manager re-checked the later nesting-and-module-docs delta in a follow-up work order.
