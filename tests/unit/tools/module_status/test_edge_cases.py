"""Regression tests for tools/module_status/module_status.py: one test per defect found in review.

Run with the repo's test command (python3 -m unittest discover -s tests -t .).
Every test asserts the behaviour the script's own docstring or comments promise. A test that goes red means the
script no longer keeps that promise; the script is never edited to make a test pass.
"""
import json, os, shutil, subprocess, sys, tempfile, unittest

from tests.unit.tools.module_status.gh_server import FakeGitHub

from tests.helpers import ROOT
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("MS_SCRIPT") or os.path.join(ROOT, "tools", "module_status", "module_status.py")


def reg_mod(key, path, extra=""):
    return f'[module.{key}]\npath = "{path}"\nowns = "o"\ncard = "{path}/AGENTS.md"\n{extra}\n'


def fixture(reg, files=(), plan=None, issues=None, github=False):
    """Build a throwaway repo + config. Entries in files ending with '/' are empty folders."""
    d = tempfile.mkdtemp(prefix="module_status_")
    with open(os.path.join(d, "modules.toml"), "w") as fh:
        fh.write(reg)
    for f in files:
        p = os.path.join(d, f)
        if f.endswith("/"):
            os.makedirs(p, exist_ok=True)
            continue
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as fh:
            fh.write("x")
    lines = [f'repo = "{d}"', f'out_dir = "{d}/out"', 'issue_title = "module: {name}"']
    if plan is not None:
        with open(os.path.join(d, "PLAN.toml"), "w") as fh:
            fh.write(plan)
        lines.append('plan_file = "PLAN.toml"')
    if github:
        lines.append('github = "owner/repo"')
    else:
        with open(os.path.join(d, "iss.json"), "w") as fh:
            json.dump(issues or {}, fh)
        lines.append(f'issues_json = "{d}/iss.json"')
    cfg = os.path.join(d, "c.toml")
    with open(cfg, "w") as fh:
        fh.write("\n".join(lines) + "\n")
    return d, cfg


def run(cfg, env_extra=None):
    env = dict(os.environ)
    env.update(env_extra or {})
    r = subprocess.run([sys.executable, SCRIPT, cfg], capture_output=True, text=True, env=env, timeout=120)
    return r.returncode, r.stdout, r.stderr


def row(out, name):
    """The markdown table row for a top-level module, or '' if absent."""
    return next((l for l in out.splitlines() if l.startswith(f"| {name} |")), "")


class Base(unittest.TestCase):
    def tmp(self, d):
        self.addCleanup(shutil.rmtree, d, True)
        return d


class Bugs(Base):
    # a module with no expected_subs list can reach COMPLETE. The script's own comment
    # says "only a module with an expected list can be called ready to close", and its report line says
    # "No expected_subs list yet (so no ready-to-close check)", yet line 194 sets complete without that check.
    def test_no_expected_list_cannot_be_complete(self):
        d, cfg = fixture(reg_mod("q", "m/q"),
                         ["m/q/src/main/Q.kt", "m/q/src/test/QTest.kt"],
                         issues={"module: q": [1, "closed"]})
        self.tmp(d)
        rc, out, err = run(cfg)
        self.assertEqual(rc, 0, err)
        self.assertTrue(row(out, "q"), "q must appear in the table:\n" + out)
        self.assertNotIn("COMPLETE", row(out, "q"), "q has no expected list, so it must not be ready-to-close:\n" + out)

    # a dead sub-module named in expected_subs satisfies the expectation, because `have`
    # (line 174) includes dead descendants while `items` skips them. "built = ... not marked dead" (docstring).
    def test_dead_expected_sub_does_not_satisfy_expectation(self):
        reg = reg_mod("w", "m/w") + reg_mod("w_one", "m/w/one") + reg_mod("w_dead", "m/w/dead", 'status = "dead"')
        files = ["m/w/src/main/W.kt", "m/w/src/test/WTest.kt",
                 "m/w/one/src/main/O.kt", "m/w/one/src/test/OTest.kt",
                 "m/w/dead/src/main/D.kt", "m/w/dead/src/test/DTest.kt"]
        plan = '[plan.w]\nexpected_subs = ["one", "dead"]\n'
        d, cfg = fixture(reg, files, plan=plan, issues={"module: w": [3, "closed"]})
        self.tmp(d)
        rc, out, err = run(cfg)
        self.assertEqual(rc, 0, err)
        self.assertNotIn("COMPLETE", row(out, "w"), "the dead expected sub 'dead' is not built, so w is not complete:\n" + out)

    # status values are not validated. status = "Dead" (capital D) is silently treated as
    # live, so a dead module with code and tests is counted DONE. Only the exact string "dead" is read.
    def test_unknown_status_value_is_refused_or_cautioned(self):
        d, cfg = fixture(reg_mod("dd", "m/dd", 'status = "Dead"'),
                         ["m/dd/src/main/D.kt", "m/dd/src/test/DTest.kt"])
        self.tmp(d)
        rc, out, err = run(cfg)
        self.assertTrue(rc != 0 or "unknown status" in out.lower(),
                        "status 'Dead' must not silently count as live:\n" + out)

    # test detection is a substring test on the whole relative folder path ("/test" in
    # "/" + rel + "/", line 74). A MAIN-code folder named testsupport/ is counted as tests, so a module
    # with no real test is shown DONE.
    def test_main_code_in_testish_folder_is_not_a_test(self):
        d, cfg = fixture(reg_mod("t", "m/t"),
                         ["m/t/src/main/Own.kt", "m/t/src/main/kotlin/testsupport/Helpers.kt"])
        self.tmp(d)
        rc, out, err = run(cfg)
        self.assertEqual(rc, 0, err)
        self.assertIn("- t: PARTIAL (module;", out, "no test file exists, so t must be PARTIAL:\n" + out)

    # a main-code file whose NAME contains "Test" (not only LatestTest-style test files) is
    # counted as a test: `"Test" in f` (line 74). Real case in a Kotlin project:
    # shared/modules/api/src/main/kotlin/dev/example/shared/api/TestServiceResult.kt
    def test_main_file_named_testX_is_not_a_test(self):
        d, cfg = fixture(reg_mod("c", "m/c"),
                         ["m/c/src/main/kotlin/Own.kt", "m/c/src/main/kotlin/TestServiceResult.kt"])
        self.tmp(d)
        rc, out, err = run(cfg)
        self.assertEqual(rc, 0, err)
        self.assertIn("- c: PARTIAL (module;", out, "TestServiceResult.kt is main code, so c has no tests:\n" + out)

    # src/androidTest is not recognised as a test folder ("/test" does not match
    # "/androidTest"), so instrumented tests that do not have "Test" in the file name are counted as CODE
    # and the module is PARTIAL although it has tests.
    def test_androidtest_source_set_counts_as_tests(self):
        d, cfg = fixture(reg_mod("a", "m/a"),
                         ["m/a/src/main/Own.kt", "m/a/src/androidTest/kotlin/OwnSpec.kt"])
        self.tmp(d)
        rc, out, err = run(cfg)
        self.assertEqual(rc, 0, err)
        self.assertIn("- a: DONE (module;", out, "an instrumented test in src/androidTest exists, so a must be DONE:\n" + out)

    # the GitHub issue map is keyed by title and the loop overwrites, so for two issues with
    # the same title the OLDEST one wins (GitHub lists newest first by default). A closed old issue hides a
    # new open one. The fixture is a local stand-in for the GitHub issues API (gh_server.py beside this file), no real network.
    def test_duplicate_issue_titles_do_not_hide_the_open_one(self):
        issues = [{"title": "module: q", "number": 20, "state": "open"},   # newest, listed first
                  {"title": "module: q", "number": 1, "state": "closed"}]  # oldest, overwrites in the loop
        d, cfg = fixture(reg_mod("q", "m/q"), ["m/q/src/main/Q.kt", "m/q/src/test/QTest.kt"],
                         plan='[plan.q]\nexpected_subs = []\n', github=True)
        self.tmp(d)
        with FakeGitHub(issues) as url:
            with open(cfg, "a") as fh:
                fh.write(f'github_api = "{url}"\n')
            rc, out, err = run(cfg, {})
        self.assertEqual(rc, 0, err)
        r = row(out, "q")
        self.assertTrue("#20" in r or "duplicate" in out.lower(),
                        "open #20 must not be hidden by closed #1 with the same title:\n" + out)

    # a network failure (connection refused, timeout) is not caught. The script's own
    # branch for an HTTP error is "CAUTION: could not read issues" and carries on; a raised exception is a
    # traceback with rc 1 and no new report, so an older status.json/report.md stays in out_dir.
    def test_network_exception_is_a_caution_not_a_crash(self):
        d, cfg = fixture(reg_mod("q", "m/q"), ["m/q/src/main/Q.kt", "m/q/src/test/QTest.kt"], github=True)
        self.tmp(d)
        with FakeGitHub(mode="down") as url:
            with open(cfg, "a") as fh:
                fh.write(f'github_api = "{url}"\n')
            rc, out, err = run(cfg, {})
        self.assertEqual(rc, 0, "a network error must be a CAUTION, not a crash:\n" + err[-600:])
        self.assertIn("could not read issues", out)

    # a 403 rate limit is printed to stdout only. report.md (the saved deliverable) never says
    # why issues are missing, and each module is then reported as "no GitHub issue titled ..." as if the
    # issue did not exist.
    def test_rate_limit_is_recorded_in_the_report(self):
        d, cfg = fixture(reg_mod("q", "m/q"), ["m/q/src/main/Q.kt", "m/q/src/test/QTest.kt"], github=True)
        self.tmp(d)
        with FakeGitHub(mode="403") as url:
            with open(cfg, "a") as fh:
                fh.write(f'github_api = "{url}"\n')
            rc, out, err = run(cfg, {})
        self.assertEqual(rc, 0, err)
        with open(os.path.join(d, "out", "report.md")) as fh:
            report = fh.read()
        self.assertIn("403", report, "the saved report must say the issue read was refused:\n" + report)

    # a registered module whose folder does not exist is NOT_STARTED with no caution.
    # a typo in a registered path must not read as a module that is simply not started yet.
    def test_registered_folder_missing_is_a_caution(self):
        d, cfg = fixture(reg_mod("g", "m/ghost"), [])
        self.tmp(d)
        rc, out, err = run(cfg)
        self.assertEqual(rc, 0, err)
        folder_cautions = [l for l in out.splitlines() if l.startswith("- CAUTION") and ("folder" in l or "m/ghost" in l)]
        self.assertTrue(folder_cautions, "a registered module with no folder must raise a folder caution:\n" + out)

    # a path with a leading "./" is not normalised (norm() strips only "/"), so the
    # sub-module does not find its parent by prefix and becomes a separate top-level module. Its expected
    # name then reads as "not created yet" although the folder exists.
    def test_dot_slash_path_still_nests_the_sub_module(self):
        reg = reg_mod("p", "./m/p") + reg_mod("p_one", "m/p/one")
        files = ["m/p/src/main/P.kt", "m/p/src/test/PTest.kt", "m/p/one/src/main/O.kt", "m/p/one/src/test/OTest.kt"]
        d, cfg = fixture(reg, files, plan='[plan.p]\nexpected_subs = ["one"]\n', issues={})
        self.tmp(d)
        rc, out, err = run(cfg)
        self.assertEqual(rc, 0, err)
        self.assertIn("| p | 2 | 2 | 0 |", out, "p_one is a sub-module of p, so p has 2 items and none missing:\n" + out)

    # an empty registry (or a wrong registry_key in the config) gives rc 0, an empty table
    # and "No cautions.". A silent green on zero modules.
    def test_empty_registry_is_not_a_clean_pass(self):
        d, cfg = fixture("# no modules at all\n", [])
        self.tmp(d)
        rc, out, err = run(cfg)
        self.assertNotIn("No cautions.", out, "zero modules found must not print a clean 'No cautions.' pass:\n" + out)

    # a dead TOP-LEVEL module is still tracked: it appears in the table as "in progress"
    # with 0 items, and a closed issue raises "CAUTION ... not everything is done". Dead modules are
    # excluded from building by the docstring, so they should not raise a caution.
    def test_dead_top_level_module_is_not_tracked_as_in_progress(self):
        d, cfg = fixture(reg_mod("legacy", "legacy", 'status = "dead"'),
                         ["legacy/src/main/L.kt", "legacy/src/test/LTest.kt"],
                         issues={"module: legacy": [7, "closed"]})
        self.tmp(d)
        rc, out, err = run(cfg)
        self.assertEqual(rc, 0, err)
        self.assertNotIn("CAUTION legacy", out, "a dead module must not raise a 'not everything is done' caution:\n" + out)

    # two registered modules whose folder BASENAMES are equal (a/core and b/core)
    # share one issue title ("module: core"), so b_core takes a_core's closed issue and reads COMPLETE.
    def test_same_basename_modules_do_not_share_an_issue(self):
        reg = reg_mod("a_core", "m/a/core") + reg_mod("b_core", "m/b/core")
        files = ["m/a/core/src/main/A.kt", "m/a/core/src/test/ATest.kt",
                 "m/b/core/src/main/B.kt", "m/b/core/src/test/BTest.kt"]
        plan = '[plan.a_core]\nexpected_subs = []\n[plan.b_core]\nexpected_subs = []\n'
        d, cfg = fixture(reg, files, plan=plan, issues={"module: core": [5, "closed"]})
        self.tmp(d)
        rc, out, err = run(cfg)
        self.assertEqual(rc, 0, err)
        self.assertNotIn("COMPLETE", row(out, "b_core"), "b_core must not inherit a_core's issue #5:\n" + out)

    # a proof path that matches an EMPTY folder counts as proof (glob matches directories,
    # and the script only checks that the glob is non-empty). A work item with no files reads DONE.
    def test_empty_folder_is_not_proof(self):
        plan = ('[plan.z]\nexpected_subs = []\n'
                '[[plan.z.items]]\nname = "docs"\nproof = ["m/z/docs_empty/"]\n')
        d, cfg = fixture(reg_mod("z", "m/z"), ["m/z/src/main/Own.kt", "m/z/src/test/ZTest.kt", "m/z/docs_empty/"],
                         plan=plan, issues={})
        self.tmp(d)
        rc, out, err = run(cfg)
        self.assertEqual(rc, 0, err)
        self.assertNotIn("- docs: DONE", out, "an empty folder is not evidence of a finished work item:\n" + out)


    # a plan entry keyed by a SUB-module name is silently dropped: the loop at line 199 skips
    # every plan key that is in mods, and plan.get(top) is only read for top-level modules. Its
    # expected_subs and issue are never used and no line says so.
    def test_plan_entry_for_a_sub_module_is_reported_not_dropped(self):
        reg = reg_mod("p", "m/p") + reg_mod("p_one", "m/p/one")
        files = ["m/p/src/main/P.kt", "m/p/src/test/PTest.kt", "m/p/one/src/main/O.kt", "m/p/one/src/test/OTest.kt"]
        d, cfg = fixture(reg, files, plan='[plan.p_one]\nexpected_subs = ["zzz"]\nissue = 9\n', issues={})
        self.tmp(d)
        rc, out, err = run(cfg)
        self.assertEqual(rc, 0, err)
        self.assertIn("zzz", out, "the plan's expected_subs under p_one must be reported or flagged:\n" + out)

    # a plan expected name that equals the key of ANOTHER registered top-level module is
    # reported as "expected, not created yet", although that module exists. The report contradicts itself.
    def test_expected_name_that_is_a_registered_module_is_not_called_not_created(self):
        reg = reg_mod("x", "m/x") + reg_mod("y", "m/y")
        files = ["m/x/src/main/X.kt", "m/x/src/test/XTest.kt", "m/y/src/main/Y.kt", "m/y/src/test/YTest.kt"]
        d, cfg = fixture(reg, files, plan='[plan.x]\nexpected_subs = ["y"]\n', issues={})
        self.tmp(d)
        rc, out, err = run(cfg)
        self.assertEqual(rc, 0, err)
        self.assertNotIn("- y: NOT_STARTED (sub-module of x", out, "y is a registered module, so it is not 'not created yet':\n" + out)

    # a package folder named "build" under src is skipped by the default skip_dirs ("build").
    # Its code is not counted, so a module whose only code lives in such a package reads NOT_STARTED.
    def test_package_named_build_is_counted_as_code(self):
        d, cfg = fixture(reg_mod("b", "m/b"),
                         ["m/b/src/main/kotlin/dev/x/build/Info.kt", "m/b/src/test/InfoTest.kt"], issues={})
        self.tmp(d)
        rc, out, err = run(cfg)
        self.assertEqual(rc, 0, err)
        self.assertIn("- b: DONE (module;", out, "a source package called build is code, not a build folder:\n" + out)

    # two registry keys with the SAME path are both tracked as top-level modules over the same
    # folder (double counted), with no caution. Other registry checkers may not reject duplicates either.
    def test_duplicate_registry_path_is_cautioned(self):
        reg = reg_mod("m1", "m/shared") + reg_mod("m2", "m/shared")
        d, cfg = fixture(reg, ["m/shared/src/main/S.kt", "m/shared/src/test/STest.kt"], issues={})
        self.tmp(d)
        rc, out, err = run(cfg)
        flagged = rc != 0 or any(("m1" in l and "m2" in l) for l in out.splitlines() if "CAUTION" in l or "NOTE" in l)
        self.assertTrue(flagged, "two keys on one folder must be cautioned:\n" + out)

    # a plan issue written as a string ("9") never matches (the lookup compares ints), so the
    # module reads "no issue" and the caution names a title lookup although the plan gave an issue number.
    def test_string_plan_issue_is_refused_or_named(self):
        d, cfg = fixture(reg_mod("q", "m/q"), ["m/q/src/main/Q.kt", "m/q/src/test/QTest.kt"],
                         plan='[plan.q]\nissue = "9"\n', issues={"module: q": [9, "closed"]})
        self.tmp(d)
        rc, out, err = run(cfg)
        flagged = rc != 0 or any("9" in l for l in out.splitlines() if l.startswith("- CAUTION"))
        self.assertTrue(flagged, "a non-integer plan issue must be refused or named in the caution:\n" + out)

if __name__ == "__main__":
    unittest.main()
