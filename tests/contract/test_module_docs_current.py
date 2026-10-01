"""Contract: every module whose code changed since the base changed its README too (MODULE SOP section 9.8).

This runs with the rest of the suite, so whoever changes code sees it fail before handing off. When it fails: reread
that module's README.md and AGENTS.md, check your change against them, and update the README (or add a
`README waiver: <module>: <why>` line to your work order for your IT manager to accept).
"""
import os
import tomllib
import unittest
from tests.helpers import ROOT
from doc_check import freshness_findings, resolve_base


class ModuleDocsCurrent(unittest.TestCase):
    def test_every_changed_module_updated_its_readme(self):
        reg = tomllib.load(open(os.path.join(ROOT, 'modules.toml'), 'rb'))
        found = freshness_findings(ROOT, reg, resolve_base(ROOT))
        self.assertEqual(found, [], 'Module docs are stale:\n' + '\n'.join(found))


if __name__ == '__main__':
    unittest.main()
