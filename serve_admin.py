"""Private editor: bind only to loopback and access through SSH."""
import os
os.umask(0o077)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portfolio.settings')
from django.core.wsgi import get_wsgi_application
from waitress import serve

if __name__ == '__main__':
    serve(get_wsgi_application(), host=os.environ.get('ADMIN_BIND', '127.0.0.1'), port=int(os.environ.get('ADMIN_PORT', '8091')), threads=2, max_request_body_size=65536, max_request_header_size=16384, connection_limit=30, channel_timeout=30, clear_untrusted_proxy_headers=True, expose_tracebacks=False)
