# MODULE SOP

**Version:** 1.8.1
**Status:** Draft pending Commander approval
**Applies to:** Every coding project, new and existing
**Change authority:** Commander only. Every change bumps the version number.

---

## 1. Elevator Pitch

The Module SOP is the operating standard for every agent on every coding project. The Commander designs the architecture outside the chain, on a planning platform of choice, then hands it to a four-level chain, Commander → Project Leaders → IT Managers → Workers, with each level gating the one below it and every handoff confirmed through the Parrot Protocol. Agents get fully briefed before they start, build in small registered modules, reuse code instead of duplicating it, and prove every change with tests that are shown to fail loudly. Scripts enforce every rule they can, the same way every time, so the LLM only handles judgment work. Nothing publishes until it passes the Commander's live smoke test, and the whole system runs from plain files in the repo, with or without the command dashboard.

## 2. Mission Statement

Agents build software the way a disciplined crew hauls freight: fully briefed, in their lane, verified at every checkpoint, and signed off before delivery. No slop ships.

## 3. Core Principles

1. **Deterministic first.** If a script can check it, a script checks it. LLMs handle only the work that takes judgment: design, coding, readbacks, judgment calls, and review. Scripts don't drift even when agents do.
2. **The repo is the source of truth.** Every order, readback, approval, and report lives as a plain file in the repo. The command dashboard automates the process but never replaces the files.
3. **No approved readback, no work.** Nothing gets built until the agent doing it has parroted back its plan and had it approved.
4. **Fail loudly.** Every change is covered by tests, and every test is proven to fail when the code it protects is broken.
5. **Reuse before write.** Search for existing code first. Duplicated logic is a defect.
6. **Stay in your lane.** A worker changes only what its work order allows. Anything else goes up the chain as a proposal.
7. **Approvals are written down.** An approval that isn't recorded in the work order file didn't happen.

## 4. Chain of Command

| Level | Role | Gated by |
|---|---|---|
| Commander | Designs the architecture (outside the chain), sets intent, holds final authority, runs the live smoke test | — |
| Project Leader | Turns intent into a project plan, owns the foundation, gates IT managers | Commander (live smoke test) |
| IT Manager | Writes slice-level work orders, runs the Parrot Protocol with workers, gates worker output | Project Leader |
| Worker | Builds one slice at a time | IT Manager |

Every link in the chain uses the Parrot Protocol (Section 8). Approvals flow down and are recorded by project leaders in the work orders. Proposals and escalations flow up.

**Authority follows the chain; communication doesn't silo.** Orders, approvals, gating, and sign-offs move one level at a time and are recorded. Conversation is free among managers: the Commander, project leaders, and IT managers may all talk to each other directly whenever it helps, and the Commander may bypass a project leader to talk to an IT manager when needed. The rule that holds it together: anything decided in a side conversation that changes a work order is written into that work order under `authorized_by`, and the project leader is told, because the project leader owns the record. Workers are not managers; a worker can talk to its IT manager and the architecture advisor, nothing else, and its work reaches the chain through that IT manager's gate.

Projects may run more than one IT manager with different roles (for example, one owning the bulk of the coding and one owning bug hunting). The routing between them is flexible, but before work reaches the Commander it has passed the coding gate, then the bug-hunting gate on the final code, then the project leader's gate, and every gate's result is in the work order.

### 4.1 The Design Space (outside the chain)

The Commander designs intent and architecture **before** anything is handed to a project leader, on a planning platform of the Commander's choice. That platform may be a planning workspace, a chat interface, one or more **architecture advisor agents**, or any combination. The chain doesn't care which; it receives the finished artifacts (intent, `ARCHITECTURE.md`, initial ADRs) and executes.

When an architecture advisor is run as an actual agent, it holds an **advisory role only** and sits beside the chain, not in it:

| Property | Rule |
|---|---|
| Authority | None. It answers questions and drafts for the Commander. It issues no orders, approves no work, and changes no design. |
| Repo access | **Read-only.** It never writes to the repo. Anything it drafts reaches the repo only through the Commander. |
| Tools | Read-only and web search only. No write tools, no shell, no code execution. This is the prompt-injection guard: an advisor that reads untrusted web content must not be able to act on it. |
| Reachable by | The Commander (design and redesign), and any agent in the chain on an as-needed consult basis (Section 8.3). |
| Output status | Advice. A revision it suggests becomes a proposal that travels the full chain to the Commander. |

The preliminary design is never done with the project leader. After handoff, the Commander may iterate and redesign with the project leader, keeping the advisor current on every approved change (Section 7.1).

## 5. The Foundation

The foundation is set at design time for new projects and applied retroactively, module by module, to existing ones (Section 12). All five items live in the repo.

### 5.1 Architecture Document (`ARCHITECTURE.md`)

The standard every decision is weighed against. Every agent reads it first, before any task, no matter how small the slice.

- States what the system is, its major modules, how they connect, and the rules that must hold.
- Has a size budget (recommended: 1,500 words or fewer). Every agent reads it on every task, so bloat here eats the context the SOP exists to save.
- Any rule in it that can be turned into a script check must be (import contract, line cap, etc.). Written rules get ignored; failing checks don't.
- Designed by the Commander in the design space (Section 4.1). Maintained in the repo by the project leader. Changes require Commander approval and a decision record.

### 5.2 Module Registry (`modules.toml`)

The codebase's self-description. Scripts check the code against it on every run, so the code can't quietly drift away from the declared structure.

```toml
[project]
name = "example"
line_cap_soft = 300
line_cap_hard = 500

[modules.cache]
path = "src/example/cache"
owns = "KV save/restore and tiering"
does_not_own = "GGUF parsing, GPU placement"
depends_on = ["gguf_meta"]
public = ["save", "restore", "evict"]
card = "src/example/cache/AGENTS.md"

[modules.gguf_meta]
path = "src/example/gguf_meta"
owns = "GGUF header reading"
does_not_own = "anything that writes files"
depends_on = []
public = ["read_header", "attention_dims"]
card = "src/example/gguf_meta/AGENTS.md"
```

Rules:
- Every package folder (one that holds code; a folder of only test fixtures or data is not one) is in the registry and every registry entry points to a real folder. An unregistered package folder fails the check.
- **A module's name says what it does.** Anyone, human or agent, should be able to tell what a module is for from its name alone, without reading a line of code. Name it for its job, the way its `owns` line reads. A sub-module's registry name is its parent's name followed by its own (`cache`, `cache_tiering`, `cache_tiering_disk`); its folder is just its own name, inside its parent's folder. No generic names (`utils`, `misc`, `helpers`, `new`, `v2`), ticket numbers, or agent names.
- `public` is the module's whole interface. In a code module it lists every public function and class (public by the language's naming convention) and nothing else; a helper that isn't part of the interface is named as private. A command-line entry point (`main`) is exempt. The card's Public Interface and Depends On say the same as the registry.
- `depends_on` is the only allowed import direction. Import contracts (Section 9.2) are generated from it.
- The registry changes only through the Interface Change Protocol (Section 6.4). Workers never edit it, except to add the entry for a sub-module their IT manager permitted them to create (Section 5.5).

### 5.3 Module Cards and READMEs (`AGENTS.md` and `README.md` per module)

Each module folder carries its own `AGENTS.md`. Agent tooling reads the nearest `AGENTS.md` in the directory tree, so a worker dropped into a module gets that module's rules automatically. The card follows a fixed template (Appendix A). Each module folder, at every level, also carries a `README.md`: what the module does and how it works, in plain words, for humans and agents. The card is the rules; the README is the explanation. A parent's README names each of its sub-modules. Every agent reads both before working in a module.

Required sections: Purpose, Owns, Does Not Own, Public Interface, Depends On, Invariants, Test Locations, Known Gotchas.

The **Does Not Own** section matters most. It's what stops a worker from putting logic in the wrong place.

### 5.4 Decision Records (`decisions/ADR-NNN.md`)

Short notes on *why* each major choice was made. They keep the architecture doc lean (it says what the rules are; ADRs say why) and stop agents from re-arguing settled decisions or "improving" something that was chosen deliberately.

Every pre-trip includes a scan of ADR titles. Any proposal that touches a settled decision must cite the ADR and explain why it should change.

Template in Appendix B.

### 5.5 Module Creation (who sets a module up)

A module exists when all of these are in place. Until they are, code in that folder is unregistered and fails the structure check.

| Step | Artifact | Responsible |
|---|---|---|
| 1 | Module boundary decided: what it owns, does not own, depends on, and exposes | Commander in the design space, **or the project leader** when the architecture doc doesn't name the module; the IT manager for a sub-module set up inside a slice |
| 2 | Registry entry in `modules.toml` | Project leader (for a sub-module set up inside a slice: the IT manager, or the worker with its permission, with the project leader notified) |
| 3 | Folder created at the registered path, with the package init file | Project leader (sub-module inside a slice: as step 2) |
| 4 | Module card `AGENTS.md` (Appendix A, all required sections filled) and `README.md`, in that folder | Project leader (sub-module inside a slice: as step 2) |
| 5 | ADR recording the boundary decision, if it is a new boundary or changes an existing one | Project leader (Commander approves) |
| 6 | Import contracts regenerated from `depends_on` | Script, run by the project leader (sub-module inside a slice: as step 2) |
| 7 | Contract test file stub at `tests/contract/test_<module>_contract.py` | Project leader (sub-module inside a slice: as step 2); workers fill it in through work orders |
| 8 | `MODULE_MAP.md` regenerated | Script (sub-module inside a slice: as step 2) |

A sub-module set up inside a slice has every step except the ADR done in the same commit as that slice. Step 5 stays with the project leader, who is notified. See the rules below.

Rules:
- **Every new feature gets its own module, or a new module with a set of sub-modules when it has separable internal parts, or occasionally a sub-module of an existing module when it clearly belongs inside that module's boundary.** The default is a new module. A sub-module is a registered module in its own right (own registry entry, own folder under the parent's path, own card) whose `depends_on` includes the parent; it is not a loose folder inside the parent. Sub-modules nest: a sub-module can have sub-modules of its own, to any depth, each set up the same way, with its folder inside its parent's folder and `depends_on` including its direct parent. The modules form a folder tree that matches the registry.
- The Commander or the architecture doc may specify the modules and sub-modules for a feature. If either does, the project leader sets them up as specified. **If neither the Commander nor the architecture doc specifies them, defining and setting them up is the project leader's job**, not something to wait on. The project leader proposes the boundary (steps 1 and 5) to the Commander, and does steps 2 through 8 once it's approved. Workers never do any of this, except as allowed under **Sub-modules by workers** below.
- No work order is issued against a module until steps 2 through 4 exist. An IT manager that receives a chunk for an unregistered module sends it back. A slice that sets up a sub-module is issued against its registered parent, and the sub-module's setup lands in the same commit as that slice.
- **Sub-modules by IT managers.** An IT manager may create a sub-module, or a sub-module inside a sub-module to any depth, inside a module already in its chunk's scope, doing steps 2 through 4 and 6 through 8 itself, provided it notifies the project leader in the work order and its next report. The setup lands in the same commit as the slice that needs it. Nested sub-modules set up in one slice are set up parent first; each counts as registered for the next once its steps are done. A new top-level module is a request to the project leader; in scope and merely not set up, the project leader sets it up; out of scope or unspecified, the project leader escalates to the Commander.
- **Sub-modules by workers.** A worker may create a sub-module only inside an existing sub-module, never a top-level module and never a sub-module directly under one, and only with its IT manager's permission. The worker asks in its readback (Appendix D, Sub-Modules Needed), or, if the need shows up after the readback is approved, in a fresh readback round for that piece, and keeps building the parts of the slice that don't depend on it while it waits. The IT manager decides the boundary and writes the permission into the work order, naming the sub-module and its boundary; a general approval of the readback is not permission. The order's write-scope then includes `modules.toml`, the new folder, the new sub-module's contract test stub, the line in the parent's README that names the new sub-module, and the files the setup regenerates (the import contracts, `MODULE_MAP.md`, and the function index). The worker does steps 2 through 4 and 6 through 8 as part of the slice. The IT manager gates the new registry entry and card like code, reading the card's Does Not Own first because the worker's own work is measured against it, commits the setup in the same commit as the slice, and notifies the project leader. Only managers commit, so nothing a worker sets up lands without a manager's gate.
- **Keeping the card and README current.** When code in a module changes, its `README.md` is updated in the same commit, and so is its parent's if the change affects what the parent describes. The worker updates the README as part of the slice. The card is the fence the worker is measured against, so the worker proposes card changes in its handoff. The IT manager rules on changes to Purpose, Invariants, Test Locations, and Known Gotchas; a change to Owns, Does Not Own, Public Interface, or Depends On is a boundary or interface change and goes up as a proposal (Sections 5.5 and 6.4). One exception: setting up a sub-module moves part of the parent's Owns into it, and that move is part of the setup, not a separate boundary change. The IT manager records it on the parent's card and README in the same commit (for a worker-built sub-module, the worker proposes the wording in its handoff), and the project leader's ADR for the new boundary (step 5) covers it. The structure check (Section 9.1) makes sure the parent's README names the new sub-module; that the rest of it still matches the parent's Owns is checked by hand at the gate. Anything more than that move, including a change to what the parent and its sub-modules own together or to the parent's public interface, still goes up as a proposal. If code changed and the README didn't, the handoff carries a README waiver saying why. A waiver holds only when the change doesn't alter what the module does, owns, exposes, or how it's used; the IT manager bounces any other waiver, the same as a missing README, and treats a cosmetic README edit as no update. Section 9.8 fails loudly on a README left stale, and Section 9.1 on a missing README or a card that no longer matches.
- Existing projects: when a work order lands in an unconverted area, the conversion step in that order is the project leader creating the module per this table, before or alongside the slice.

### 5.6 Function Index (`.sop/function_index.json`, generated)

A machine-generated index of every public function and class: module, name, signature, docstring, file, and line. Regenerated by script on every gate run. Workers search it before writing anything new (Section 10.1). Never hand-edited.

### 5.7 Root Module Map (`MODULE_MAP.md`, generated)

One line per module, generated from the registry and module cards, so any agent can find the right slice without opening code. Never hand-edited.

## 6. Project Setup

Done once when a project starts. Adjustable at any time by the Commander together with the project leader.

### 6.1 Approval List (`APPROVALS.md`)

Defines who can approve what. Recommended starting point:

| Decision | IT Manager | Project Leader | Commander |
|---|---|---|---|
| Worker readback within the work order | ✔ | | |
| Reprompt after a minor strike (Section 11.1) | ✔ | | |
| Worker compaction after a major strike (Section 11.3) | ✔ | | |
| New top-level module inside an existing plan (a sub-module follows Section 5.5) | | ✔ | |
| Interface change | | ✔ | |
| Editing or removing an existing test | ✔ (own slice) | ✔ | |
| Scope change to an active work order | | | ✔ |
| Recon finding that becomes new work | | | ✔ |
| Architecture doc change / new ADR | | | ✔ |
| Worker reassignment after 3 strikes | ✔ | | |
| Architecture advisor consult (Section 8.3) | any level, as needed, logged | | |
| Sending a work order back to design | | ✔ | |
| Commit to a branch | ✔ | | |
| Merge to main | | ✔ | |
| Host, container, and deployment operations | ✔ (own sub-work-order) | ✔ | |
| Release / publish | | | ✔ |
| SOP change | | | ✔ |

**Commits and infrastructure.** Workers never commit. The coding IT manager commits to a branch after its gate; the project leader merges after its gate; nothing is released until the Commander's smoke test. Host, container, and deployment operations, and anything crossing container boundaries, are IT manager work or above, never worker work. The IT manager covers them with a numbered sub-work-order of its own, so its work is audited like a worker's.

### 6.2 Smoke Test Checklist (`SMOKE_TEST.md`)

What the Commander's final live test covers for this project. Scriptable parts are scripted and run by the project leader before handoff; the live run stays as the Commander's judgment call. Template in Appendix G.

### 6.3 Check-In Intervals

The Commander sets the project leader's scheduled check-in interval (Section 7.6) at project setup. Default: every 2 to 3 hours while work is out. Recorded in the project plan; adjustable by the Commander at any time.

IT managers set their own worker check interval per dispatch: 30 minutes by default, up to 2 hours only for a hard slice or a slow worker, judged by slice complexity and the worker's actual speed. Recorded in the work order. The other IT manager clocks are in Section 7.6.

### 6.4 Interface Change Protocol

A module's public interface (its `public` list in the registry) is a contract. Internals can change freely; interfaces can't.

1. The requesting agent files a proposal up the chain with the reason, the new interface, and every dependent module affected.
2. The project leader approves or denies and records it in the work order.
3. On approval: the registry and module card are updated, contract tests are updated, and a work order is issued for every dependent module that must adapt.
4. No interface change ships without every dependent module's contract tests passing.

## 7. The Cycles

### 7.1 Commander Cycle

1. **Design.** Work out the intent and the architecture on the planning platform of choice, with architecture advisors as needed (Section 4.1). This step is never done with the project leader.
2. **Set intent.** Hand the project leader the mission, priorities, constraints, `ARCHITECTURE.md`, and any initial ADRs.
3. **Approve the foundation** and the project setup items (approval list, smoke test checklist).
4. **Confirm the readback.** The project leader parrots the intent back as a plan. Approve or correct it before any work orders go out.
5. **Rule on proposals.** Approve or deny recon findings, scope changes, and advisor-flagged revisions coming up the chain. Approvals are given to the project leader, who records them in the work orders.
6. **Redesign as needed.** Execution surfaces what design didn't see. Iterate with the project leader, keep the architecture advisor current on every approved change so its consult answers don't go stale, and land every revision as an updated `ARCHITECTURE.md` plus an ADR.
7. **Handle escalations.** Serious bugs, disputes, and anything that hit a strike cap.
8. **Run the live smoke test** on completed work. Pass means publish. Fail means nothing publishes and a bounce-back report goes to the project leader, then down the chain like any other error.
9. **Tune the SOP.** Review what keeps failing and update the rules. Bump the version.

### 7.2 Project Leader Cycle

1. **Pre-trip** (Section 7.5).
2. **Plan.** Receive the intent and `ARCHITECTURE.md` from the Commander's design space. Turn them into a project plan that matches the architecture doc. Parrot it back and get approval. Consult the architecture advisor when something in the codebase doesn't fit the design (Section 8.3), and take any needed revision to the Commander as a proposal.
3. **Record approvals.** Every Commander approval is written into the relevant work order under `authorized_by`.
4. **Own the foundation.** Keep the architecture doc, registry, module cards, and decision records current. Own all interface changes.
5. **Gate IT managers.** Review their reports up, confirm slices from different workers integrate (cross-module integration tests), and bounce back anything that doesn't.
6. **Run the scripted smoke tests.** Hand completed work to the Commander for the live run with a summary of open issues and proposals.
7. **Log to memory.** Errors, fixes, and decisions.

### 7.3 IT Manager Cycle

1. **Pre-trip** (Section 7.5).
2. **Write work orders.** Split the plan into slices, one module per order, with write-scope and acceptance criteria that match the architecture doc. Template in Appendix C.
3. **Run the Parrot Protocol down.** Approve or correct worker readbacks. Send out-of-scope recon findings up as proposals.
4. **Gate the work** (Section 10.4): automated checks first, then compare against the approved readback, bug sweep, unification check, and independent break tests. Send bounce-back reports until every touched test passes normally and fails loudly when broken.
5. **Correct, compact, and reassign workers.** Classify each failed submission as minor or major (Section 11.1). Minor gets a reprompt; major gets a compaction. Three strikes on one work order and the order is reassigned to a different worker. IT managers choose which worker gets each order; project leaders never bypass the chain to assign workers directly. Escalate to the project leader only when the order itself is the problem.
6. **Report up** to the project leader. Log errors and fixes to memory.

### 7.4 Worker Cycle

1. **Receive the work order** and read it fully.
2. **Pre-trip and recon** (Section 7.5). Name what was found.
3. **Parrot back** the plan and findings in the fixed format. Wait for approval. No approved readback, no work.
4. **Build.** Stay in the slice. Search the function index before writing. Unify instead of duplicating. Write unit, contract, and integration tests.
5. **Prove it.** All tests pass. Collateral breaks are justified. New or touched tests are shown to fail loudly through mutation testing and the worker's own break tests.
6. **Hand off** with the fixed report (Appendix E).
7. **Fix bounce-backs** until signed off.

### 7.5 Pre-Trip Check (all levels)

Every agent at every level completes a pre-trip before starting a task. The pre-trip goes into the readback (workers, IT managers) or the plan (project leaders). It must **name what was found**, not just claim a check was done.

| Check | What to record |
|---|---|
| Memory | Which entries were read: past decisions, past bugs in this module, prior work orders on this area |
| Skills | Which skills apply to this task, by name |
| MCP servers / tools | Which connected tools could help, by name, and which will be used |
| Project docs | Confirmation the architecture doc, module map, assigned module card and its README, and relevant ADRs were read |
| Recon (workers) | What was found in the module: existing functions to reuse, surprises, anything outside the order |

A pre-trip that says "checked memory: yes" with nothing specific is a failed pre-trip. With the dashboard, the pre-trip is verified against tool logs. Without it, the named-evidence rule plus manager spot checks stand in.

### 7.6 Scheduled Check-In (project leaders and IT managers)

Projects outlast sessions. Agents get compacted or reset several times before a project is done, and an agent that forgets to send a message can stall a whole chain. The check-in is the guard against both. Two levels run it, on different clocks.

| Level | Interval | Re-orients from | Sweeps |
|---|---|---|---|
| Project leader | Every 2 to 3 hours while any chunk is out. Set by the Commander at project setup. Repeats until all work is signed off, or indefinitely for ongoing projects. | Plan file, `ARCHITECTURE.md`, goal statement, every active work order | Every IT manager with a chunk out |
| IT manager | Four clocks while any worker is dispatched (below). The worker check is 30 minutes by default, up to 2 hours only for a hard slice or a slow worker, set per dispatch. | The active work orders themselves. IT managers keep less in a plan file and more in the work orders, so the work orders are the to-do list. | Every worker it has out |

- **Trigger.** A scheduled job, recurring task, cron entry, or a manual trigger from the level above or the dashboard. If an agent can't schedule itself, the level above triggers it.
- **Re-orient.** Reread the files in the table. All of them, not the remembered ones; after a compaction, memory of having read them is not evidence of having read them. Compactions also happen naturally as contexts fill, at every level, and an agent doesn't always know it happened, so re-orientation is unconditional: on every trigger, and on any sign of a gap between triggers.
- **Update the record.** Bring the plan file (project leader) and the work orders (both levels) in line with reality before anything else, so the next context starts from the truth.
- **Sweep.** Request an update from every agent below with work out. The project leader's sweep reaches IT managers; each IT manager's sweep reaches its workers. The request travels down to the lowest active agent; answers come back up the same route. No update depends on anyone remembering to send one.
- **Reply instructions.** Every update request states how to reply: channel, format, command or tool. Agents lose their reply path across compactions even when they have a skill for it. The reminder is one line and is written as a nudge, not a correction.
- **Act.** Strikes, proposals, escalations, and stalled agents surfaced by the sweep are handled per the normal cycle and Section 11.
- **Report up.** An IT manager reports the sweep result to the project leader at the project leader's next check-in, or sooner if something needs a ruling. The project leader sends the Commander a TLDR only if something changed or a decision is needed. Otherwise the updated files are the record.

IT managers run four clocks while workers are out, each watching something different: a **read-back watch** (about 4 min) armed in the same action as dispatch, silent unless the worker spoke last, retired once the read-back is approved; a **live-state check** (about 2 min) using screen peek or your setup's equivalent, the only instrument that sees a worker parked at an interactive prompt or sitting on an unsubmitted message; the **worker check** (30 min default, 2 h ceiling for a hard slice or slow worker, never the starting point); and a **work-order re-read** (about 2 h) that cross-checks what the orders claim against the actual repo. Clocks fire on odd minutes, offset from each other, and are written to a restore file so they survive a memory wipe. The restore file is for recovery, not authority: check what's actually armed before recreating anything. No work out means no clocks armed. Project leaders may screen-peek IT managers but normally don't need to; the open channel to the Commander covers it.

Workers don't run a check-in. They are the ones being checked on. Their part is to answer the sweep in the format the request specifies.

## 8. Communication Protocol

### 8.1 Parrot Protocol

A radio readback. The sender gives the order, the receiver reads back its understanding, and nothing moves until the readback matches. Runs on every link: Commander → project leader, project leader → IT manager, IT manager → worker.

Rules:
1. **Fixed format.** Readbacks use the template in Appendix D so they can be compared line by line.
2. **Three-round cap.** If a readback hasn't matched after three rounds, the problem is usually the order, not the receiver. It escalates one level, or the order goes back to design.
3. **Recon findings never expand the current order.** Anything new becomes a separate proposal that goes up the chain. The current order stays exactly as approved.
4. **Proposals travel the full chain.** A worker's finding goes worker → IT manager → project leader → Commander, and the ruling comes back the same route. Each hop is recorded.
5. **The approved readback is the contract.** At gate time, work is compared against the approved readback, not just the original order.

### 8.2 Message Formats

All messages are files or sections of the work order file:

| Message | Direction | Template |
|---|---|---|
| Intent | Commander → PL | Appendix C (intent block) |
| Plan | PL → Commander | Appendix D |
| Work order | IT manager → worker | Appendix C |
| Readback | Any receiver → sender | Appendix D |
| Handoff report | Worker → IT manager | Appendix E |
| Bounce-back report | Any gate → the level below | Appendix F |
| Report up | Any level → the level above | Appendix E (summary block) |
| Proposal | Any level → the level above | Appendix D (proposal block) |

### 8.3 Architecture Advisor Consults

The Commander designs the architecture outside the chain, on a planning platform of choice, often with one or more architecture advisor agents. Those advisors sit outside the chain of command and run read-only with web search only (Section 4.1).

Any agent at any level may consult the architecture advisor **as needed** to check whether something it discovered in the codebase matches the architectural design intent. Rules:

1. The advisor answers questions. It never issues orders, approves work, or changes the design.
2. An advisor answer that implies a design revision is a **proposal**, and it travels the full chain to the Commander before anything changes.
3. Every consult is recorded in the work order file: question, answer, and what the agent did with it.
4. The Commander keeps the advisor current on every approved architecture change so its answers don't go stale.
5. Consults are as-needed, not routine. An agent that consults the advisor on every step is padding its context; the architecture doc and module card should answer most questions.

### 8.4 Work Order File

Everything about a piece of work lives in one file: `workorders/WO-NNN.md`. It carries a `status` field and grows as the work moves: order, readback rounds, approvals, handoff report, bounce-backs, sign-off. This is how the system runs without the dashboard, and it's the audit trail with it.

Status values: `draft`, `awaiting_readback`, `approved`, `in_progress`, `submitted`, `bounced`, `compacted`, `signed_off`, `escalated`, `reassigned`, `parked`, `closed`.

`parked` means deliberately left open. It requires a written reason in the work order. No sweep closes a parked order, and no agent closes another agent's order on a timer's say-so; a timer firing is not a decision.

## 9. Automated Checks

These run on every worker submission, before any manager spends context on it. All of them are deterministic. A failure returns the exact output to the worker. The scripts write their results into the work order themselves, with a hash of the exact code they ran against; a worker's own claim of green is never a substitute.

### 9.1 Structure Checks (`sop check`)

- Every package folder is in `modules.toml`; every registry entry points to a real folder.
- Every module, at every level, has an `AGENTS.md` with all required sections.
- Every module, at every level, has a `README.md`, and a parent's README names each of its sub-modules.
- Every sub-module sits inside its parent's folder, and its `depends_on` names that direct parent.
- Each card's Public Interface and Depends On match the registry, and a code module's `public` list matches its real public functions.
- A module marked `docs_pending` (Section 12.2) is exempt from the README bullet and the card-match bullet above until the mark comes off.
- No file exceeds `line_cap_hard`. Files over `line_cap_soft` produce a warning that must be acknowledged in the handoff.
- `MODULE_MAP.md` and the function index are regenerated and match the code.

### 9.2 Import Contracts

Generated from `depends_on` in the registry and enforced by the language's import-boundary tool. For Python, Import Linter: a `forbidden` or `layers` contract per module so a worker who imports something the registry doesn't allow breaks the build. Other languages plug in their equivalent (dependency-cruiser for JS/TS, ArchUnit for Java, etc.); the SOP only requires that one exists.

### 9.3 Write-Scope Check

A diff check against the work order's `write_scope`. Any changed file outside the scope fails the gate. Test files inside the module's declared test locations are always in scope, and so is the module's `README.md`.

### 9.4 Duplicate Detection

Three levels, two of them fully scripted:

| Level | What it catches | How |
|---|---|---|
| Copy-paste and near-copies | Repeated blocks | jscpd (cross-language) or pylint `duplicate-code`; fail above the configured threshold |
| Renamed copies | Same logic, different names | Script parses each function, strips identifiers, hashes the shape; matching hashes are flagged |
| Same purpose, different code | Logic that does the same job | Script narrows candidates from the function index by name/signature/docstring similarity; the unification review (Section 10.3) makes the call |

### 9.5 Test Run

Full test suite. All tests pass or the submission fails. Any test outside the worker's slice that changed from pass to fail is a **collateral break** and must appear in the handoff report with a justification.

### 9.6 Mutation Testing

Run on only the files the worker touched, so it stays fast. For Python, mutmut targeting the changed modules. Every mutant that survives (a deliberate break that no test caught) is reported to the worker. The gate fails if any survivor is in code the work order added or changed.

Mutation runs with a timeout. Each module card may declare an accepted class of equivalent mutants (for example, async or I/O paths where mutants can't be killed); survivors in a declared class need no further justification, and anything outside it does.

### 9.7 Test Integrity Check

A diff check on test files. Any existing test that was edited, weakened, skipped, or deleted fails the gate unless the work order file contains an approval for that exact change.

### 9.8 Docs-Current Check

A diff check against the commit the work order started from: every module whose code changed must also have its `README.md` changed, unless the handoff carries a README waiver for it (Appendix E). It runs with the tests, so a worker sees it fail before handing off, rereads the module's card and README, and fixes the README or explains why it needs no change. A module marked `docs_pending` (Section 12.2) is skipped.

## 10. Build Rules

### 10.1 Reuse Before Write

Before writing any new function, the worker searches the function index. The handoff report records the search: what was searched, the closest match, and whether it was reused or why not. A handoff with no search recorded is bounced.

### 10.2 Code Unification

When new logic is similar to existing logic, reuse the existing code and branch at the input and the output as needed (adapter pattern). Do not copy and modify.

Limits:
- Unify only when the pieces really are the same logic, not code that merely looks similar.
- A shared function may carry at most two mode flags. Past that, split it into a shared core with thin wrappers per use. This stops the unified function from becoming the next giant file.
- The `common`/`shared` module has its own card and its own line caps. It is not a junk drawer. Anything that only one module uses belongs in that module.

### 10.3 Unification Review

The IT manager's judgment pass on the duplicate candidates the scripts flagged at Section 9.4 level three. Outcomes: "same logic, unify" (bounce with instructions), "different logic, keep both" (recorded so the same pair isn't re-flagged), or "unify later" (a new proposal up the chain).

### 10.4 Split Rules (both directions)

- **Too big:** any file over `line_cap_hard` must be split before sign-off. Split along the module's own responsibilities, not by line count.
- **Too small:** do not create a module unless it has a real interface worth hiding. A folder with one 40-line file and no interface is not a module. Prefer deep modules (lots of implementation behind a small interface) over many shallow ones, because every extra file costs an agent a tool call.

### 10.5 Tests

Three tiers, all required where they apply:

| Tier | Lives in | Proves |
|---|---|---|
| Unit | Inside the module | The module's internals work |
| Contract | At the module's interface | The public interface behaves as the card says |
| Integration | Cross-module test folder | Modules work together |

Rules:
- Tests target the interface, not the internals, wherever possible. Tests that reach into internals break on every reorganization and bury real failures under refactor noise.
- Failure messages name the module and point to its card, so a worker seeing a red test knows where to look.
- Every new or touched test must be shown to fail loudly: the worker breaks the code deliberately, confirms the test catches it, and restores the code. Mutation testing (Section 9.6) backs this up automatically.
- Tests are never weakened, skipped, or edited to get a pass without an approval recorded in the work order.

### 10.6 Manager Gate (judgment layer)

Runs only after every automated check passes.

1. Compare the delivered work to the approved readback, line by line.
2. Bug sweep on the touched code.
3. Unification review (Section 10.3).
4. Independent break tests: the manager breaks the worker's code in ways the worker didn't try and confirms the tests catch it. Managers hold the bigger picture, so this often surfaces a collateral break the worker's report missed.
5. If anything fails: bounce-back report (Appendix F). If everything passes: sign-off recorded in the work order.

## 11. Error Protocol

### 11.1 Three Strikes

Every failed submission is a strike against the current agent on the current work order. The manager classifies the failure before responding, and the classification decides the response:

| Class | What it looks like | Response | Counts as |
|---|---|---|---|
| **Minor** | One specific, contained issue: a single failing check, a missed acceptance criterion, a naming slip, a test that passes but doesn't fail loudly, an unrecorded function index search, an incomplete handoff section. The rest of the submission is sound. | **Reprompt.** The manager sends the exact failure output and the required action. The agent fixes it inside its slice with its current context intact. | One strike |
| **Major** | Wholesale buggy: fails broadly across the automated checks, fails the manager gate on multiple independent issues, or shows the agent has lost the thread of the order. **Or** any always-major item below. | **Compaction** (Section 11.3). The agent's context is reset to essentials and it starts again from pre-trip, memory check included. No patching. | One strike |
| **Third strike** | The agent's third strike on this work order, any mix. | **Reassignment** to a different agent: fresh context, same order and readback, count back to zero. Replaces the reprompt or compaction the third strike would otherwise get. | — |

**Always major**, one occurrence is enough: code written before readback approval; any file touched outside write-scope; logic in a module whose card says it doesn't own it; any test edited, skipped, deleted, or loosened without recorded approval (including editing a test to "fix" a collateral break); any edit to `modules.toml`, an `AGENTS.md`, `ARCHITECTURE.md`, or `decisions/` by an agent not authorized for it; a module or sub-module created by an agent not authorized to create it.

A compaction that happens naturally because a context filled is not a strike.

Rules:

1. **Three strikes on one work order**, in any mix of minor and major, and the manager stops working with that agent on that order. For workers, the IT manager **reassigns the order to a different worker** (fresh context, same order and readback). For IT managers and project leaders, the level above takes the same decision.
2. Strikes are per agent per work order. A reassigned worker starts at zero.
3. If the strikes point at the **order** rather than the agent (readbacks keep failing on the same point, or two different workers fail the same slice), that's a design problem. It escalates one level, and the order goes back to design. Don't burn a third worker on a bad order.
4. Every strike, its class, the response, and the outcome are recorded in the work order file's Strike Log and logged to memory.

When in doubt between minor and major, treat it as major. A reprompt into a bad context makes the context worse; a compaction into a good one costs a pre-trip.

### 11.2 Collateral Breaks

- Any test outside the slice that the work broke must be justified to the manager in the handoff report.
- The fix is never "change the other test." Editing another module's test requires an approval recorded in the work order (Section 9.7).
- If a collateral break shows the work order was wrong, it goes up as a proposal, and the order is revised before work continues.

### 11.3 Worker Compaction Cycle

The major-mistake response. A worker whose submission is wholesale buggy is not sent back to keep patching. Its context has usually gone bad, and patching a bad context makes it worse.

1. The IT manager orders a **compaction**: the worker's context is compressed or reset to the essentials only, meaning the work order, the approved readback, the module card, the architecture doc, and the bounce-back report. Accumulated conversation is dropped.
2. The worker re-runs its pre-trip from the compacted state, parrots back again, and resubmits.
3. The compaction counts as one strike under Section 11.1. Three strikes, in any mix of reprompts and compactions, and the IT manager reassigns the order to a different worker. IT managers know their workers, so the choice of worker is theirs; project leaders never bypass the chain to assign workers directly.
4. If the failures point at the order itself rather than the worker, the IT manager escalates to the project leader, who sends the order back to design.
5. Every compaction, reassignment, and reason is recorded in the work order file and logged to memory. If the same slice fails across two different workers, that's a design problem, not a worker problem: the IT manager escalates to the project leader, who takes it to the Commander.

### 11.4 Repeat Breaks

Code that breaks repeatedly gets both a bug hunt and a unification review. Repeat bugs usually mean duplicated or tangled code, not bad luck.

### 11.5 Memory Logging

Every error, its cause, and its fix is logged to memory, keyed to the module, so the next agent's pre-trip catches it. Managers verify the log entry exists before closing the work order.

### 11.6 Escalation Path

Worker → IT manager → project leader → Commander. Serious issues (data loss risk, security, anything that breaks the smoke test) go to the Commander directly through the project leader without waiting for caps.

### 11.7 Failed Smoke Test

Nothing publishes. The Commander sends a bounce-back report to the project leader, who traces it to the responsible work orders and reopens them. The fix flows through the normal cycle, and the smoke test runs again from the top.

## 12. Rollout

### 12.1 New Projects

Start from the template repo, which ships with: `ARCHITECTURE.md` (skeleton), `modules.toml` (empty), `APPROVALS.md` (default table), `SMOKE_TEST.md` (template), `decisions/`, `workorders/`, `.sop/` check scripts, CI configuration that runs the gate, and this SOP.

Project setup (Section 6) is the first work order.

### 12.2 Existing Projects

Converted **on touch, never big-bang**. When a work order touches a file in an unconverted area:

1. The work order includes a conversion step: register the module, write its card and its README, and split the file if it's over the hard cap.
2. Conversion and the feature work are separate readback items so they can be gated separately.
3. Until a module is converted, its files are exempt from the line cap but still subject to every other check.
4. When a project adopts this version, the project leader marks every module registered before READMEs were required `docs_pending = true` in the registry, in one pass. The README, card-match, and docs-current checks skip a marked module until a work order touches it. That order's conversion step has the worker write the README and propose card and `public` changes as usual; the IT manager applies the approved card and registry changes and removes the mark in the same commit as the slice. Recording an interface that already exists is not an interface change; anything that would change it goes up as a proposal. No big-bang: the marks come off one module at a time, with the work.

A stable production system stays stable. Conversion follows the work; it doesn't lead it.

### 12.3 Dashboard Integration

The command dashboard automates the SOP but never replaces the files:

- Pushes memory, skill lists, tool lists, and project docs into agent context at task start (push instead of pull).
- Routes readbacks and proposals along the chain and holds approvals.
- Verifies pre-trips against tool logs: a claimed memory check with no memory read in the log fails the gate.
- Runs the automated checks and posts results into the work order file.
- Tracks strikes per agent per work order and triggers reassignment or escalation automatically.

Without the dashboard: agents read and write the work order files directly, the check scripts run from the command line or CI, and pre-trip verification falls back to named evidence plus manager spot checks. The SOP states this gap rather than pretending it doesn't exist.

## 13. Glossary

| Term | Meaning |
|---|---|
| Pre-trip | The mandatory check of memory, skills, tools, and docs before any task |
| Parrot Protocol | Readback confirmation on every link of the chain |
| Readback | The receiver's restatement of an order, in fixed format, awaiting approval |
| Work order | The file that holds one slice of work from order to sign-off |
| Write-scope | The set of files a worker is allowed to change |
| Module card | The `AGENTS.md` in a module folder |
| Module README | The `README.md` in a module folder: what the module does and how it works, in plain words |
| Sub-module | A registered module inside another module's folder, set up the same way; sub-modules nest to any depth |
| `docs_pending` | A registry mark on a module registered before READMEs were required; the README and card checks skip it until a work order converts it |
| Contract test | A test at a module's public interface |
| Collateral break | A test outside the slice that the work caused to fail |
| Mutation testing | Automated deliberate code breaking to prove tests catch it |
| Break test | A worker's or manager's manual version of the same thing |
| Bounce-back | A gate failure returned to the level below with exact findings |
| TLDR | Short, plain-language summary written for the human Commander, leading with whether a decision is needed; the full record stays in the work orders |
| Check-in | The scheduled re-orientation and update sweep run on a timer while work is out: project leaders every 2–3 h; IT managers on four clocks (read-back watch, live-state check, worker check at 30 min default / 2 h ceiling, work-order re-read) |
| Compaction | Resetting an agent's context to essentials. Ordered by the manager after a major (wholesale-buggy) submission, and counted as a strike; also happens naturally when a context fills, which is normal, expected, and not a strike. Agents don't always know they were compacted, so every level re-orients from the record on any sign of a gap |
| Reprompt | Sending a worker the exact failure and required fix after a minor mistake, context intact |
| Strike | One failed submission by one agent on one work order; three and the order is reassigned |
| Design space | Where the Commander designs intent and architecture, outside the chain, on a platform of choice |
| Architecture advisor | A read-only, web-search-only agent the Commander designs with; consultable by the chain, advisory only |
| Unification | Reusing existing logic and branching at input/output instead of duplicating |
| Deep module | Lots of implementation behind a small interface |

---

# Appendices: Templates

## Appendix A: Module Card (`AGENTS.md`)

```markdown
# Module: <name>

## Purpose
One or two sentences on what this module is for.

## Owns
- <responsibility>
- <responsibility>

## Does Not Own
- <thing that belongs elsewhere, and where it belongs>

## Public Interface
- `function_name(args) -> return`: one line on what it does
- `ClassName`: one line

## Depends On
- <module> (why)

## Invariants
- <something that must always be true>

## Test Locations
- Unit: `tests/unit/<module>/`
- Contract: `tests/contract/test_<module>_contract.py`

## Known Gotchas
- <thing that has bitten agents before, with ADR or WO reference>
```

## Appendix B: Decision Record (`decisions/ADR-NNN.md`)

```markdown
# ADR-NNN: <title>

**Status:** proposed | accepted | superseded by ADR-MMM
**Date:** YYYY-MM-DD
**Approved by:** Commander (WO-NNN)

## Context
What situation forced a decision.

## Decision
What was chosen.

## Reasons
Why, in plain terms.

## Consequences
What this rules in and rules out going forward.
```

## Appendix C: Work Order (`workorders/WO-NNN.md`)

```markdown
# WO-NNN: <title>

**Status:** draft
**Issued by:** <IT manager>
**Assigned to:** <worker>
**Authorized by:** <project leader / Commander, with date>
**Project plan reference:** <plan section or WO-NNN>
**Check-in interval:** <30 min default; up to 2 h only for a hard slice or slow worker (Section 7.6)>
**Reply path:** <how the worker reports back: channel / format / command>

## Intent (Commander, if applicable)
Verbatim or summarized Commander intent this order serves.

## Task
What to build or fix, in plain terms.

## Module
<module name from modules.toml>

## Write-Scope
- `src/<module>/`
- `tests/unit/<module>/`
- `tests/contract/test_<module>_contract.py`

## Acceptance Criteria
- [ ] <criterion>
- [ ] <criterion>
- [ ] All tests pass; new/touched tests proven to fail loudly
- [ ] No survivors in mutation testing on changed code
- [ ] Function index searched before any new function

## Constraints
- Architecture doc sections that apply
- ADRs that apply

## Conversion Step (existing projects only)
Register module / write card and README / split file, if required.

---
## Readback Rounds
(appended by worker and manager, Appendix D format)

## Advisor Consults
| # | Asked by | Question | Advisor answer | Action taken |
|---|---|---|---|---|

## Approvals
(appended, with who and when)

## Handoff Report
(appended by worker, Appendix E format)

## Bounce-Backs
(appended by manager, Appendix F format)

## Strike Log
| # | Class (minor/major) | Response (reprompt/compaction) | Reason | Outcome |
|---|---|---|---|---|

## Sign-Off
Signed by: <IT manager>, <date>
```

## Appendix D: Readback

```markdown
## Readback — Round N
**From:** <agent>
**To:** <agent>

### Understood Task
My restatement of what I'm being asked to do.

### Planned Files
- <file> (new / modify)

### Planned Tests
- <test> proves <what>

### Sub-Modules Needed
None | <name> inside <parent>: owns <what>, does not own <what> (a worker may ask only for a sub-module inside an existing sub-module, never a top-level module or one directly under it)

### Pre-Trip Findings
- Memory: <named entries>
- Skills: <named skills>
- Tools/MCP: <named tools>
- Docs read: architecture doc, module card <name> and its README, ADR-NNN

### Recon Findings
- Reusable: <function from index>
- Surprises: <anything unexpected>

### Proposals (outside this order)
- <finding> → requesting ruling

### Open Questions
- <question>

---
**Manager ruling:** approved | corrected (see below) | escalated
```

## Appendix E: Handoff Report

```markdown
## Handoff Report
**Worker:** <agent>
**WO:** WO-NNN
**Against readback round:** N

### Files Touched
- <file>: <what changed>

### Interface Changes
None | <change, with approval reference>

### README and Card
- README: updated | README waiver: <module>: <why no change is needed>
- Card changes proposed: none | <change>
- Sub-modules set up: none | <name>, permitted in this work order
- Parent Owns moved: none | <parent> to <sub-module>: <proposed wording for the parent's card and README>

### Function Index Search
- Searched: <terms>
- Closest match: <function> in <module>
- Reused: yes | no, because <reason>

### Tests Added / Touched
- <test>: <what it proves>

### Proof of Loud Failure
- <test>: broke <code> by <method>, test failed with <message>, restored

### Mutation Results
Survivors on changed code: 0 | <list, with justification>

### Collateral Breaks
None | <test>: <justification>

### Line Cap Warnings
None | <file> at <n> lines, <plan>

### Memory Log Entry
<key> written: yes
```

## Appendix F: Bounce-Back Report

```markdown
## Bounce-Back
**From:** <gate level>
**To:** <agent>
**WO:** WO-NNN
**Type:** reprompt (minor) | compaction (major) | escalation

### What Failed
- <check or finding>, exact output:
  ```
  <output>
  ```

### Not in Your Report
- <collateral break or issue the worker missed>

### Required Action
- <specific instruction>

### Counts
Strike N/3 on this WO — Class: minor (reprompt) | major (compaction)
```

## Appendix G: Smoke Test Checklist (`SMOKE_TEST.md`)

```markdown
# Smoke Test — <project>

**Approved by:** Commander, <date>
**Last revised with:** <project leader>, <date>

## Scripted (run by project leader before handoff)
- [ ] Full test suite green
- [ ] Mutation run: no survivors on changed code
- [ ] Build from clean checkout succeeds
- [ ] <project-specific scripted check>

## Live (run by Commander)
- [ ] <core workflow 1 works end to end>
- [ ] <core workflow 2>
- [ ] <known-fragile area behaves>

## On Failure
Bounce-back to project leader → trace to WO(s) → reopen → rerun from top.
```
