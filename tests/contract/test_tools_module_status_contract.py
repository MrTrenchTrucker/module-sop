"""Contract: tools/module_status exposes a command line, and its run never writes into the repo it reads (ADR-011; card: tools/module_status/AGENTS.md)."""
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from tests.helpers import ROOT

MODULE = os.path.join(ROOT, 'tools', 'module_status')
SCRIPT = os.path.join(MODULE, 'module_status.py')
OUTPUTS = ['report.md', 'module_tree.csv', 'status.json', 'Module_Status.xlsx']


def snapshot(root):
    """Map of every file under root (relative path) to its sha256."""
    found = {}
    for dp, _dn, files in os.walk(root):
        for fn in files:
            p = os.path.join(dp, fn)
            with open(p, 'rb') as fh:
                found[os.path.relpath(p, root)] = hashlib.sha256(fh.read()).hexdigest()
    return found


class ModuleStatusContract(unittest.TestCase):
    def test_card_and_readme_present(self):
        for f in ('AGENTS.md', 'README.md'):
            self.assertTrue(os.path.isfile(os.path.join(MODULE, f)), f'tools/module_status/{f}: see tools/module_status/AGENTS.md')

    def test_run_writes_only_into_out_dir_and_never_into_the_repo(self):
        work = tempfile.mkdtemp(prefix='module_status_contract_')
        self.addCleanup(shutil.rmtree, work, True)
        repo, out = os.path.join(work, 'repo'), os.path.join(work, 'out')
        for rel in ('m/one/src/main/One.kt', 'm/one/src/test/OneTest.kt'):
            os.makedirs(os.path.dirname(os.path.join(repo, rel)), exist_ok=True)
            with open(os.path.join(repo, rel), 'w') as fh:
                fh.write('x')
        with open(os.path.join(repo, 'modules.toml'), 'w') as fh:
            fh.write('[modules.one]\npath = "m/one"\nowns = "o"\ncard = "m/one/AGENTS.md"\n')
        cfg = os.path.join(work, 'config.toml')
        with open(cfg, 'w') as fh:
            fh.write(f'repo = "{repo}"\nout_dir = "{out}"\n')
        before = snapshot(repo)
        r = subprocess.run([sys.executable, SCRIPT, cfg], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, 'tools/module_status/AGENTS.md: a normal run exits 0\n' + r.stderr[-600:])
        self.assertEqual(snapshot(repo), before, 'tools/module_status/AGENTS.md: the run must not write into the repo it reads')
        for f in OUTPUTS:
            self.assertTrue(os.path.isfile(os.path.join(out, f)), f'tools/module_status/AGENTS.md: {f} missing from out_dir')


if __name__ == '__main__':
    unittest.main()
