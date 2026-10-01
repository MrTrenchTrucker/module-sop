# Module: adapters

## Purpose
Harness adapter packs: worked mappings from the SOP chain of command onto
concrete agent harnesses, so a shop can adopt the SOP without rebuilding its
own orchestration. Each adapter names the harness roles, the work-order
form, and the reply paths — and nothing else.

## Owns
- `hermes-bot-mode.md`: the Hermes Bot Mode adapter (roles, work-order
  form, reply paths, loading discipline).

## Does Not Own
- The SOP texts (module `docs`).
- The class skills (module `skills`).
- Any harness's own internals, config formats, or deployment tooling.

## Public Interface
- `hermes-bot-mode.md`: role map, work-order form, reply paths, loading
  discipline, what is deliberately not mapped.

## Depends On
- docs (the chain-of-command terms the adapters map: work order, readback,
  handoff, bounce-back, module, write-scope)

## Invariants
- Adapters are docs-only: no code, no imports, no line-cap surface.
- An adapter never restates SOP rules; it maps them onto harness machinery
  and cites the SOP section for the rule itself.
- An adapter never invents a new class or gate; unmapped concepts are
  listed explicitly under "Deliberately not mapped".

## Test Locations
- Contract: `tests/contract/` (structure only — the adapters module is
  covered by the repo-wide registry/card/README checks, no dedicated suite)

## Known Gotchas
- Keep harness-vendor names and product paths out of adapter text where a
  generic term works; adapters describe machinery, not deployments.
- If the SOP chain changes a mapped term, the adapter goes stale — flag it
  in the PR that changes the term.
