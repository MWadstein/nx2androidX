#!/usr/bin/env python3
"""Append seedds/nxnative profile READMEs as provenance to matching local pages.

The local README.md is our generated game page. seedds/nxnative's README is the
original bring-up history (allocator evidence, issues, stability fixes). Append
it under a marker instead of replacing the local page, so both histories survive.
Requires a fetched upstream-nxnative remote; makes no network calls.
"""
import argparse
import subprocess
from pathlib import Path

SEEDDS = 'upstream-nxnative/main'
MARK = b'<!-- upstream-nxnative README:'


def git(*args):
    return subprocess.check_output(['git', *args])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()

    paths = git('ls-tree', '-r', '--name-only', SEEDDS, '--', 'dm/games').decode().splitlines()
    added = skipped = 0
    for src in paths:
        if not src.endswith('/README.md'):
            continue
        local = 'nxnative/' + src
        exists = subprocess.run(['git', 'rev-parse', 'HEAD:' + local],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if exists.returncode:
            skipped += 1
            continue
        existing = Path(local).read_bytes()
        if MARK in existing:
            skipped += 1
            continue
        up = git('show', f'{SEEDDS}:{src}')
        if existing.strip() == up.strip():
            skipped += 1  # already the same history, nothing to add
            continue
        header = ('\n\n<!-- upstream-nxnative README: ' + SEEDDS + ' -->\n\n'
                  '## Upstream bring-up history (seedds/nxnative)\n\n').encode()
        if not a.dry_run:
            Path(local).write_bytes(existing.rstrip() + b'\n' + header + up)
        added += 1
    print(f'appended {added} README(s), skipped {skipped}'
          + (' (dry run)' if a.dry_run else ''))


if __name__ == '__main__':
    main()
