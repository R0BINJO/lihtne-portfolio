#!/usr/bin/env python3
"""Build a database-free GitHub Pages artifact from reviewed public JSON."""
import argparse
import json
import shutil
from html import escape
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent.parent
PUBLIC_ASSETS = ['site.css', 'site.js', 'favicon.svg', 'fonts/space-grotesk.ttf', 'fonts/OFL.txt']
CSP = "default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' https:; font-src 'self'; connect-src 'none'; base-uri 'none'; form-action 'none'; object-src 'none'; upgrade-insecure-requests"


def build(content_path, output, base_path=''):
    if base_path and (not base_path.startswith('/') or any(character not in '/abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.' for character in base_path) or '..' in base_path):
        raise ValueError('Base path must be an absolute URL path without traversal.')
    payload = json.loads(content_path.read_text())
    if payload.get('schema_version') != 1:
        raise ValueError('Unsupported public content schema.')

    from django.conf import settings
    settings.configure(
        INSTALLED_APPS=['django.contrib.staticfiles'],
        STATIC_URL=base_path.rstrip('/') + '/static/',
        TEMPLATES=[{'BACKEND': 'django.template.backends.django.DjangoTemplates', 'DIRS': [ROOT / 'templates']}],
        USE_TZ=True,
    )
    import django
    django.setup()
    from django.template.loader import render_to_string

    categories = {'development': 'Development', 'design': 'Design', 'experiment': 'Experiment'}
    projects = []
    for project in payload['projects']:
        project = dict(project)
        project['pk'] = int(project.pop('id'))
        project['tag_list'] = [tag.strip() for tag in project['tags'].split(',') if tag.strip()][:8]
        project['get_category_display'] = categories[project['category']]
        projects.append(SimpleNamespace(**project))
    html = render_to_string('index.html', {'profile': SimpleNamespace(**payload['profile']), 'projects': projects})
    # Pages cannot configure origin response headers. Enforce supported CSP directives in HTML.
    html = html.replace('<head>', '<head>\n<meta http-equiv="Content-Security-Policy" content="' + escape(CSP, quote=True) + '">', 1)
    html = html.replace('<meta name="theme-color"', '<meta name="referrer" content="no-referrer"><meta name="theme-color"', 1)
    output.mkdir(parents=True, exist_ok=True)
    (output / 'index.html').write_text(html)
    (output / '.nojekyll').touch()
    (output / 'robots.txt').write_text('User-agent: *\nAllow: /\n')
    (output / '404.html').write_text('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Not found</title></head><body><h1>Page not found</h1><p><a href="' + escape(base_path.rstrip('/') + '/', quote=True) + '">Return to portfolio</a></p></body></html>')
    for asset in PUBLIC_ASSETS:
        source = ROOT / 'static' / asset
        target = output / 'static' / asset
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    print('Static Pages artifact built from public content only.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--content', type=Path, default=ROOT / 'content/portfolio.json')
    parser.add_argument('--output', type=Path, default=ROOT / 'pages-dist')
    parser.add_argument('--base-path', default='')
    arguments = parser.parse_args()
    build(arguments.content, arguments.output, arguments.base_path)
