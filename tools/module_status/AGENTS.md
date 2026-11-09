# Module: tools_module_status

## Purpose
Shows, for every module and sub-module of a repo split into modules, whether it is built, partial or not started, and
whether its issue can be closed. The rules are fixed, so the same inputs always give the same report. It writes a
status workbook, a CSV table, a JSON file and a text report into the output folder its config names.

## Owns
- `module_status.py`: the status rules (built, partial, not started, expected sub-modules, issue matching, COMPLETE and
  ready-to-close checks), the report, the CSV table and the JSON file. One command-line argument: the config file.
- `module_status_xlsx.py`: the workbook builder (Summary, Modules and Items sheets, live COUNTIF formulas). Standard
  library only. The status script runs it as a command.
- The config format and the rules, in `README.md`, and the two examples: `example_config.toml`, `example_MODULE_PLAN.toml`.

## Does Not Own
- Checking the repo. The gates (`tools/sop_check.py`, `tools/doc_check.py`, `tools/skill_lint.py`) do that. This module
  only reads the registry and reports on it.
- Any file in the repo it reads. It writes only into its own output folder (ADR-011).
- GitHub issues: it reads them, and never creates, edits or closes one.
- The SOP text (`docs`) and the skills (`skills`).

## Public Interface
No Python function or class is public. The interface is the command line:
- `python3 module_status.py CONFIG.toml`: reads the config, writes into the config's `out_dir`, prints the report.
  Exit 0 normally (CAUTION and NOTE lines are not errors); exit 2 when the config is unreadable, has no `repo` key,
  or the registry lists no modules.
- `python3 module_status_xlsx.py OUT.xlsx STATUS.json [--title TEXT] [--asof TEXT] [--sha TEXT]`: builds the workbook
  from a status JSON file. Exit 0 on success.
- Config keys and their defaults: `README.md`, section "Config keys".

## Depends On
- `tools`: the parent module. The code uses only the Python standard library, including `urllib` for the optional
  read of GitHub issues when a config asks for it (ADR-011).

## Invariants
- Every output goes into the config's `out_dir`; it writes nowhere else. If `out_dir` is inside the repo it reads, the
  report says so in a CAUTION (ADR-011).
- Its only network use is reading GitHub issues, and only when the config names a GitHub repository. With
  `issues_json` or no issue source, a run is offline.
- The same inputs give the same output. No model, no randomness, no clock except the "as of" time in the report header.
- A problem with the inputs is a CAUTION line, not a failure. Exit 2 is the clean-run refusal (unreadable config, no `repo` key, or no modules at all).
- Every status in the report traces to a rule in `README.md`.
- Helpers are private (leading underscore), so the public list in the registry stays empty.

## Test Locations
- Unit and regression: `tests/unit/tools/module_status/test_module_status.py`, `test_edge_cases.py`,
  `test_module_status_xlsx.py`.
- Contract: `tests/contract/test_tools_module_status_contract.py`.
- Local GitHub stand-in: `tests/unit/tools/module_status/gh_server.py` (a tiny HTTP server the tests point `github_api` at).

## Known Gotchas
- `out_dir` and `xlsx_builder` are relative to the folder you run the script from. `plan_file` is relative to `repo`.
- `module_status.py` (about 365 lines) and `module_status_xlsx.py` (about 331 lines) are over the 300-line soft cap, so
  `tools/sop_check.py` warns about each. The warnings are acknowledged in the handoff (MODULE SOP 9.1). They are not
  split: the status script is one top-level flow, and a split would move its shared state across files.
- The example config names a `sample_repo/` folder and an `example_issues.json` that are not shipped (see `README.md`,
  "Example").
- In the workbook, module names are used as COUNTIF criteria, so `*` and `?` in a name give wrong counts.
