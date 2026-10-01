"""Contract: sub-module skills_itm exposes the standalone skill `module-sop-itm` (card: skills/itm/AGENTS.md)."""
import os
import re
import unittest
from tests.helpers import ROOT
from skill_lint import lint

SD = os.path.join(ROOT, 'skills', 'itm', 'module-sop-itm')


class SkillsItmContract(unittest.TestCase):
    def test_name_is_the_public_interface(self):
        body = open(os.path.join(SD, 'SKILL.md')).read()
        self.assertEqual(re.match(r'^---\nname: (\S+)\n', body).group(1), 'module-sop-itm', 'skills/itm/SKILL.md (see its card)')

    def test_ships_as_one_file(self):
        self.assertEqual(sorted(f for f in os.listdir(SD) if f not in ('AGENTS.md', 'README.md')), ['SKILL.md'], 'skills/itm/module-sop-itm ships SKILL.md only')

    def test_standalone_and_faithful(self):
        self.assertEqual(lint(os.path.join(SD, 'SKILL.md'), 'itm', ROOT), [], 'skills/itm: fix per tools/skill_lint.py')


if __name__ == '__main__':
    unittest.main()
