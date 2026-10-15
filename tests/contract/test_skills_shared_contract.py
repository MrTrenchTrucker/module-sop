"""Contract: the shared pack exposes the standalone skill `subagent-plan-file` (cards: skills/shared/AGENTS.md and
skills/shared/subagent-plan-file/AGENTS.md)."""
import os
import re
import unittest
from tests.helpers import ROOT
from skill_lint import lint_shared, shared_skill_path, SHARED

PACK = os.path.join(ROOT, 'skills', 'shared')
SD = os.path.join(PACK, 'subagent-plan-file')
LINES = (
    '"Read your plan file first. Do the READ GATE and sign the READ CERTIFICATE before any other tool call that changes a file."',
    '"Quote, do not paraphrase. If a section is too long to read, say so in the plan file; do not summarise from the heading."',
    '"Tick a box only after the step is done. Write what you could not do instead of skipping it."',
    '"Only you tick your boxes, write your quotes and sign your certificates. Nobody else may do it for you."',
    '"End with the closing certificate. Your work is checked against it."',
    "I have read in full, end to end, every file in my READ GATE: <list of paths>. I read them before changing any file.",
    "I read every READ GATE item in full. I skipped no step. Not done or not checked: <list, or 'none'>.",
)


class SkillsSharedContract(unittest.TestCase):
    def test_pack_holds_the_registered_shared_skills(self):
        folders = sorted(f for f in os.listdir(PACK) if os.path.isdir(os.path.join(PACK, f)))
        self.assertEqual(folders, sorted(p.split('/')[-1] for p in SHARED.values()), 'skills/shared (see its card)')

    def test_name_is_the_public_interface(self):
        body = open(os.path.join(SD, 'SKILL.md')).read()
        self.assertEqual(re.match(r'^---\nname: (\S+)\n', body).group(1), 'subagent-plan-file', 'see its card')

    def test_ships_as_one_file(self):
        self.assertEqual(sorted(f for f in os.listdir(SD) if f not in ('AGENTS.md', 'README.md')), ['SKILL.md'])

    def test_every_shared_skill_passes_the_gate(self):
        for name in SHARED:
            v = lint_shared(shared_skill_path(ROOT, name), name)
            self.assertEqual(v, [], f'skills/shared/{name}: fix per tools/skill_lint.py: {v[:5]}')

    def test_copied_lines_stay_word_for_word(self):
        body = open(os.path.join(SD, 'SKILL.md')).read()
        for line in LINES:
            self.assertIn(line, body, 'agents copy these lines; see the card Invariants')


if __name__ == '__main__':
    unittest.main()
