"""Contract: docs/ exposes what the skills are built from (module docs; card: docs/AGENTS.md)."""
import os
import unittest
from tests.helpers import ROOT
from sections import section, sop_version

CLASS_SOPS = ['PROJECT_LEADER_SOP.md', 'IT_MANAGER_SOP.md', 'WORKER_SOP.md']


class DocsContract(unittest.TestCase):
    def test_every_sop_present_with_a_version(self):
        for f in ['MODULE_SOP.md', 'COMMANDER_SOP.md'] + CLASS_SOPS:
            text = open(os.path.join(ROOT, 'docs', f)).read()
            self.assertRegex(sop_version(text), r'^\d+\.\d+\.\d+$', f'docs/{f}: version line (see docs/AGENTS.md)')

    def test_class_sops_have_the_sections_skills_quote(self):
        for f in CLASS_SOPS:
            text = open(os.path.join(ROOT, 'docs', f)).read()
            self.assertIn('- [ ]', section(text, '## Quick Reference', '## One-Paragraph Version'), f'docs/{f}')
            self.assertGreater(len(section(text, '## One-Paragraph Version')), 200, f'docs/{f}')


if __name__ == '__main__':
    unittest.main()
