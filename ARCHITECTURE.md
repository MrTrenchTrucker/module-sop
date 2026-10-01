# ARCHITECTURE: module-sop

## What this is
The Commander's MODULE SOP set, and one agent skill per agent class built from it. The skills are
installed on every agent as **locked, always-on** skills, next to the matching
`parrot-protocol-<class>` skill from `parrot-protocol`. That makes two class skills per agent.

## Modules
| Module | Path | Role |
|---|---|---|
| docs | `docs/` | The source of truth: the five SOPs, verbatim. |
| tools | `tools/` | Gates the skills (standalone + faithful), checks structure and module docs, generates the map and index. |
| skills | `skills/` | The class packs. One sub-module per class (`project-leader`, `itm`, `worker`), each with one sub-module per skill. |

## Data flow
```
docs/  --(authored under two reviewer passes)-->  skills/<class>/SKILL.md   (one standalone file per class)
docs/ + skills/  --(tools/skill_lint.py)-->  PASS / FAIL
whole repo  --(tools/sop_check.py)-->  PASS / FAIL, MODULE_MAP.md, .sop/function_index.json
changes since the base  --(tools/doc_check.py, in the test suite)-->  PASS / FAIL per module README
```

## Rules that must hold (each is enforced by a script)
1. **Standalone.** A class skill is one `SKILL.md` that needs nothing else. It never points at another
   document (SOP names, sections, appendices, paths, the repo). Its only outside reference is its readback
   skill `parrot-protocol-<class>`. No agent names. "Work order" stays generic. (`skill_lint.py`, ADR-007)
2. **Faithful.** It carries the class SOP's rules in the SOP's own words, with the *Quick Reference* and
   *One-Paragraph Version* byte-for-byte verbatim. Every change to a skill or to `docs/` gets two independent
   reviewer passes (fidelity, standalone usability). `MODULE_MAP.md` and `.sop/function_index.json` are
   generated. (`sop_check.py` freshness)
3. **Registered structure, as a folder tree.** Every folder is in `modules.toml`. A sub-module sits inside its
   parent's folder and names that direct parent in `depends_on`, at any depth. Every module has a full card and a
   README, and a parent's README names its sub-modules. (`sop_check.py`, `doc_check.py`)
4. **Line caps** on code: soft 300, hard 500. `docs/` is exempt. (ADR-003)
5. **Imports** follow `depends_on`: only `tools/` has code, and it imports only its own files and the
   standard library. (`sop_check.py`)
6. **Docs current.** Each card matches the registry and the code (`public` is the whole interface), and a module
   whose code changed has changed its README too, or a work order carries a README waiver. (`doc_check.py`, ADR-009)
7. **One skill per class**, self-contained. `docs/` is the source and never ships to agents. (ADR-002, ADR-007)

## Who changes what
- **SOP text:** the Commander only, with a version bump.
- **Everything else:** per `APPROVALS.md`.

Installing skills on agents is outside this repo's scope (ADR-004).

## Out of scope
- The Parrot Protocol (its own repo).
- Per-agent install scripts (your own deployment tooling).
- Release and distribution logistics (outside this repo).
