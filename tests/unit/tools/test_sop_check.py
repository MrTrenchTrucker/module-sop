"""Unit tests for tools/sop_check.py: PASS on the repo, and each rule watched failing (module tools)."""
import os
import shutil
import unittest
from tests.helpers import ROOT, scratch_copy
from sop_check import check


class SopCheckTest(unittest.TestCase):
    def setUp(self):
        self.repo = scratch_copy()

    def tearDown(self):
        shutil.rmtree(os.path.dirname(self.repo))

    def test_repo_passes(self):
        fails, _ = check(ROOT)
        self.assertEqual(fails, [], 'tools/sop_check.py: the committed repo must pass (see tools/AGENTS.md)')

    def test_unregistered_folder_fails(self):
        os.mkdir(os.path.join(self.repo, 'stray'))
        self.assertIn('unregistered folder: stray', check(self.repo)[0])

    def test_unregistered_subfolder_fails(self):
        os.mkdir(os.path.join(self.repo, 'skills', 'rogue'))
        self.assertIn('unregistered sub-folder: skills/rogue', check(self.repo)[0])

    def test_non_module_dirs_entry_is_exempt(self):
        os.mkdir(os.path.join(self.repo, '.pytest_cache'))
        fails, _ = check(self.repo)
        self.assertEqual(fails, [], 'a dir listed in non_module_dirs must not fail the registry check')

    def _set_depends(self, block, value):
        p = os.path.join(self.repo, 'modules.toml')
        text = open(p).read()
        head, tail = text.split(f'[modules.{block}]\n', 1)
        body, rest = tail.split('\n\n', 1) if '\n\n' in tail else (tail, '')
        lines = [f'depends_on = {value}' if l.startswith('depends_on') else l for l in body.split('\n')]
        open(p, 'w').write(head + f'[modules.{block}]\n' + '\n'.join(lines) + ('\n\n' + rest if rest else ''))

    def test_sub_module_without_parent_dependency_fails(self):
        self._set_depends('skills_itm', '[]')
        self.assertIn('skills_itm: sub-module of skills, but depends_on does not name its parent', check(self.repo)[0])

    def test_sub_sub_module_must_name_direct_parent_not_grandparent(self):
        self._set_depends('skills_itm_module_sop', '["skills"]')
        self.assertIn('skills_itm_module_sop: sub-module of skills_itm, but depends_on does not name its parent',
                      check(self.repo)[0])

    def test_card_missing_section_fails(self):
        p = os.path.join(self.repo, 'tools', 'AGENTS.md')
        open(p, 'w').write(open(p).read().replace('## Does Not Own', '## Something Else'))
        self.assertIn('tools: card section missing: ## Does Not Own', check(self.repo)[0])

    def test_hard_line_cap_fails(self):
        open(os.path.join(self.repo, 'tools', 'big.py'), 'w').write('x = 1\n' * 501)
        self.assertTrue(any('big.py: 501 lines > hard cap' in f for f in check(self.repo)[0]))

    def test_architecture_budget_fails(self):
        with open(os.path.join(self.repo, 'ARCHITECTURE.md'), 'a') as f:
            f.write(' word' * 1600)
        self.assertTrue(any(f.startswith('ARCHITECTURE.md:') for f in check(self.repo)[0]))

    def test_stale_module_map_fails(self):
        with open(os.path.join(self.repo, 'MODULE_MAP.md'), 'a') as f:
            f.write('hand edit\n')
        self.assertIn('MODULE_MAP.md is stale or missing (run tools/sop_check.py --write)', check(self.repo)[0])

    def test_relative_import_from_other_module_fails(self):
        with open(os.path.join(self.repo, 'docs', 'rogue.py'), 'w') as f:
            f.write('from . import sop_check\n')
        self.assertTrue(any('docs/rogue.py imports sop_check from module tools' in x for x in check(self.repo)[0]))


if __name__ == '__main__':
    unittest.main()
