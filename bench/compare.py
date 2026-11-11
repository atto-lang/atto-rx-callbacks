#!/usr/bin/env python3
"""Measure real two-model guest processes; host code only launches and verifies."""
import argparse
import json
import os
from pathlib import Path
import platform
import re
import statistics
import subprocess
import time


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], text=True).strip()


def identity(root):
    if git(root, 'status', '--porcelain', '--untracked-files=all'):
        raise SystemExit(f'Refusing dirty source checkout: {root}')
    return {'path': str(root), 'commit': git(root, 'rev-parse', 'HEAD'),
            'tree': git(root, 'rev-parse', 'HEAD^{tree}')}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--peer', required=True, type=Path)
    parser.add_argument('--compiler-root', required=True, type=Path)
    parser.add_argument('--runs', type=int, default=3)
    parser.add_argument('--warmups', type=int, default=1)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    if args.runs < 1 or args.warmups < 0:
        parser.error('runs >= 1 and warmups >= 0 required')
    root = Path(__file__).resolve().parents[1]
    peer, compiler = args.peer.resolve(), args.compiler_root.resolve()
    sources = [root, peer]
    pin = (root / 'compiler.lock').read_text().strip()
    tree = (root / 'compiler-tree.txt').read_text().strip()
    compiler_identity = identity(compiler)
    if compiler_identity['commit'] != pin or compiler_identity['tree'] != tree:
        raise SystemExit('Built compiler source differs from compiler commit/tree pin')
    for source in sources:
        if (source / 'compiler.lock').read_text().strip() != pin or (source / 'compiler-tree.txt').read_text().strip() != tree:
            raise SystemExit('Refusing mixed compiler pins')
    classpath = os.environ['ORES_CLASSPATH']
    if str((compiler / 'target/classes').resolve()) not in [str(Path(x).resolve()) for x in classpath.split(os.pathsep)]:
        raise SystemExit('Classpath omits selected compiler target/classes')
    java = os.environ.get('JAVA', 'java')
    command = [java, '--enable-native-access=ALL-UNNAMED',
               '-Dpolyglot.engine.Compilation=false', '-Dpolyglot.engine.WarnInterpreterOnly=false',
               '-cp', classpath, 'dev.oreslang.launcher.OresMain']
    report = {'compiler': compiler_identity, 'sources': [identity(x) for x in sources],
              'platform': platform.platform(), 'java': subprocess.run([java, '-version'], capture_output=True, text=True).stderr,
              'profile': 'Java/Graal guest interpreter; whole-process wall time and peak RSS including startup',
              'pipelines_per_process': 200, 'expected_stdout': '3600\n', 'warmups': args.warmups,
              'samples': []}
    for round_index in range(args.warmups + args.runs):
        order = sources[round_index % 2:] + sources[:round_index % 2]
        for source in order:
            guest = command + [str(source / 'bench/common.atto')]
            if platform.system() == 'Darwin':
                timed = ['/usr/bin/time', '-l', *guest]
            elif platform.system() == 'Linux':
                timed = ['/usr/bin/time', '-f', 'PEAK_RSS_KIB=%M', *guest]
            else:
                raise SystemExit('Peak RSS supported on macOS/Linux only')
            start = time.perf_counter()
            result = subprocess.run(timed, text=True, capture_output=True, timeout=120)
            elapsed = time.perf_counter() - start
            if platform.system() == 'Darwin':
                match = re.search(r'(\d+)\s+maximum resident set size', result.stderr)
                rss = int(match[1]) if match else None
            else:
                match = re.search(r'PEAK_RSS_KIB=(\d+)', result.stderr)
                rss = int(match[1]) * 1024 if match else None
            sample = {'source': str(source), 'round': round_index, 'warmup': round_index < args.warmups,
                      'command': timed, 'exit_status': result.returncode, 'stdout': result.stdout,
                      'stderr': result.stderr, 'wall_seconds': elapsed, 'peak_rss_bytes': rss}
            report['samples'].append(sample)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(report, indent=2) + '\n')
            if result.returncode or result.stdout != '3600\n' or rss is None:
                raise SystemExit(f'Guest benchmark failed; see {args.output}')
    report['summary'] = []
    for source in sources:
        samples = [x for x in report['samples'] if x['source'] == str(source) and not x['warmup']]
        row = {'source': str(source), 'median_wall_seconds': statistics.median(x['wall_seconds'] for x in samples),
               'median_peak_rss_bytes': statistics.median(x['peak_rss_bytes'] for x in samples)}
        report['summary'].append(row)
        print(json.dumps(row))
    args.output.write_text(json.dumps(report, indent=2) + '\n')

if __name__ == '__main__':
    main()
