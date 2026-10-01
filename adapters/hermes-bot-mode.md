# Adapter: Hermes Bot Mode

Maps the SOP chain (MODULE SOP) onto a harness with one orchestrating
agent, delegated task workers, a reviewer role, and kanban records. Rule
cites are MODULE SOP sections; the rules themselves live in `docs/`.

## Role map

| SOP class | Harness part | Notes |
|---|---|---|
| Commander (human) | The human operator | Owns hard gates (push, merge, deploy, live effects). Same as the SOP: only the Commander changes the SOP-equivalents (here: the skill library). |
| Project Leader | Folded into the orchestrator | A separate planning role earns its keep past ~3 parallel workstreams; below that it is ceremony. Split it out when one orchestrator context holds more plans than it can track. |
| IT Manager | The orchestrating agent | Issues work orders, approves readbacks, gates handoffs, sends bounce-backs. One per workstream at most. |
| Worker | A delegated task worker | One slice per task. Builds, proves, reports. Never decides scope or done — same as the SOP. |
| Bug-hunting IT Manager | The reviewer role | Read-only pass over the worker's handoff before the orchestrator accepts it. No implementation, no fixes — findings back as bounce-back. |

## Work-order form

The kanban task body is the work order. It carries, in fixed fields:

- **Goal** — one paragraph: what done looks like.
- **Write-scope** — the exact paths the worker may touch. Anything else is out of scope, no exceptions.
- **Acceptance test** — the commands the worker runs to prove the slice, decided before the build starts.
- **Reply path** — where the readback and the handoff go (the task's comment thread).

## Readback, handoff, bounce-back

- **Readback.** The worker's first task comment restates the brief in its
  own words — goal, scope, acceptance test — before writing code. The
  orchestrator approves it or corrects it. Nothing builds on an
  unapproved readback (Parrot Protocol, same as the SOP).
- **Handoff report.** The completion summary: what changed (files),
  the acceptance-test evidence (exact output, not paraphrase), and what
  was deliberately left out.
- **Bounce-back.** The reviewer or orchestrator returns the task with
  concrete required changes quoted against the handoff. The worker
  addresses each one; a re-handoff answers each point.

## Loading discipline (deliberate drift)

The SOP ships class skills locked and always-on. On metered harnesses
that cost is real, so this adapter loads lazily instead: a ~50-line role
card stays resident per active role; the full class SOP is pulled only
when that role activates (delegation time for workers, review time for
the reviewer). Same rules, smaller resident footprint. The tradeoff is
stated plainly: a worker that never pulls the full SOP is running on the
card, so cards must carry every hard gate (write-scope, readback,
acceptance test) verbatim, never summarized.

## Check-ins and compaction

- **Check-in.** The orchestrator's scheduled status sweep maps onto the
  harness's own heartbeat/cron. Workers answer; they never run one.
- **Compaction is normal.** Context compression is routine, not failure.
  After a compaction the worker re-orients from the work order and the
  module card — both are files, so they survive it.

## Deliberately not mapped

- **Project Leader as a separate role** (folded in; see above).
- **Per-agent install mechanics** (ADR-004: outside repo scope here too).
- **The readback skill forms** (`parrot-protocol-*`): the harness's task
  comments carry the readback, so the fixed readback forms stay in the
  class skills, unchanged.
