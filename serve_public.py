"""Static-only public server. Never imports Django, opens a DB, or reads secrets."""
import os
from pathlib import Path
from waitress import serve
from whitenoise import WhiteNoise

ROOT = Path(__file__).resolve().parent
PUBLIC = Path(os.environ.get('PUBLISHED_DIR', ROOT / 'published'))
ASSETS = Path(os.environ.get('ASSET_DIR', ROOT / 'static'))
CSP = "default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' https:; font-src 'self'; connect-src 'none'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'; object-src 'none'; upgrade-insecure-requests"
HEADERS = [('Content-Security-Policy', CSP), ('X-Content-Type-Options', 'nosniff'), ('X-Frame-Options', 'DENY'), ('Referrer-Policy', 'no-referrer'), ('Permissions-Policy', 'camera=(), microphone=(), geolocation=(), payment=()'), ('Strict-Transport-Security', 'max-age=31536000')]

def site(environ, start_response):
    path = environ.get('PATH_INFO', '/')
    status, kind = '200 OK', 'text/html; charset=utf-8'
    if path == '/':
        try:
            body = (PUBLIC / 'index.html').read_bytes()
        except FileNotFoundError:
            status, body = '503 Service Unavailable', b'Portfolio is being prepared.'
    elif path == '/healthz':
        body, kind = b'ok', 'text/plain'
    elif path == '/robots.txt':
        body, kind = b'User-agent: *\nAllow: /\n', 'text/plain'
    else:
        status, body = '404 Not Found', b'Not found'
    start_response(status, [('Content-Type', kind), ('Content-Length', str(len(body))), ('Cache-Control', 'no-cache')])
    return [body if environ['REQUEST_METHOD'] != 'HEAD' else b'']

static_app = WhiteNoise(site, root=str(ASSETS), prefix='static/', max_age=3600, autorefresh=False)

def application(environ, start_response):
    def secure_start(status, headers, exc_info=None):
        return start_response(status, headers + HEADERS, exc_info)
    if environ['REQUEST_METHOD'] not in ('GET', 'HEAD'):
        secure_start('405 Method Not Allowed', [('Allow', 'GET, HEAD'), ('Content-Type', 'text/plain'), ('Content-Length', '0')])
        return [b'']
    return static_app(environ, secure_start)

if __name__ == '__main__':
    serve(application, host=os.environ.get('PUBLIC_BIND', '127.0.0.1'), port=int(os.environ.get('PUBLIC_PORT', '8090')), threads=2, max_request_body_size=1024, max_request_header_size=16384, connection_limit=100, channel_timeout=30, clear_untrusted_proxy_headers=True, expose_tracebacks=False)
