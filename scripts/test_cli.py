#!/usr/bin/env python3
"""Execute the real guest CLI; fail if take(2) waits for more input or EOF."""
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
command = [os.environ.get('JAVA', 'java'), '--enable-native-access=ALL-UNNAMED',
           '-Dpolyglot.engine.WarnInterpreterOnly=false', '-cp', os.environ['ORES_CLASSPATH'],
           'dev.oreslang.launcher.OresMain', str(ROOT / 'examples/process-lines.atto')]

def check_input(payload, expected, keep_open=False):
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, text=True)
    try:
        if keep_open:
            process.stdin.write(payload)
            process.stdin.flush()
            process.wait(timeout=30)  # stdin remains OPEN: no sixth line or EOF available.
            actual, diagnostic = process.stdout.read(), process.stderr.read()
        else:
            actual, diagnostic = process.communicate(payload, timeout=30)
        if process.returncode != 0 or actual != expected:
            raise SystemExit(f'CLI exit={process.returncode}, expected={expected!r}, actual={actual!r}\n{diagnostic}')
        print(f'PASS CLI keep_open={keep_open} expected={expected!r}')
    finally:
        if process.poll() is None:
            process.kill()
            process.wait()
        for stream in (process.stdin, process.stdout, process.stderr):
            stream.close()

check_input('\nalpha\n\nbeta\ngamma\n', 'beta!\ngamma!\n', keep_open=True)
check_input('', '')
check_input('alpha\nbeta\n', 'beta!\n')
