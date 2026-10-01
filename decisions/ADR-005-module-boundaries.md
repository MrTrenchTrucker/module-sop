# ADR-005: Three top-level modules: docs, tools, skills (skills split by class)

**Status:** accepted
**Date:** 2026-09-24
**Approved by:** Commander (WO-001)

## Context
The repo holds three different kinds of thing:
- the Commander's source text;
- deterministic scripts;
- generated agent-facing skills.

MODULE SOP 5.5 asks for the boundary decision to be recorded.

## Decision
- `docs` owns the source text.
- `tools` owns every script.
- `skills` owns the generated output, with one sub-module per agent class (`project-leader`, `itm`, `worker`), each registered with `depends_on = ["skills"]`.

## Reasons
- The three change for different reasons and at different hands: the Commander (docs), a code change under gate (tools), and a rebuild (skills).
- Splitting skills by class lets each agent's package be read, verified and installed alone.

## Consequences
- A class skill never contains another class's material.
- Adding a class means a new sub-module (registry, folder, card, contract test) and an entry in `tools/build_skills.py`.
