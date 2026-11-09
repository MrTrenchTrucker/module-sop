"""Tests for module_status_xlsx.py. Run: python3 -m unittest -v test_module_status_xlsx

MSX_SCRIPT=<path> points the tests at another builder copy (used for the red-first runs).

Checks, per workbook:
  * every part is well-formed XML and the zip opens;
  * every count and percentage equals a value computed here from the JSON, by a different method
    than the builder uses (no builder code is imported);
  * every live formula, recomputed by a small evaluator over the cell values, gives its cached value.
"""
import ast
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile

from tests.helpers import ROOT
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("MSX_SCRIPT") or os.path.join(ROOT, "tools", "module_status", "module_status_xlsx.py")
M = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"

FIXTURE = {"modules": [
    {"name": "alpha_core", "path": "alpha/modules/core", "items": [
        {"item": "alpha_core (its own code)", "status": "DONE", "evidence": "3 code files, 2 test files"},
        {"item": "alpha_core_extra", "status": "PARTIAL", "evidence": "1 of 2 proof paths exist"}]},
    {"name": "alpha_ui", "path": "alpha/ui", "items": [
        {"item": "alpha_ui (its own code)", "status": "NOT_STARTED", "evidence": "0 code files"}]},
    {"name": "beta", "path": "beta", "items": [
        {"item": "beta (its own code)", "status": "DONE", "evidence": "5 code files"},
        {"item": "beta_two", "status": "DONE", "evidence": "x"},
        {"item": "beta_three", "status": "NOT_STARTED", "evidence": ""}]},
    {"name": "gamma_svc", "path": "gamma/svc/deep", "items": [
        {"item": "gamma (its own code)", "status": "PARTIAL", "evidence": "a"}]},
    {"name": "delta_empty", "path": "delta/empty", "items": []},
    {"name": "xy_mod", "path": "x-y/z", "items": [
        {"item": "xy_mod item", "status": "DONE", "evidence": "ok"}]},
]}


def run_builder(args):
    return subprocess.run([sys.executable, SCRIPT] + args, capture_output=True, text=True)


def expected(doc):
    """Independent computation from the JSON: per module, per area, overall."""
    mods, areas = {}, {}
    all_status = []
    for m in doc["modules"]:
        area = m["path"].split("/")[0]
        st = [i["status"] for i in m["items"]]
        all_status += st
        row = {"area": area, "items": len(st), "done": st.count("DONE"),
               "partial": st.count("PARTIAL"), "ns": st.count("NOT_STARTED")}
        row["pct"] = row["done"] / row["items"] if row["items"] else 0.0
        mods[m["name"]] = row
        a = areas.setdefault(area, {"modules": 0, "items": 0, "done": 0, "partial": 0, "ns": 0})
        a["modules"] += 1
        for k in ("items", "done", "partial", "ns"):
            a[k] += row[k]
    for a in areas.values():
        a["pct"] = a["done"] / a["items"] if a["items"] else 0.0
    n = len(all_status)
    overall = {"modules": len(mods), "items": n, "done": all_status.count("DONE"),
               "partial": all_status.count("PARTIAL"), "ns": all_status.count("NOT_STARTED")}
    overall["pct"] = overall["done"] / n if n else 0.0
    return mods, areas, overall


def expected_item_rows(doc):
    return sorted((m["path"].split("/")[0], m["name"], i["item"], i["status"], i["evidence"])
                  for m in doc["modules"] for i in m["items"])


# ---- reading a workbook --------------------------------------------------------------------
def read_book(path):
    """Return ({sheet name: {ref: (value, formula)}}, [all xml parts parsed]). Raises on bad XML."""
    z = zipfile.ZipFile(path)
    assert z.testzip() is None, "zip member CRC failed"
    parsed_parts = {}
    for name in z.namelist():
        if name.endswith(".xml") or name.endswith(".rels"):
            parsed_parts[name] = ET.fromstring(z.read(name))   # raises ParseError if not well-formed
    sst = []
    if "xl/sharedStrings.xml" in parsed_parts:
        for si in parsed_parts["xl/sharedStrings.xml"].findall(M + "si"):
            sst.append("".join(t.text or "" for t in si.iter(M + "t")))
    rels = {r.get("Id"): r.get("Target") for r in parsed_parts["xl/_rels/workbook.xml.rels"]}
    book = {}
    for sh in parsed_parts["xl/workbook.xml"].find(M + "sheets"):
        target = "xl/" + rels[sh.get(R + "id")]
        cells = {}
        for c in parsed_parts[target].iter(M + "c"):
            v, f, t = c.find(M + "v"), c.find(M + "f"), c.get("t")
            if t == "s":
                val = sst[int(v.text)]
            elif v is None:
                val = None
            elif t == "str":
                val = v.text or ""
            else:
                val = float(v.text)
            cells[c.get("r")] = (val, f.text if f is not None else None)
        book[sh.get("name")] = cells
    return book, parsed_parts


def col_num(letters):
    n = 0
    for ch in letters:
        n = n * 26 + ord(ch) - 64
    return n


def col_letters(n):
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def grid(book, sheet):
    """Rows of a sheet as lists, dropping the header row; empty cells are None."""
    cells = book[sheet]
    last_row = max(int(re.sub(r"[A-Z]+", "", k)) for k in cells)
    last_col = max(col_num(re.sub(r"\d+", "", k)) for k in cells)
    rows = []
    for r in range(2, last_row + 1):
        row = []
        for c in range(1, last_col + 1):
            row.append(cells.get(f"{col_letters(c)}{r}", (None, None))[0])
        rows.append(row)
    return rows


# ---- a small evaluator for the formula forms the builder writes ------------------------------
TOK = re.compile(r"""
    (?P<ws>\s+)
  | (?P<str>"(?:[^"]|"")*")
  | (?P<range>(?:[A-Za-z_]\w*!)?\$?[A-Z]{1,3}\$?\d+:\$?[A-Z]{1,3}\$?\d+)
  | (?P<ref>(?:[A-Za-z_]\w*!)?\$?[A-Z]{1,3}\$?\d+)
  | (?P<func>[A-Z]+(?=\())
  | (?P<num>\d+(?:\.\d+)?)
  | (?P<op><>|<=|>=|[=<>+\-*/(),])
""", re.X)
RANGE_PARTS = re.compile(r"^(?:([A-Za-z_]\w*)!)?\$?([A-Z]{1,3})\$?(\d+):\$?([A-Z]{1,3})\$?(\d+)$")
REF_PARTS = re.compile(r"^(?:([A-Za-z_]\w*)!)?\$?([A-Z]{1,3})\$?(\d+)$")


def tokenize(f):
    out, pos = [], 0
    while pos < len(f):
        m = TOK.match(f, pos)
        if not m:
            raise ValueError(f"cannot tokenize {f[pos:]!r}")
        pos = m.end()
        if m.lastgroup != "ws":
            out.append((m.lastgroup, m.group(m.lastgroup)))
    return out


class Parser:
    def __init__(self, toks, cur_sheet):
        self.t, self.i, self.cur = toks, 0, cur_sheet

    def peek(self):
        return self.t[self.i] if self.i < len(self.t) else (None, None)

    def eat(self, value=None):
        tok = self.peek()
        if value is not None and tok[1] != value:
            raise ValueError(f"expected {value!r}, got {tok[1]!r}")
        self.i += 1
        return tok

    def parse(self):
        node = self.comparison()
        if self.i != len(self.t):
            raise ValueError("trailing tokens")
        return node

    def comparison(self):
        node = self.additive()
        if self.peek()[1] in ("=", "<>", "<", ">", "<=", ">="):
            op = self.eat()[1]
            node = ("bin", op, node, self.additive())
        return node

    def additive(self):
        node = self.term()
        while self.peek()[1] in ("+", "-"):
            op = self.eat()[1]
            node = ("bin", op, node, self.term())
        return node

    def term(self):
        node = self.unary()
        while self.peek()[1] in ("*", "/"):
            op = self.eat()[1]
            node = ("bin", op, node, self.unary())
        return node

    def unary(self):
        if self.peek()[1] == "-":
            self.eat()
            return ("neg", self.unary())
        return self.primary()

    def primary(self):
        kind, val = self.peek()
        if kind == "num":
            self.eat()
            return ("num", float(val))
        if kind == "str":
            self.eat()
            return ("str", val[1:-1].replace('""', '"'))
        if kind == "range":
            self.eat()
            s, c1, r1, c2, r2 = RANGE_PARTS.match(val).groups()
            return ("range", s or self.cur, c1, int(r1), c2, int(r2))
        if kind == "ref":
            self.eat()
            s, c, r = REF_PARTS.match(val).groups()
            return ("ref", s or self.cur, c, int(r))
        if kind == "func":
            self.eat()
            self.eat("(")
            args = []
            if self.peek()[1] != ")":
                args.append(self.comparison())
                while self.peek()[1] == ",":
                    self.eat()
                    args.append(self.comparison())
            self.eat(")")
            return ("func", val, args)
        if val == "(":
            self.eat()
            node = self.comparison()
            self.eat(")")
            return node
        raise ValueError(f"unexpected token {val!r}")


def num_of(v):
    if v is None:
        return 0.0
    if isinstance(v, float):
        return v
    raise ValueError(f"arithmetic on text {v!r}")


def matches(cell, crit):
    """COUNTIF criterion: plain text or number means equal; a leading <> = < > <= >= compares."""
    if isinstance(crit, str):
        if "*" in crit or "?" in crit:
            raise NotImplementedError("wildcards are not used by the builder")
        m = re.match(r"^(<>|<=|>=|=|<|>)?(.*)$", crit, re.S)
        op, val = m.group(1) or "=", m.group(2)
        if op == "=":
            return isinstance(cell, str) and cell.lower() == val.lower()
        if op == "<>":
            return not (isinstance(cell, str) and cell.lower() == val.lower())
        raise NotImplementedError("only = and <> text criteria are used by the builder")
    return isinstance(cell, float) and cell == crit


def evaluate(node, book):
    kind = node[0]
    if kind in ("num", "str"):
        return node[1]
    if kind == "ref":
        return book[node[1]].get(f"{node[2]}{node[3]}", (None, None))[0]
    if kind == "range":
        _, s, c1, r1, c2, r2 = node
        assert c1 == c2, "single-column ranges only"
        lo, hi = sorted((r1, r2))   # a spreadsheet normalises a reversed range, so does this
        return [book[s].get(f"{c1}{r}", (None, None))[0] for r in range(lo, hi + 1)]
    if kind == "neg":
        return -num_of(evaluate(node[1], book))
    if kind == "bin":
        op, a, b = node[1], evaluate(node[2], book), evaluate(node[3], book)
        if op in ("+", "-", "*", "/"):
            x, y = num_of(a), num_of(b)
            if op == "/":
                if y == 0:
                    raise ZeroDivisionError("#DIV/0!")
                return x / y
            return {"+": x + y, "-": x - y, "*": x * y}[op]
        if a is None:
            a = "" if isinstance(b, str) else 0.0
        if b is None:
            b = "" if isinstance(a, str) else 0.0
        if isinstance(a, str) and isinstance(b, str):
            a, b = a.lower(), b.lower()
        return {"=": a == b, "<>": a != b, "<": a < b, ">": a > b, "<=": a <= b, ">=": a >= b}[op]
    if kind == "func":
        name, args = node[1], node[2]
        if name == "IF":
            cond = evaluate(args[0], book)
            return evaluate(args[1], book) if cond else evaluate(args[2], book)
        if name in ("COUNTIF", "COUNTIFS"):
            if len(args) % 2:
                raise ValueError(f"{name} needs criteria pairs")
            pairs = [(evaluate(args[i], book), evaluate(args[i + 1], book)) for i in range(0, len(args), 2)]
            n_rows = len(pairs[0][0])
            if any(len(rng) != n_rows for rng, _ in pairs):
                raise ValueError("COUNTIFS ranges differ in size")
            return float(sum(all(matches(rng[k], crit) for rng, crit in pairs) for k in range(n_rows)))
        if name == "COUNTA":
            return float(sum(1 for v in evaluate(args[0], book) if v not in (None, "")))
        if name == "SUM":
            total = 0.0
            for a in args:
                v = evaluate(a, book)
                for x in (v if isinstance(v, list) else [v]):
                    if isinstance(x, float):
                        total += x
            return total
        raise ValueError(f"unknown function {name}")
    raise ValueError(f"unknown node {kind}")


def recompute(formula, sheet, book):
    return evaluate(Parser(tokenize(formula), sheet).parse(), book)


class T(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        cls.src = os.path.join(cls.tmp, "status.json")
        with open(cls.src, "w") as fh:
            json.dump(FIXTURE, fh)
        cls.out = os.path.join(cls.tmp, "status.xlsx")
        r = run_builder([cls.out, cls.src, "--title", "Fixture title", "--asof", "2026-01-02 03:04Z",
                         "--sha", "abc1234"])
        assert r.returncode == 0, r.stderr
        cls.mods, cls.areas, cls.overall = expected(FIXTURE)
        cls.book, cls.parts, cls.read_error = None, None, None
        try:
            cls.book, cls.parts = read_book(cls.out)
        except Exception as e:   # a broken part must fail the tests, not abort the whole class
            cls.read_error = e

    def need(self):
        if self.read_error is not None:
            self.fail(f"workbook unreadable or not well-formed: {self.read_error!r}")

    def test_zip_and_every_part_well_formed(self):
        self.need()
        self.assertIn("xl/worksheets/sheet1.xml", self.parts)
        self.assertEqual(set(self.book), {"Summary", "Modules", "Items"})
        for name, root in self.parts.items():
            self.assertIsNotNone(root.tag, name)
        wb = self.parts["xl/workbook.xml"]
        self.assertEqual(wb.find(M + "calcPr").get("fullCalcOnLoad"), "1")

    def test_items_sheet_matches_json(self):
        self.need()
        got = sorted((r[0], r[1], r[2], r[3], r[4] or "") for r in grid(self.book, "Items"))
        self.assertEqual(got, expected_item_rows(FIXTURE))

    def test_modules_counts_and_pct_match_json(self):
        self.need()
        rows = grid(self.book, "Modules")
        self.assertEqual(len(rows), len(self.mods))
        for row in rows:
            area, name, path, n, done, partial, ns, pct = row
            want = self.mods[name]
            self.assertEqual(area, want["area"], name)
            self.assertEqual((n, done, partial, ns), (want["items"], want["done"], want["partial"], want["ns"]), name)
            self.assertAlmostEqual(pct, want["pct"], places=9, msg=name)

    def summary_rows(self, book=None):
        """Area rows start at row 5 of Summary and end at the row whose column A is 'Overall'."""
        cells = (book or self.book)["Summary"]
        out, r = {}, 5
        while True:
            a = cells.get(f"A{r}", (None, None))[0]
            values = [cells.get(f"{c}{r}", (None, None))[0] for c in "BCDEFG"]
            if a == "Overall":
                return out, values
            if a is None:
                raise AssertionError("no Overall row found")
            out[a] = values
            r += 1

    def test_summary_per_area_and_overall_match_json(self):
        self.need()
        by_area, overall = self.summary_rows()
        self.assertEqual(set(by_area), set(self.areas))
        for a, want in self.areas.items():
            mods_, items, done, partial, ns, pct = by_area[a]
            self.assertEqual((mods_, items, done, partial, ns), (want["modules"], want["items"], want["done"],
                                                              want["partial"], want["ns"]), a)
            self.assertAlmostEqual(pct, want["pct"], places=9, msg=a)
        o = self.overall
        self.assertEqual(overall[:5], [o["modules"], o["items"], o["done"], o["partial"], o["ns"]])
        self.assertAlmostEqual(overall[5], o["pct"], places=9)

    def test_spot_values_by_hand(self):
        self.need()
        # Hand count written into the test, checked against the WORKBOOK (not against expected()):
        # 6 modules, 8 items (alpha 3, beta 3, gamma 1, x-y 1), 4 done, 2 partial, 2 not started.
        by_area, overall = self.summary_rows()
        self.assertEqual(overall[:5], [6, 8, 4, 2, 2])
        self.assertAlmostEqual(overall[5], 0.5)
        self.assertAlmostEqual(by_area["alpha"][5], 1 / 3)   # 1 done of 3: the PARTIAL item is not done
        self.assertEqual(by_area["delta"][5], 0.0)           # area with no items: 0%, no division error
        self.assertIn("x-y", by_area)                        # area name keeps its hyphen
        mods = {row[1]: row for row in grid(self.book, "Modules")}
        self.assertAlmostEqual(mods["alpha_core"][7], 0.5)   # 1 done of 2 items

    def test_every_count_is_a_live_formula_and_recomputes_to_cache(self):
        self.need()
        n_formulas = 0
        for sheet in ("Summary", "Modules"):
            for ref, (val, f) in self.book[sheet].items():
                if f is None:
                    continue
                n_formulas += 1
                got = recompute(f, sheet, self.book)
                if isinstance(val, float):
                    self.assertAlmostEqual(got, val, places=9, msg=f"{sheet}!{ref} = {f}")
                else:
                    self.assertEqual(got, val, f"{sheet}!{ref}")
        self.assertGreater(n_formulas, 20)   # guard against a vacuous pass

    def test_count_cells_hold_formulas_not_numbers(self):
        self.need()
        for sheet, refs in (("Modules", ["D2", "E2", "F2", "G2", "H2"]), ("Summary", ["B5", "C5", "D5", "E5", "F5", "G5"])):
            for ref in refs:
                self.assertIsNotNone(self.book[sheet][ref][1], f"{sheet}!{ref} has no formula")

    def test_builder_uses_stdlib_only_and_no_hard_coded_areas(self):
        with open(SCRIPT, encoding="utf-8") as fh:
            src = fh.read()
        for node in ast.walk(ast.parse(src)):
            names = []
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or ""]
            for n in names:
                self.assertIn(n.split(".")[0], sys.stdlib_module_names, n)
        for banned in ("tier", "CORE", "DEPLOY", "side("):
            self.assertNotIn(banned, src)

    def test_cli_title_asof_sha_appear_on_summary(self):
        self.need()
        self.assertEqual(self.book["Summary"]["A1"][0], "Fixture title")
        info = self.book["Summary"]["A2"][0]
        self.assertIn("2026-01-02 03:04Z", info)
        self.assertIn("abc1234", info)

    def test_bad_status_is_refused_and_nothing_written(self):
        bad = os.path.join(self.tmp, "bad.json")
        with open(bad, "w") as fh:
            json.dump({"modules": [{"name": "m", "path": "a/m", "items": [
                {"item": "i", "status": "PARTLY", "evidence": ""}]}]}, fh)
        out = os.path.join(self.tmp, "bad.xlsx")
        r = run_builder([out, bad])
        self.assertNotEqual(r.returncode, 0)
        self.assertFalse(os.path.exists(out))

    def test_module_without_path_is_refused(self):
        bad = os.path.join(self.tmp, "nopath.json")
        with open(bad, "w") as fh:
            json.dump({"modules": [{"name": "m", "items": []}]}, fh)
        r = run_builder([os.path.join(self.tmp, "np.xlsx"), bad])
        self.assertNotEqual(r.returncode, 0)

    def test_empty_path_string_is_refused(self):
        bad = os.path.join(self.tmp, "emptypath.json")
        with open(bad, "w") as fh:
            json.dump({"modules": [{"name": "m", "path": "", "items": []}]}, fh)
        r = run_builder([os.path.join(self.tmp, "ep.xlsx"), bad])
        self.assertNotEqual(r.returncode, 0)
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "ep.xlsx")))

    def test_empty_modules_list_still_builds_valid_workbook(self):
        empty = os.path.join(self.tmp, "empty.json")
        with open(empty, "w") as fh:
            json.dump({"modules": []}, fh)
        out = os.path.join(self.tmp, "empty.xlsx")
        r = run_builder([out, empty])
        self.assertEqual(r.returncode, 0, r.stderr)
        book, _ = read_book(out)
        by_area, overall = self.summary_rows(book)
        self.assertEqual(by_area, {})
        self.assertEqual(overall[0], 0.0)                 # Overall modules, no area rows
        for sheet in ("Summary", "Modules"):
            for ref, (val, f) in book[sheet].items():
                if f:
                    self.assertEqual(recompute(f, sheet, book), val, f"{sheet}!{ref}")

    def test_duplicate_module_name_is_refused(self):
        dup = os.path.join(self.tmp, "dup.json")
        m = {"name": "m", "path": "a/m", "items": []}
        with open(dup, "w") as fh:
            json.dump({"modules": [m, m]}, fh)
        r = run_builder([os.path.join(self.tmp, "dup.xlsx"), dup])
        self.assertNotEqual(r.returncode, 0)


if __name__ == "__main__":
    unittest.main()
