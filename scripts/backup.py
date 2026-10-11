#!/usr/bin/env python3
"""Consistent private backup; keep the latest seven successful snapshots."""
import os
import shutil
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
os.umask(0o077)
root = Path(__file__).resolve().parent.parent
backups = root / 'backups'
backups.mkdir(mode=0o700, exist_ok=True)
target = backups / datetime.now(timezone.utc).strftime('portfolio-%Y%m%dT%H%M%S%fZ')
target.mkdir(mode=0o700)
try:
    with sqlite3.connect(f'file:{root / "private/db.sqlite3"}?mode=ro', uri=True) as source, sqlite3.connect(target / 'db.sqlite3') as destination:
        source.backup(destination)
        if destination.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
            raise RuntimeError('Backup integrity check failed')
    shutil.copy2(root / 'private/secret.key', target / 'secret.key')
    (target / 'COMPLETE').write_text('SQLite backup and matching application key. Re-export public pages after restoring.\n')
except Exception:
    shutil.rmtree(target)
    raise
for old in sorted(path for path in backups.glob('portfolio-*') if (path / 'COMPLETE').exists())[:-7]:
    shutil.rmtree(old)
print(f'Backup complete: {target.name}')
