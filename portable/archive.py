#!/usr/bin/env python3
# -- coding: utf-8 --
"""Create a normalized ZIP or tar.gz portable release archive."""

# Imports
import argparse
import gzip
import os
import stat
import tarfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath


DEFAULT_EPOCH = 315532800  # 1980-01-01, the earliest ZIP timestamp.


def archive_paths(source):
    return sorted((source, *source.rglob('*')), key=lambda path: path.relative_to(source).as_posix())


def create_tar(source, output, root_name, epoch):
    with output.open('wb') as raw_file:
        with gzip.GzipFile(filename='', mode='wb', fileobj=raw_file, mtime=epoch) as gzip_file:
            with tarfile.open(fileobj=gzip_file, mode='w') as archive:
                for path in archive_paths(source):
                    relative = path.relative_to(source)
                    name = PurePosixPath(root_name, relative.as_posix())
                    info = archive.gettarinfo(str(path), arcname=str(name))
                    info.uid = 0
                    info.gid = 0
                    info.uname = ''
                    info.gname = ''
                    info.mtime = epoch
                    if path.is_file():
                        with path.open('rb') as input_file:
                            archive.addfile(info, input_file)
                    else:
                        archive.addfile(info)


def create_zip(source, output, root_name, epoch):
    timestamp = datetime.fromtimestamp(max(epoch, DEFAULT_EPOCH), tz=timezone.utc)
    zip_time = (timestamp.year, timestamp.month, timestamp.day, timestamp.hour, timestamp.minute, timestamp.second)
    with zipfile.ZipFile(output, mode='w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in archive_paths(source):
            relative = path.relative_to(source)
            name = PurePosixPath(root_name, relative.as_posix())
            if path.is_dir():
                name = PurePosixPath(str(name) + '/')
            info = zipfile.ZipInfo(str(name), date_time=zip_time)
            info.create_system = 3
            mode = path.stat().st_mode
            info.external_attr = (mode & 0xFFFF) << 16
            if path.is_dir():
                info.external_attr |= 0x10
                archive.writestr(info, b'')
            elif stat.S_ISLNK(mode):
                info.external_attr = (stat.S_IFLNK | 0o777) << 16
                archive.writestr(info, os.readlink(path).encode('utf-8'))
            else:
                archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--root-name', required=True)
    options = parser.parse_args(argv)

    source = options.input.resolve()
    output = options.output.resolve()
    if not source.is_dir():
        parser.error('input directory does not exist: %s' % source)
    output.parent.mkdir(parents=True, exist_ok=True)
    epoch = int(os.environ.get('SOURCE_DATE_EPOCH', DEFAULT_EPOCH))

    if output.name.endswith('.tar.gz'):
        create_tar(source, output, options.root_name, epoch)
    elif output.suffix == '.zip':
        create_zip(source, output, options.root_name, epoch)
    else:
        parser.error('output must end in .tar.gz or .zip')
    print(output)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
