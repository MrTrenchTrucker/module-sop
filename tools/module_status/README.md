# Module status tracker (`module_status.py`)

A deterministic status sheet for a repository that is split into modules and sub-modules.

## The problem it solves

A repository organised as modules (each with its own folder, code, tests and a tracking issue) soon
reaches a point where nobody can answer simple questions at a glance: which modules are built, which
are only half done, which planned sub-modules were never created, and whether a module's issue can be
closed.

`module_status.py` answers those questions with fixed rules. It reads the repository's module registry
(`modules.toml`), looks at the folders and files on disk, optionally reads the repository's GitHub issues
(or an offline list of them), and writes a report, a CSV table, a JSON file and a workbook. It uses no AI
and no model: the same inputs always give the same output, and every status can be traced to a rule below.

The script is repository agnostic. Only its config file names a repository.

## Requirements

- Python 3.11 or newer (it uses the standard `tomllib` module).
- `git` and the `date` command on the PATH. The report header uses `git rev-parse` for the commit id and
  `date` for the UTC time. Tested on Linux only.
- Nothing else to install: the optional GitHub read uses the standard library (`urllib`).
- `module_status_xlsx.py`, next to `module_status.py`. It uses only the standard library. It is the
  default workbook builder (see `xlsx_builder`).

## Running it

```
python3 module_status.py my_config.toml
```

The report is printed to standard output and the files are written into `out_dir`.

Exit codes:

- `0`: the run finished. This is also the case when the report has CAUTION or NOTE lines. They are for a
  person to read, not errors.
- `2`: the registry has no modules at all. The script prints one line (see the CAUTION table) and writes
  no report. The output folder is still created.
- `1` (a Python traceback): the config file or the registry file is missing or is not valid TOML, a
  module has no `path`, or the `plan_file` or `issues_json` file is missing or is not valid. A reply
  from GitHub that is not JSON is not caught either.

## Config keys

The config is a TOML file. These are the 19 keys the script reads. Any other key is ignored. Relative
paths are relative to the folder you run the script from, except `plan_file`, which is relative to `repo`.

| key | default | meaning |
|---|---|---|
| `repo` | (required) | Path to the repository root. A leading `~` is expanded. |
| `name` | folder name of `repo` | Title of the report and of the workbook. |
| `registry` | `modules.toml` | Registry file, relative to `repo`. |
| `registry_key` | `module` | Table in the registry that holds the modules. If that table is missing or empty, the table `modules` is read. |
| `code_ext` | `[".kt", ".java", ".py", ".js", ".ts"]` | File extensions that count as code. Markdown does not count unless you add it. |
| `skip_dirs` | `["build", "node_modules", ".gradle", "__pycache__", ".git"]` | Folder names that are never walked. `build` is skipped only at the module's root folder. |
| `test_dirs` | `["test", "tests", "androidTest", "testFixtures", "__tests__"]` | A code file below the module's root, inside a folder with one of these names, counts as a test. |
| `test_suffixes` | `["Test.kt", "Tests.kt", "Test.java", "Tests.java", "_test.py", ".test.js", ".test.ts", ".spec.js", ".spec.ts"]` | A code file whose name ends with one of these counts as a test. A file whose name starts with `test_` always counts as a test; that is not configurable. |
| `container_depth` | `0` | A registered module whose path has this many parts or fewer is an area folder (for example `apps` when the depth is 1). See "Edge cases". `0` means no area folders. |
| `expected` | (empty table) | Table of `registry key = ["name", ...]`. Used when neither the plan file nor the registry entry gives an `expected_subs` list for that top-level module. |
| `plan_file` | none | Master plan file, relative to `repo`. |
| `github` | none | `owner/repo`. The script reads that repository's issues through the GitHub API. |
| `github_api` | `https://api.github.com` | Base address of the GitHub API (for GitHub Enterprise, or a local stand-in in tests). |
| `token_var` | `GITHUB_TOKEN` | Name of the environment variable that holds the GitHub token. |
| `token_env_file` | none | File with lines `VAR=value` (a leading `export ` is allowed). It is read only when the environment variable is empty. |
| `issues_json` | none | Offline issue list, a JSON object `{"title": [number, "open" or "closed"]}`. When set, `github` is not used. |
| `issue_title` | `module: {name}` | Title pattern for a top-level module's issue. `{name}` is the last folder name of the module's path; `{key}` is its registry key. |
| `out_dir` | `out` | Folder for all output files. Created if missing. |
| `xlsx_name` | `Module_Status.xlsx` | Workbook file name inside `out_dir`. |
| `xlsx_builder` | `module_status_xlsx.py` next to the script | Script that builds the workbook. It is run as `builder OUT.xlsx STATUS.json --title NAME --asof TIME --sha COMMIT`. |

## Registry (modules.toml)

Each module is one table. The script reads these keys:

| key | meaning |
|---|---|
| `path` | Required. Folder of the module, relative to the repository root. A module without `path` stops the run with an error. |
| `status` | `"live"` (the default) or `"dead"`. Any other value prints a CAUTION and the module is treated as live. |
| `docs_pending` | Any true value. A module that has code and tests is then PARTIAL, not DONE. |
| `expected_subs` | List of sub-module names this top-level module must eventually have. A sub-module's own `expected_subs` is never read. |

A registry entry whose `path` lies inside another module's folder is that module's sub-module. Other keys in
a module table (for example `owns` or `card`) are not read.

```toml
[module.billing]
path = "apps/billing"
expected_subs = ["invoices", "refunds"]

[module.billing_invoices]
path = "apps/billing/invoices"
```

## Master plan file (plan_file)

The plan file is optional. It holds the plan for the whole project. It is a TOML file with `[plan.KEY]`
tables, where KEY is a registry key:

```toml
[plan.billing]
issue = 2                         # issue number on GitHub (or in issues_json)
expected_subs = ["invoices", "refunds"]

[[plan.billing.items]]            # a work item: DONE when all its proof paths exist
name = "invoice export"
proof = ["apps/billing/export/*.py", "apps/billing/tests/test_export.py"]

[plan.future_module]              # a planned module: no folder yet
issue = 9
expected_subs = ["alpha"]
```

- `issue`: a number. Text that is a number (for example `"12"`) is read as that number, with a CAUTION.
  Other text is ignored, with a CAUTION, and the title lookup is used instead.
- `expected_subs`: a list. An empty list `[]` means "documented: no sub-modules". It still counts as an
  expected list (so COMPLETE is possible), but it is not a definition of done (see "Ready to close").
- `items`: work items. `proof` is one glob pattern or a list of them, relative to the repository root. A
  pattern matches when it finds a file, or a folder that contains at least one file. A work item is DONE
  when every pattern matches, PARTIAL when some do, NOT_STARTED when none do.
- A plan entry for a sub-module's key is ignored, with a CAUTION. A plan entry for a container key (see
  "Edge cases") is ignored without a message.
- A plan key that is not in the registry is a planned module. It shows as NOT_STARTED with its
  `expected_subs`, and its `issue` is checked. Its `items` are not read, and `path` is only written to
  `status.json`.

## Issues

- Source: either `github` (the GitHub API, all issue states, pull requests skipped, 100 per page until an
  empty page) or `issues_json` (offline). The same matching rules apply to both. Messages say "GitHub" in
  both cases.
- Token: the environment variable named by `token_var` is used first. If it is empty, `token_env_file`
  is read. The value is used only in the request header and is never printed. With no token the requests
  are anonymous, and a CAUTION says so.
- Matching, top-level modules only (sub-modules have no issue): if the plan gives an `issue` number, that
  number is used. Otherwise the title from `issue_title` is used. If the folder's last name is shared by
  two or more top-level modules and the plan gives no number, nothing is matched.
- Duplicate titles: the higher issue number is kept, with a CAUTION. The lower number is then not found
  by number.
- A network error or a non-200 answer prints a CAUTION and the run goes on with no issues. Every module
  then gets a "no GitHub issue" CAUTION.

## Status rules

Each folder (a top-level module or a live sub-module) gets one status, decided in this order:

1. Dead (`status = "dead"`) is not tracked. A dead top-level module has no tree row, no summary row, no
   `status.json` entry and no CAUTION. A dead sub-module has no tree row and never counts as present for an
   expected name.
2. No code files of its own: `NOT_STARTED`.
3. Code files, and no test files or `docs_pending` is set: `PARTIAL`.
4. Code files and test files: `DONE`.

A registered folder that does not exist gets `NOT_STARTED` and a CAUTION, once.

Counting code and tests:

- Code files are files whose name ends in an extension from `code_ext`, found by walking the folder. The walk
  skips `skip_dirs` and skips the folders of the module's own sub-modules, so a parent never counts a child's
  files.
- A code file is a test file when a folder below the module's root has a name from `test_dirs`, or the file
  name starts with `test_`, or the file name ends with one of `test_suffixes`. Otherwise it is a code file.

Expected names (`expected_subs`, from the plan, the registry or `expected`), for each top-level module:

- A name matches a live descendant whose folder name or registry key is that name. A matched name is
  present. A live sub-module that is not named is still counted, and gets the flag NEW.
- A name that matches no live descendant is NOT_STARTED and counts as expected missing. The reason shown is
  "no registered folder", or "its folder is registered but marked dead" when a dead descendant has that name.
- If the name is also the registry key or folder name of any top-level module (dead or live), the script
  prints a CAUTION "registered elsewhere" instead, and the name is not counted as missing.

Module states, in the summary table:

- `COMPLETE`: every item is DONE, no expected name is missing, an expected list exists (`[]` is enough), and
  the issue is closed.
- `closed, not verified`: every item is DONE, the issue is closed, and there is no expected list.
- `in progress`: anything else, including an open issue.
- `planned`: a planned module from the plan file, with no folder.

Ready to close: a module whose items are all DONE, whose issue is open, and that has a definition of done
(a non-empty `expected_subs`, or plan work items) gets a CAUTION. Without a definition of done it gets a NOTE
saying the script cannot tell whether the module is finished.

## Output files

All are written into `out_dir`:

- `report.md`: the text the script prints. The heading, the CAUTIONS list (or "No cautions."), the
  expected-list line, the tree and the summary table. The heading shows `?` for the commit id when the
  repository is not a git checkout.
- `module_tree.csv`: one row per module, sub-module, work item or expected name. Columns:
  `top_module, level, name, kind, status, code_files, test_files, plan`.
  - `level` is 0 for a top-level module. A sub-module is deeper. A work item and an expected name are at level 1.
  - For a work item, `code_files` is the number of proof patterns that match and `test_files` is the number of
    patterns. The report's tree prints the same two numbers with the labels `code` and `test`. For a work item,
    read them as "matching" and "total". For example, `refund flow: NOT_STARTED (... 0 code, 2 test ...)` means
    none of its two patterns match.
  - `plan` says where the row came from. Values: `registered, not in plan`, `registered + plan` (top-level);
    `registered`, `registered + expected`, `NEW, not in expected list` (sub-module); `plan work item (proof paths)`;
    `expected, not usable: no registered folder`; `expected, not usable: its folder is registered but marked dead`;
    `planned only`; `planned only, no folder yet`.
- `status.json`: `{"modules": [...]}`, one object per live top-level module and per planned module, with `name`,
  `path` and `items` (`item`, `status`, `evidence`).
- The workbook (`xlsx_name`), from `module_status_xlsx.py`. It has a Summary sheet (one row per area, which is
  the first segment of a module's path, and an Overall row), a Modules sheet (one row per module) and an Items
  sheet (the data). Counts are formulas. Module names are used as COUNTIF criteria, so avoid `*` and `?` in names.

The summary table:

| column | meaning |
|---|---|
| `items` | number of items: the module's own code, its sub-modules, work items and expected names |
| `done` | how many of those items are DONE |
| `expected missing` | how many expected names are missing (see "Expected names") |
| `issue` | `#N open`, `#N closed`, or `no issue` |
| `state` | `COMPLETE`, `closed, not verified`, `in progress`, or `planned` |

## Every CAUTION and NOTE line

`{...}` marks a value the script fills in. Lines are listed by what starts them. A CAUTION line is something a
person should look at. A NOTE line is a fact for the reader. Neither stops the run, except the first line, which
goes with exit code 2.

| exact text | when it is printed |
|---|---|
| `CAUTION: the registry lists no modules; nothing to track.` | The registry has no modules. The script exits with code 2 and writes no report. |
| `CAUTION registry: {k} and {first} share the folder '{path}'; both are counted.` | Two registry entries have the same path. Both are counted. |
| `CAUTION {k}: unknown status '{st}' (use live or dead); treated as live.` | A `status` other than `live` or `dead`. |
| `CAUTION {k}: its registered folder '{path}' does not exist.` | A registered folder is missing. Printed once per module, also for dead modules. |
| `CAUTION issues: two issues are titled '{title}' (#{old} and #{new}); the newer one is used.` | Two GitHub issues have the same title. The higher number is kept. |
| `CAUTION issues: no GitHub token found; anonymous calls are limited to 60 an hour.` | `github` is set and no token was found. |
| `CAUTION issues: could not read issues, GitHub not reachable ({ExceptionName}); issue columns are incomplete.` | The request raised an error, for example `ConnectionError`. |
| `CAUTION issues: could not read issues, GitHub answered {status}; issue columns are incomplete.` | The answer was not HTTP 200. |
| `CAUTION {key}: plan issue '{n}' should be a number, not text; read as {int}.` | The plan's `issue` is numeric text. |
| `CAUTION {key}: plan issue '{n}' is not a number; ignored.` | The plan's `issue` is other text. The title lookup is used. |
| `NOTE {top}: sub-module {c} is registered but not in its expected list; counted.` | A live sub-module the expected list does not name. It is counted and flagged NEW. |
| `CAUTION {top}: expected sub-module '{e}' is registered elsewhere as a module of its own.` | An expected name is also the key or folder name of a top-level module (dead or live), and no live descendant has it. |
| `CAUTION {top}: no GitHub {want} found.` | No issue matched. `{want}` is `issue #{n}` (plan number), `issue titled '{title}'`, or `issue ('{base}' is shared by {names}; name one in the plan)`. |
| `CAUTION {top}: everything built and tested, but issue #{n} is still OPEN. Close it out.` | Ready to close: all DONE, a definition of done, and the issue is open. |
| `NOTE {top}: built and tested, issue #{n} still open; no sub-modules or work items are listed, so it cannot be told whether it is finished.` | All DONE and the issue is open, but there is no definition of done. |
| `CAUTION {top}: issue #{n} is CLOSED but not everything is done ({m} expected missing, {k} not DONE).` | The issue is closed while the module is incomplete. |
| `CAUTION plan: '{key}' is a sub-module in the registry; plan entries belong to top-level modules, so its {dict} is ignored.` | The plan has an entry for a sub-module. `{dict}` is the ignored keys, for example `{'expected_subs': ['x']}`. |
| `CAUTION {key}: planned module names issue #{n}, which was not found.` | A planned module's issue number is not among the issues read. |
| `CAUTION {key}: issue #{n} is CLOSED but the module has no folder yet.` | A planned module has a closed issue. |
| `NOTE {k}: registered in the registry but not listed in the master plan file.` | A live top-level module is not in the plan. Printed only when `plan_file` is set; not for containers or dead modules. |
| `CAUTION workbook not built: {last line of the builder's error output, at most 200 characters}` | The workbook builder exited with an error. |
| `No cautions.` | There are no CAUTION or NOTE lines. Otherwise the heading `## CAUTIONS (not failures)` is printed above the list. |
| `No expected_subs list yet (so COMPLETE and ready-to-close checks are off): {names}` | Lists the live top-level modules that have no expected list, sorted. |

The last line of standard output is `wrote {xlsx} (builder rc {rc}), {status.json}`.

## Edge cases

- Containers: with `container_depth` N, a registered module whose path has N parts or fewer is an area
  folder. If it has registered sub-modules, it is not tracked: its issue, its plan entry and its
  `expected_subs` are ignored, with no message. If it has no registered sub-modules, it is tracked like any
  top-level module, but it gets no "not listed in the master plan file" NOTE.
- A dead top-level module is not tracked. A live module inside its folder is treated as a sub-module of the
  dead module, so it is not shown either, and no CAUTION is printed for it.
- With `container_depth` at its default of 0, no module is a container.
- Two modules with the same folder: both are counted, with a CAUTION.
- The tree says `registered, not in plan` for each top-level module when no `plan_file` is set.

## Example

The example config names a small invented repository, `sample_repo/`, and an offline issue list, `example_issues.json`.
Neither is shipped with this folder. To run the example, create `sample_repo/` (a registry, a few module folders with
code and tests) and `example_issues.json` beside `example_config.toml`, and copy `example_MODULE_PLAN.toml` to
`sample_repo/MODULE_PLAN.toml`. The output below is from a run against such a repository.
Run it from the folder that holds the config, because the config's paths are relative to where you run it:

```
python3 module_status.py example_config.toml
```

This is the real output of that run (the first part, then the summary table):

```
# Module status, Example project at ?, 2026-11-09 22:32Z

## CAUTIONS (not failures)
- NOTE billing: sub-module billing_extra is registered but not in its expected list; counted.
- CAUTION billing: issue #2 is CLOSED but not everything is done (1 expected missing, 3 not DONE).
- CAUTION parser: no GitHub issue titled 'module: parser' found.
- CAUTION reporting: everything built and tested, but issue #4 is still OPEN. Close it out.
- CAUTION future_module: issue #9 is CLOSED but the module has no folder yet.
- NOTE ingest: registered in the registry but not listed in the master plan file.
- NOTE parser: registered in the registry but not listed in the master plan file.

No expected_subs list yet (so COMPLETE and ready-to-close checks are off): ingest, parser

| module | items | done | expected missing | issue | state |
|---|---|---|---|---|---|
| archive | 1 | 1 | 0 | #5 closed | COMPLETE |
| billing | 6 | 3 | 1 | #2 closed | in progress |
| ingest | 1 | 1 | 0 | #1 closed | closed, not verified |
| parser | 1 | 0 | 0 | no issue | in progress |
| reporting | 2 | 2 | 0 | #4 open | in progress |
| future_module | 2 | 0 | 1 | #9 closed | planned |
```

## Tests

The tests live in `tests/unit/tools/module_status/` (unit and regression tests) and `tests/contract/test_tools_module_status_contract.py`
(the contract). They build small fake repositories in temporary folders and run the script on them. They run with the
repo's own test command, from the repo root:

```
python3 -m unittest discover -s tests -t .
```

`MS_SCRIPT` (for the script) and `MSX_SCRIPT` (for the workbook builder) point the tests at other copies of the scripts,
for example a mutated copy when checking that a test goes red.

