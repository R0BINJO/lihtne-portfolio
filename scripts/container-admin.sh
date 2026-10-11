#!/bin/sh
set -eu
umask 077
python scripts/init.py
python manage.py migrate --noinput
python scripts/init_admin.py
python manage.py seed
python manage.py collectstatic --noinput
exec python serve_admin.py
