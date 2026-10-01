"""Unit tests for tools/sections.py (module tools; card: tools/AGENTS.md)."""
import unittest
from tests.helpers import ROOT  # noqa: F401  (puts tools/ on sys.path)
from sections import section, sop_version

DOC = "# T\n\n**Version:** 1.2.3\n\n## A\nline a\n\n## B\nline b\n"


class SectionsTest(unittest.TestCase):
    def test_section_to_next_heading(self):
        self.assertEqual(section(DOC, '## A', '## B'), '## A\nline a\n')

    def test_section_to_eof(self):
        self.assertEqual(section(DOC, '## B'), '## B\nline b\n')

    def test_missing_heading_fails_loudly(self):
        with self.assertRaises(ValueError, msg='tools: a renamed SOP heading must fail, not return empty'):
            section(DOC, '## Missing')

    def test_missing_stop_heading_fails_loudly(self):
        with self.assertRaises(ValueError):
            section(DOC, '## A', '## Nope')

    def test_heading_with_trailing_space_matches(self):
        doc = '## A  \nline a\n\n## B\nline b\n'
        self.assertEqual(section(doc, '## A', '## B'), '## A  \nline a\n')

    def test_heading_on_first_line_needs_no_preceding_newline(self):
        self.assertEqual(section('## A\nline a\n', '## A'), '## A\nline a\n')

    def test_stop_heading_above_start_fails_loudly(self):
        with self.assertRaises(ValueError):
            section('## B\nb\n## A\na\n', '## A', '## B')

    def test_repeated_stop_heading_matches_after_start(self):
        self.assertEqual(section('## X\n## A\na\n## X\nx\n', '## A', '## X'), '## A\na\n')

    def test_version(self):
        self.assertEqual(sop_version(DOC), '1.2.3')
        with self.assertRaises(ValueError):
            sop_version('no version here')


if __name__ == '__main__':
    unittest.main()
