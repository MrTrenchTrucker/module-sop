#!/usr/bin/env python3
"""Module docs checks (MODULE SOP sections 5.2, 5.3, 9.1 and 9.8).

Every module, at every level, carries a card (`AGENTS.md`) and a `README.md`. The card must agree with the registry,
and a code module's registry `public` list must be its real public functions. A parent's README names each of its
sub-modules. And a module whose code changed since the base commit must have changed its README too, unless a work
order carries a README waiver for it. Modules marked `docs_pending` in the registry are skipped (section 12.2).

Usage: doc_check.py [--base REF]   exit 1 on any finding. The base defaults to $SOP_BASE, then the merge-base with main.
The base must be the commit the work order started from: on a branch carrying several slices, set SOP_BASE per slice,
or a later slice rides on an earlier slice's README edit.
"""
import argparse
import ast
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sections import section  # noqa: E402

WAIVER = re.compile(r'README waiver:\s*`?([A-Za-z0-9_]+)`?\s*:\s*\S')
CLI_ENTRY = 'main'


def _code_public(root, m):
    """Public top-level functions and classes of a code module, as `file.name`."""
    names, full = set(), os.path.join(root, m['path'])
    for fn in sorted(os.listdir(full)):
        if fn.endswith('.py'):
            for node in ast.parse(open(os.path.join(full, fn)).read()).body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and not node.name.startswith('_'):
                    names.add(f'{fn[:-3]}.{node.name}')
    return names


def _artifacts(root, m):
    """What a non-code module can expose: its file names and the skill names in its SKILL.md files."""
    found = set()
    for dp, _dn, files in os.walk(os.path.join(root, m['path'])):
        for fn in files:
            found.add(fn)
            if fn == 'SKILL.md':
                hit = re.search(r'^name:\s*(\S+)', open(os.path.join(dp, fn)).read(4000), re.M)
                if hit:
                    found.add(hit.group(1))
    return found


def _ticked(text):
    return {t.split('(')[0].strip() for t in re.findall(r'`([^`\n]+)`', text)}


def card_findings(root, reg):
    """Static checks: README present, card matches registry and code, parent README names its sub-modules."""
    mods, out = reg['modules'], []
    by_path = {m['path']: n for n, m in mods.items()}
    for name, m in mods.items():
        if m.get('docs_pending'):
            continue
        p = m['path']
        if not os.path.isfile(os.path.join(root, p, 'README.md')):
            out.append(f'{name}: {p}/README.md is missing. Every module, at every level, needs one: what it does and how it '
                       f'works, in plain words.')
        card_path = os.path.join(root, m['card'])
        if not os.path.isfile(card_path):
            continue  # sop_check reports a missing card
        card = open(card_path).read()
        try:
            iface, deps_text = section(card, '## Public Interface', '## Depends On'), section(card, '## Depends On', '## Invariants')
        except ValueError:
            continue  # sop_check reports a missing card section
        public, code = set(m.get('public', [])), _code_public(root, m)
        exposable = code if code else _artifacts(root, m)
        listed = {t for t in _ticked(iface) if t in exposable or t in public}
        for t in sorted(public - listed):
            out.append(f'{name}: the registry lists `{t}` as public, but the card\'s Public Interface does not. Card and '
                       f'registry must say the same thing; reread {m["card"]}.')
        for t in sorted(listed - public):
            out.append(f'{name}: the card\'s Public Interface lists `{t}`, but the registry\'s public list does not. Card and '
                       f'registry must say the same thing; an interface change goes through your IT manager.')
        if code:
            for t in sorted(code - public):
                if t.split('.', 1)[1] != CLI_ENTRY:
                    out.append(f'{name}: `{t}` is public in the code but not in the registry\'s public list. Name it private '
                               f'(leading underscore) or ask your IT manager to add it to the interface.')
            for t in sorted(public - code):
                out.append(f'{name}: the registry lists `{t}` as public, but the code has no such public function or class. '
                           f'The interface changed without the card and registry; reread {m["card"]}.')
        else:
            for t in sorted(public - exposable):
                out.append(f'{name}: the registry lists `{t}` as public, but nothing in {p}/ provides it.')
        named = {n for n in mods if n != name and re.search(rf'(?<![\w-]){re.escape(n)}(?![\w-])', deps_text)}
        if named != set(m.get('depends_on', [])):
            out.append(f'{name}: the card\'s Depends On names {sorted(named)}, but the registry says '
                       f'{sorted(m.get("depends_on", []))}. Card and registry must say the same thing.')
        parts = p.split('/')
        for i in range(len(parts) - 1, 0, -1):
            parent = by_path.get('/'.join(parts[:i]))
            if parent:
                readme = os.path.join(root, mods[parent]['path'], 'README.md')
                if not mods[parent].get('docs_pending') and os.path.isfile(readme) and \
                        not re.search(rf'(?<![\w-]){re.escape(name)}(?![\w-])', open(readme).read()):
                    out.append(f'{parent}: its README does not name its sub-module `{name}`. A parent\'s README names each of '
                               f'its sub-modules; update {mods[parent]["path"]}/README.md.')
                break
    return out


def resolve_base(root):
    """The commit the work started from: $SOP_BASE, else the merge-base of HEAD with main. Raises if neither resolves."""
    if os.environ.get('SOP_BASE'):
        return os.environ['SOP_BASE']
    for ref in ('origin/main', 'main'):
        r = subprocess.run(['git', '-C', root, 'merge-base', 'HEAD', ref], capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    raise RuntimeError('cannot find the commit your work started from: set SOP_BASE to the base commit in your work order')


def _changed_files(root, base):
    """Files changed since `base`, including uncommitted edits and new untracked files."""
    def git(*a):
        return subprocess.run(['git', '-C', root, *a], capture_output=True, text=True, check=True).stdout.split('\n')
    return {f for f in set(git('diff', '--name-only', base)) | set(git('ls-files', '--others', '--exclude-standard')) if f}


def freshness_findings(root, reg, base):
    """A module whose code changed since `base` must also have changed its README, or carry a README waiver."""
    mods, changed = reg['modules'], _changed_files(root, base)
    waivers = set()
    for f in changed:
        if f.startswith('workorders/') and f.endswith('.md') and os.path.isfile(os.path.join(root, f)):
            waivers |= set(WAIVER.findall(open(os.path.join(root, f)).read()))
    code, readme = set(), set()
    for f in changed:
        owners = [n for n, m in mods.items() if f.startswith(m['path'].rstrip('/') + '/')]
        if not owners:
            continue
        owner = max(owners, key=lambda n: len(mods[n]['path']))
        rest = f[len(mods[owner]['path'].rstrip('/')) + 1:]
        if rest == 'README.md':
            readme.add(owner)
        elif rest != 'AGENTS.md':
            code.add(owner)
    out = []
    for name in sorted(code - readme - waivers):
        if mods[name].get('docs_pending'):
            continue
        p = mods[name]['path']
        out.append(f'{name}: you changed code in {p}/ but not {p}/README.md. Reread {p}/README.md and {mods[name]["card"]}, '
                   f'check your change against them, and update the README in this same slice. If it truly needs no change, '
                   f'add "README waiver: {name}: <why>" to your handoff for your IT manager to accept.')
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--base', help='commit to compare against (default: $SOP_BASE, then the merge-base with main)')
    ap.add_argument('--root', default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    a = ap.parse_args()
    import tomllib
    reg = tomllib.load(open(os.path.join(a.root, 'modules.toml'), 'rb'))
    found = card_findings(a.root, reg) + freshness_findings(a.root, reg, a.base or resolve_base(a.root))
    print('\n'.join(found) if found else 'module docs: every card and README present, matching, and current')
    print(f'RESULT {"FAIL (" + str(len(found)) + ")" if found else "PASS"}')
    return 1 if found else 0


if __name__ == '__main__':
    sys.exit(main())
