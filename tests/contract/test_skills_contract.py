"""Contract: every class skill is standalone and faithful (module skills; card: skills/AGENTS.md)."""
import os
import unittest
from tests.helpers import ROOT
from skill_lint import lint, skill_path, CLASSES


class SkillsContract(unittest.TestCase):
    def test_every_class_skill_passes_the_standalone_gate(self):
        for cls in CLASSES:
            v = lint(skill_path(ROOT, cls), cls, ROOT)
            self.assertEqual(v, [], f'skills/{cls}/SKILL.md (see skills/AGENTS.md): {v[:5]}')


if __name__ == '__main__':
    unittest.main()
