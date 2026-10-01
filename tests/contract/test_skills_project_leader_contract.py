"""Contract: sub-module skills_project_leader exposes the standalone skill `module-sop-project-leader` (card: skills/project-leader/AGENTS.md)."""
import os
import re
import unittest
from tests.helpers import ROOT
from skill_lint import lint

SD = os.path.join(ROOT, 'skills', 'project-leader', 'module-sop-project-leader')


class SkillsProject_leaderContract(unittest.TestCase):
    def test_name_is_the_public_interface(self):
        body = open(os.path.join(SD, 'SKILL.md')).read()
        self.assertEqual(re.match(r'^---\nname: (\S+)\n', body).group(1), 'module-sop-project-leader', 'skills/project-leader/SKILL.md (see its card)')

    def test_ships_as_one_file(self):
        self.assertEqual(sorted(f for f in os.listdir(SD) if f not in ('AGENTS.md', 'README.md')), ['SKILL.md'], 'skills/project-leader/module-sop-project-leader ships SKILL.md only')

    def test_standalone_and_faithful(self):
        self.assertEqual(lint(os.path.join(SD, 'SKILL.md'), 'project-leader', ROOT), [], 'skills/project-leader: fix per tools/skill_lint.py')


if __name__ == '__main__':
    unittest.main()
