"""Unit tests for tools/skill_lint.py: a clean synthetic skill passes, and every rule is watched failing (module tools)."""
import os
import shutil
import tempfile
import unittest
from tests.helpers import ROOT
from sections import section
from skill_lint import lint

W = open(os.path.join(ROOT, 'docs', 'WORKER_SOP.md')).read()
CLEAN = ('---\nname: module-sop-worker\ndescription: >-\n  LOCKED, ALWAYS-ON. You are a worker.\n---\n\n'
         '# Worker\n\nRead back with your `parrot-protocol-worker` skill. Your module card is `AGENTS.md`.\n\n'
         + section(W, '## Quick Reference', '## One-Paragraph Version') + '\n' + section(W, '## One-Paragraph Version'))


class SkillLintTest(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix='skill-lint-')
        self.p = os.path.join(self.d, 'SKILL.md')

    def tearDown(self):
        shutil.rmtree(self.d)

    def run_lint(self, text):
        open(self.p, 'w').write(text)
        return lint(self.p, 'worker', ROOT)

    def test_clean_skill_passes(self):
        self.assertEqual(self.run_lint(CLEAN), [])

    def assertFlags(self, extra, rule):
        v = self.run_lint(CLEAN.replace('# Worker\n', '# Worker\n' + extra + '\n'))
        self.assertTrue(any(x.startswith(rule) for x in v), f'tools/skill_lint.py rule {rule} did not fire: {v}')

    def test_sop_document_pointer(self):
        self.assertFlags('Read the MODULE SOP in full.', 'sop_document')

    def test_section_pointer(self):
        self.assertFlags('Use the form in Appendix D.', 'section_pointer')

    def test_doc_path(self):
        self.assertFlags('See references/WORKER_SOP.md.', 'doc_path')

    def private_root(self, names):
        """A throwaway repo root holding the worker SOP and, if given, a private-names file."""
        root = os.path.join(self.d, 'root')
        os.makedirs(os.path.join(root, 'docs'))
        shutil.copy(os.path.join(ROOT, 'docs', 'WORKER_SOP.md'), os.path.join(root, 'docs'))
        if names is not None:
            os.makedirs(os.path.join(root, '.sop'))
            open(os.path.join(root, '.sop', 'private_names.txt'), 'w').write(names)
        return root

    def lint_in(self, root, extra):
        open(self.p, 'w').write(CLEAN.replace('# Worker\n', '# Worker\n' + extra + '\n'))
        return lint(self.p, 'worker', root)

    def test_private_name_from_local_file(self):
        root = self.private_root('# our own names\nACMEBOT\nTICKET-42\n')
        for extra in ('Report to ACMEBOT.', 'Close TICKET-42 first.'):
            v = self.lint_in(root, extra)
            self.assertTrue(any(x.startswith('private_name') for x in v), f'private_name did not fire on {extra!r}: {v}')

    def test_private_names_are_whole_words(self):
        v = self.lint_in(self.private_root('ACME\n'), 'An ACMEBOTS reference is not the name ACME-less.')
        self.assertFalse(any(x.startswith('private_name') for x in v), v)

    def test_no_private_names_file_means_no_private_rule(self):
        v = self.lint_in(self.private_root(None), 'Report to ACMEBOT.')
        self.assertFalse(any(x.startswith('private_name') for x in v), v)
        self.assertEqual(v, [])

    def test_private_address(self):
        self.assertFlags('The server is at 10.1.2.3.', 'host_path_ip')

    def test_host_path(self):
        self.assertFlags('Files live in /mnt/data.', 'host_path_ip')

    def test_other_md_file(self):
        self.assertFlags('Also read NOTES.md.', 'md_file')

    def test_module_readme_is_a_project_working_file(self):
        v = self.run_lint(CLEAN + '\nRead the module README.md with its card.\n')
        self.assertFalse(any(x.startswith('md_file') for x in v), v)

    def test_edited_checklist_breaks_fidelity(self):
        v = self.run_lint(CLEAN.replace('- [ ]', '- [x]', 1))
        self.assertTrue(any(x.startswith('fidelity') for x in v), v)

    def test_missing_pairing(self):
        v = self.run_lint(CLEAN.replace('parrot-protocol-worker', 'the readback skill'))
        self.assertTrue(any(x.startswith('pairing') for x in v), v)

    def test_file_without_class_is_a_usage_error_not_a_crash(self):
        from skill_lint import main
        self.assertEqual(main(['--file', self.p]), 2)

    def test_file_with_unknown_class_is_a_usage_error(self):
        from skill_lint import main
        self.assertEqual(main(['--file', self.p, '--class', 'janitor']), 2)

    def test_references_folder_is_refused(self):
        os.mkdir(os.path.join(self.d, 'references'))
        v = self.run_lint(CLEAN)
        self.assertTrue(any(x.startswith('packaging') for x in v), v)


if __name__ == '__main__':
    unittest.main()
