import json, os, subprocess, sys, tempfile, textwrap, unittest
from tests.helpers import ROOT
from tests.unit.tools.module_status.gh_server import FakeGitHub
SCRIPT = os.environ.get("MS_SCRIPT") or os.path.join(ROOT, "tools", "module_status", "module_status.py")

def touch(root, rel, text="x"):
    p = os.path.join(root, rel); os.makedirs(os.path.dirname(p), exist_ok=True); open(p, "w").write(text)

def build():
    d = tempfile.mkdtemp()
    reg = ""
    def mod(key, path, extra=""):
        nonlocal reg
        reg += f'[module.{key}]\npath = "{path}"\nowns = "o"\ncard = "{path}/AGENTS.md"\n{extra}\n'
    mod("x", "m/x", 'expected_subs = ["one", "two", "three"]')
    mod("x_one", "m/x/one"); mod("x_two", "m/x/two")
    mod("y", "m/y", 'expected_subs = ["one"]'); mod("y_one", "m/y/one")
    mod("z", "m/z", 'expected_subs = ["one"]'); mod("z_one", "m/z/one")
    mod("w", "m/w", 'expected_subs = ["one"]'); mod("w_one", "m/w/one"); mod("w_two", "m/w/two"); mod("w_dead", "m/w/dead", 'status = "dead"')
    open(os.path.join(d, "modules.toml"), "w").write(reg)
    for k in ("x", "y", "z", "w"):
        touch(d, f"m/{k}/src/main/Own.kt"); touch(d, f"m/{k}/src/test/OwnTest.kt")
    for p in ("x/one", "y/one", "z/one", "w/one", "w/two", "w/dead"):
        touch(d, f"m/{p}/src/main/A.kt"); touch(d, f"m/{p}/src/test/ATest.kt")
    touch(d, "m/x/two/README.md")      # registered, no code: NOT_STARTED
    os.remove(os.path.join(d, "m/x/two/src/main/A.kt")) if os.path.exists(os.path.join(d, "m/x/two/src/main/A.kt")) else None
    return d

class T(unittest.TestCase):
    def run_script(self, issues):
        d = build(); out = os.path.join(d, "out")
        json.dump(issues, open(os.path.join(d, "iss.json"), "w"))
        open(os.path.join(d, "c.toml"), "w").write(textwrap.dedent(f"""
            repo = "{d}"
            out_dir = "{out}"
            issues_json = "{d}/iss.json"
            issue_title = "module: {{name}}"
        """))
        r = subprocess.run([sys.executable, SCRIPT, os.path.join(d, "c.toml")], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout

    def test_cases(self):
        out = self.run_script({"module: x": [1, "closed"], "module: y": [2, "open"], "module: z": [3, "closed"], "module: w": [4, "open"]})
        self.assertIn("CAUTION x: issue #1 is CLOSED but not everything is done", out)      # missing expected + closed
        self.assertIn("CAUTION y: everything built and tested, but issue #2 is still OPEN", out)
        self.assertNotIn("CAUTION z", out)                                                  # truly complete: quiet
        self.assertIn("| z | 2 | 2 | 0 | #3 closed | COMPLETE |", out)
        self.assertIn("NOTE w: sub-module w_two is registered but not in its expected list", out)   # new one auto counted
        self.assertIn("| w | 3 | 3 | 0 | #4 open | in progress |", out)                          # counted, 3 items
        self.assertIn("| x | 4 | 2 | 1 | #1 closed | in progress |", out)                        # 1 expected missing

    def test_plan_file_overrides_and_issue_number(self):
        d = build(); out = os.path.join(d, "out")
        json.dump({"module: zzz": [9, "closed"]}, open(os.path.join(d, "iss.json"), "w"))
        open(os.path.join(d, "PLAN.toml"), "w").write('[plan.y]\nexpected_subs = ["one", "two"]\nissue = 9\n')
        open(os.path.join(d, "c.toml"), "w").write(f'repo = "{d}"\nout_dir = "{out}"\nissues_json = "{d}/iss.json"\nplan_file = "PLAN.toml"\n')
        o = subprocess.run([sys.executable, SCRIPT, os.path.join(d, "c.toml")], capture_output=True, text=True).stdout
        self.assertIn("| y | 3 | 2 | 1 | #9 closed | in progress |", o)   # plan names 'two' (missing); issue found by number

    def test_tree_planned_module_and_unplanned_note(self):
        d = build(); out = os.path.join(d, "out")
        json.dump({"module: future": [9, "closed"]}, open(os.path.join(d, "iss.json"), "w"))
        open(os.path.join(d, "PLAN.toml"), "w").write('[plan.x]\nexpected_subs = ["one", "two"]\n[plan.y]\n[plan.w]\n[plan.future]\nexpected_subs = ["alpha"]\nissue = 9\n')
        open(os.path.join(d, "c.toml"), "w").write(f'repo = "{d}"\nout_dir = "{out}"\nissues_json = "{d}/iss.json"\nplan_file = "PLAN.toml"\n')
        o = subprocess.run([sys.executable, SCRIPT, os.path.join(d, "c.toml")], capture_output=True, text=True).stdout
        self.assertIn("- x_one: DONE (sub-module of x;", o)                    # sub-module listed under its parent
        self.assertIn("- x_two: NOT_STARTED (sub-module of x;", o)               # registered, no code
        self.assertIn("- future: NOT_STARTED (module; 0 code, 0 test; planned only, no folder yet)", o)
        self.assertIn("- alpha: NOT_STARTED (sub-module of future;", o)
        self.assertIn("NOTE z: registered in the registry but not listed in the master plan file", o)
        self.assertIn("CAUTION future: issue #9 is CLOSED but the module has no folder yet", o)
        rows = open(os.path.join(out, "module_tree.csv")).read()
        self.assertIn("x,1,x_one,sub-module of x,DONE", rows)

    def test_work_items_by_proof_paths(self):
        d = build(); out = os.path.join(d, "out")
        json.dump({}, open(os.path.join(d, "iss.json"), "w"))
        open(os.path.join(d, "PLAN.toml"), "w").write('[plan.z]\nexpected_subs = ["one"]\n[[plan.z.items]]\nname = "has both"\nproof = ["m/z/src/main/Own.kt", "m/z/src/test/*.kt"]\n[[plan.z.items]]\nname = "has one"\nproof = ["m/z/src/main/Own.kt", "m/z/NOPE.md"]\n[[plan.z.items]]\nname = "has none"\nproof = ["m/z/NOPE.md"]\n')
        open(os.path.join(d, "c.toml"), "w").write(f'repo = "{d}"\nout_dir = "{out}"\nissues_json = "{d}/iss.json"\nplan_file = "PLAN.toml"\n')
        o = subprocess.run([sys.executable, SCRIPT, os.path.join(d, "c.toml")], capture_output=True, text=True).stdout
        self.assertIn("- has both: DONE (work item of z;", o)
        self.assertIn("- has one: PARTIAL (work item of z;", o)
        self.assertIn("- has none: NOT_STARTED (work item of z;", o)

    def test_duplicate_issue_titles_newest_wins_whatever_the_order(self):
        d = build(); out = os.path.join(d, "out")
        issues = [{"title": "module: z", "number": 1, "state": "closed"}, {"title": "module: z", "number": 20, "state": "open"}]  # OLDEST first
        with FakeGitHub(issues) as url:
            open(os.path.join(d, "c.toml"), "w").write(f'repo = "{d}"\nout_dir = "{out}"\ngithub = "o/r"\ngithub_api = "{url}"\n')
            o = subprocess.run([sys.executable, SCRIPT, os.path.join(d, "c.toml")], capture_output=True, text=True).stdout
        self.assertIn("two issues are titled 'module: z' (#1 and #20)", o)
        self.assertIn("| z | 2 | 2 | 0 | #20 open | in progress |", o)

    def test_open_issue_without_a_definition_of_done_is_a_note_not_a_caution(self):
        d = build(); out = os.path.join(d, "out")
        json.dump({"module: z": [3, "open"]}, open(os.path.join(d, "iss.json"), "w"))
        open(os.path.join(d, "PLAN.toml"), "w").write('[plan.z]\nexpected_subs = []\n')
        open(os.path.join(d, "c.toml"), "w").write(f'repo = "{d}"\nout_dir = "{out}"\nissues_json = "{d}/iss.json"\nplan_file = "PLAN.toml"\n')
        o = subprocess.run([sys.executable, SCRIPT, os.path.join(d, "c.toml")], capture_output=True, text=True).stdout
        self.assertIn("NOTE z: built and tested, issue #3 still open; no sub-modules or work items are listed", o)
        self.assertNotIn("CAUTION z: everything built", o)

    def test_dead_top_with_live_kids_and_unreadable_inputs_are_loud(self):
        d = tempfile.mkdtemp(); out = os.path.join(d, "out")
        reg = '[module.old]\npath = "m/old"\nstatus = "dead"\n[module.old_kid]\npath = "m/old/kid"\n[module.nopath]\nowns = "x"\n[module.ok]\npath = "m/ok"\n'
        open(os.path.join(d, "modules.toml"), "w").write(reg)
        for p in ("m/old/kid/src/main/K.kt", "m/ok/src/main/O.kt", "m/ok/src/test/OTest.kt"):
            touch(d, p)
        open(os.path.join(d, "c.toml"), "w").write(f'repo = "{d}"\nout_dir = "{out}"\n')
        o = subprocess.run([sys.executable, SCRIPT, os.path.join(d, "c.toml")], capture_output=True, text=True).stdout
        self.assertIn("CAUTION old: marked dead, but it holds live modules (old_kid)", o)
        self.assertIn("CAUTION registry: nopath has no path; it is left out.", o)
        open(os.path.join(d, "modules.toml"), "w").write("this is [not toml")
        r = subprocess.run([sys.executable, SCRIPT, os.path.join(d, "c.toml")], capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)
        self.assertIn("CAUTION: cannot read the registry", r.stdout)

if __name__ == "__main__":
    unittest.main()
