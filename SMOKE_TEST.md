# Smoke Test: module-sop

**Approved by:** Commander (WO-001)

## Scripted (run by the project leader before handoff)
- [ ] `python3 tools/skill_lint.py` → RESULT PASS (standalone + verbatim anchors)
- [ ] `python3 tools/sop_check.py` → RESULT PASS
- [ ] `python3 -m unittest discover -s tests -t .` → OK, including the red-arm tests
- [ ] Mutation (manual, ADR-006): break one rule in `tools/`, watch its guard test fail, restore

## Live (run by the Commander, or the project leader on his word)
- [ ] One agent per class loads its `module-sop-<class>` skill and names its first checklist items back
- [ ] An installed copy refuses an edit (locked)

## On Failure
Bounce-back to the project leader → trace to the WO → reopen → rerun from the top.
