# docs: the Commander's SOP set

**What it does.** Holds the MODULE SOP set exactly as the Commander wrote or approved it: `MODULE_SOP.md` (the master rules every
class plays by) and one SOP per class, `COMMANDER_SOP.md`, `PROJECT_LEADER_SOP.md`, `IT_MANAGER_SOP.md`, `WORKER_SOP.md`.
It is the source of truth the class skills are written from.

**How it works.**
- Only the Commander changes these files, and every change bumps that SOP's `**Version:**` line.
- The five SOP files are the Commander's text, or an amendment he approved by merging it; nothing here is paraphrased or summarised.
- `AGENTS.md` in this folder is the module card, not an SOP.
- The skills gate (`tools/skill_lint.py`) checks each class skill's Quick Reference and One-Paragraph Version against these
  files word for word, so a change here is caught in the skills until they are updated to match.
- The same texts are posted, unchanged, to the shared document store's SOP folders for each class.
