#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
remote='projects/portfolio'
# Explicit allowlist: no laptop credentials, databases, or environments are transferred.
tar -czf - portfolio showcase templates static scripts tests content requirements.txt manage.py serve_admin.py serve_public.py README.md SECURITY.md DESIGN.md DEPLOYMENT.md deploy Dockerfile compose.yaml .dockerignore |
  ssh -F "$HOME/.ssh/config" -o BatchMode=yes a52 "umask 077; mkdir -p $remote; tar -xzf - -C $remote"
ssh -F "$HOME/.ssh/config" -o BatchMode=yes a52 'bash projects/portfolio/scripts/install-termux.sh'
ssh -F "$HOME/.ssh/config" -o BatchMode=yes a52 'sv restart "$PREFIX/var/service/portfolio-public" "$PREFIX/var/service/portfolio-admin"'
