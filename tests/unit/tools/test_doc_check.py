"""Unit tests for tools/doc_check.py: the repo passes, and each rule is watched failing (module tools)."""
import os
import shutil
import subprocess
import tomllib
import unittest
from tests.helpers import ROOT, scratch_copy
from doc_check import card_findings, freshness_findings, resolve_base


def registry(root):
    return tomllib.load(open(os.path.join(root, 'modules.toml'), 'rb'))


def git(root, *args):
    return subprocess.run(['git', '-C', root, '-c', 'user.name=t', '-c', 'user.email=t@t', *args],
                          capture_output=True, text=True, check=True).stdout.strip()


class _Scratch(unittest.TestCase):
    def setUp(self):
        self.repo = scratch_copy()

    def tearDown(self):
        shutil.rmtree(os.path.dirname(self.repo))

    def edit(self, rel, old, new):
        p = os.path.join(self.repo, rel)
        text = open(p).read()
        self.assertIn(old, text, f'test setup: {old!r} not in {rel}')
        open(p, 'w').write(text.replace(old, new))

    def append(self, rel, text):
        with open(os.path.join(self.repo, rel), 'a') as f:
            f.write(text)


class CardFindingsTest(_Scratch):
    def found(self):
        return '\n'.join(card_findings(self.repo, registry(self.repo)))

    def test_repo_is_clean(self):
        self.assertEqual(card_findings(ROOT, registry(ROOT)), [], 'tools/doc_check.py: the committed repo must pass')

    def test_missing_readme_fails(self):
        os.remove(os.path.join(self.repo, 'skills', 'itm', 'module-sop-itm', 'README.md'))
        self.assertIn('skills_itm_module_sop: skills/itm/module-sop-itm/README.md is missing', self.found())

    def test_card_lists_an_interface_the_registry_does_not(self):
        self.edit('modules.toml', 'public = ["module-sop-itm", "parrot-protocol-itm"]', 'public = ["module-sop-itm"]')
        self.assertIn("skills_itm: the card's Public Interface lists `parrot-protocol-itm`, but the registry's public list "
                      "does not", self.found())

    def test_registry_public_missing_from_card_fails(self):
        self.edit('tools/AGENTS.md', '- `sop_check.load_registry(root) -> dict`: the parsed `modules.toml`.\n', '')
        self.assertIn("tools: the registry lists `sop_check.load_registry` as public, but the card's Public Interface does not",
                      self.found())

    def test_undeclared_public_function_fails(self):
        self.append('tools/sections.py', '\n\ndef new_helper():\n    return 1\n')
        self.assertIn("tools: `sections.new_helper` is public in the code but not in the registry's public list", self.found())

    def test_declared_function_missing_from_code_fails(self):
        self.edit('tools/sections.py', 'def sop_version(', 'def _sop_version(')
        self.assertIn('tools: the registry lists `sections.sop_version` as public, but the code has no such public function',
                      self.found())

    def test_cli_main_is_exempt(self):
        self.append('tools/sections.py', '\n\ndef main():\n    return 0\n')
        self.assertNotIn('sections.main', self.found())

    def test_depends_on_mismatch_fails(self):
        self.edit('skills/itm/AGENTS.md', '- skills (parent)', '- tools')
        self.assertIn("skills_itm: the card's Depends On names ['tools'], but the registry says ['skills']", self.found())

    def test_parent_readme_must_name_each_sub_module(self):
        self.edit('skills/itm/README.md', 'skills_itm_parrot_protocol', 'the Parrot skill')
        self.assertIn('skills_itm: its README does not name its sub-module `skills_itm_parrot_protocol`', self.found())

    def test_docs_pending_module_is_skipped(self):
        os.remove(os.path.join(self.repo, 'skills', 'itm', 'module-sop-itm', 'README.md'))
        self.edit('modules.toml', 'card = "skills/itm/module-sop-itm/AGENTS.md"',
                  'card = "skills/itm/module-sop-itm/AGENTS.md"\ndocs_pending = true')
        self.assertNotIn('skills_itm_module_sop', self.found())


class FreshnessTest(_Scratch):
    def setUp(self):
        super().setUp()
        git(self.repo, 'init', '-q')
        self.commit('base')

    def commit(self, msg):
        git(self.repo, 'add', '-A')
        git(self.repo, 'commit', '-qm', msg)
        self.base = git(self.repo, 'rev-parse', 'HEAD')

    def found(self):
        return freshness_findings(self.repo, registry(self.repo), self.base)

    def test_unchanged_tree_passes(self):
        self.assertEqual(self.found(), [])

    def test_code_change_without_readme_fails_loudly_with_what_to_do(self):
        self.append('tools/sections.py', '\n# touched\n')
        found = self.found()
        self.assertEqual(len(found), 1, found)
        self.assertIn('tools: you changed code in tools/ but not tools/README.md', found[0])
        self.assertIn('Reread tools/README.md and tools/AGENTS.md', found[0])
        self.assertIn('README waiver: tools:', found[0])

    def test_code_change_with_readme_passes(self):
        self.append('tools/sections.py', '\n# touched\n')
        self.append('tools/README.md', '\nNoted.\n')
        self.assertEqual(self.found(), [])

    def test_new_untracked_file_counts_as_a_code_change(self):
        open(os.path.join(self.repo, 'tools', 'extra.py'), 'w').write('X = 1\n')
        self.assertIn('tools: you changed code', '\n'.join(self.found()))

    def test_committed_change_is_still_seen_against_the_base(self):
        base = self.base
        self.append('tools/sections.py', '\n# touched\n')
        self.commit('slice')
        self.base = base
        self.assertIn('tools: you changed code', '\n'.join(self.found()))

    def test_readme_or_card_only_change_passes(self):
        self.append('tools/README.md', '\nNoted.\n')
        self.append('tools/AGENTS.md', '\n')
        self.assertEqual(self.found(), [])

    def test_nested_change_needs_its_own_readme_not_its_parents(self):
        self.append('skills/itm/module-sop-itm/SKILL.md', '\n')
        self.append('skills/itm/README.md', '\nNoted.\n')
        found = '\n'.join(self.found())
        self.assertIn('skills_itm_module_sop: you changed code in skills/itm/module-sop-itm/', found)
        self.assertNotIn('skills_itm:', found)

    def test_waiver_in_a_changed_work_order_passes(self):
        self.append('tools/sections.py', '\n# touched\n')
        self.append('workorders/WO-001-project-setup.md', '\nREADME waiver: tools: comment-only change\n')
        self.assertEqual(self.found(), [])

    def test_waiver_left_in_an_old_work_order_does_not_count(self):
        self.append('workorders/WO-001-project-setup.md', '\nREADME waiver: tools: an old slice\n')
        self.commit('old slice')
        self.append('tools/sections.py', '\n# touched\n')
        self.assertIn('tools: you changed code', '\n'.join(self.found()))

    def test_docs_pending_module_is_skipped(self):
        self.edit('modules.toml', 'card = "tools/AGENTS.md"', 'card = "tools/AGENTS.md"\ndocs_pending = true')
        self.commit('mark pending')
        self.append('tools/sections.py', '\n# touched\n')
        self.assertEqual(self.found(), [])


class ResolveBaseTest(unittest.TestCase):
    def test_sop_base_wins(self):
        old = os.environ.get('SOP_BASE')
        os.environ['SOP_BASE'] = 'abc123'
        try:
            self.assertEqual(resolve_base(ROOT), 'abc123')
        finally:
            os.environ.pop('SOP_BASE') if old is None else os.environ.__setitem__('SOP_BASE', old)

    def test_no_base_fails_loudly(self):
        repo = scratch_copy()
        old = os.environ.pop('SOP_BASE', None)
        try:
            with self.assertRaises(RuntimeError):
                resolve_base(repo)
        finally:
            shutil.rmtree(os.path.dirname(repo))
            if old is not None:
                os.environ['SOP_BASE'] = old


if __name__ == '__main__':
    unittest.main()
