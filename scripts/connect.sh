#!/usr/bin/env bash
set -euo pipefail
# Explicit config avoids the machine's unreadable global SSH include.
exec ssh -F "$HOME/.ssh/config" -o ExitOnForwardFailure=yes -N \
  -L 127.0.0.1:8090:127.0.0.1:8090 \
  -L 127.0.0.1:8091:127.0.0.1:8091 a52
