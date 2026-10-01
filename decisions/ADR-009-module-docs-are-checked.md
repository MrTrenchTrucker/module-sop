# ADR-009: Every module carries a card and a README, and scripts keep both honest

**Status:** accepted
**Date:** 2026-09-24
**Approved by:** Commander:
- "every module probably needs an agents.md and probably a readme along with all levels of sub modules which the agents need to read before working on it ... and those documents get updated every time code changes in that module and set of sub modules."
- Tests that fail loudly if they aren't updated.
- "Proceed!": "when a worker works on the code, they will see the test fail and say ... this other test that is for the agents.md and readme failed! I should see why and read the files again."

## Context
A module card (`AGENTS.md`) is the fence a worker is measured against. Nothing checked that the card still matched the registry or the code. Nothing gave humans and agents a plain explanation of what a module actually does. And nothing noticed when code moved on and its docs didn't.

## Decision
`tools/doc_check.py` enforces four rules, and each has a planted-fault test:
1. **Present.** Every module, at every level, has `AGENTS.md` and `README.md`.
2. **Card matches the registry and the code.** Card and registry list the same public names and the same `depends_on`. In a code module, `public` is every public function and class and nothing else; `main` is exempt. An interface change without a card change fails.
3. **Parent README names each sub-module**, by registry name.
4. **Docs current.** Compared against the base commit (the merge-base with main, or `$SOP_BASE`), counting uncommitted and untracked files: a module whose code changed must also have changed its README.
   - The owning module is the deepest one, so a sub-module's change needs its own README.
   - A `README waiver: <module>: <why>` line in a work order changed in the same diff excuses it, for the IT manager to accept.

Rules 1 to 3 run inside `sop_check.py`. Rule 4 runs as a contract test (`tests/contract/test_module_docs_current.py`), so whoever runs the tests sees it fail before handing off, and the message says what to reread.

A module registered before READMEs were required can be marked `docs_pending = true`; rules 1 to 4 skip it until a work order converts it.

## Reasons
- A card is only a fence if it's true, and "keep the docs updated" written as a rule gets ignored; a failing test doesn't.
- Rule 2 is a content check, not a touch check. Forcing a card edit on every code change would produce junk edits, since most changes don't change a module's rules.
- The README is a touch check with a waiver. A check can prove a file changed; whether the prose is right stays the IT manager's review.

## Consequences
- Helpers that aren't part of a module's interface are named private (leading underscore).
- Every commit that changes a module's code also touches its README, or carries a waiver.
- Mutation evidence (2026-09-24): 11 of 11 mutants of `doc_check.py` were killed, each by its guard test. The unchanged control and a comment-only edit both passed.
