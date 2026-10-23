#!/usr/bin/env python3
"""Explicit, offline correction of installer-generated control flags; never restarts services."""
import argparse
import os
from pathlib import Path
import re
import secrets
import stat
import tempfile

FLAGS = ('HUE_WRITES_ENABLED', 'HUE_COLOR_ENABLED', 'HUE_WHITE_ENABLED')


def inspect(path):
    path = Path(path).absolute()
    if path.name not in ('.env', 'settings.env'):
        raise ValueError('Select the installer .env or native settings.env, not Compose or a secret file')
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError('Symbolic settings paths are not supported')
    metadata = path.stat()
    if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
        raise ValueError('Settings must be a regular, unlinked file')
    content = path.read_bytes()
    lines = content.decode('utf-8').splitlines(keepends=True)
    values, positions = {}, {}
    for index, line in enumerate(lines):
        for flag in FLAGS:
            if re.match(r'\s*(?:export\s+)?' + flag + r'\s*=', line):
                match = re.fullmatch(flag + r'=([01])(?:\r?\n)?', line)
                if flag in values or not match:
                    raise ValueError('Duplicate or nonstandard control flag: ' + flag)
                values[flag], positions[flag] = match[1], index
    if set(values) != set(FLAGS):
        raise ValueError('Missing generated control flags; customized stacks need separate review')
    return path, metadata, content, lines, values, positions


def enable(path):
    path, metadata, original, lines, values, positions = inspect(path)
    if all(value == '1' for value in values.values()):
        return values, None
    if os.geteuid() != 0 and metadata.st_uid != os.geteuid():
        raise PermissionError('Run as the settings owner or root')
    backup = path.with_name(path.name + '.controls-before-' + secrets.token_hex(6))
    fd = os.open(backup, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        os.fchmod(stream.fileno(), 0o600)
        stream.write(original)
        stream.flush()
        os.fsync(stream.fileno())
    for flag, index in positions.items():
        ending = '\r\n' if lines[index].endswith('\r\n') else '\n' if lines[index].endswith('\n') else ''
        lines[index] = flag + '=1' + ending
    fd, temporary = tempfile.mkstemp(prefix='.' + path.name + '.controls-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            os.fchmod(stream.fileno(), stat.S_IMODE(metadata.st_mode))
            if os.geteuid() == 0:
                os.fchown(stream.fileno(), metadata.st_uid, metadata.st_gid)
            elif os.fstat(stream.fileno()).st_gid != metadata.st_gid:
                os.fchown(stream.fileno(), -1, metadata.st_gid)
            stream.write(''.join(lines).encode())
            stream.flush()
            os.fsync(stream.fileno())
        current = path.stat()
        if (current.st_dev, current.st_ino) != (metadata.st_dev, metadata.st_ino) or path.read_bytes() != original:
            raise ValueError('Settings changed during correction; nothing replaced')
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return {flag: '1' for flag in FLAGS}, backup


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--settings', type=Path, required=True)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--check', action='store_true')
    action.add_argument('--enable-supported-control', action='store_true', help='Explicit operator opt-in; changes all three flags to 1')
    args = parser.parse_args()
    try:
        if args.check:
            values, backup = inspect(args.settings)[4], None
        else:
            values, backup = enable(args.settings)
        for flag in FLAGS:
            print(flag + '=' + values[flag])
        if backup:
            print('Private settings backup: ' + str(backup))
        if not args.check:
            print('Only settings changed. Recreate the Docker container or restart the native service to apply; no Hue request was sent.')
    except (OSError, UnicodeError, ValueError) as error:
        parser.exit(1, 'Control correction stopped: ' + str(error) + '\n')
