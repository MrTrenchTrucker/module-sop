#!/usr/bin/env python3
"""Build a module status workbook (.xlsx) from one status JSON. Standard library only.

usage: module_status_xlsx.py OUT.xlsx STATUS.json [--title TEXT] [--asof TEXT] [--sha TEXT]

STATUS.json shape:
  {"modules": [{"name": str, "path": str,
                "items": [{"item": str, "status": "DONE|PARTIAL|NOT_STARTED", "evidence": str}]}]}

The area of a module is the first segment of its "path": "alpha/modules/core" -> "alpha".
Sheets:
  Summary  one row per area, then an Overall row: modules, items, done, partial, not started, % complete
  Modules  one row per module: area, module, path, items, done, partial, not started, % complete
  Items    the data: area, module, item, status, evidence
Counts are live COUNTIF / COUNTIFS formulas over the Items and Modules sheets. Cached values are
computed here the same way, and the workbook is flagged fullCalcOnLoad so a spreadsheet recalculates
on open. Module names are used as COUNTIF criteria, so avoid * and ? in module names.
"""
import argparse
import json
import re
import sys
import zipfile
from xml.sax.saxutils import escape

STATUSES = ("DONE", "PARTIAL", "NOT_STARTED")
NS = 'xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"'
RELS_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
BAD_XML = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f￾￿]")

# indexes into cellXfs (see STYLES below)
ST_DEFAULT, ST_HEAD, ST_PCT, ST_BOLD, ST_TITLE, ST_WRAP, ST_CENTER = range(7)
ST_TOT_NUM, ST_TOT_PCT, ST_TOT_TEXT, ST_PCT_TOP = 7, 8, 9, 10


def _clean(text):
    return BAD_XML.sub("?", str(text))


def _area_of(path):
    """First segment of a module path: 'alpha/modules/core' -> 'alpha'."""
    seg = _clean(path).strip().strip("/").split("/")[0].strip()
    if not seg:
        raise ValueError(f"module path {path!r} has no area segment")
    return seg


def _load(path):
    """Read the status JSON; return the modules sorted by (area, name)."""
    with open(path, encoding="utf-8") as fh:
        doc = json.load(fh)
    mods = doc.get("modules") if isinstance(doc, dict) else None
    if not isinstance(mods, list):
        raise ValueError('status file must be {"modules": [...]}')
    out, seen = [], set()
    for m in mods:
        try:
            name = _clean(m["name"])
            path = _clean(m["path"])
            area = _area_of(path)
            items = []
            for it in m.get("items", []):
                st = str(it["status"]).strip().upper()
                if st not in STATUSES:
                    raise ValueError(f"bad status {st!r} in module {name!r}")
                items.append((_clean(it["item"]), st, _clean(it.get("evidence", ""))))
        except (KeyError, TypeError) as e:
            raise ValueError(f"module entry needs name, path and items with item and status: {e}")
        if name in seen:
            raise ValueError(f"duplicate module name {name!r}")
        seen.add(name)
        out.append({"area": area, "name": name, "path": path, "items": items})
    out.sort(key=lambda x: (x["area"], x["name"]))
    return out


def _tally(items):
    counts = {s: 0 for s in STATUSES}
    for _, st, _ in items:
        counts[st] += 1
    return counts


def _pct(part, whole):
    return part / whole if whole else 0.0


def _col(n):  # 1 -> A
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def _num_xml(v):
    return str(v) if isinstance(v, int) else repr(float(v))


class _SST:
    """Workbook string table (sharedStrings part)."""

    def __init__(self):
        self.items, self.index, self.refs = [], {}, 0

    def add(self, text):
        text = _clean(text)
        self.refs += 1
        if text not in self.index:
            self.index[text] = len(self.items)
            self.items.append(text)
        return self.index[text]

    def xml(self):
        body = "".join(f'<si><t xml:space="preserve">{escape(t)}</t></si>' for t in self.items)
        return (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                f'<sst {NS} count="{self.refs}" uniqueCount="{len(self.items)}">{body}</sst>')


class _Sheet:
    def __init__(self):
        self.cells = {}   # row -> col -> (kind, value, style, formula)
        self.heights = {}

    def set(self, r, c, kind, value, style=ST_DEFAULT, formula=None):
        self.cells.setdefault(r, {})[c] = (kind, value, style, formula)

    def rows_xml(self, sst):
        parts = []
        for r in sorted(self.cells):
            cells = []
            for c in sorted(self.cells[r]):
                kind, value, style, formula = self.cells[r][c]
                ref = f"{_col(c)}{r}"
                if kind == "s":
                    cells.append(f'<c r="{ref}" s="{style}" t="s"><v>{sst.add(value)}</v></c>')
                elif formula is None:
                    cells.append(f'<c r="{ref}" s="{style}"><v>{_num_xml(value)}</v></c>')
                else:
                    cells.append(f'<c r="{ref}" s="{style}"><f>{escape(formula)}</f>'
                                 f'<v>{_num_xml(value)}</v></c>')
            ht = f' ht="{self.heights[r]}" customHeight="1"' if r in self.heights else ""
            parts.append(f'<row r="{r}"{ht}>{"".join(cells)}</row>')
        return "".join(parts)

    def xml(self, sst, widths, freeze=False, autofilter=None, extra=""):
        if freeze:
            views = ('<sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" '
                     'activePane="bottomLeft" state="frozen"/></sheetView></sheetViews>')
        else:
            views = '<sheetViews><sheetView workbookViewId="0"/></sheetViews>'
        cols = "<cols>" + "".join(f'<col min="{i}" max="{i}" width="{w}" customWidth="1"/>'
                                  for i, w in enumerate(widths, 1)) + "</cols>"
        af = f'<autoFilter ref="{autofilter}"/>' if autofilter else ""
        return (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<worksheet {NS}>{views}'
                f'<sheetFormatPr defaultRowHeight="15"/>{cols}<sheetData>{self.rows_xml(sst)}</sheetData>'
                f'{af}{extra}</worksheet>')


STYLES = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet {NS}>
<fonts count="4"><font><sz val="11"/><name val="Calibri"/></font><font><b/><sz val="11"/><name val="Calibri"/></font><font><b/><sz val="11"/><color rgb="FFFFFFFF"/><name val="Calibri"/></font><font><b/><sz val="15"/><name val="Calibri"/></font></fonts>
<fills count="4"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill><fill><patternFill patternType="solid"><fgColor rgb="FF1F3864"/><bgColor indexed="64"/></patternFill></fill><fill><patternFill patternType="solid"><fgColor rgb="FFE2EFDA"/><bgColor indexed="64"/></patternFill></fill></fills>
<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>
<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
<cellXfs count="11">
<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>
<xf numFmtId="0" fontId="2" fillId="2" borderId="0" xfId="0" applyFont="1" applyFill="1" applyAlignment="1"><alignment horizontal="center" vertical="center" wrapText="1"/></xf>
<xf numFmtId="9" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1" applyAlignment="1"><alignment horizontal="center"/></xf>
<xf numFmtId="0" fontId="1" fillId="0" borderId="0" xfId="0" applyFont="1"/>
<xf numFmtId="0" fontId="3" fillId="0" borderId="0" xfId="0" applyFont="1"/>
<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0" applyAlignment="1"><alignment vertical="top" wrapText="1"/></xf>
<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0" applyAlignment="1"><alignment horizontal="center" vertical="top"/></xf>
<xf numFmtId="0" fontId="1" fillId="3" borderId="0" xfId="0" applyFont="1" applyFill="1" applyAlignment="1"><alignment horizontal="center"/></xf>
<xf numFmtId="9" fontId="1" fillId="3" borderId="0" xfId="0" applyNumberFormat="1" applyFont="1" applyFill="1" applyAlignment="1"><alignment horizontal="center"/></xf>
<xf numFmtId="0" fontId="1" fillId="3" borderId="0" xfId="0" applyFont="1" applyFill="1"/>
<xf numFmtId="9" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1" applyAlignment="1"><alignment horizontal="center" vertical="top"/></xf>
</cellXfs>
<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>
<dxfs count="0"/>
</styleSheet>'''


def _write_workbook(out_path, mods, title, asof, sha):
    sst = _SST()
    flat = [(m["area"], m["name"], item, st, ev) for m in mods for (item, st, ev) in m["items"]]
    LI = max(2, len(flat) + 1)   # last Items row; never below 2 so the ranges stay valid when empty
    LM = max(2, len(mods) + 1)   # last Modules row
    IA, IB, ID = f"Items!$A$2:$A${LI}", f"Items!$B$2:$B${LI}", f"Items!$D$2:$D${LI}"
    MA, MB = f"Modules!$A$2:$A${LM}", f"Modules!$B$2:$B${LM}"
    areas = sorted({m["area"] for m in mods})

    # Items: the data
    items = _Sheet()
    for c, h in enumerate(["Area", "Module", "Sub-module / work item", "Status", "Evidence"], 1):
        items.set(1, c, "s", h, ST_HEAD)
    for r, (area, name, item, st, ev) in enumerate(flat, start=2):
        items.set(r, 1, "s", area, ST_WRAP)
        items.set(r, 2, "s", name, ST_WRAP)
        items.set(r, 3, "s", item, ST_WRAP)
        items.set(r, 4, "s", st, ST_CENTER)
        items.set(r, 5, "s", ev, ST_WRAP)
    items_dv = (f'<dataValidations count="1"><dataValidation type="list" allowBlank="0" showErrorMessage="1" '
                f'sqref="D2:D{LI}"><formula1>"DONE,PARTIAL,NOT_STARTED"</formula1></dataValidation></dataValidations>')

    # Modules: one row per module, counted from Items
    modules = _Sheet()
    modules.heights[1] = 32
    for c, h in enumerate(["Area", "Module", "Path", "Items", "Done", "Partial", "Not started", "% complete"], 1):
        modules.set(1, c, "s", h, ST_HEAD)
    for r, m in enumerate(mods, start=2):
        cnt, n = _tally(m["items"]), len(m["items"])
        modules.set(r, 1, "s", m["area"], ST_WRAP)
        modules.set(r, 2, "s", m["name"], ST_WRAP)
        modules.set(r, 3, "s", m["path"], ST_WRAP)
        modules.set(r, 4, "n", n, ST_CENTER, f"COUNTIF({IB},B{r})")
        modules.set(r, 5, "n", cnt["DONE"], ST_CENTER, f'COUNTIFS({IB},B{r},{ID},"DONE")')
        modules.set(r, 6, "n", cnt["PARTIAL"], ST_CENTER, f'COUNTIFS({IB},B{r},{ID},"PARTIAL")')
        modules.set(r, 7, "n", cnt["NOT_STARTED"], ST_CENTER, f'COUNTIFS({IB},B{r},{ID},"NOT_STARTED")')
        modules.set(r, 8, "n", _pct(cnt["DONE"], n), ST_PCT_TOP, f"IF(D{r}=0,0,E{r}/D{r})")

    # Summary: one row per area, then Overall; all counts are live
    summ = _Sheet()
    summ.set(1, 1, "s", title, ST_TITLE)
    info = ", ".join(x for x in [f"As of {asof}" if asof else "", f"revision {sha}" if sha else "" ] if x)
    summ.set(2, 1, "s", (info + ". " if info else "")
             + "Every count below is a live formula over the Modules and Items sheets.")
    summ.heights[4] = 32
    for c, h in enumerate(["Area", "Modules", "Items", "Done", "Partial", "Not started", "% complete"], 1):
        summ.set(4, c, "s", h, ST_HEAD)
    printed = []
    r = 5
    for a in areas:
        ms = [m for m in mods if m["area"] == a]
        its = [x for m in ms for x in m["items"]]
        cnt, n = _tally(its), len(its)
        summ.set(r, 1, "s", a, ST_BOLD)
        summ.set(r, 2, "n", len(ms), ST_CENTER, f"COUNTIF({MA},A{r})")
        summ.set(r, 3, "n", n, ST_CENTER, f"COUNTIF({IA},A{r})")
        summ.set(r, 4, "n", cnt["DONE"], ST_CENTER, f'COUNTIFS({IA},A{r},{ID},"DONE")')
        summ.set(r, 5, "n", cnt["PARTIAL"], ST_CENTER, f'COUNTIFS({IA},A{r},{ID},"PARTIAL")')
        summ.set(r, 6, "n", cnt["NOT_STARTED"], ST_CENTER, f'COUNTIFS({IA},A{r},{ID},"NOT_STARTED")')
        summ.set(r, 7, "n", _pct(cnt["DONE"], n), ST_PCT, f"IF(C{r}=0,0,D{r}/C{r})")
        printed.append((a, len(ms), n, cnt))
        r += 1
    all_items = [x for m in mods for x in m["items"]]
    cnt, n = _tally(all_items), len(all_items)
    summ.set(r, 1, "s", "Overall", ST_TOT_TEXT)
    summ.set(r, 2, "n", len(mods), ST_TOT_NUM, f"COUNTA({MB})")
    summ.set(r, 3, "n", n, ST_TOT_NUM, f"COUNTA({ID})")
    summ.set(r, 4, "n", cnt["DONE"], ST_TOT_NUM, f'COUNTIF({ID},"DONE")')
    summ.set(r, 5, "n", cnt["PARTIAL"], ST_TOT_NUM, f'COUNTIF({ID},"PARTIAL")')
    summ.set(r, 6, "n", cnt["NOT_STARTED"], ST_TOT_NUM, f'COUNTIF({ID},"NOT_STARTED")')
    summ.set(r, 7, "n", _pct(cnt["DONE"], n), ST_TOT_PCT, f"IF(C{r}=0,0,D{r}/C{r})")
    overall = (len(mods), n, cnt)
    notes = ["How to read this",
             "Done counts only DONE items. PARTIAL and NOT_STARTED items are not counted as done.",
             "% complete = done items / all items. An area or module with no items shows 0%.",
             "Edit the Status column on the Items sheet (DONE / PARTIAL / NOT_STARTED) and the Modules and Summary numbers update."]
    for i, t in enumerate(notes):
        summ.set(r + 2 + i, 1, "s", t, ST_BOLD if i == 0 else ST_DEFAULT)

    parts = {
        "xl/worksheets/sheet1.xml": summ.xml(sst, [30, 11, 11, 11, 11, 13, 14]),
        "xl/worksheets/sheet2.xml": modules.xml(sst, [18, 26, 34, 9, 9, 9, 13, 14], freeze=True,
                                                autofilter=f"A1:H{LM}"),
        "xl/worksheets/sheet3.xml": items.xml(sst, [18, 26, 46, 14, 80], freeze=True,
                                              autofilter=f"A1:E{LI}", extra=items_dv),
    }
    wb = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<workbook {NS} xmlns:r="{RELS_NS}"><sheets>'
          '<sheet name="Summary" sheetId="1" r:id="rId1"/><sheet name="Modules" sheetId="2" r:id="rId2"/>'
          '<sheet name="Items" sheetId="3" r:id="rId3"/></sheets>'
          f'<definedNames><definedName name="_xlnm._FilterDatabase" localSheetId="1" hidden="1">Modules!$A$1:$H${LM}</definedName>'
          f'<definedName name="_xlnm._FilterDatabase" localSheetId="2" hidden="1">Items!$A$1:$E${LI}</definedName></definedNames>'
          '<calcPr calcId="191029" fullCalcOnLoad="1"/></workbook>')
    wbrels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
              '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
              + "".join(f'<Relationship Id="rId{i}" Type="{RELS_NS}/worksheet" Target="worksheets/sheet{i}.xml"/>'
                        for i in (1, 2, 3))
              + f'<Relationship Id="rId4" Type="{RELS_NS}/styles" Target="styles.xml"/>'
              + f'<Relationship Id="rId5" Type="{RELS_NS}/sharedStrings" Target="sharedStrings.xml"/></Relationships>')
    ctypes = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
              '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
              '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
              '<Default Extension="xml" ContentType="application/xml"/>'
              '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
              + "".join(f'<Override PartName="/xl/worksheets/sheet{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
                        for i in (1, 2, 3))
              + '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
              '<Override PartName="/xl/sharedStrings.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sharedStrings+xml"/></Types>')
    rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            f'<Relationship Id="rId1" Type="{RELS_NS}/officeDocument" Target="xl/workbook.xml"/></Relationships>')

    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", ctypes)
        z.writestr("_rels/.rels", rels)
        z.writestr("xl/workbook.xml", wb)
        z.writestr("xl/_rels/workbook.xml.rels", wbrels)
        z.writestr("xl/styles.xml", STYLES)
        for name in sorted(parts):
            z.writestr(name, parts[name])
        z.writestr("xl/sharedStrings.xml", sst.xml())   # last: every sheet has registered its strings
    return printed, overall


def main(argv=None):
    ap = argparse.ArgumentParser(description="Build a module status workbook (.xlsx) from a status JSON.")
    ap.add_argument("out", help="workbook to write (.xlsx)")
    ap.add_argument("status", help='status JSON: {"modules": [...]}')
    ap.add_argument("--title", default="Module status", help="title on the Summary sheet")
    ap.add_argument("--asof", default="", help="date text shown on the Summary sheet")
    ap.add_argument("--sha", default="", help="revision text shown on the Summary sheet")
    args = ap.parse_args(argv)
    try:
        mods = _load(args.status)
    except (OSError, ValueError) as e:
        sys.exit(f"module_status_xlsx: {e}")
    printed, (nmod, nitem, cnt) = _write_workbook(args.out, mods, _clean(args.title), _clean(args.asof), _clean(args.sha))
    for a, nm, n, c in printed:
        print(f"{a}: modules {nm}, items {n}, done {c['DONE']}, partial {c['PARTIAL']}, "
              f"not started {c['NOT_STARTED']}, {round(100 * _pct(c['DONE'], n))}% complete")
    print(f"Overall: modules {nmod}, items {nitem}, done {cnt['DONE']}, partial {cnt['PARTIAL']}, "
          f"not started {cnt['NOT_STARTED']}, {round(100 * _pct(cnt['DONE'], nitem))}% complete")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
