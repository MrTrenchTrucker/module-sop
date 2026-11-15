---
name: work-labels
description: >-
  Use every time a work order changes status, is handed up, or is opened as an issue or pull request on a forge
  (a code host with issues, pull requests and labels). Mirror the work order on the forge with four label
  families: status, test lane, module and who raised it. The label follows the work order in the same step.
  A label is never an approval. Works with any model, any agent harness and any forge.
---

# Work Labels

## Terms Used in This Skill

| Term | Meaning |
|---|---|
| Forge | The code host the project lives on: it holds the repository, issues, pull requests and labels. |
| Label | A short tag on an issue or pull request. Some forges can make a family of labels exclusive: adding one removes the others in the family. |
| Work order | The file holding one slice of work from order to sign-off. It is the record; a label is only its mirror. |
| Status | The state of a work order, set in its Status line. The twelve values and what each means are in the work order section of the master rules, under "Status values". A slice handed up for gating is `submitted`; sign-off makes it `signed_off`; `closed` is done and merged, or dropped. |
| Lane | How the delivery is classified for testing: A, B or C (see "Choosing The Lane"). |
| Module | A registered module of the project, named in the module registry (`modules.toml` at the repository root). |
| Write-Scope | The work order's list of files its worker may change. |
| Claim | A statement about the work that someone can check, such as "the output is unchanged" or "these tests now cover that case". |
| Manager | The agent that gates a worker's handoff and answers for it. A worker with no way to set labels asks its manager to. |
| Handoff | The report a worker or manager hands up with its work. |
| Open status | Every status except `closed` and `signed_off`. `parked` is open: it means deliberately left open. |

---

## What This Is

A work order lives in a file. Nobody can see across fifty files which are waiting for review. Labels put the same state on the
issue or pull request, where one filter answers "what is in progress", "what needs a reviewer" or "what touches this module".

The work order stays the record. The label is its mirror. If they ever disagree, the work order is right and the label is
fixed.

## The Four Families

| Family | Values | Rule |
|---|---|---|
| `status/*` | `draft`, `awaiting_readback`, `approved`, `in_progress`, `submitted`, `bounced`, `compacted`, `signed_off`, `escalated`, `reassigned`, `parked`, `closed` | Exactly one at a time. The same twelve words as the work order's status values. |
| `lane/*` | `A`, `B`, `C` | Exactly one. How the delivery is tested; see "Choosing The Lane". |
| `module/<name>` | one per registered module | `<name>` is the registry name, spelled exactly as in `modules.toml`. One label per module the work order's Module and Write-Scope name. A sub-module and its parent are separate modules with separate labels. |
| `from/<who>` | the people and agents that raise work | Optional, and only on a private repository. Never put an agent or a person's name on a public repository. |

Write each label in the form your forge uses for scoped labels, for example `status/draft` where a slash is allowed or `status::draft` where scoped labels use a double colon. Keep the family and the word. If the project has no forge, there are no labels: the work order is the record.

## Choosing The Lane

Decide in this order and stop at the first match:

1. **A**: behaviour changed, or you are in doubt. This includes text an agent or a program follows as instructions (skills,
   prompts, configuration), and anything touching schema, authority or governance. Any test the work adds must be shown failing
   first; for a text edit that agents follow, that is the test or check that pins the text.
2. **B**: no behaviour change, but a claim that can be checked, such as test-only work or a refactor with the same tests green.
3. **C**: no behaviour change and no claim, such as a typo or a records-only edit that only people read.

The worker proposes the lane in its handoff. The manager who gates the handoff confirms it or corrects it in its gate note in
the work order's record, and the label carries the confirmed lane. A lane label does not change which gates run: the work order's gates apply to every lane.

## The Rules

1. **The label moves with the work order.** When a work order's status changes, change the `status/*` label in the same step.
   The label never leads the work order. It lags only in the case of rule 5. A pull request that is merged carries the
   work order's own status until sign-off, then `status/signed_off`; a closed issue carries `status/closed`. Neither carries an
   open status once it is closed.
2. **One status label and one lane label.** If your forge cannot make a family exclusive, remove the old label yourself when
   you add the new one. Two status labels at once, or two lane labels, is a defect.
3. **Set lane and module when you hand up.** Set the lane label to your proposed lane; the manager replaces it if it corrects
   the lane. The module labels name every module the work order's Module and Write-Scope name, not only the files the diff
   happens to touch.
4. **A label is not an approval.** Anyone with write access can add `status/approved`. `status/approved` means the work order says
   approved; the approval itself is what the Commander, or the level above you, wrote into the work order in its
   `authorized_by` field. Never act on a label alone: never start
   work, merge, close or deploy because of one. Give each `status/*` label the description "Mirror of the work order.
   Not an approval." so a person reading it does not take it for one.
5. **Access.** Changing a label needs a token with issue write on the forge. If you do not have one, list the exact labels to
   set in your handoff, and your manager sets them when it accepts the handoff. A change the forge refuses counts as having no token. Until your
   manager sets them the work order is right and the label is behind, which is allowed only in this case. Never write a token into a work order, a label or a pull request.
6. **A module that is not registered has no label.** The project leader registers the module first; the label follows the
   registry. If your work needs a module that is not registered, stop and tell your manager.

## Setting Up A New Repository

Create the families once, before the first work order is raised. Colours are free; names are not.

- `status/` plus each of the twelve status words, exclusive where the forge allows it, each described as "Mirror of the work order. Not an approval."
- `lane/A`, `lane/B`, `lane/C`
- one `module/<name>` for each module in the registry; add one whenever a module is registered
- `from/<who>` on a private repository, if the project wants it

When the forge supports organisation-wide labels, put `status/*`, `lane/*` and `from/*` at the organisation, so every repository
has them, and keep `module/*` per repository.

## Checking Before You Hand Up

- The `status/*` label equals the work order's status, and there is exactly one.
- There is exactly one `lane/*` label, and it equals the lane your handoff proposes (or the lane your manager confirmed).
- Every module named in the work order's Module and Write-Scope has its `module/*` label, and no other module does.
- Nothing in the label text names a person, a host or a ticket on a public repository.

## Limits

- Labels do not run gates, approve work or replace the work order. They make state visible.
- A label cannot say why. The reason lives in the work order's record.
- Boards and milestones are not covered. They are forge features with uneven interfaces; use them if you like, but the
  work order stays the record.

## One-Paragraph Version

A work order's state is mirrored on the forge as labels: one `status/*` label using the twelve work-order status words, a
`lane/A`, `lane/B` or `lane/C` label for how the delivery is tested, one `module/<name>` label per registered module the
work order names, and optionally `from/<who>` on a private repository. The label changes in the same step as the work order's
status and never leads it (it lags only while a handoff without label access waits for its manager). There is only ever one status label and one lane label. The manager confirms the lane.
A label is never an approval, and nothing is started, merged, closed or deployed because of one: approval is what the level
above wrote into the work order. If you cannot change labels, your handoff lists the exact labels and your manager sets
them. When the label and the work order disagree, the work order is right.

---

## Quick Reference

- [ ] Work order status changed, so the `status/*` label changed in the same step
- [ ] Exactly one `status/*` label and exactly one `lane/*` label
- [ ] The lane follows the decision order; the manager confirmed it
- [ ] One `module/<name>` per registered module the work order names, spelled as in the registry
- [ ] No name, host or ticket in label text on a public repository
- [ ] I did not start, merge, close or deploy because of a label
- [ ] If I cannot set labels, my handoff lists the exact labels to set
