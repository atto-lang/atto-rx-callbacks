#!/usr/bin/env python3
"""Fetch and build the exact Oreslang compiler revision used by callback rx."""
from pathlib import Path
import subprocess
import shlex
import re

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / '.work' / 'oreslang-source.java'
REVISION = (ROOT / 'compiler.lock').read_text().strip()
EXPECTED_TREE = (ROOT / 'compiler-tree.txt').read_text().strip()
if not all(re.fullmatch(r'[0-9a-f]{40}', pin) for pin in (REVISION, EXPECTED_TREE)):
    raise SystemExit('compiler revision and tree must be full Git SHAs')
SOURCE.parent.mkdir(exist_ok=True)
if not SOURCE.exists():
    subprocess.run(['git', 'clone', '--no-checkout', '--depth', '1',
                    'https://github.com/ores-truffle-oreslang/oreslang-source.java.git',
                    str(SOURCE)], check=True)
checkout_root = subprocess.check_output(
    ['git', '-C', str(SOURCE), 'rev-parse', '--show-toplevel'], text=True).strip()
if Path(checkout_root).resolve() != SOURCE.resolve():
    raise SystemExit('compiler path must be its own Git checkout')

def tree_identity():
    result = subprocess.run(['git', '-C', str(SOURCE), 'rev-parse', 'HEAD^{tree}'],
                            text=True, capture_output=True)
    return result.stdout.strip() if result.returncode == 0 else None

# CI can provide a same-repository source mirror with identical Git content.
if tree_identity() != EXPECTED_TREE:
    subprocess.run(['git', '-C', str(SOURCE), 'fetch', '--depth', '1', 'origin', REVISION], check=True)
    subprocess.run(['git', '-C', str(SOURCE), 'checkout', '--detach', REVISION], check=True)
if tree_identity() != EXPECTED_TREE:
    raise SystemExit('compiler source tree does not match compiler-tree.txt')
status = subprocess.check_output(['git', '-C', str(SOURCE), 'status', '--porcelain',
                                  '--untracked-files=all'], text=True)
if status:
    raise SystemExit('compiler checkout must be clean; preserve local changes before building')
subprocess.run(['mvn', '-q', '-f', str(SOURCE / 'pom.xml'), '-DskipTests', 'package'], check=True)
classpath_file = ROOT / '.work' / 'classpath.txt'
subprocess.run(['mvn', '-q', '-f', str(SOURCE / 'pom.xml'), 'dependency:build-classpath',
                f'-Dmdep.outputFile={classpath_file}'], check=True)
classpath = str(SOURCE / 'target/classes') + ':' + classpath_file.read_text().strip()
(ROOT / '.work' / 'env.sh').write_text('export ORES_CLASSPATH=' + shlex.quote(classpath) + '\n')
print('Compiler ready. Run: source .work/env.sh && python3 scripts/test.py')
