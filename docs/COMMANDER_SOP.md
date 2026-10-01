# COMMANDER SOP

**Version:** 1.3.0
**Audience:** The human at the top of the chain
**Companion to:** `MODULE_SOP.md` (the full standard the agents follow)

---

## What This Is

You run a chain of AI agents that builds software. This document is your side of the deal: what you do, what comes to you, what doesn't, and how to tell when the system is working.

The full rulebook lives in `MODULE_SOP.md`. You don't need to memorize it. You need to know the shape of it, because you're the only one who can change it.

## The Shape of the System

Four levels in the chain of command, each gating the one below it, plus your design space beside it:

```
DESIGN SPACE (outside the chain)          CHAIN OF COMMAND
─────────────────────────────────         ──────────────────────────────────────
Your planning platform                    Commander (you)
  + Architecture Advisor(s)  ◄─────────►     ↓ intent, architecture doc, approvals, smoke test
                                          Project Leaders
        ▲                                    ↓ project plans, work orders authorized in writing
        │ consult only, as needed:        IT Managers
        │ "does this match design intent?"   ↓ slice-level work orders, worker gating
        └──────────────────────────────── Workers
                                             ↓ code, tests, handoff reports

Orders go DOWN the chain. Proposals, escalations, finished work go UP.
Advisors answer questions. They never issue orders, and a revision they
suggest is not a revision until it has gone up the chain to you.
```

Authority follows the chain: orders, approvals, gating, and sign-offs move one level at a time and get recorded. Project leaders don't hand work to workers. Workers can talk only to their IT manager and the architecture advisor; you can message a worker directly and it can answer, but that's not a channel it uses on its own.

Conversation doesn't. You, the project leaders, and the IT managers are all managers, and managers talk to each other whenever it helps. You can go straight to an IT manager when that's what the job needs; IT managers talk to each other constantly. The one rule: if a side conversation changes a work order, the change gets written into that work order and the project leader is told, because the project leader owns the record. Forcing every conversation through the project leader would silo information for no gain; skipping the record would lose it.

What reaches you is written for a human: a short TLDR that leads with whether you need to decide anything, with the full record linked behind it. If a project leader sends you the full record instead, send it back and ask for the TLDR.

Every handoff between levels uses the **Parrot Protocol**: the receiver reads back what it thinks it was told, and nothing moves until the sender confirms the readback. It's a radio readback, and it's the single cheapest error-catcher in the system.

## What You Own

You hold five things nobody else can:

1. **Intent.** What gets built, why, and what matters most.
2. **The foundation.** The architecture doc and the decision records change only with your say-so.
3. **Scope.** Anything that would change an active work order, or turn a discovery into new work, gets your ruling.
4. **Release.** Nothing publishes until it passes your live smoke test.
5. **The rules.** The SOP itself changes only through you, and every change gets a version bump.

Everything else is delegated on purpose. If something reaches you that isn't on this list, ask why the chain didn't handle it.

## Where the Design Work Happens

Intent and architecture don't get designed inside the chain. They get designed by you, on whatever planning platform you prefer, before anything is handed to a project leader.

That platform is yours to choose. It might be a planning workspace, a chat interface on your phone, or a set of advisor agents you've built for exactly this purpose. Any or all of them are fine. What matters is the split:

- **Advisors help you think.** Research, weigh options, draft the architecture doc, stress-test a decision. They sit outside the chain and issue no orders.
- **Project leaders execute.** They receive the finished intent and the approved architecture doc, and turn them into plans and work orders.

The preliminary design work is never done with the project leader. The project leader's job starts when the design is good enough to hand over.

Once the design is settled, three artifacts leave your platform and enter the repo: the intent, the architecture doc, and any decision records the design produced. From that point the chain owns execution.

### Redesigning after handoff

Execution surfaces things design didn't see. Once the architecture is in the project leader's hands, you can iterate and redesign **with the project leader**, because it now holds the execution picture. When you do:

- Keep your architecture advisor in the loop on every change, so its understanding of the design stays current. An advisor working from a stale design gives stale answers.
- Every revision still lands as an updated architecture doc and a decision record, approved by you. Nothing changes by conversation alone.

### Advisor access for the chain

Every agent in the chain, at every level, may consult the architecture advisor that designed the system with you, **on an as-needed basis only**. The purpose is narrow: when an agent discovers something in the codebase, it can ask the advisor whether that discovery matches the architectural design intent. This keeps discoveries from being misread and keeps the design's reasoning available without pulling you in for every question.

The limits:

- The advisor **answers questions**. It does not issue orders, approve work, or change the design.
- If the advisor's answer is "that doesn't match the intent, the design needs revising," that is a **proposal**, not a decision. It goes up the chain, level by level, to you. You rule on it, and only then does the architecture doc change.
- Every consult is recorded in the work order file: what was asked, what the advisor said, and what the agent did with it.

This is what keeps the human in the loop. Agents can check the design's reasoning any time, but only you can change the design.

## Your Cycle

### 1. Set intent

Work out what you want on your planning platform, with advisors if you use them, until it's clear enough to state in plain terms: the goal, the priorities, and the constraints. Then hand it to the project leader. You don't write work orders. You describe the destination.

### 2. Approve the foundation

For a new project, sign off on:
- the architecture doc
- the approval list (who can approve what)
- the smoke test checklist (what your final test covers)

The approval list and smoke test checklist are yours to adjust at any time with the project leader. They're the two dials that control how much comes to you.

Also set the **check-in interval**: how often the project leader wakes on a timer to reread its plan, update the work orders, and sweep the chain for updates. Default is every two to three hours while work is out, repeating until the project is done or indefinitely if it's ongoing. Projects run for days and agents get compacted along the way; the check-in is what keeps them from stalling or forgetting the goal. IT managers run shorter clocks of their own on their workers; those are theirs to set, not yours. If your setup can't schedule the project leader, you or the dashboard trigger it instead. You'll hear from it after a check-in only if something changed or needs your decision.

### 3. Confirm the readback

The project leader parrots your intent back as a plan. Read it. If it isn't what you meant, correct it now. Fixing a misunderstanding at this step costs a paragraph; fixing it after the work is done costs a rebuild. Three rounds is the cap. If it still doesn't match, the intent itself probably needs rewording.

### 4. Rule on proposals

Workers do recon before they start, and they find things. Those findings travel up the chain as proposals. You approve or deny. Your ruling goes to the project leader, who writes it into the work order. If it isn't written into a work order, it didn't happen.

Proposals never expand the work already in progress. Approving one creates new work; it doesn't change the current order.

### 5. Handle escalations

You hear about:
- anything serious (data loss risk, security, something that would break the smoke test)
- disputes the chain can't settle
- work orders that hit a cap: three readback rounds, three retries on one issue, or three compactions
- the same slice failing across two different workers, which means the design is wrong, not the worker

You don't hear about ordinary bounce-backs, retries, or reassignments. Those are the managers' job.

### 6. Run the live smoke test

When the project leader hands you finished work, the scripted checks have already passed. Your job is the live run: use the thing the way it'll actually be used, against the checklist you approved.

- **Pass:** you approve publication.
- **Fail:** nothing publishes. Send a bounce-back to the project leader describing what broke. It traces the failure to the responsible work orders, reopens them, and the fix flows through the normal cycle. Then you run the smoke test again from the top.

### 7. Tune the SOP

Periodically look at what keeps coming to you and what keeps failing. Those are the rules that need changing. Edit the SOP, bump the version, and tell the project leaders. Agents read the version so they know which rules they're on.

When a rule keeps failing to fire, don't write a better paragraph. Find what the agent actually executes (its checklist, its profile, its standing instructions) and change that. If the written rule and the executed checklist disagree, the checklist wins every time. That makes the Quick Reference checklists and the agents' profile files the real SOP, and every edit to a body section needs its checklist updated in the same change.

## What Never Comes to You

- Which worker gets which order (IT managers know their workers)
- Bounce-backs, retries, and compactions
- Worker reassignment
- Interface changes between modules (project leaders)
- New modules inside an approved plan (project leaders)
- Test edits inside a slice (IT managers)

If any of these show up at your level, the approval list is wrong or someone skipped the chain. Fix the list or send it back down.

## How to Tell It's Working

Good signs:
- Readbacks match on the first or second round most of the time.
- Proposals arrive as short, specific asks with a clear yes/no.
- Smoke tests pass on the first run more often than not.
- The same bug doesn't come back.
- Fewer things reach you over time, not more.

Bad signs, and what they usually mean:
- **Readbacks hitting three rounds:** your intent is vague, or the architecture doc is out of date.
- **Frequent compactions on one slice:** the module is badly cut, or the work order is asking for two things.
- **Smoke test failures on things the tests covered:** tests are being weakened, or the mutation gate is off.
- **Lots of proposals for small things:** the approval list is too tight. Loosen it.
- **Surprises in the smoke test:** the project leader's scripted checks don't match your checklist. Revise the checklist together.

## Quick Reference

Before a new project:
- [ ] Architecture designed on your planning platform, with advisors as needed
- [ ] Intent written and handed to a project leader
- [ ] Architecture doc approved
- [ ] Approval list approved
- [ ] Smoke test checklist approved
- [ ] Project leader's plan readback confirmed

During the work:
- [ ] Rule on proposals as they come up
- [ ] Handle escalations only
- [ ] Every approval you give is written into a work order by the project leader

Before release:
- [ ] Scripted checks confirmed green by the project leader
- [ ] Live smoke test run against the checklist
- [ ] Pass → publish. Fail → bounce-back, fix, rerun from the top.

Ongoing:
- [ ] Review what keeps reaching you
- [ ] Tune the approval list, smoke test checklist, or the SOP
- [ ] Bump the version on every SOP change
- [ ] A rule that keeps failing: change the checklist or profile the agent executes, not just the paragraph
- [ ] Every body edit has its checklist updated in the same change

## One-Paragraph Version

You set the destination and hold the keys. Project leaders plan the route and write down your approvals. IT managers dispatch the workers and check their work. Workers haul one load at a time and prove it arrived intact. Everyone reads back their orders before moving. Scripts check what scripts can check, and nothing ships until you've driven it yourself.
