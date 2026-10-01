"""Shared test helpers: repo root, tools on sys.path, scratch copies of the repo for red arms."""
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))


def scratch_copy():
    """Copy the repo (minus .git) to a temp dir and return its path. Caller removes it."""
    d = tempfile.mkdtemp(prefix='module-sop-test-')
    dst = os.path.join(d, 'repo')
    shutil.copytree(ROOT, dst, ignore=shutil.ignore_patterns('.git', '__pycache__'))
    return dst
