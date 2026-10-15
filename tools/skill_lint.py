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
Shared skills (skills/shared/, ADR-010) get rules (1), (2), (4) and (5); they have no class SOP, so no fidelity check, and they
name no class skill and no model, model vendor or agent harness. CLI: tools/skill_lint.py --file PATH --shared NAME.
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
CLASS_SKILL = re.compile(r'\b(parrot-protocol|module-sop)-(project-leader|itm|worker)\b')
FRONTMATTER = re.compile(r'^---\nname: (\S+)\ndescription: >-\n(.+?)\n---\n', re.S)
# a shared skill names no model, model vendor or agent harness (ADR-010); class skills are not held to this
MODEL_HARNESS = re.compile(r'\b(Claude|Anthropic|Haiku|Sonnet|Opus|Fable|GPT[-\w.]*|ChatGPT|OpenAI|Gemini|Qwen|Llama|'
                           r'Mistral|DeepSeek|Nemotron|Hermes|Codex|Cursor|Copilot|Aider)\b')
# shared skills any class may carry: skill name -> folder under skills/ (ADR-010)
SHARED = {'subagent-plan-file': 'shared/subagent-plan-file'}


def skill_path(root, cls):
    """Return the path of a class's MODULE-standard skill inside its class pack."""
    return os.path.join(root, 'skills', cls, f'module-sop-{cls}', 'SKILL.md')


def shared_skill_path(root, name):
    """Return the path of a shared skill inside the shared pack."""
    return os.path.join(root, 'skills', *SHARED[name].split('/'), 'SKILL.md')


def _line_findings(text, root):
    """Rules (1) and (2), line by line: pointers to other documents, private names, other .md files."""
    out = []
    rules = RULES + [r for r in (_private_names_rule(root),) if r]
    for i, line in enumerate(text.splitlines(), 1):
        if i <= 5 and line.startswith('name: '):
            continue
        for rule, rx in rules:
            for hit in rx.finditer(line):
                out.append(f'{rule} line {i}: {hit.group(0)!r}: {line.strip()[:120]}')
        for f in MD_FILE.findall(line):
            if f.split('/')[-1] not in ALLOWED_FILES and not re.fullmatch(r'(workorders/WO|decisions/ADR)-[A-Z0-9]+\.md', f):
                out.append(f'md_file line {i}: {f!r} is not one of the project working files')
    return out


def _packaging(path):
    if os.path.isdir(os.path.join(os.path.dirname(path), 'references')):
        return ['packaging: a references/ folder ships with the skill (a standalone skill carries everything in SKILL.md)']
    return []


def lint_shared(path, name, root=None):
    """Return a list of violation strings for one shared SKILL.md: rules (1), (2), (4), (5), no class skill, model or harness."""
    root = root or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    text = open(path).read()
    out = []
    m = FRONTMATTER.match(text)
    if not m or m.group(1) != name:
        out.append(f'frontmatter: name must be {name}')
    out += _line_findings(text, root)
    for i, line in enumerate(text.splitlines(), 1):
        for hit in MODEL_HARNESS.finditer(line):
            out.append(f'model_harness line {i}: {hit.group(0)!r}: {line.strip()[:120]}')
    for hit in sorted(set(CLASS_SKILL.findall(text[m.end():] if m else text))):
        out.append(f'pairing: a shared skill names no class skill, found {hit[0]}-{hit[1]}')
    return out + _packaging(path)


def lint(path, cls, root):
    """Return a list of violation strings for one SKILL.md."""
    name, src = CLASSES[cls]
    text = open(path).read()
    out = []
    m = FRONTMATTER.match(text)
    if not m or m.group(1) != name:
        out.append(f'frontmatter: name must be {name}')
    body = text[m.end():] if m else text
    out += _line_findings(text, root)
    t = open(os.path.join(root, 'docs', src)).read()
    for h, stop in (('## Quick Reference', '## One-Paragraph Version'), ('## One-Paragraph Version', None)):
        if section(t, h, stop).rstrip('\n') not in body:
            out.append(f'fidelity: "{h}" is not verbatim from the {cls} SOP')
    want = f'parrot-protocol-{cls}'
    if want not in body:
        out.append(f'pairing: the skill must name its readback skill `{want}`')
    for ref in set(SKILL_REF.findall(body)) - {cls}:
        out.append(f'pairing: names another class\'s skill parrot-protocol-{ref}')
    return out + _packaging(path)


def main(argv):
    args = [a for a in argv if not a.startswith('--')]
    if '--file' in argv and '--shared' in argv:
        path, name = argv[argv.index('--file') + 1], argv[argv.index('--shared') + 1]
        args = [a for a in args if a not in (path, name)]
        root = args[0] if args else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        targets = [(path, 'shared', name)]
    elif '--file' in argv:
        path, cls = argv[argv.index('--file') + 1], argv[argv.index('--class') + 1]
        root = args[0] if args and os.path.isdir(os.path.join(args[0], 'docs')) else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        targets = [(path, cls, None)]
    else:
        root = args[0] if args else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        targets = [(skill_path(root, c), c, None) for c in CLASSES] + [(shared_skill_path(root, n), 'shared', n) for n in SHARED]
    bad = 0
    for path, cls, name in targets:
        v = lint_shared(path, name, root) if name else lint(path, cls, root)
        size = os.path.getsize(path)
        print(f'{name or cls}: {"CLEAN" if not v else f"{len(v)} VIOLATION(S)"}  ({size} bytes)')
        for x in v:
            print('   ', x)
        bad += len(v)
    print('RESULT', 'PASS' if not bad else f'FAIL ({bad})')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
