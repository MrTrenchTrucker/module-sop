"""Contract: the shared pack exposes the standalone skills `subagent-plan-file` and `work-labels` (cards: skills/shared/AGENTS.md,
skills/shared/subagent-plan-file/AGENTS.md and skills/shared/work-labels/AGENTS.md)."""
import os
import re
import unittest
from tests.helpers import ROOT
from skill_lint import lint_shared, shared_skill_path, SHARED

PACK = os.path.join(ROOT, 'skills', 'shared')
SD = os.path.join(PACK, 'subagent-plan-file')
WL = os.path.join(PACK, 'work-labels')
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


class WorkLabelsContract(unittest.TestCase):
    def test_name_is_the_public_interface(self):
        body = open(os.path.join(WL, 'SKILL.md')).read()
        self.assertEqual(re.match(r'^---\nname: (\S+)\n', body).group(1), 'work-labels', 'see its card')

    def test_ships_as_one_file(self):
        self.assertEqual(sorted(f for f in os.listdir(WL) if f not in ('AGENTS.md', 'README.md')), ['SKILL.md'])

    def test_status_words_equal_the_sop_status_values(self):
        sop = open(os.path.join(ROOT, 'docs', 'MODULE_SOP.md')).read()
        want = re.search(r'^Status values: (.+)\.$', sop, re.M).group(1)
        want = [w.strip('` ') for w in want.split(',')]
        body = open(os.path.join(WL, 'SKILL.md')).read()
        row = re.search(r'^\| `status/\*` \| (.+?) \|', body, re.M).group(1)
        self.assertEqual([w.strip('` ') for w in row.split(',')], want, 'change both in one commit (see the card)')

    def test_a_label_is_never_an_approval(self):
        body = open(os.path.join(WL, 'SKILL.md')).read()
        self.assertIn('**A label is not an approval.**', body, 'see the card Invariants')

    def test_rules_that_close_the_loopholes_stay_in(self):
        body = ' '.join(open(os.path.join(WL, 'SKILL.md')).read().split())
        for needle in ('Exactly one. How the delivery is tested',
                       'merge, close or deploy because of one',
                       '`parked` is open',
                       "Never put an agent or a person's name on a public repository.",
                       'confirms it or corrects it',
                       'or you are in doubt',
                       'Not an approval.'):
            self.assertIn(needle, body, 'see the card Invariants')

    def test_the_three_lanes_are_defined(self):
        body = open(os.path.join(WL, 'SKILL.md')).read()
        for lane in ('1. **A**', '2. **B**', '3. **C**'):
            self.assertIn(lane, body, 'the decision order starts with "in doubt, A"')


if __name__ == '__main__':
    unittest.main()
