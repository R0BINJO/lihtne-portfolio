# My portfolio

A green landing-page portfolio with project images, category filters, and a private project editor. Native Python deployment for the Samsung A52/Termux; optional hardened Docker Compose deployment for a conventional Linux host.

[Public website](https://r0binjo.github.io/lihtne-portfolio/) · [GitHub source](https://github.com/R0BINJO/lihtne-portfolio) · [Automatic hosting instructions](#github-repository-and-automatic-hosting) · [A52 domain setup](#connect-a-public-domain-to-the-a52)

## Open the A52 site and editor

Both services bind to phone loopback. With Tailscale connected, run from this project:

```bash
./scripts/connect.sh
```

Keep that terminal open. Visit:

- Portfolio: http://localhost:8090/
- Private studio: http://localhost:8091/admin/

The username is `robin`. The generated password is in `private/admin-access.txt` on the phone; the deployment handoff also stores a private local copy in `private/a52-admin-access.txt`. Change it under Studio → Password. No public registration exists.

Projects support title, summary, long description, category, tags, bundled project images or an HTTPS image URL, development status, live/source links, display order, and draft/published status. Saving updates the public export immediately; drafts never enter it. Profile edits control the name, headline, bio, availability, location, email, GitHub and LinkedIn links. Delete actions require confirmation.

The six projects come from [projects.md](projects.md). Four have supplied photos/screenshots; acq and My own environment use text-only cards. Select a bundled image in the editor, provide an HTTPS cover URL, or leave both image fields blank. GitHub is linked in the navigation; email contact details can be added under Profile.

## Local development

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/init.py
.venv/bin/python manage.py migrate
.venv/bin/python scripts/init_admin.py
.venv/bin/python manage.py seed
.venv/bin/python manage.py collectstatic --noinput
.venv/bin/python serve_public.py
# Another terminal:
.venv/bin/python serve_admin.py
```

Check: `.venv/bin/python manage.py test tests -v 2`. Production processes use Waitress, not Django's development server. The website needs no Node.js build, third-party CDN scripts, or database on its public process.

## Deploy and operate on the A52

```bash
./scripts/deploy.sh
ssh -F ~/.ssh/config a52 'sv status "$PREFIX/var/service/portfolio-public" "$PREFIX/var/service/portfolio-admin" "$PREFIX/var/service/portfolio-backup"'
```

Phone directory: `~/projects/portfolio`. The deployment allowlists source files, preserves existing accounts/data, installs a private virtualenv, migrates the database, exports static content, and registers runit services with bounded logs. It uses the existing Termux:Boot/runit setup; it does not alter the Gmail collector or SSH configuration. Existing secrets are never overwritten. Back up before schema upgrades.

```bash
ssh -F ~/.ssh/config a52 'cd ~/projects/portfolio && .venv/bin/python scripts/backup.py'
ssh -F ~/.ssh/config a52 'sv restart "$PREFIX/var/service/portfolio-public" "$PREFIX/var/service/portfolio-admin"'
# Password recovery (interactive):
ssh -t -F ~/.ssh/config a52 'cd ~/projects/portfolio && .venv/bin/python manage.py changepassword robin'
# Clear an admin lockout:
ssh -F ~/.ssh/config a52 'cd ~/projects/portfolio && .venv/bin/python manage.py axes_reset'
```

Seven daily private backups are retained under `backups/`; copy them off-phone. Logs: `private/logs/portfolio-{public,admin,backup}/current`. Unrestricted battery settings and Termux:Boot activation matter for uptime. A real phone reboot is not part of the automatic deployment.

## Connect a public domain to the A52

This guide connects a domain you own, such as `portfolio.example.com`, to the portfolio running on the phone. It uses a **named Cloudflare Tunnel** and the existing Termux/runit services. The public website will work without the laptop being on.

**Current state:** the portfolio is deployed on the A52, but no real domain or Cloudflare Tunnel has been configured. These are setup instructions, not a claim that public HTTPS is already working.

### How the connection works

```text
Visitor → HTTPS at Cloudflare → encrypted outbound tunnel to the A52
                                      ↓
                              http://127.0.0.1:8090
                              public portfolio only

Your laptop → Tailscale + SSH tunnel → http://127.0.0.1:8091/admin/
                                      private project editor
```

The phone makes the connection outward. No public phone IP, router port forwarding, Docker, or root access is needed. The address `100.114.184.13` is for private Tailscale administration; do not create public A/AAAA records pointing to it. The domain routes to Cloudflare's tunnel hostname instead. Cloudflare documents this outbound model in its [tunnel configuration guide](https://developers.cloudflare.com/tunnel/configuration/).

### Before you start

Have these ready:

- A registered domain and access to its registrar's nameserver settings.
- A Cloudflare account with access to manage that domain. Enable account two-factor authentication.
- The A52 connected to the internet, with Termux running and the portfolio already deployed at `~/projects/portfolio`.
- A browser for Cloudflare login and a laptop terminal with the existing `a52` SSH alias. Tailscale must be connected for SSH access.

Use `portfolio.example.com` as a placeholder throughout this guide. Replace it with your real hostname. A root domain such as `example.com` also works; choosing a subdomain lets you leave an existing website at the root. Root domains and first-level subdomains are covered by Cloudflare Universal SSL on a full DNS setup; deeper names such as `portfolio.home.example.com` need additional certificate coverage. See [Universal SSL coverage](https://developers.cloudflare.com/ssl/edge-certificates/universal-ssl/).

**Where commands run:** the first SSH command runs on the laptop. After it connects, run the commands labeled **A52 / Termux** in that phone shell. External HTTPS checks later run on the laptop. `$HOME` and `$PREFIX` in phone commands must expand to Termux paths, not laptop paths. Keep the same phone shell open through setup; if you reconnect, re-enter the example variables in steps 4 and 5.

### 1. Add your domain to Cloudflare DNS

**In a browser:**

1. Open the [Cloudflare dashboard](https://dash.cloudflare.com/), choose **Domains → Onboard a domain** (older layouts may say **Add a domain**), and enter the root domain, for example `example.com`.
2. Choose the Free plan for this setup.
3. Review the imported DNS records against your current DNS provider. Preserve existing websites and email records, including MX, SPF, DKIM, DMARC, and verification TXT records. The automatic scan may miss records.
4. Copy the two nameservers Cloudflare assigns to this domain.
5. At your domain registrar, replace the current nameservers with those two nameservers. If DNSSEC is already enabled, follow the registrar's instructions to disable the old DNSSEC/DS configuration before the change.
6. Wait until Cloudflare shows the domain as **Active**. Nameserver changes can take up to 24 hours. Then re-enable DNSSEC using Cloudflare's new values and your registrar's instructions.

If the domain already uses Cloudflare and is Active in the correct account, skip this step. You can keep the domain registered at its current registrar. [Cloudflare's nameserver setup instructions](https://developers.cloudflare.com/dns/zone-setups/full-setup/setup/) explain the DNS-record and DNSSEC checks.

### 2. Connect to the A52 and check the website

**Laptop:**

```bash
ssh -F ~/.ssh/config a52
```

**A52 / Termux:**

```bash
cd "$HOME/projects/portfolio"
sv status "$PREFIX/var/service/portfolio-public"
sv status "$PREFIX/var/service/portfolio-admin"
curl -fsS http://127.0.0.1:8090/healthz
curl -sS -o /dev/null -w 'Portfolio HTTP status: %{http_code}\n' http://127.0.0.1:8090/
```

Both services should show `run:`, the health endpoint should return `ok`, and the portfolio should return `200`. Fix a failed local service before creating the tunnel:

```bash
sv restart "$PREFIX/var/service/portfolio-public"
tail -n 40 "$HOME/projects/portfolio/private/logs/portfolio-public/current"
```

Only **8090** belongs in the public tunnel. Port **8091** is the admin editor; keep it private.

### 3. Install the native Termux tunnel package

**A52 / Termux:**

```bash
pkg update
pkg install cloudflared curl termux-services
cloudflared --version
```

Use Termux's package, which is built for Android. See the [official Termux cloudflared package](https://github.com/termux/termux-packages/blob/master/packages/cloudflared/build.sh). If the package cannot be found, run `termux-change-repo`, choose an official main-repository mirror, and repeat `pkg update` and the installation.

The installed package may also provide a disabled service named `cloudflared`. This guide creates a dedicated service named `portfolio-tunnel`; use that service for the portfolio. The existing portfolio supervisor is already installed. If you install `termux-services` on a fresh phone, open a new Termux shell afterward as described by [Termux services](https://github.com/termux/termux-services).

### 4. Authorize Cloudflare and create a named tunnel

**A52 / Termux:**

```bash
umask 077
mkdir -p "$HOME/.cloudflared"
chmod 700 "$HOME/.cloudflared"
cloudflared tunnel login
```

Open the login URL displayed by the command in a browser, sign in, select the domain, and approve authorization. If a browser does not open over SSH, use the displayed URL on the laptop while leaving the command running on the phone. Wait for the command to report successful login; it saves `cert.pem` in the phone's `.cloudflared` directory.

Then create the tunnel:

```bash
portfolio_tunnel_name='robin-portfolio'
cloudflared tunnel create "$portfolio_tunnel_name"
cloudflared tunnel list
```

Record the returned **tunnel UUID** and credential JSON path. The UUID is an identifier, not the JSON credential itself. If a tunnel with this name already exists, inspect the existing tunnel and use its UUID and matching credential file; do not keep creating replacement tunnels during troubleshooting.

`cert.pem` authorizes tunnel management; the `<UUID>.json` file authorizes running this tunnel. Keep both private, outside this repository and all public asset directories. Do not paste their contents into messages or commit them. This follows the [locally managed tunnel workflow](https://developers.cloudflare.com/tunnel/features/locally-managed-tunnels/create-local-tunnel/).

### 5. Write a configuration that exposes only the portfolio

**A52 / Termux:** replace the two example values before running this block:

```bash
portfolio_domain='portfolio.example.com'
portfolio_tunnel_id='REPLACE_WITH_THE_TUNNEL_UUID'

# This must exist: use the exact JSON path reported by tunnel creation.
test -f "$HOME/.cloudflared/$portfolio_tunnel_id.json"
```

If `test` fails, correct the UUID/path before continuing. If you already have `~/.cloudflared/portfolio.yml`, back it up before replacing it. Leave any configuration for other tunnels alone.

```bash
cat > "$HOME/.cloudflared/portfolio.yml" <<EOF_CONFIG
tunnel: $portfolio_tunnel_id
credentials-file: $HOME/.cloudflared/$portfolio_tunnel_id.json
ingress:
  - hostname: $portfolio_domain
    service: http://127.0.0.1:8090
  - service: http_status:404
EOF_CONFIG

chmod 600 "$HOME/.cloudflared/portfolio.yml"
chmod 600 "$HOME/.cloudflared/$portfolio_tunnel_id.json"
chmod 600 "$HOME/.cloudflared/cert.pem"

cloudflared tunnel --config "$HOME/.cloudflared/portfolio.yml" ingress validate
cloudflared tunnel --config "$HOME/.cloudflared/portfolio.yml" ingress rule "https://$portfolio_domain/"
cloudflared tunnel --config "$HOME/.cloudflared/portfolio.yml" ingress rule https://unmatched.example.net/
```

Validation must succeed. Your hostname should match the rule for `http://127.0.0.1:8090`; the unmatched example should match the final `http_status:404` rule. Use an exact hostname rather than a wildcard. The local HTTP hop stays on the phone's loopback interface; the tunnel carries it over an encrypted connection. Do not change the origin URL to HTTPS: the current portfolio listener does not have a local TLS certificate.

The project also contains [deploy/cloudflared.yml.example](deploy/cloudflared.yml.example). The commands above create the real configuration privately on the phone. See [Cloudflare ingress configuration](https://developers.cloudflare.com/tunnel/features/locally-managed-tunnels/configuration-file/).

### 6. Create the DNS route and test the tunnel in the foreground

**A52 / Termux:**

```bash
cloudflared tunnel route dns "$portfolio_tunnel_id" "$portfolio_domain"
cloudflared tunnel --config "$HOME/.cloudflared/portfolio.yml" run "$portfolio_tunnel_id"
```

The DNS command creates a CNAME to `<UUID>.cfargotunnel.com`. In the Cloudflare dashboard, open your domain's **DNS → Records** and confirm that the chosen hostname has that target and is **Proxied** (orange cloud). Keep TTL on Auto. If a conflicting A, AAAA, or CNAME already exists for this exact hostname, review it before replacing it; records for other hostnames and email remain needed. Do not use the overwrite flag blindly.

Leave the foreground tunnel running while testing `https://YOUR_REAL_HOSTNAME/` in a browser. Successful tunnel logs should show registered connections. After the first successful check, press **Ctrl+C** in the phone shell and continue with the supervised service below. The DNS record alone cannot serve the site while no tunnel connector is running.

### 7. Keep the tunnel running after you disconnect

Create a dedicated runit service using the A52's existing supervisor. This block writes scripts for the tunnel; it does not alter the public or admin servers.

**A52 / Termux:**

```bash
portfolio_service="$PREFIX/var/service/portfolio-tunnel"
portfolio_logs="$HOME/projects/portfolio/private/logs/portfolio-tunnel"

umask 077
mkdir -p "$portfolio_service/log" "$portfolio_logs"
touch "$portfolio_service/down"

cat > "$portfolio_service/run" <<EOF_RUN
#!$PREFIX/bin/sh
umask 077
exec 2>&1
exec "$PREFIX/bin/cloudflared" tunnel --config "$HOME/.cloudflared/portfolio.yml" run
EOF_RUN

cat > "$portfolio_service/log/run" <<EOF_LOG
#!$PREFIX/bin/sh
exec "$PREFIX/bin/svlogd" -tt "$portfolio_logs"
EOF_LOG

printf 's1000000\nn3\n' > "$portfolio_logs/config"
chmod 700 "$portfolio_service/run" "$portfolio_service/log/run"
sv-enable portfolio-tunnel
sv status "$portfolio_service"
```

The status should show `run:` for the service and its logger. Logs rotate at roughly 1 MB per file with three old files retained. Read them with:

```bash
tail -n 40 "$HOME/projects/portfolio/private/logs/portfolio-tunnel/current"
```

If runit reports `unable to open supervise/ok`, wait a few seconds for the existing supervisor to discover the new directory and run `sv up "$PREFIX/var/service/portfolio-tunnel"` again. If the supervisor itself is stopped, run `service-daemon start` inside Termux, then retry. The phone already has the Termux:Boot script `~/.termux/boot/20-minu-services` to start the supervisor; an enabled `portfolio-tunnel` service is discovered by that same supervisor.

Daily commands, run on the A52:

```bash
sv status "$PREFIX/var/service/portfolio-tunnel"
sv restart "$PREFIX/var/service/portfolio-tunnel"
# Temporarily stop until explicitly started or supervision restarts:
sv down "$PREFIX/var/service/portfolio-tunnel"
# Start again:
sv up "$PREFIX/var/service/portfolio-tunnel"
# Disable persistently, including across supervisor/phone restarts:
sv-disable portfolio-tunnel
# Enable again:
sv-enable portfolio-tunnel
```

Use the Termux runit service, not `sudo`, `systemctl`, or `cloudflared service install`.

### 8. Turn on HTTPS redirection and check the edge certificate

**In the Cloudflare dashboard, for your domain:**

1. Open **SSL/TLS → Edge Certificates** and check that Universal SSL has an active certificate covering your hostname. New certificates may take time to become active.
2. Enable **Always Use HTTPS**. If the option is unavailable, check that the SSL/TLS encryption mode is not Off. This setting applies to the domain's proxied hosts; ensure any other existing hosts support HTTPS before enabling it across the zone.
3. Set the **Minimum TLS Version** to TLS 1.2 or newer, and enable TLS 1.3 where available.
4. Keep the tunnel origin at `http://127.0.0.1:8090`. The visitor certificate is supplied by Cloudflare, and the tunnel connection is encrypted; you do not need Certbot or a publicly reachable port 443 on the A52 for this setup.

The portfolio already sends `Strict-Transport-Security: max-age=31536000`. Do not enable HSTS preload or `includeSubDomains` for your entire domain unless all affected hosts are ready for HTTPS. See [Always Use HTTPS](https://developers.cloudflare.com/ssl/edge-certificates/additional-options/always-use-https/) and [edge TLS options](https://developers.cloudflare.com/ssl/edge-certificates/additional-options/).

### 9. Verify the public website and security boundary

Use the real hostname below. **Laptop terminal:**

```bash
portfolio_domain='portfolio.example.com'

# Expect 200, a valid certificate, and the security headers.
curl -sS -D - -o /dev/null "https://$portfolio_domain/"

# Expect a redirect to https:// with 301 or another redirect status.
curl -sS -D - -o /dev/null "http://$portfolio_domain/"

# These paths must return 404 from the public website.
for portfolio_path in /admin/ /admin/login/ /private/db.sqlite3 /private/secret.key /.env; do
  curl -sS -o /dev/null -w "%{http_code} $portfolio_path\n" "https://$portfolio_domain$portfolio_path"
done

# Keep the traversal path intact; expect 404 (an edge rejection also blocks access).
curl --path-as-is -sS -o /dev/null -w '%{http_code}\n' \
  "https://$portfolio_domain/static/../private/secret.key"

# Public writes are disabled: expect 405 from the application.
curl -sS -X POST -d '{}' -o /dev/null -w '%{http_code}\n' "https://$portfolio_domain/"
```

Do not add `-k`/`--insecure`: a certificate error must be fixed. In the HTTPS response look for `Content-Security-Policy`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, and `Strict-Transport-Security`. The portfolio response should not set a login/session cookie. If Cloudflare WAF returns a block/challenge instead of the expected application status, inspect its security events and confirm the origin checks on the phone; never count a `200` page at an admin/private-file path as a successful check.

Also open the site from a browser outside your tailnet, for example a second device on mobile data with Tailscale off. Check the layout, project filters and project dialogs. Close the laptop SSH session or shut down the laptop and check the public site again: the phone's supervised tunnel must keep serving it independently.

The local origin checks remain available on the A52:

```bash
cd "$HOME/projects/portfolio"
.venv/bin/python scripts/verify_http.py
```

The helper checks HTTP status, security headers, and blocked private routes without depending on a particular headline.

### 10. Edit projects after the domain is connected

**Laptop, from this project directory:**

```bash
./scripts/connect.sh
```

Keep the terminal open, then visit **http://localhost:8091/admin/**. Your private credentials are described in [Open the A52 site and editor](#open-the-a52-site-and-editor). Saving a published project updates the export served at your public domain. The domain's `/admin/` URL stays unavailable.

If a tunnel is already open on laptop ports 8090/8091, reuse it. An `Address already in use` error means another process already has the port; avoid starting duplicate tunnels. No domain setting belongs in Django's `ALLOWED_HOSTS` for this design: Django serves the private editor on localhost; the separate public server serves the domain.

Leave Cloudflare's default caching in place. Do not create a **Cache Everything** rule for the HTML homepage: its `Cache-Control: no-cache` response allows project updates to be seen promptly. If an existing custom cache rule serves stale HTML, exclude this hostname/homepage or purge its cached page after correcting the rule.

### Optional: use the root domain and `www`

For the simplest root-only setup, use `example.com` instead of `portfolio.example.com` in steps 5 and 6. Cloudflare handles the root CNAME through its DNS setup.

To serve the same portfolio at both `example.com` and `www.example.com`, add **both exact hostnames** before the final catch-all rule in `~/.cloudflared/portfolio.yml`:

```yaml
ingress:
  - hostname: example.com
    service: http://127.0.0.1:8090
  - hostname: www.example.com
    service: http://127.0.0.1:8090
  - service: http_status:404
```

Keep the existing `tunnel` and `credentials-file` fields. On the A52, create a DNS route for each name using the same tunnel UUID, validate, and restart:

```bash
cloudflared tunnel route dns "$portfolio_tunnel_id" example.com
cloudflared tunnel route dns "$portfolio_tunnel_id" www.example.com
cloudflared tunnel --config "$HOME/.cloudflared/portfolio.yml" ingress validate
sv restart "$PREFIX/var/service/portfolio-tunnel"
```

Replace both example names with your real names. If you want `www` to redirect to the root instead, configure a Cloudflare Redirect Rule after both names work over HTTPS. A second DNS name needs a matching ingress rule or an edge redirect; DNS alone does not make it match your first hostname.

### Android uptime and a reboot check

Keep the A52 charged and connected. Open the **Termux:Boot** launcher once, and allow unrestricted/background battery use for Termux and Termux:Boot. Tailscale also needs background access for remote administration. A wake lock is already part of this phone's boot setup; it affects battery use and does not defeat Android force-stop behavior.

At a convenient time, reboot the A52, unlock it once, and confirm the public domain works while the laptop is off. Then reconnect over SSH and check:

```bash
sv status "$PREFIX/var/service/portfolio-public"
sv status "$PREFIX/var/service/portfolio-tunnel"
```

If Android suppresses startup, open Termux and check its battery/Boot settings. A powered-off phone, lost network connection, or force-stopped Termux cannot serve this website. The application deployment was tested; the new domain tunnel and real reboot must be tested after you configure them.

### Troubleshooting

| Symptom | What to check |
| --- | --- |
| Cloudflare zone stays Pending | Verify the two assigned nameservers at the registrar and any old DNSSEC/DS settings. Wait for delegation to update. |
| `NXDOMAIN` / domain not found | Confirm the zone is Active and that the exact hostname has the proxied CNAME route. A subdomain route does not create a root-domain route. |
| DNS route says a record already exists | Inspect the A/AAAA/CNAME for that exact name. Replace only the conflicting website record if you intend to move it; preserve other DNS and mail records. |
| Cloudflare error **1033** | No healthy connector is reachable. Check `portfolio-tunnel` status, phone internet access, the UUID/credential match, and the tunnel log. |
| Cloudflare **502 Bad Gateway** | Check `curl http://127.0.0.1:8090/` on the phone. Confirm ingress uses **HTTP**, port **8090**, and the public service is running. |
| Your domain returns **404** | Confirm its exact spelling in ingress and the DNS record's tunnel UUID. Run `ingress rule` with the real URL. A typo can match the catch-all rule. |
| Browser certificate error | Check the Active edge certificate, hostname coverage, zone activation and DNS/CAA issues. Do not bypass certificate validation. |
| Tunnel repeatedly disconnects | Read rotated logs, check battery restrictions and connectivity, and allow outbound tunnel traffic on port 7844. If UDP/QUIC is blocked, use the HTTP/2 fallback below. |
| Website goes offline when SSH closes | The foreground tunnel was used instead of the enabled `portfolio-tunnel` service. Confirm `sv-enable portfolio-tunnel` and `run:` status. |
| Updates appear stale | Check the public export and custom Cloudflare/browser caching. Remove an HTML Cache Everything override and purge that page if needed. |
| Public `/admin/` returns 404 | This is expected. Open the editor through `scripts/connect.sh` and localhost:8091. |

If your network blocks QUIC, add this top-level line to `~/.cloudflared/portfolio.yml`, alongside `tunnel` and `credentials-file`:

```yaml
protocol: http2
```

Then validate and restart `portfolio-tunnel`. HTTP/2 still needs outbound TCP port 7844; this is an outbound allowance, not router forwarding. Refer to [tunnel connectivity requirements](https://developers.cloudflare.com/tunnel/configuration/) and [Cloudflare troubleshooting](https://developers.cloudflare.com/tunnel/troubleshooting/).

### Stop public access or recover later

To take the portfolio's public tunnel offline without deleting website data, run on the A52:

```bash
sv-disable portfolio-tunnel
sv status "$PREFIX/var/service/portfolio-tunnel"
```

The public domain will stop serving once the connector disconnects; the private editor and exports remain. Remove the hostname's CNAME in Cloudflare DNS as well if you want to remove the route. Do not delete the domain's other DNS records. Re-enable with `sv-enable portfolio-tunnel` when ready.

Back up `~/.cloudflared/portfolio.yml` and the matching tunnel JSON securely, separately from the application's daily database backups: those backups do not include `.cloudflared`. Keep a protected copy of `cert.pem` only if you need this CLI authorization for management. If tunnel credentials are exposed, revoke/recreate the affected tunnel and update its DNS and service configuration rather than merely changing file permissions.

This guide keeps only port 8090 on public ingress. Review [SECURITY.md](SECURITY.md) for the existing application protections and the shared Termux-account isolation limit. Setup should be considered complete only after the external HTTPS, private-path, laptop-off, and reboot checks succeed.

## GitHub repository and automatic hosting

Source repository: **https://github.com/R0BINJO/lihtne-portfolio**.

Public GitHub Pages address: **https://r0binjo.github.io/lihtne-portfolio/**. The deployment workflow reports the actual deployment status in the repository's **Actions** tab.

Every push to `main` runs the security tests, builds the public portfolio, and deploys it through `.github/workflows/pages.yml`. Pull requests run tests and build without publishing. Repository **Settings → Pages → Source** must be **GitHub Actions**. HTTPS should be enforced in Pages settings.

GitHub Pages serves a static copy of the public portfolio; the Python admin editor continues to run privately on the A52. Pages stays online independently of the phone, but edits made in the A52 editor need a refreshed content snapshot and a Git push before they appear there. [GitHub Pages supports static hosting, not a Python server](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site).

### Update GitHub Pages after editing projects on the A52

In a normal clone on the laptop, with Tailscale connected:

```bash
git clone https://github.com/R0BINJO/lihtne-portfolio.git
cd lihtne-portfolio
# For later updates, use your existing clone and pull main first.
./scripts/sync-public-content.sh
git diff -- content/portfolio.json
git add content/portfolio.json
git commit -m "Update published portfolio content"
git push origin main
```

`sync-public-content.sh` requests only the public profile and published projects using `manage.py export_content`. It does not retrieve the private database, drafts, users, sessions, passwords, or application key. Review the JSON before committing: any contact email or project description you have published will also be visible in this public repository. Source changes to templates, public styles, and scripts deploy on push as well.

The export command is included in the A52 source after deployment. If you restore an older phone backup/source version and it is missing, run `scripts/deploy.sh` from the current clone first.

### Build a Pages preview locally

After installing the Python dependencies:

```bash
.venv/bin/python scripts/build_pages.py --base-path /lihtne-portfolio
# To preview at localhost root instead, use an empty base path:
.venv/bin/python scripts/build_pages.py --base-path ''
.venv/bin/python -m http.server 8080 --bind 127.0.0.1 --directory pages-dist
```

Open `http://localhost:8080/` after the root-path build. Only the allowlisted visitor assets, referenced bundled project images, and exported HTML are packaged; backend code and private directories are excluded from the Pages artifact. The source repository still contains the backend code for running the A52 editor.

### Use a custom domain with GitHub Pages

If you choose GitHub Pages as the public host, set the domain under repository **Settings → Pages → Custom domain**, then follow [GitHub's custom-domain DNS instructions](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site). For a subdomain such as `portfolio.example.com`, the DNS CNAME points to `r0binjo.github.io` (no repository path). Verify domain ownership using GitHub's TXT verification before sharing it and enable **Enforce HTTPS** once its certificate is ready.

After changing the domain, rerun the Pages workflow so `actions/configure-pages` supplies the correct base path. Use either the GitHub Pages route or the A52 Cloudflare Tunnel route for a particular hostname; do not point the same hostname at both.

### Security differences from A52 hosting

Pages controls HTTP response headers, so the Python public server's full security-header configuration does not apply to Pages. The static build adds the supported Content Security Policy directives as an HTML meta policy and retains escaped text, safe external links, local scripts/fonts, and HTTPS hosting. A meta policy cannot enforce `frame-ancestors` or set `X-Frame-Options`, `X-Content-Type-Options`, or `Cache-Control` headers. The A52 origin remains the option when you need control of those headers.

No GitHub credential is installed on the phone for this workflow. GitHub's short-lived Actions token publishes the site. Secrets and backups remain excluded from Git. See [GitHub's Pages workflow documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).

## Docker alternative

The inspected A52 has no Docker runtime and is an unprivileged Termux environment. On a supported Docker host:

```bash
docker compose build
docker compose up -d
# Read the initial credential privately:
docker compose exec admin cat private/admin-access.txt
```

Two non-root containers, loopback-published ports, read-only roots, dropped capabilities, resource limits, bounded logs, and a public container that has only a read-only exported-content volume. The database/key volumes mount exclusively into the admin container. Use a host SSH tunnel for administration and a TLS reverse proxy for the public service. Docker files are provided for portability; native Termux is the verified target.

## Gmail / n8n

Existing migration records and live A52 service inspection show Gmail already runs natively under `minu-email` on the A52. The laptop n8n email workflow was deactivated during that prior migration; the remaining n8n demo is separate. This portfolio deployment preserves the working collector and does not re-enable duplicate Gmail polling or copy private email content into this project. Moving the remaining n8n engine is not required for Gmail and is not implemented on unprivileged Termux.

See [DESIGN.md](DESIGN.md) for internet inspiration and font licensing.
