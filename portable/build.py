#!/usr/bin/env python3
# -- coding: utf-8 --
"""Build the portable Impacket onedir distribution."""

# Imports
import argparse
from pathlib import Path

import PyInstaller.__main__


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dist-dir', type=Path, default=PROJECT_ROOT / 'dist' / 'portable')
    parser.add_argument('--work-dir', type=Path, default=PROJECT_ROOT / 'build' / 'portable')
    options = parser.parse_args(argv)

    PyInstaller.__main__.run([
        '--clean',
        '--noconfirm',
        '--distpath', str(options.dist_dir.resolve()),
        '--workpath', str(options.work_dir.resolve()),
        str(PROJECT_ROOT / 'portable' / 'impacket.spec'),
    ])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
