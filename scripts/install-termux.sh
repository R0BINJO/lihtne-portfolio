#!/usr/bin/env bash
set -euo pipefail
: "${PREFIX:?Run this installer inside Termux}"
root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"
umask 077
python -m venv .venv
.venv/bin/pip install --disable-pip-version-check -r requirements.txt
.venv/bin/python scripts/init.py
.venv/bin/python manage.py migrate --noinput
.venv/bin/python scripts/init_admin.py
.venv/bin/python manage.py seed
.venv/bin/python manage.py collectstatic --noinput
.venv/bin/python manage.py check
for name in portfolio-public portfolio-admin portfolio-backup; do
  service="$PREFIX/var/service/$name"
  mkdir -p "$service/log" "$root/private/logs/$name"
  touch "$service/down"
  case "$name" in
    portfolio-public) program=serve_public.py ;;
    portfolio-admin) program=serve_admin.py ;;
    portfolio-backup) program=scripts/backup_loop.py ;;
  esac
  cat > "$service/run" <<RUN
#!$PREFIX/bin/sh
cd "$root"
umask 077
exec 2>&1
exec "$root/.venv/bin/python" -u "$program"
RUN
  cat > "$service/log/run" <<RUN
#!$PREFIX/bin/sh
exec "$PREFIX/bin/svlogd" -tt "$root/private/logs/$name"
RUN
  printf 's1000000\nn3\n' > "$root/private/logs/$name/config"
  chmod 700 "$service/run" "$service/log/run"
  rm "$service/down"
  for attempt in 1 2 3 4 5; do
    test -e "$service/supervise/ok" && break
    sleep 1
  done
  sv up "$service"
 done
sleep 2
sv status "$PREFIX/var/service/portfolio-public" "$PREFIX/var/service/portfolio-admin" "$PREFIX/var/service/portfolio-backup"
