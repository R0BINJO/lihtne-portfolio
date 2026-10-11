#!/usr/bin/env python3
"""Read-only HTTP verification of the two separate listeners."""
import json
import time
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

def fetch(port, path, method='GET'):
    for attempt in range(10):
        try:
            result = urlopen(Request(f'http://127.0.0.1:{port}{path}', method=method), timeout=5)
        except HTTPError as error:
            result = error
        except (URLError, TimeoutError):
            if attempt == 9:
                raise
            time.sleep(0.5)
            continue
        return result.status, result.headers, result.read()

status, headers, body = fetch(8090, '/')
assert status == 200 and b'class="project-grid"' in body
assert "form-action 'none'" in headers['Content-Security-Policy']
assert headers['X-Frame-Options'] == 'DENY'
assert headers['Strict-Transport-Security'] == 'max-age=31536000'
assert 'Set-Cookie' not in headers
for path in ['/admin/', '/admin/login/', '/private/db.sqlite3', '/.env', '/static/../private/secret.key', '/api/projects']:
    assert fetch(8090, path)[0] == 404, path
assert fetch(8090, '/', 'POST')[0] == 405
assert fetch(8090, '/static/site.css')[0] == 200
assert fetch(8090, '/static/site.js')[0] == 200
status, headers, body = fetch(8091, '/admin/login/')
assert status == 200 and b'csrfmiddlewaretoken' in body
assert headers['Referrer-Policy'] == 'same-origin'
assert headers['Cache-Control'] == 'no-store'
print(json.dumps({'public':'healthy','admin':'private login healthy','public_admin_routes':'404','sensitive_files':'404','public_mutations':'405','security_headers':'present'}))
