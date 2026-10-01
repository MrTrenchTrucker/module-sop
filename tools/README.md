# tools: the gates

**What it does.** The scripts that decide whether this repo is in shape. They are deterministic and exit 1 on any failure.

**How it works.**
- `skill_lint.py --file <SKILL.md> --class <class>`: the standalone-skill gate. A class skill must not point at other
  documents or contain private identifiers (your agents' names, hosts, internal systems, private addresses and paths —
  your own names go one per line in `.sop/private_names.txt`, git-ignored; private addresses and host paths are flagged
  generically), must carry its SOP's Quick Reference and One-Paragraph Version word for word, and must pair
  with `parrot-protocol-<class>`.
- `sop_check.py [--write]`: the structure check. Every folder is registered, every sub-module sits in its parent's folder and
  depends on it, every card has its sections, files stay under the line caps, imports follow `depends_on`, and the generated
  `MODULE_MAP.md` and `.sop/function_index.json` are current (`--write` regenerates them). It also runs the static docs
  checks below.
- `doc_check.py [--base REF]`: the module docs checks.
  - Every module has a card and a README.
  - Each card matches the registry and the code.
  - Each parent README names its sub-modules.
  - A module whose code changed since the base changed its README too, unless a work order carries a
    `README waiver: <module>: <why>` line.
  - The same check runs in the test suite (`tests/contract/test_module_docs_current.py`), so whoever changes code sees it
    fail before handing off.
  - The base is the commit the work order started from. The default (the merge-base with main) is right for a branch that carries one work order. On a branch carrying several slices, set `SOP_BASE` to the commit each slice started from; otherwise a later slice rides on an earlier slice's README edit and the check passes when it shouldn't.
- `sections.py`: the one shared Markdown section reader the other scripts use. Headings match with trailing
  whitespace tolerated and need no preceding newline, so editor trimming never fails a gate.
- `sop_check.py` import contract also covers relative imports (`from . import x` names the sibling).

Every rule each script enforces has a test that plants the fault and watches it fail (`tests/unit/tools/`).
