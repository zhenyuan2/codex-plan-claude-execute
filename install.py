#!/usr/bin/env python3
"""Install the standalone skill without changing Codex plugin configuration."""
import argparse
from pathlib import Path
import shutil
import tempfile

NAME = 'codex-plan-claude-execute'
SOURCE = Path(__file__).resolve().parent / 'plugins' / NAME / 'skills' / NAME


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dest', type=Path, default=Path.home() / '.agents' / 'skills' / NAME,
                        help='full destination skill directory')
    parser.add_argument('--replace', action='store_true', help='back up an existing directory before replacing it')
    args = parser.parse_args()
    destination = args.dest.expanduser().absolute()
    if destination.is_symlink():
        parser.error('destination is a symlink; refusing to replace it')
    destination = destination.resolve()
    if destination == SOURCE or destination in SOURCE.parents or SOURCE in destination.parents:
        parser.error('source and destination must not overlap')
    if destination.exists() and (not args.replace or not destination.is_dir()):
        parser.error('destination exists; use --replace to back up and replace an existing directory')
    destination.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix='.skill-install-', dir=destination.parent))
    backup = None
    try:
        shutil.copytree(SOURCE, stage / NAME, ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.DS_Store'))
        if destination.exists():
            backup_root = destination.parent.parent / '.skill-backups'
            backup_root.mkdir(exist_ok=True)
            backup = Path(tempfile.mkdtemp(prefix=NAME+'-', dir=backup_root)) / NAME
            destination.rename(backup)
        try:
            (stage / NAME).rename(destination)
        except OSError:
            if backup is not None:
                backup.rename(destination)
            raise
    finally:
        shutil.rmtree(stage)
    print('Installed:', destination)
    if backup:
        print('Previous version:', backup)
    print('Invoke in Codex: $' + NAME)


if __name__ == '__main__':
    main()
