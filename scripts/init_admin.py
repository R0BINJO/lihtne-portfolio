#!/usr/bin/env python3
"""Create a first admin once. The random password is written privately, never logged."""
import os
import secrets
import sys
from pathlib import Path
root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portfolio.settings')
os.umask(0o077)
import django
django.setup()
from django.conf import settings
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    password = secrets.token_urlsafe(24)
    User.objects.create_superuser('robin', password=password)
    path = settings.PRIVATE_DIR / 'admin-access.txt'
    path.write_text('Portfolio studio\nURL: http://localhost:8091/admin/\nUsername: robin\nPassword: ' + password + '\n\nOpen the SSH tunnel first. Change the password in Studio → Password.\n')
    path.chmod(0o600)
    print('First administrator created. Credentials saved in private/admin-access.txt.')
else:
    print('Existing administrator preserved.')
