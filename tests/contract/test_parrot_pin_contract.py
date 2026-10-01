"""Contract: the vendored Parrot Protocol skills are byte-for-byte what the pin says (ADR-008; cards: skills/*/parrot-protocol-*/AGENTS.md)."""
import hashlib
import os
import shutil
import tomllib
import unittest
from tests.helpers import ROOT, scratch_copy


def check_pin(root):
    """Return a list of mismatches between skills/PARROT_PIN.toml and the vendored files."""
    with open(os.path.join(root, 'skills', 'PARROT_PIN.toml'), 'rb') as f:
        pin = tomllib.load(f)
    out = []
    for rel, want in pin['files'].items():
        p = os.path.join(root, 'skills', rel)
        got = hashlib.sha256(open(p, 'rb').read()).hexdigest() if os.path.isfile(p) else 'missing'
        if got != want:
            out.append(f'{rel}: {got[:12]} != pinned {want[:12]}')
    return out


class ParrotPinContract(unittest.TestCase):
    def test_pin_covers_every_class(self):
        with open(os.path.join(ROOT, 'skills', 'PARROT_PIN.toml'), 'rb') as f:
            pin = tomllib.load(f)
        self.assertEqual(len(pin['files']), 3)
        self.assertRegex(pin['source_commit'], r'^[0-9a-f]{40}$')

    def test_vendored_files_match_the_pin(self):
        self.assertEqual(check_pin(ROOT), [], 'vendored Parrot skill drifted: fix in the Parrot repo, then re-vendor (ADR-008)')

    def test_an_edited_vendored_copy_is_caught(self):
        repo = scratch_copy()
        try:
            with open(os.path.join(repo, 'skills', 'worker', 'parrot-protocol-worker', 'SKILL.md'), 'a') as f:
                f.write('local edit\n')
            self.assertTrue(any(x.startswith('worker/parrot-protocol-worker/SKILL.md') for x in check_pin(repo)))
        finally:
            shutil.rmtree(os.path.dirname(repo))


if __name__ == '__main__':
    unittest.main()
