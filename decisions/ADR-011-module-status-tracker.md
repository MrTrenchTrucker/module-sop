# ADR-011: The module status tracker is a sub-module of tools, and it only reads the repo it reports on

**Status:** accepted
**Date:** 2026-11-09
**Approved by:** Commander (2026-11-09)

## Context
- A repo split into modules needs one view of what is built, what is partial, which planned sub-modules do not exist
  yet, and whether a module's issue can be closed. `tools/module_status/` answers those questions with fixed rules.
- The tracker reads the repo's `modules.toml`, the folders and files on disk, an optional master plan, and optionally
  GitHub issues. It writes a workbook, a CSV table, a JSON file and a report.
- Two places could hold it: a new top-level module, or a sub-module of `tools`. It is a reporting tool with no
  interface other modules need, and it works on any repo that keeps a registry.
- It is the first code in the repo that can reach the network (only when a config asks for GitHub issues). It uses
  only the standard library.

## Decision
- The tracker lives in `tools/module_status/` as the sub-module `tools_module_status`, with `depends_on = ["tools"]`.
  It has its own card and README, and `tools/README.md` and `tools/AGENTS.md` name it.
- It reads only: the registry of the repo its config names, the optional master plan, and, when configured, an offline
  issue list or GitHub issues (read-only).
- It writes only into the output folder its config names (`out_dir`). It never writes into the repo it reads.
- Its interface is its command line. It exposes no Python function or class.
- Its one network use, an optional read-only HTTPS request for GitHub issues, goes through the standard library
  (`urllib`), so `ARCHITECTURE.md` rule 5 holds without an exception. The API address is configurable
  (`github_api`), which also lets the tests run against a local stand-in.

## Reasons
- A sub-module of `tools` keeps the gates and the reporting tools in one place, under one registry entry and one set
  of checks (structure, line caps, cards, README freshness, import contracts).
- Reading only, and writing only into a folder the config names, means a report can never change the repo it describes,
  so the report cannot make the repo look built when it is not.
- The network path is off by default. A run without GitHub is offline and deterministic, so its output can be checked
  without a network.

## Consequences
- `tools/` now holds one more folder of code, with its own line caps and card. `tools/AGENTS.md` notes the exception to
  its "No network" invariant, and says the exception belongs to the sub-module.
- `ARCHITECTURE.md` is unchanged: rule 5 ("only `tools/` has code, and it imports only its own files and the standard
  library") is kept.
- Adding a second report-style tool later goes under `tools/` the same way, as its own sub-module.
- Installing or running the tracker on any agent's infrastructure is outside this repo (ADR-004).
