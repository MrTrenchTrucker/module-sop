"""Contract: sub-module skills_worker exposes the standalone skill `module-sop-worker` (card: skills/worker/AGENTS.md)."""
import os
import re
import unittest
from tests.helpers import ROOT
from skill_lint import lint

SD = os.path.join(ROOT, 'skills', 'worker', 'module-sop-worker')


class SkillsWorkerContract(unittest.TestCase):
    def test_name_is_the_public_interface(self):
        body = open(os.path.join(SD, 'SKILL.md')).read()
        self.assertEqual(re.match(r'^---\nname: (\S+)\n', body).group(1), 'module-sop-worker', 'skills/worker/SKILL.md (see its card)')

    def test_ships_as_one_file(self):
        self.assertEqual(sorted(f for f in os.listdir(SD) if f not in ('AGENTS.md', 'README.md')), ['SKILL.md'], 'skills/worker/module-sop-worker ships SKILL.md only')

    def test_standalone_and_faithful(self):
        self.assertEqual(lint(os.path.join(SD, 'SKILL.md'), 'worker', ROOT), [], 'skills/worker: fix per tools/skill_lint.py')


if __name__ == '__main__':
    unittest.main()
