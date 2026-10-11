# Security boundary

The internet-facing process (`serve_public.py`) is a static WSGI server. It imports neither Django nor the account/project database. Its only public routes are `/`, `/healthz`, `/robots.txt`, and enumerated assets inside `static/`. All methods except GET/HEAD are rejected. The index is an atomic export of explicitly published projects, rendered with HTML escaping. Drafts, sessions, password hashes, secrets, backups and admin endpoints are excluded.

The editor runs separately on **127.0.0.1:8091**. Access is through an authenticated SSH tunnel over the existing Tailscale connection. Do not forward this port, create a public tunnel to it, or expose `ADMIN_BIND=0.0.0.0` on a native host. The Docker-only bind override is contained behind a loopback-published Docker port. The admin server uses Django password hashing, database-backed sessions, CSRF tokens, same-site HttpOnly cookies, host validation, a one-hour session lifetime, and django-axes lockout after five failures per username or source IP for 15 minutes. HTTP-only localhost cookies are deliberate: the remote segment is SSH-encrypted. If the editor's access model changes to public HTTPS, its settings and threat model must be reworked first.

Both surfaces reject embedding and MIME sniffing and use restrictive Content Security Policies without inline script or eval. Public responses include HSTS for the future HTTPS origin. All editable external links require HTTPS; templates escape text, and links opened in a new tab use `noopener noreferrer`. Optional external cover images load in visitors' browsers, never through a server-side URL fetch. Only configure trusted image hosts.

## What this does not guarantee

No website can be guaranteed invulnerable. Native Termux processes share one Android app UID: the portfolio and Gmail collector are **not OS-isolated**. The public process intentionally has no route to Gmail data, but a native runtime compromise could access files owned by Termux. Stronger isolation requires a separate device/user or supported container/VM host; the supplied Docker configuration separates the public container from private application data. Do not install privileged Docker workarounds or root the phone merely to host this site.

The domain/TLS edge cannot be tested until a domain and its provider access are supplied. Prefer a named outbound Cloudflare Tunnel to public port 8090, with Always Use HTTPS enabled, modern TLS, and managed DDoS protection. Keep 8091, SSH, n8n, and all Gmail services off public ingress. Do not open router ports to the phone. Android uptime, Termux battery settings and physical reboot recovery still need device-level verification.

## Maintenance

- Update pinned dependencies deliberately, run tests and dependency audit, then redeploy. Current pins reflect installation on 2026-10-11, not a promise of future safety.
- Use a unique admin password; initial random credentials are in private storage. Change via Studio → Password and remove the handoff file when stored in a password manager.
- The Termux backup service uses SQLite's online backup API daily, retaining seven consistent snapshots and the matching application key. Copy backups securely off the phone regularly; same-device backups do not protect against device loss. Docker users should schedule `docker compose exec -T admin python scripts/backup.py` daily separately.
- Backups contain sensitive account/session data. Restore only with editor stopped, verify file permissions, then run `manage.py publish` and restart services. Delete old sessions after restoring (`manage.py shell -c 'from django.contrib.sessions.models import Session; Session.objects.all().delete()'`).
- Run `manage.py clearsessions` periodically. Logs are rotated; routine logs never include submitted passwords or Gmail data.

References: [Django deployment checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/), [OWASP session management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html), [Waitress reverse-proxy guidance](https://docs.pylonsproject.org/projects/waitress/en/stable/reverse-proxy.html), [Cloudflare tunnel configuration](https://developers.cloudflare.com/tunnel/features/locally-managed-tunnels/configuration-file/).

`manage.py check --deploy` intentionally reports the four HTTPS-only warnings for the private SSH-tunneled editor (security.W004/W008/W012/W016). The editor is not the public WSGI app. They must not be waived for any future publicly exposed Django deployment. Ordinary `manage.py check` passes without warnings.

## GitHub Pages deployment

The public repository includes application source and a reviewed public-content snapshot (`content/portfolio.json`). Its workflow packages only `pages-dist`: exported visitor HTML, robots/404 pages, and five allowlisted public assets plus the validated bundled images referenced by published projects. Account records, drafts, database files, application keys, credentials, backups, and admin assets are excluded from that deployment artifact. Published profile/project text is public in both the repository and deployed site.

GitHub Pages serves static content and cannot run the editor or the Python response-header middleware. The build embeds a supported CSP meta policy, while frame-embedding and other response headers are controlled by GitHub's hosting platform. The Pages version therefore does not claim the exact origin-header protections of `serve_public.py`. Keep HTTPS enforced in repository Pages settings.

Actions run with read-only repository access in the build job; only the deployment job receives `pages: write` and `id-token: write`. All five official Actions are pinned to verified commit SHAs. The workflow uses GitHub's temporary credentials and installs no repository token or deploy key on the A52. Public content is synchronized from the phone through the existing authenticated SSH connection on the laptop, then reviewed and pushed as a normal Git commit.

Bundled project covers are selected from explicit model choices under `static/projects/`. The Pages builder independently rejects traversal and non-image asset paths before packaging. Project-import validation runs in a database transaction and preserves accounts, unrelated projects, and existing contact links when the source has no replacement. Only the three known starter concept records are removed during import.
