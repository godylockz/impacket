#!/usr/bin/env python3
# -- coding: utf-8 --
"""Smoke-test every command in a built portable Impacket distribution."""

# Imports
import argparse
import subprocess
import sys
from pathlib import Path


EXCLUDED_TOOLS = {'sniff', 'split'}


def run(command, timeout=30):
    result = subprocess.run(command, capture_output=True, check=False, text=True, timeout=timeout)
    combined = result.stdout + result.stderr
    if result.returncode != 0:
        raise RuntimeError('%r exited %d:\n%s' % (command, result.returncode, combined))
    if 'Traceback (most recent call last)' in combined:
        raise RuntimeError('%r printed a traceback:\n%s' % (command, combined))
    return result.stdout


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--executable', required=True, type=Path)
    parser.add_argument('--source-root', type=Path, default=Path(__file__).resolve().parents[1])
    options = parser.parse_args(argv)

    executable = options.executable.resolve()
    if not executable.is_file():
        parser.error('executable does not exist: %s' % executable)
    command_prefix = [str(executable)]
    if executable.suffix == '.py':
        command_prefix.insert(0, sys.executable)

    expected = {
        path.stem for path in (options.source_root / 'examples').glob('*.py') if path.stem not in EXCLUDED_TOOLS
    }
    actual = set(run([*command_prefix, '--list']).splitlines())
    if actual != expected:
        raise RuntimeError('command inventory mismatch: missing=%r unexpected=%r'
                           % (sorted(expected - actual), sorted(actual - expected)))

    run([*command_prefix, '--version'])
    run([*command_prefix, '--self-test'])
    failures = []
    for tool in sorted(actual, key=str.lower):
        try:
            run([*command_prefix, tool, '--help'])
        except (RuntimeError, subprocess.TimeoutExpired) as error:
            failures.append('%s: %s' % (tool, error))
    if failures:
        raise RuntimeError('portable command smoke-test failures:\n\n%s' % '\n\n'.join(failures))

    print('Smoke tests passed for %d portable commands.' % len(actual))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
