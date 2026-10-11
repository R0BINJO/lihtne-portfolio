#!/usr/bin/env python3
import os
import secrets
from pathlib import Path
root = Path(__file__).resolve().parent.parent
private = root / 'private'
private.mkdir(mode=0o700, exist_ok=True)
key = private / 'secret.key'
if not key.exists():
    fd = os.open(key, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w') as file:
        file.write(secrets.token_urlsafe(64))
print('Private application key ready.')
