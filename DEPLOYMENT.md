# A52 deployment verification — 2026-10-11

Deployed to `~/projects/portfolio` over the pre-existing authenticated Tailscale SSH connection. Native Termux Python virtualenv; no Docker runtime was present. No root access, kernel modifications, or changes to the Gmail collector were made.

Running under the existing runit supervisor:
- `portfolio-public`: static-only visitor server, 127.0.0.1:8090.
- `portfolio-admin`: authenticated editor, 127.0.0.1:8091.
- `portfolio-backup`: daily consistent SQLite/key backups, seven retained.

Verified on the phone:
- All 16 security/publishing tests pass on the deployed source.
- Browser tests through an SSH tunnel pass: desktop/mobile display, no mobile horizontal overflow, category filters, keyboard-dismissible project dialogs, reduced motion, login, new draft, publish, public visibility, delete, logout. No browser JavaScript or CSP errors in the passing run.
- Public `/admin/`, `/admin/login/`, private database/key paths, `.env`, traversal attempts and `/api/projects` return 404. Public POST returns 405. Static resources and security headers are present.
- Service restart preserves projects and accounts. First-time credentials are preserved on repeat deployment.
- Private directory is 0700; application key and credential handoff files are 0600.
- Daily backup service successfully produced a consistent snapshot. An off-phone copy at `backups/a52-portfolio-initial.tar.gz` was extracted in a temporary directory and verified: SQLite integrity OK, three starter projects, one administrator, matching application key file present.
- Existing `minu-email` remained running with its original PID throughout deployment.
- Pinned Python dependency audit reports no known vulnerabilities at the time of deployment. Docker Compose syntax validates; Docker execution is not verified because native Termux is the deployment target.

`manage.py check` passes. `check --deploy` reports four expected HTTPS warnings for the **private loopback-only editor** (HSTS, redirect, Secure session cookie, Secure CSRF cookie). They are deliberately not silenced. The editor is accessible through encrypted SSH; the public application is a separate static server. The public server sets HSTS, and HTTPS redirection/certificates must be verified at the domain edge before launch.

Desktop/mobile/login/studio screenshots are in local `artifacts/`. A private tunnel was opened on the laptop for localhost:8090 and localhost:8091; reconnect later with `scripts/connect.sh`. Phone services are independent of that tunnel and the laptop.

Outstanding: actual domain/DNS provider access, named outbound tunnel configuration and external HTTPS verification; device reboot/battery survival test. Public domain access has not been enabled. Strong isolation from other Termux services is not claimed; see SECURITY.md.

## Practical project portfolio update — 2026-10-11

The owner supplied `projects.md` and four original images. The site now shows all six documented projects, with images for the plant box, Fastbite, Gmail summaries, and Agent farm, and text-only cards for acq and My own environment. No project dates or unsupported features are displayed. The presentation uses compact practical headings, a moderately dark blue accent, and an RK SVG mark. Decorative hero graphics and slogans were removed.

Bundled-image selection and development status are now editable in the private admin. A schema migration adds those fields, and a validated import replaces only the known starter concept records while preserving accounts, unrelated projects, and contact details. An A52 backup was taken before migration/import. Desktop and mobile browser checks passed for all six cards, four images, two text-only cards, category filtering, keyboard-dismissed image dialogs, and admin image/status editing. The updated suite contains 20 passing tests, including public image packaging and import rollback/privacy checks.
