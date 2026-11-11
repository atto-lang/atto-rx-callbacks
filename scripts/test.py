#!/usr/bin/env python3
"""Check and run callback-only rx programs with the pinned compiler."""
import os
import re
from pathlib import Path
import subprocess
import sys
from fixture_inventory import validate_cases

ROOT = Path(__file__).resolve().parents[1]
JAVA = os.environ.get('JAVA', 'java')
CLASSPATH = os.environ.get('ORES_CLASSPATH')
if not CLASSPATH:
    sys.exit('Set ORES_CLASSPATH (run scripts/setup.py first).')
COMMAND = [JAVA, '--enable-native-access=ALL-UNNAMED',
           '-Dpolyglot.engine.WarnInterpreterOnly=false', '-cp', CLASSPATH,
           'dev.oreslang.launcher.OresMain']

POINTER_STYLE = (
    (re.compile(r'Fnc\s*<\s*&'), 'borrow marker inside Fnc<...>'),
    (re.compile(r'&mut\b'), 'pointer-style &mut'),
    (re.compile(r'(^|[\(\[,=])\s*&\s*[A-Za-z_(]', re.MULTILINE),
     'unary address-of style &value'),
    (re.compile(r'\b(?:[A-Z][A-Za-z0-9_]*(?:<[^>\n]+>)?|int|bool|string|String)\s*\*\s+[A-Za-z_]'),
     'pointer-style T* declaration'),
)

def assert_pointerless():
    roots = [ROOT / 'src', ROOT / 'tests', ROOT / 'bench']
    for root in roots:
        for path in checked_sources(root):
            text = path.read_text()
            for pattern, label in POINTER_STYLE:
                match = pattern.search(text)
                if match:
                    line = text.count('\n', 0, match.start()) + 1
                    sys.exit(f'{path}:{line}: forbidden {label}; use pointerless rt ownership semantics')

def checked_sources(root):
    # Validate all executable and regex-scanned .ores paths before opening them.
    # Purely source-local preflight; this does not make a writable tree TOCTOU-safe.
    if root.is_symlink() or (root.exists() and not root.is_dir()):
        sys.exit(f'source directory must be a real directory: {root}')
    parent = root.resolve(strict=True) if root.exists() else None
    for path in sorted(root.glob('*.ores')):
        if (path.is_symlink() or not path.is_file() or
                path.resolve(strict=True).parent != parent):
            sys.exit(f'source must be an in-tree regular file: {path}')
        yield path

def run(args):
    result = subprocess.run(COMMAND + args, text=True, capture_output=True, timeout=30)
    if result.returncode or ': error:' in result.stderr:
        sys.exit(result.stdout + result.stderr)
    return result.stdout.strip()

TESTS = validate_cases(ROOT / 'tests', ('.out', '.err'))
REJECTS = validate_cases(ROOT / 'tests/reject', ('.err',))
assert_pointerless()
for path in TESTS:
    failure_file = path.with_suffix('.err')
    if failure_file.is_file():
        failed = subprocess.run(COMMAND + [str(path)], text=True,
                                capture_output=True, timeout=30)
        expected_error = failure_file.read_text().strip()
        diagnostic = failed.stderr + failed.stdout
        if failed.returncode == 0 or expected_error not in diagnostic:
            sys.exit(f'{path.name}: expected runtime failure containing {expected_error!r}\\n{diagnostic}')
        print(f'PASS {path.stem} (expected runtime failure)')
        continue
    actual = run([str(path)])
    expected = path.with_suffix('.out').read_text().strip()
    if actual != expected:
        sys.exit(f'{path.name}: expected {expected!r}, got {actual!r}')
    print(f'PASS {path.stem}')

for path in REJECTS:
    result = subprocess.run(COMMAND + ['--check', str(path)], text=True,
                            capture_output=True, timeout=30)
    expected = path.with_suffix('.err').read_text().strip()
    diagnostic = result.stdout + result.stderr
    if result.returncode == 0 or expected not in diagnostic:
        sys.exit(f'{path.name}: expected rejection containing {expected!r}\n{diagnostic}')
    print(f'PASS reject/{path.stem}')
