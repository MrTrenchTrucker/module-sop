# Module: tools

## Purpose
The deterministic gates: a class skill is standalone and faithful, and the repo's structure matches its registry.

## Owns
- `sections.py`: the one shared Markdown section extractor.
- `skill_lint.py`: the standalone-skill gate:
  - no pointers to other documents, and no private identifiers (your agents' names, hosts, internal systems,
    private addresses and paths — your own names go in `.sop/private_names.txt`);
  - verbatim Quick Reference + One-Paragraph Version;
  - frontmatter name;
  - pairing with `parrot-protocol-<class>`;
  - no `references/` folder.
- `sop_check.py`:
  - structure check (registry vs folders, sub-module nesting (a module inside another module's folder must name that direct parent in `depends_on`, at any depth), cards, line caps, word budget, imports);
  - generation of `MODULE_MAP.md` and `.sop/function_index.json`.

## Does Not Own
- SOP content (module `docs`).
- Skill content (module `skills`, authored under review).
- Packaging decisions (`decisions/`).
- Installing skills on agents (agent deployment ops, ADR-004).

## Public Interface
- `sections.section(text, heading, stop_heading=None) -> str`: raises `ValueError` if a heading is missing.
- `sections.sop_version(text) -> str`
- `skill_lint.lint(path, cls, root) -> list[str]`: violations (empty list = clean).
- `skill_lint.skill_path(root, cls) -> str`: where the class skill lives.
- `sop_check.check(root, write=False) -> (failures, warnings)`
- `sop_check.load_registry(root) -> dict`: the parsed `modules.toml`.
- `doc_check.card_findings(root, reg) -> list[str]`: every module has a card and a README, each card matches the registry and the code, and a parent README names its sub-modules.
- `doc_check.freshness_findings(root, reg, base) -> list[str]`: a module whose code changed since `base` changed its README too, or a work order carries a README waiver for it.
- `doc_check.resolve_base(root) -> str`: `$SOP_BASE`, else the merge-base of HEAD with main; raises if neither resolves.
- The CLI forms exit 1 on any failure.

## Depends On
- docs (reads the SOP files)

## Invariants
- Standard library only (Python 3.11+ for `tomllib`). No network.
- A missing heading or file raises; it is never silently skipped.
- Every lint rule has a red-arm test in `tests/unit/tools/test_skill_lint.py`.

## Test Locations
- Unit: `tests/unit/tools/`
- Contract: via the skills contract tests (they run the gate on the real skills)

## Known Gotchas
- `skill_lint.py` allows the project's own working files (`ARCHITECTURE.md`, `AGENTS.md`, `README.md`, `APPROVALS.md`, `SMOKE_TEST.md`, `MODULE_MAP.md`, `workorders/WO-NNN.md`, `decisions/ADR-NNN.md`). Any other `.md` name is flagged.
- `sop_check.py` without `--write` treats a stale `MODULE_MAP.md` or function index as a failure.
- `doc_check.py`'s docs-current check: The base is the commit the work order started from. The default (the merge-base with main) is right for a branch that carries one work order. On a branch carrying several slices, set `SOP_BASE` to the commit each slice started from; otherwise a later slice rides on an earlier slice's README edit and the check passes when it shouldn't.
- The fidelity gate checks only the Quick Reference and the One-Paragraph Version. The rest of each skill body consolidates the class SOP and the MODULE SOP, so drift there is caught by the reviewer passes, not by `skill_lint.py`.
