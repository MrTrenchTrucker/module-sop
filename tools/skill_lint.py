#!/usr/bin/env python3
"""Standalone-skill gate: a class skill must be usable with NOTHING else loaded.

Usage: tools/skill_lint.py [REPO_ROOT] [--file PATH --class CLASS]   exit 0 = clean, 1 = any violation.
Rules: (1) no pointer to another document (SOP names, sections, appendices, docs/, references/, the repo);
(2) no private identifiers (your agents' names, hosts, internal systems, private addresses and paths) -
    skills are generic. Your own names are not in this file: list them one per line in
    .sop/private_names.txt (git-ignored; lines starting with # are comments);
(3) the class SOP's Quick Reference and One-Paragraph Version appear VERBATIM (the fidelity anchor);
(4) frontmatter name is the registered skill name; (5) no references/ folder ships with the skill.
Allowed references: other skills named parrot-protocol-<class>, and the project's own working files.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sections import section  # noqa: E402

CLASSES = {
    'project-leader': ('module-sop-project-leader', 'PROJECT_LEADER_SOP.md'),
    'itm': ('module-sop-itm', 'IT_MANAGER_SOP.md'),
    'worker': ('module-sop-worker', 'WORKER_SOP.md'),
}
# the project's own working files a skill legitimately names (the system it teaches), not documents to go read
ALLOWED_FILES = {'ARCHITECTURE.md', 'AGENTS.md', 'README.md', 'APPROVALS.md', 'SMOKE_TEST.md', 'MODULE_MAP.md', 'WO-NNN.md',
                 'ADR-NNN.md', 'ADR-MMM.md'}
RULES = [
    ('sop_document', re.compile(r'\b(MODULE|COMMANDER|PROJECT[ _]LEADER|IT[ _]MANAGER|WORKER)[ _]SOP\b', re.I)),
    ('section_pointer', re.compile(r'§|\bSection \d|\bAppendix [A-G]\b|\bsee (the )?(master|companion)\b', re.I)),
    ('doc_path', re.compile(r'\b(docs|references)/|\bmodule-sop\b(?!-)', re.I)),
    ('host_path_ip', re.compile(r'/mnt/|/opt/|/root/|\b192\.168\.\d|\b10\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
                                r'|\b172\.(1[6-9]|2\d|3[01])\.\d')),
]
PRIVATE_NAMES_FILE = os.path.join('.sop', 'private_names.txt')


def _private_names_rule(root):
    """Return the ('private_name', regex) rule built from ROOT/.sop/private_names.txt, or None if absent or empty."""
    try:
        with open(os.path.join(root, PRIVATE_NAMES_FILE), encoding='utf-8') as f:
            names = [n.strip() for n in f if n.strip() and not n.lstrip().startswith('#')]
    except FileNotFoundError:
        return None
    if not names:
        return None
    return ('private_name', re.compile(r'(?<![\w-])(' + '|'.join(re.escape(n) for n in names) + r')(?![\w-])'))


MD_FILE = re.compile(r'\b[\w./-]+\.md\b')
SKILL_REF = re.compile(r'\bparrot-protocol-(project-leader|itm|worker)\b')


def skill_path(root, cls):
    """Return the path of a class's MODULE-standard skill inside its class pack."""
    return os.path.join(root, 'skills', cls, f'module-sop-{cls}', 'SKILL.md')


def lint(path, cls, root):
    """Return a list of violation strings for one SKILL.md."""
    name, src = CLASSES[cls]
    text = open(path).read()
    out = []
    rules = RULES + [r for r in (_private_names_rule(root),) if r]
    m = re.match(r'^---\nname: (\S+)\ndescription: >-\n(.+?)\n---\n', text, re.S)
    if not m or m.group(1) != name:
        out.append(f'frontmatter: name must be {name}')
    body = text[m.end():] if m else text
    for i, line in enumerate(text.splitlines(), 1):
        if i <= 5 and line.startswith('name: '):
            continue
        for rule, rx in rules:
            for hit in rx.finditer(line):
                out.append(f'{rule} line {i}: {hit.group(0)!r}: {line.strip()[:120]}')
        for f in MD_FILE.findall(line):
            if f.split('/')[-1] not in ALLOWED_FILES and not re.fullmatch(r'(workorders/WO|decisions/ADR)-[A-Z0-9]+\.md', f):
                out.append(f'md_file line {i}: {f!r} is not one of the project working files')
    t = open(os.path.join(root, 'docs', src)).read()
    for h, stop in (('## Quick Reference', '## One-Paragraph Version'), ('## One-Paragraph Version', None)):
        if section(t, h, stop).rstrip('\n') not in body:
            out.append(f'fidelity: "{h}" is not verbatim from the {cls} SOP')
    want = f'parrot-protocol-{cls}'
    if want not in body:
        out.append(f'pairing: the skill must name its readback skill `{want}`')
    for ref in set(SKILL_REF.findall(body)) - {cls}:
        out.append(f'pairing: names another class\'s skill parrot-protocol-{ref}')
    if os.path.isdir(os.path.join(os.path.dirname(path), 'references')):
        out.append('packaging: a references/ folder ships with the skill (a standalone skill carries everything in SKILL.md)')
    return out


def main(argv):
    args = [a for a in argv if not a.startswith('--')]
    if '--file' in argv:
        try:
            path = argv[argv.index('--file') + 1]
            cls = argv[argv.index('--class') + 1]
        except (ValueError, IndexError):
            print('usage: tools/skill_lint.py [REPO_ROOT] [--file PATH --class CLASS]', file=sys.stderr)
            return 2
        if cls not in CLASSES:
            print(f'unknown class {cls!r} (one of: {", ".join(CLASSES)})', file=sys.stderr)
            return 2
        root = args[0] if args and os.path.isdir(os.path.join(args[0], 'docs')) else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        targets = [(path, cls)]
    else:
        root = args[0] if args else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        targets = [(skill_path(root, c), c) for c in CLASSES]
    bad = 0
    for path, cls in targets:
        v = lint(path, cls, root)
        size = os.path.getsize(path)
        print(f'{cls}: {"CLEAN" if not v else f"{len(v)} VIOLATION(S)"}  ({size} bytes)')
        for x in v:
            print('   ', x)
        bad += len(v)
    print('RESULT', 'PASS' if not bad else f'FAIL ({bad})')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
