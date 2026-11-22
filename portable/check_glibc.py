#!/usr/bin/env python3
# -- coding: utf-8 --
"""Reject Linux bundle objects that require a newer glibc than supported."""

# Imports
import argparse
import re
import subprocess
from pathlib import Path


GLIBC_PATTERN = re.compile(r'GLIBC_(\d+(?:\.\d+)+)')


def version_tuple(version):
    return tuple(int(component) for component in version.split('.'))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True, type=Path)
    parser.add_argument('--maximum', required=True)
    options = parser.parse_args(argv)

    maximum = version_tuple(options.maximum)
    highest = (0,)
    highest_path = None
    violations = []
    for path in sorted(options.root.resolve().rglob('*')):
        if not path.is_file():
            continue
        with path.open('rb') as input_file:
            if input_file.read(4) != b'\x7fELF':
                continue
        result = subprocess.run(
            ['readelf', '--version-info', str(path)],
            capture_output=True,
            check=True,
            text=True,
        )
        versions = [version_tuple(match) for match in GLIBC_PATTERN.findall(result.stdout)]
        required = max(versions, default=(0,))
        if required > highest:
            highest = required
            highest_path = path
        if required > maximum:
            violations.append((path, required))

    if violations:
        details = '\n'.join('%s requires GLIBC_%s' % (path, '.'.join(map(str, version)))
                            for path, version in violations)
        raise RuntimeError('glibc compatibility floor exceeds %s:\n%s' % (options.maximum, details))
    if highest_path is None:
        raise RuntimeError('no ELF files found below %s' % options.root)
    print('glibc compatibility passed: maximum GLIBC_%s (%s)'
          % ('.'.join(map(str, highest)), highest_path))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
