#!/usr/bin/env bash
# Refresh the GitHub Pages source from already-published A52 content.
set -euo pipefail
cd "$(dirname "$0")/.."
portfolio_temporary="$(mktemp content/.portfolio-XXXXXX)"
trap 'rm -f "$portfolio_temporary"' EXIT
ssh -F "$HOME/.ssh/config" -o BatchMode=yes a52 \
  'cd projects/portfolio && .venv/bin/python manage.py export_content' > "$portfolio_temporary"
python3 - "$portfolio_temporary" <<'PY'
import json
import sys
from pathlib import Path
content = json.loads(Path(sys.argv[1]).read_text())
assert content['schema_version'] == 1
assert isinstance(content['profile'], dict)
assert isinstance(content['projects'], list)
PY
mv "$portfolio_temporary" content/portfolio.json
printf 'Public content snapshot refreshed. Review, commit, and push to deploy Pages.\n'
