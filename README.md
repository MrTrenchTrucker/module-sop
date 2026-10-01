# MODULE SOP: the Commander's coding-project standard, as agent skills

The MODULE SOP set (master + one SOP per class) and one **locked, always-on** skill per agent class.

| Class | Agents | Skill | Its SOP |
|---|---|---|---|
| Commander (human) | the Commander | none (read `docs/COMMANDER_SOP.md`) | `docs/COMMANDER_SOP.md` |
| Project Leader | the project leader | `skills/project-leader/` (`module-sop-project-leader`) | `docs/PROJECT_LEADER_SOP.md` |
| IT Manager | the IT manager (coding), a second IT manager (bug hunting) | `skills/itm/` (`module-sop-itm`) | `docs/IT_MANAGER_SOP.md` |
| Worker | one or more workers | `skills/worker/` (`module-sop-worker`) | `docs/WORKER_SOP.md` |

The master rules every class plays by are in `docs/MODULE_SOP.md`.

## How the skills are built
- **Each class skill is ONE standalone `SKILL.md`.** An agent loads it and knows what to do, without reading anything else.
- **Never points at another document.** Every place the class SOP says "see the MODULE SOP" carries the actual rule or form instead.
- **Only outside reference:** the class's readback skill `parrot-protocol-<class>`.
- **"Work order" stays generic.**
- **Faithful.** The SOP's own words; the **Quick Reference** and **One-Paragraph Version** are byte-for-byte verbatim.
- **Gated by `tools/skill_lint.py`** (every rule watched failing), plus two independent reviewer passes per change (fidelity, standalone usability).
- **`docs/` is the source of truth** and never ships to agents (ADR-007).

Each agent carries two class skills: this repo's `module-sop-<class>`, and `parrot-protocol-<class>` from `parrot-protocol` (v0.2.0).

## Repo structure (it follows the MODULE SOP itself)
- **Foundation:**
  - `ARCHITECTURE.md`: what this is, the modules, the rules.
  - `modules.toml`: the registry.
  - `AGENTS.md` card and `README.md` in every module folder, at every level.
  - `decisions/`: ADR-001 to ADR-009.
- **`docs/`** is the Commander's SOP set: the five `*_SOP.md` files, as he wrote or approved them. `docs/AGENTS.md` is that folder's module card, not an SOP, so a byte-for-byte check covers the five SOP files only.
- **Setup and records:**
  - `APPROVALS.md`, `SMOKE_TEST.md`.
  - `workorders/WO-001-project-setup.md`, plus later work orders (not shipped individually) that added module nesting support and per-module docs.
- **Generated, never hand-edited:** `MODULE_MAP.md`, `.sop/function_index.json`. The skills are authored under review (ADR-007).
- **Checks:**
  - `python3 tools/skill_lint.py`
  - `python3 tools/sop_check.py`
  - `python3 tools/doc_check.py` (module docs: present, matching the code, current against main)
  - `python3 -m unittest discover -s tests -t .`
  - All four must pass. Each test suite includes red arms, and tampering is caught.

## Rules
- **Only the Commander changes the SOPs**, and every change bumps the version.
- **To change a skill:**
  1. The Commander changes `docs/` (or approves a skill fix).
  2. Re-author the affected skill.
  3. Run `tools/skill_lint.py` + two reviewer passes + the tests.
  4. Commit on the Commander's word.
- Installed copies (`SKILL.md` only) are **read-only and pinned** in each agent's harness. Never edit an installed copy; change the source here.

This repository ships the SOP set and skills only; installing them onto your own agents' infrastructure (hosts, paths, per-agent names) is outside its scope.
