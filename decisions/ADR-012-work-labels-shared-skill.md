# ADR-012: Work labels, as a second shared skill

**Status:** proposed
**Date:** 2026-11-08
**Approved by:** pending: the Commander, on merge

## Context
- A work order is a file. Across many files nobody sees at a glance which are waiting for review, which are in progress, or
  which touch a module.
- A first project run under this SOP put its work-order state on the forge as labels: a status label per issue and pull
  request, a test-lane label, and a module label. The Commander saw it work and asked for it on every forge in use.
- The SOP already fixes the twelve status values. It says nothing about showing them on a forge.
- ADR-010 made a shared pack for practices every class shares. ADR-002 and ADR-007 keep each class to two skills about
  that class.

## Decision
- A second shared skill, `work-labels` (`skills/shared/work-labels/`), a sub-module of `skills_shared`.
- Four label families: `status/*` (the twelve status words, exactly one), `lane/A|B|C`, `module/<name>` (the registry name),
  and optionally `from/<who>` on a private repository only.
- The label changes in the same step as the work order and never leads or lags it. On any disagreement the work order wins.
- A label is never an approval, and nothing is started, merged, closed or deployed because of one. Approval is what the level
  above wrote into the work order.
- The lane is proposed by the worker and confirmed by the manager who gates the handoff, by a fixed decision order whose first
  step is "in doubt, A". The SOP's work order template has no lane field; adding one is a change to the SOP text and is not
  made here.
- The skill names no model, harness, tool or forge product. `tools/skill_lint.py` gates it as a shared skill. A contract test
  compares its status words with the status values in `docs/MODULE_SOP.md`.
- The SOP text and the class skills do not change.

## Reasons
- One copy cannot drift between the four class skills, and the class skills stay byte-identical to their pins.
- Labels are on every common forge, and an agent can read and set them through the forge's interface, so state is visible
  to people and agents with one filter.
- A mirror that the work order overrules cannot become a second source of truth.
- Saying "a label is not an approval" closes the easiest way this could be abused: anyone with write access can add a label.

## Consequences
- An agent that moves work orders carries `work-labels` next to its class pack. Installing it on agents is agent
  setup (ADR-004) and needs the Commander's word.
- The skill alone does not create labels on a forge or give an agent a token. A project sets the labels up once, and an agent
  without issue-write access says so in its handoff and its manager sets the label.
- A change to the SOP's status values changes the skill in the same commit; the contract test fails until it does.
- Later decision, not made here: whether the class skills or the SOP point at `work-labels`, and whether a script check
  compares a work order's status with its issue's label on a forge that can be reached.
