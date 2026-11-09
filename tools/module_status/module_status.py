#!/usr/bin/env python3
"""module_status.py CONFIG.toml : track every module and sub-module of a module-sop repo.

Reads the repo's modules.toml (the registry), decides per module whether it is built, compares each
top-level module with its expected sub-modules, checks the module's GitHub issue, and writes a
workbook, a flat CSV table and a short report. Repo agnostic: only CONFIG.toml names the repo.

Rules (printed in the report too):
  built      = registered, not marked dead, has code files of its own AND test files  -> DONE
               code but no tests (or docs_pending)                                    -> PARTIAL
               no code of its own                                                     -> NOT_STARTED
  expected   = `expected_subs = [...]` on a top-level module in the plan file (or modules.toml, or
               [expected] in the config). `[]` means "documented: no sub-modules". A sub-module named
               there and not registered is NOT_STARTED. A registered sub-module not named there is
               counted anyway and flagged NEW. A dead sub-module never satisfies an expectation.
  complete   = every item DONE, nothing expected is missing, an expected list exists, AND the module's
               issue is closed. Without an expected list a closed, fully built module is shown as
               "closed, not verified".
  caution    = printed loudly, never an error: all built but the issue is still open, the issue is
               closed while something is missing, unknown or stale names, unreadable inputs.
Exit code: 0 normally, 2 when the registry has no modules at all.
"""
import csv, glob, json, os, subprocess, sys, tomllib, urllib.error, urllib.parse, urllib.request

cfg_path = sys.argv[1]
cfg = tomllib.load(open(cfg_path, "rb"))
repo = os.path.expanduser(cfg["repo"])
out_dir = cfg.get("out_dir", "out")
os.makedirs(out_dir, exist_ok=True)
CODE = tuple(cfg.get("code_ext", [".kt", ".java", ".py", ".js", ".ts"]))
SKIP = set(cfg.get("skip_dirs", ["build", "node_modules", ".gradle", "__pycache__", ".git"]))
TEST_DIRS = set(cfg.get("test_dirs", ["test", "tests", "androidTest", "testFixtures", "__tests__"]))
TEST_SUFFIX = tuple(cfg.get("test_suffixes", ["Test.kt", "Tests.kt", "Test.java", "Tests.java", "_test.py",
                                              ".test.js", ".test.ts", ".spec.js", ".spec.ts"]))
cautions = []

def _load_toml(path, what):
    try:
        with open(path, "rb") as fh:
            return tomllib.load(fh)
    except (OSError, tomllib.TOMLDecodeError) as e:
        print(f"CAUTION: cannot read {what} '{path}': {e}")
        sys.exit(2)


reg = _load_toml(os.path.join(repo, cfg.get("registry", "modules.toml")), "the registry")
mods = reg.get(cfg.get("registry_key", "module")) or reg.get("modules") or {}
if not mods:
    print("CAUTION: the registry lists no modules; nothing to track.")
    sys.exit(2)
expected_cfg = cfg.get("expected", {})
plan = {}
if cfg.get("plan_file"):  # the master module plan: [plan.<registry key>] expected_subs, issue, [[plan.KEY.items]]
    plan = _load_toml(os.path.join(repo, cfg["plan_file"]), "the plan file").get("plan", {})


def _norm(p):
    return os.path.normpath(str(p).replace("\\", "/")).replace("\\", "/").strip("/")


for k in [k for k, v in mods.items() if "path" not in v]:
    print(f"CAUTION registry: {k} has no path; it is left out.")
    del mods[k]
paths = {k: _norm(v["path"]) for k, v in mods.items()}
seen = {}
for k, p in sorted(paths.items()):
    if p in seen:
        cautions.append(f"CAUTION registry: {k} and {seen[p]} share the folder '{p}'; both are counted.")
    seen.setdefault(p, k)
for k, v in mods.items():
    st = v.get("status", "live")
    if st not in ("live", "dead"):
        cautions.append(f"CAUTION {k}: unknown status '{st}' (use live or dead); treated as live.")

# A container is an area folder that only groups modules (android, server, shared); it is not tracked itself.
CDEPTH = cfg.get("container_depth", 0)
containers = {k for k, p in paths.items() if CDEPTH and p.count("/") + 1 <= CDEPTH}


def _parent_of(k):
    best = None
    for o, op in paths.items():
        if o != k and o not in containers and paths[k].startswith(op + "/") and (best is None or len(op) > len(paths[best])):
            best = o
    return best


parent = {k: _parent_of(k) for k in mods}
has_kids = {parent[k] for k in mods} | {k for k in mods if any(paths[c].startswith(paths[k] + "/") for c in mods if c != k)}
tops = [k for k in mods if parent[k] is None and not (k in containers and k in has_kids)]
warned_missing = set()


def _own_files(k):
    """Code and test files in this module's folder, leaving out the folders of its sub-modules."""
    base = os.path.join(repo, paths[k])
    if not os.path.isdir(base):
        if k not in warned_missing:
            warned_missing.add(k)
            cautions.append(f"CAUTION {k}: its registered folder '{paths[k]}' does not exist.")
        return 0, 0
    kids = [paths[c] for c in mods if parent[c] == k]
    code, tests = 0, 0
    for d, dirs, files in os.walk(base):
        rel = _norm(os.path.relpath(d, repo))
        inside = os.path.relpath(d, base)
        # "build" is only a build folder at the module root (a package may be called build deeper down)
        dirs[:] = [x for x in dirs if _norm(os.path.join(rel, x)) not in kids
                   and not (x in SKIP and (x != "build" or inside == "."))]
        in_test_dir = any(seg in TEST_DIRS for seg in ([] if inside == "." else inside.replace("\\", "/").split("/")))
        for f in files:
            if not f.endswith(CODE):
                continue
            if in_test_dir or f.startswith("test_") or f.endswith(TEST_SUFFIX):
                tests += 1
            else:
                code += 1
    return code, tests


def _state(k):
    t = mods[k]
    code, tests = _own_files(k)
    if t.get("status") == "dead":
        return None, code, tests
    if code == 0:
        return "NOT_STARTED", code, tests
    if tests == 0 or t.get("docs_pending"):
        return "PARTIAL", code, tests
    return "DONE", code, tests


# ---- GitHub issues (optional) -------------------------------------------
issues = {}
gh = cfg.get("github")


def _add_issue(title, number, st):
    title = title.strip()
    old = issues.get(title)
    if old and old[0] != number:
        cautions.append(f"CAUTION issues: two issues are titled '{title}' (#{old[0]} and #{number}); the newer one is used.")
    if not old or number > old[0]:
        issues[title] = (number, st)


if cfg.get("issues_json"):  # offline / test: {"title": [number, "open"|"closed"]}
    for t, v in json.load(open(cfg["issues_json"])).items():
        _add_issue(t, v[0], v[1])
    gh = "offline"
elif gh:
    api = cfg.get("github_api", "https://api.github.com").rstrip("/")
    var = cfg.get("token_var", "GITHUB_TOKEN")
    tok = os.environ.get(var, "")
    envf = cfg.get("token_env_file")
    if not tok and envf and os.path.exists(envf):
        for line in open(envf):
            line = line.strip()
            if line.startswith("export "):
                line = line[7:].strip()
            if line.startswith(var + "="):
                tok = line.split("=", 1)[1].strip().strip("\"'")
    H = {"Accept": "application/vnd.github+json"}
    if tok:
        H["Authorization"] = "Bearer " + tok
    else:
        cautions.append("CAUTION issues: no GitHub token found; anonymous calls are limited to 60 an hour.")
    page = 1
    while True:
        url = f"{api}/repos/{gh}/issues?" + urllib.parse.urlencode({"state": "all", "per_page": 100, "page": page})
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=40) as resp:
                status, got = resp.status, json.load(resp)
        except urllib.error.HTTPError as e:
            status, got = e.code, None
        except Exception as e:  # any network or reply failure is a caution, never a crash
            cautions.append(f"CAUTION issues: could not read issues, GitHub not reachable ({type(e).__name__}); issue columns are incomplete.")
            break
        if status != 200:
            cautions.append(f"CAUTION issues: could not read issues, GitHub answered {status}; issue columns are incomplete.")
            break
        if not got:
            break
        for i in got:
            if "pull_request" not in i:
                _add_issue(i["title"], i["number"], i["state"])
        page += 1
pattern = cfg.get("issue_title", "module: {name}")
by_number = {v[0]: v for v in issues.values()}


def _plan_issue(key):
    """The issue number named in the plan, as an int, or None."""
    n = plan.get(key, {}).get("issue")
    if n is None:
        return None
    if isinstance(n, int) and not isinstance(n, bool):
        return n
    try:
        cautions.append(f"CAUTION {key}: plan issue '{n}' should be a number, not text; read as {int(n)}.")
        return int(n)
    except (TypeError, ValueError):
        cautions.append(f"CAUTION {key}: plan issue '{n}' is not a number; ignored.")
        return None


# ---- per top-level module -------------------------------------------------
result, rows, noexp, tree = [], [], [], []
basenames = {}
for k in tops:
    basenames.setdefault(os.path.basename(paths[k]), []).append(k)


def _depth_of(k):
    d = 0
    while parent[k]:
        k = parent[k]
        d += 1
    return d


for top in sorted(tops):
    s, code, tests = _state(top)
    if s is None:  # a dead top-level module is retired, not tracked
        live_kids = [c for c in mods if paths[c].startswith(paths[top] + "/") and mods[c].get("status") != "dead"]
        if live_kids:
            cautions.append(f"CAUTION {top}: marked dead, but it holds live modules ({', '.join(sorted(live_kids))}); they are not tracked.")
        continue
    subs = [k for k in mods if parent[k] == top]
    stack, desc = list(subs), []  # every descendant counts, not only direct children
    while stack:
        c = stack.pop()
        desc.append(c)
        stack += [x for x in mods if parent[x] == c]
    base = os.path.basename(paths[top])
    exp = plan.get(top, {}).get("expected_subs", mods[top].get("expected_subs", expected_cfg.get(top)))
    items = []
    tree.append((top, 0, top, "module", s, code, tests, "registered" + (" + plan" if top in plan else ", not in plan")))
    if code or not desc:
        items.append({"item": f"{top} (its own code)", "status": s, "evidence": f"{code} code files, {tests} test files"})
    live = []
    for c in sorted(desc):
        s, code, tests = _state(c)
        if s is None:
            continue
        live.append(c)
        flag = ""
        if exp is not None and os.path.basename(paths[c]) not in exp and c not in exp:
            flag = " NEW (not in the expected list)"
            cautions.append(f"NOTE {top}: sub-module {c} is registered but not in its expected list; counted.")
        items.append({"item": c + flag, "status": s, "evidence": f"{code} code files, {tests} test files"})
        tree.append((top, _depth_of(c) - _depth_of(top), c, "sub-module of " + parent[c], s, code, tests,
                     "NEW, not in expected list" if flag else ("registered + expected" if exp is not None else "registered")))
    for w in plan.get(top, {}).get("items", []):
        proofs = w.get("proof", [])
        proofs = [proofs] if isinstance(proofs, str) else proofs
        hit = 0
        for p in proofs:
            for x in glob.glob(os.path.join(repo, p)):
                if os.path.isfile(x) or (os.path.isdir(x) and any(files for _, _, files in os.walk(x))):
                    hit += 1
                    break
        st = "NOT_STARTED" if not hit else ("DONE" if hit == len(proofs) else "PARTIAL")
        items.append({"item": f"{w['name']} (work item)", "status": st, "evidence": f"{hit} of {len(proofs)} proof paths exist"})
        tree.append((top, 1, w["name"], "work item of " + top, st, hit, len(proofs), "plan work item (proof paths)"))
    missing = []
    if exp is not None:
        have = {os.path.basename(paths[c]) for c in live} | set(live)
        other_tops = {os.path.basename(paths[t]) for t in tops if t != top} | {t for t in tops if t != top}
        for e in exp:
            if e in have:
                continue
            if e in other_tops:
                cautions.append(f"CAUTION {top}: expected sub-module '{e}' is registered elsewhere as a module of its own.")
                continue
            dead_hit = any(mods[c].get("status") == "dead" and (e == c or e == os.path.basename(paths[c])) for c in desc)
            missing.append(e)
            why = "its folder is registered but marked dead" if dead_hit else "no registered folder"
            tree.append((top, 1, e, "sub-module of " + top, "NOT_STARTED", 0, 0, "expected, not usable: " + why))
            items.append({"item": f"{e} (expected, not created yet)", "status": "NOT_STARTED", "evidence": "named in expected_subs, " + why})
    num = _plan_issue(top)
    if num is not None:
        iss = by_number.get(num)
        want = f"issue #{num}"
    elif len(basenames[base]) > 1:
        iss, want = None, f"issue ('{base}' is shared by {', '.join(basenames[base])}; name one in the plan)"
    else:
        iss = issues.get(pattern.format(name=base, key=top))
        want = f"issue titled '{pattern.format(name=base, key=top)}'"
    if gh and iss is None:
        cautions.append(f"CAUTION {top}: no GitHub {want} found.")
    all_done = bool(items) and all(i["status"] == "DONE" for i in items) and not missing
    if exp is None:
        noexp.append(top)
    # "built" alone proves little: only a module with a definition of done (expected sub-modules or listed work
    # items) can be called ready to close; otherwise this is a plain note.
    has_dod = bool(exp) or bool(plan.get(top, {}).get("items"))
    if iss and iss[1] == "open" and all_done and has_dod:
        cautions.append(f"CAUTION {top}: everything built and tested, but issue #{iss[0]} is still OPEN. Close it out.")
    elif iss and iss[1] == "open" and all_done:
        cautions.append(f"NOTE {top}: built and tested, issue #{iss[0]} still open; no sub-modules or work items are listed, so it cannot be told whether it is finished.")
    if iss and iss[1] == "closed" and not all_done:
        cautions.append(f"CAUTION {top}: issue #{iss[0]} is CLOSED but not everything is done "
                        f"({len(missing)} expected missing, {sum(i['status'] != 'DONE' for i in items)} not DONE).")
    if all_done and iss and iss[1] == "closed":
        state_word = "COMPLETE" if exp is not None else "closed, not verified"
    else:
        state_word = "in progress"
    result.append({"name": top, "path": paths[top], "items": items or [{"item": top, "status": "NOT_STARTED", "evidence": ""}]})
    rows.append((top, len(items), sum(i["status"] == "DONE" for i in items), len(missing),
                 f"#{iss[0]} {iss[1]}" if iss else "no issue", state_word))

for key, p in sorted(plan.items()):
    if key in mods:
        if key in containers and key in has_kids:
            cautions.append(f"CAUTION plan: '{key}' is an area folder that only groups modules; its plan entry is ignored.")
        elif key not in tops:
            cautions.append(f"CAUTION plan: '{key}' is a sub-module in the registry; plan entries belong to top-level modules, so its "
                            f"{ {a: b for a, b in p.items() if a in ('expected_subs', 'issue', 'items')} } is ignored.")
        continue
    nm = p.get("path", key)
    num = _plan_issue(key)
    iss = by_number.get(num) if num is not None else None
    if num is not None and iss is None and gh:
        cautions.append(f"CAUTION {key}: planned module names issue #{num}, which was not found.")
    items = [{"item": f"{key} (planned module, not created yet)", "status": "NOT_STARTED", "evidence": "named in the plan file only"}]
    for e in p.get("expected_subs", []):
        items.append({"item": f"{e} (expected, not created yet)", "status": "NOT_STARTED", "evidence": "named in the plan file only"})
        tree.append((key, 1, e, "sub-module of " + key, "NOT_STARTED", 0, 0, "planned only"))
    tree.append((key, 0, key, "module", "NOT_STARTED", 0, 0, "planned only, no folder yet"))
    result.append({"name": key, "path": nm, "items": items})
    rows.append((key, len(items), 0, len(items) - 1, f"#{iss[0]} {iss[1]}" if iss else "no issue", "planned"))
    if iss and iss[1] == "closed":
        cautions.append(f"CAUTION {key}: issue #{iss[0]} is CLOSED but the module has no folder yet.")
if plan:
    for k in tops:
        if k not in plan and mods[k].get("status") != "dead":
            cautions.append(f"NOTE {k}: registered in the registry but not listed in the master plan file.")

# ---- outputs ----------------------------------------------------------------
js = os.path.join(out_dir, "status.json")
json.dump({"modules": result}, open(js, "w"), indent=1)
sha = subprocess.run(["git", "-C", repo, "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip() or "?"
asof = subprocess.run(["date", "-u", "+%Y-%m-%d %H:%MZ"], capture_output=True, text=True).stdout.strip()
xlsx = os.path.join(out_dir, cfg.get("xlsx_name", "Module_Status.xlsx"))
builder = cfg.get("xlsx_builder", os.path.join(os.path.dirname(os.path.abspath(__file__)), "module_status_xlsx.py"))
b = subprocess.run([sys.executable, builder, xlsx, js, "--title", cfg.get("name", os.path.basename(repo)),
                    "--asof", asof, "--sha", sha], capture_output=True, text=True)
if b.returncode:
    cautions.append("CAUTION workbook not built: " + (b.stderr.strip().splitlines() or ["?"])[-1][:200])
lines = [f"# Module status, {cfg.get('name', os.path.basename(repo))} at {sha}, {asof}", ""]
lines += (["## CAUTIONS (not failures)"] + [f"- {c}" for c in cautions] + [""]) if cautions else ["No cautions.", ""]
if noexp:
    lines += [f"No expected_subs list yet (so COMPLETE and ready-to-close checks are off): {', '.join(sorted(noexp))}", ""]
with open(os.path.join(out_dir, "module_tree.csv"), "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["top_module", "level", "name", "kind", "status", "code_files", "test_files", "plan"])
    w.writerows(tree)
lines += ["## Every module and sub-module (parent shown)", ""]
for t in tree:
    lines.append(f"{'    ' * t[1]}- {t[2]}: {t[4]} ({t[3]}; {t[5]} code, {t[6]} test; {t[7]})")
lines += [""]
lines += ["| module | items | done | expected missing | issue | state |", "|---|---|---|---|---|---|"]
lines += [f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} |" for r in rows]
open(os.path.join(out_dir, "report.md"), "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
print(f"\nwrote {xlsx} (builder rc {b.returncode}), {js}")
