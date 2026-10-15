---
name: subagent-plan-file
description: >-
  Use every time you hand work to a sub-agent (a helper agent you start and wait for). Each sub-agent gets one
  plan file: a read gate with exact quotes, a reading certificate signed before any change, work steps ticked
  with evidence, and a closing certificate. Only the sub-agent marks them. You check the plan file before you
  accept the work. Works with any model and any agent harness.
---

# Sub-Agent Plan File

## Terms Used in This Skill

| Term | Meaning |
|---|---|
| Sub-agent | A helper agent you start for one piece of work and wait for. |
| You | The agent that hands out the work and answers for the result. |
| Plan file | One plain text or markdown file per sub-agent: read gate, reading certificate, work steps, closing certificate, plan changes. |
| Read gate | The list of files and sections the sub-agent must read, each proven with an exact quote, before it changes anything. |
| Reading certificate | The sub-agent's signed statement, before its first change, that it read every read gate file in full. |
| Closing certificate | The sub-agent's last statement: that it read everything, skipped nothing, and what it did not do. |
| Plan changes | The one part of the plan file you may write in after the sub-agent starts: your dated changes to its plan. |
| Reviewer | Whoever checks your work after you hand it up. |

---

## What This Is

When you hand a piece of work to a sub-agent, it gets one plan file. The plan file makes the sub-agent read
what it must read before it changes anything, sign that it did, show its evidence as it goes, and say in
writing what it did not do. You check the plan file before you accept the work.

It costs tokens: sub-agents working this way spend more than sub-agents without a plan file. What it buys is
reading you can check. In a side-by-side trial on the same task, both runs passed the same gate, but the run
with plan files found a defect in a shared file that the other run skimmed past, asked all its questions up
front, and every quote it wrote down was real. Thoroughness is worth the extra tokens. Use a plan file for
every sub-agent, every time.

## One Plan File Per Sub-Agent

Write the plan file before the sub-agent starts. One sub-agent, one plan file, never shared. Keep it with your
work records, not in the code being changed, and hand it up with your delivery.

The plan file has four parts, in this order, and a plan changes section at the end.

### 1. Read Gate

You list every file and section the sub-agent must read for this task, by path and heading: the module's rules
file and README, the parts of the architecture the task touches, the decision records it touches, and the work
order. The sub-agent fills in each line before its first change:

```
[x] path#section | lines read N-M | quote: "<one exact line from that section>" | what it means for my task: <one sentence>
```

- No file is changed until every read gate line is ticked.
- The quote is copied, never paraphrased.
- If a section is too long to read in full, the sub-agent says so on that line. It never summarises from the
  heading.

### 2. Reading Certificate

When every read gate line is ticked, and before its first change, the sub-agent signs:

```
I have read in full, end to end, every file in my READ GATE: <list of paths>. I read them before changing any file.
```

Before the first change, you search two of its quotes word for word in the named files. One not found sends the
sub-agent back to reading. Where the sub-agent cannot be paused, split reading and changing into two runs.

### 3. Work Steps

You list the steps in order. The sub-agent ticks each one only after it is done, with its evidence on the same
line: the test that failed first and then passed, or the command it ran and its result. A step it could not do
is written down as not done, with the reason. Nothing is skipped silently.

### 4. Closing Certificate

The last lines of the sub-agent's part of the plan file, written by the sub-agent:

```
I read every READ GATE item in full. I skipped no step. Not done or not checked: <list, or 'none'>.
```

A "none" that turns out to be false counts as a skip.

### Plan Changes

If you change the sub-agent's plan after it starts, write the change here: the date, what changed and why. This
is the only part of the plan file you write in after the sub-agent starts.

## Only The Sub-Agent Marks Its Own Reading

Only the sub-agent ticks its read gate, writes its quotes, and signs its reading and closing certificates. You
never do it for the sub-agent, not even to rescue a plan after the sub-agent stopped early. Your mark proves
only that you believe the files were read; the point is that the sub-agent proves it read them.

- A tick, quote or signature written by you is void. The plan file fails your reviewer's check, even when the
  work is right.
- If a sub-agent stopped before its reading was done, start it again (or steer it) with: "Do your own READ GATE
  ticks and exact quotes, and sign your READ CERTIFICATE before you change any file."
- Your own changes go under Plan Changes, never in the read gate, the work steps or the certificates.

## Lines For The Sub-Agent's Instructions

Put these five lines, word for word, in every sub-agent's starting instructions:

- "Read your plan file first. Do the READ GATE and sign the READ CERTIFICATE before any other tool call that changes a file."
- "Quote, do not paraphrase. If a section is too long to read, say so in the plan file; do not summarise from the heading."
- "Tick a box only after the step is done. Write what you could not do instead of skipping it."
- "Only you tick your boxes, write your quotes and sign your certificates. Nobody else may do it for you."
- "End with the closing certificate. Your work is checked against it."

## Checking A Plan File Before You Accept The Work

1. Every box is ticked, or marked not done with a reason.
2. The marks are the sub-agent's own. Where your harness keeps a separate record for each agent, the read gate
   lines and both certificates show up in the sub-agent's record, not in yours. Nothing but Plan Changes was
   written by you.
3. Pick two quotes from the read gate. Search for each one in the named file with an exact text search. If
   one quote is not found word for word, the sub-agent goes back to reading and the work is not accepted.
4. Both certificates are there, the reading certificate signed before the first change.
5. The "not done" list goes into your own delivery notes, unchanged.
6. Record the tokens the sub-agent used and its wall time with your delivery.

Wait until every sub-agent has returned before you judge the work. If a sub-agent's work is wrong, start a
fresh sub-agent with the same plan file and what failed. Do not patch around a skipped read gate.

## What Your Reviewer Checks

A plan file for every sub-agent, both certificates read, the quotes spot-checked, and every tick, quote and
signature the sub-agent's own. A mark written by you, or a false "none" in a certificate, sends the work back
for the missing reading; the code is judged separately.

## Limits

- A plan file makes reading checkable. It does not make the result correct: in the same trial, a wrong line
  still got through in the run with plan files. Every gate still runs.
- Telling who wrote a line is only as good as the records your harness keeps. Where it keeps none, the quote
  check is the remaining proof.
- The plan file works with any model and any agent harness. Nothing in it depends on a named model or tool.

## Plan File Template

Copy this for each sub-agent and fill in the parts in angle brackets:

```
# Plan file: <task>, sub-agent <n>

## READ GATE (no file is changed until every line is ticked; only the sub-agent ticks)
[ ] <path>#<section> | lines read <N-M> | quote: "<exact line>" | what it means for my task: <one sentence>
[ ] <path>#<section> | lines read <N-M> | quote: "<exact line>" | what it means for my task: <one sentence>

## READ CERTIFICATE (signed by the sub-agent before its first change)
I have read in full, end to end, every file in my READ GATE: <list of paths>. I read them before changing any file.

## WORK STEPS (tick only when done; evidence on the same line)
[ ] 1. <step> | evidence: <test red then green, or command and result>
[ ] 2. <step> | evidence: <...>

## NOT DONE (with the reason)
- <step or check>: <why>

## CLOSING CERTIFICATE (signed by the sub-agent)
I read every READ GATE item in full. I skipped no step. Not done or not checked: <list, or 'none'>.

## PLAN CHANGES (the only part the agent who started the sub-agent writes in)
- <date>: <what changed and why>
```

---

## Quick Reference

Before a sub-agent starts:
- [ ] One plan file for this sub-agent, not shared
- [ ] Read gate lists every file and section by path and heading
- [ ] Work steps listed in order
- [ ] The five instruction lines are in its starting instructions, word for word

Before a sub-agent changes any file:
- [ ] Read gate filled in and reading certificate signed, both by the sub-agent
- [ ] Two quotes found word for word with an exact text search

Before you accept the work:
- [ ] Every box ticked, or marked not done with a reason
- [ ] Every tick, quote and signature is the sub-agent's own; yours are only under Plan Changes
- [ ] Two quotes found word for word with an exact text search
- [ ] Both certificates present and true
- [ ] "Not done" list carried into your delivery notes
- [ ] Tokens and wall time recorded
- [ ] Every sub-agent returned before you judge

## One-Paragraph Version

Every sub-agent you start gets its own plan file, written before it begins. The plan file has a read gate, a
reading certificate, work steps and a closing certificate. The read gate names every file and section the
sub-agent must read, and the sub-agent proves each one with an exact quote and one sentence on what it means
for the task, then signs the reading certificate, before it changes any file. You search two of those quotes
before its first change, and a quote you cannot find sends it back to reading. It ticks each work step only when
the step is done, with the evidence on the same line, and writes down what it could not do instead of skipping
it. It ends with a closing certificate saying it read everything, skipped nothing, and listing what it did not
do. Only the sub-agent marks its own reading: a tick, quote or signature written by you is void, and your own
changes go under Plan Changes. Before you accept the work, you check every box, check the marks are the
sub-agent's own, find two of its quotes word for word with an exact text search, read both certificates, and
carry its "not done" list into your delivery. A wrong quote, a mark that is not the sub-agent's, or a false
"none" sends it back. It costs more tokens and it is worth it; it makes reading checkable, it does not replace
the gates.
