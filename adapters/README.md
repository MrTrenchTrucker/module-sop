# adapters: harness adapter packs

**What it does.** Maps the SOP chain of command onto concrete agent
harnesses, one file per harness. An adapter tells a shop running that
harness which of its roles, records, and channels play each SOP part —
without changing the SOP or the harness.

**How it works.**
- Each adapter is one Markdown file. It maps roles, the work-order form,
  and the reply paths, then lists what it deliberately does not map.
- Adapters cite SOP rules; they never restate them. The rule lives in
  `docs/`; the adapter says where that rule fires in the harness.
- Adapters are docs-only. No code ships here, so no lint surface beyond
  the repo-wide registry, card, and README checks.

**Packs.**
- `hermes-bot-mode.md` — the Hermes Bot Mode adapter (orchestrator,
  delegated task workers, reviewer role, kanban records).
