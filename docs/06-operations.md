# 06 — Operations

One maintainer, many customer-controlled hosts. Everything here aims for **installs you can repeat, updates you can undo, and backups you've tested.**

## Support matrix

| Item | Supported |
|---|---|
| CPU architecture | x86_64, ARM64 |
| OS | Ubuntu 26.04 LTS, Debian 13 (the latest stable releases; see [#029](09-decisions.md#029--use-the-latest-stable-versions)) |
| Container runtime | Docker Engine (current major) + Compose v2 plugin |
| Minimum spec | 2 cores, 4 GB RAM, 40 GB SSD |
| Recommended | 4 cores, 8–16 GB RAM, SSD, UPS (on-prem) |
| Not supported | Windows hosts, NAS appliances, Docker Desktop for production |

Re-check the minimum spec once the solver exists (P6) and update this table.

## Deployment targets

| | On-prem | Cloud (customer-owned account) |
|---|---|---|
| Who pays for infrastructure | Customer (hardware) | Customer (provider bill) |
| Internet exposure | **Cloudflare Tunnel** (default) or port forward + dynamic DNS | Public IP; Caddy automatic TLS |
| Firewall | No inbound ports with a tunnel | Only 80/443 inbound |
| Maintainer access | Tailscale SSH | Tailscale SSH + admin access in the cloud account |
| Backups go to | Customer's cloud bucket or a USB drive | Object storage in the same cloud account |
| Database | Postgres container | Postgres container (managed Postgres optional through `DATABASE_URL`) |

> **Cloudflare Tunnel trade-off:** traffic is decrypted at Cloudflare. Tell customers this; offer port forwarding if they want no third party in the path.

## Install

1. **Provision the host:** run the Ansible playbook (or cloud-init on cloud servers). It applies:
   - OS updates, `unattended-upgrades` for security patches
   - UFW firewall, SSH key-only login, fail2ban
   - Docker Engine + Compose, Tailscale, time sync (chrony)
   - Optional disk encryption (LUKS + TPM unlock so reboots don't need a passphrase)
2. **Run `punchedn install`:**
   - **Preflight:** checks CPU architecture, RAM, free disk, Docker/Compose versions, that ports are free, **that the clock is in sync**, and outbound DNS/HTTPS
   - Generates secrets → `/opt/punchedn/.env` (`0600`)
   - Pulls the pinned image version, starts the stack, runs migrations, creates the first admin
   - Sets up backups and the optional heartbeat
3. **Walk through the onboarding checklist** with the customer (branding, SMTP test, first admin login, backup destination test).

## The `punchedn` admin command

| Command | Does |
|---|---|
| `install` | Preflight check + first-time setup |
| `status` | Container health, version, disk, last backup, last heartbeat |
| `update [version]` | **Backup → pull → migrate → health check → roll back automatically if it fails** |
| `rollback` | Restore the previous image version + the database from before the update |
| `backup` | Encrypted `pg_dump` + uploads archive → local + offsite |
| `restore <file>` | Restore to a running or fresh host |
| `support-bundle` | Zips logs (personal data removed), versions, config (secrets removed), `status` output |
| `logs [service]` | Tail logs |

### Update safety

- Images are pinned by version (`ghcr.io/<you>/punchedn:1.4.2`), never `latest`.
- Images are **signed with cosign** in CI; `update` checks the signature and refuses unsigned or tampered images.
- **Support policy:** the latest two minor versions are supported. Hosts on older versions are flagged in the heartbeat dashboard.
- Migrations must work when **upgrading from any earlier supported release**. CI tests N-1 → N (and the oldest supported → N once there are several).
- Destructive schema changes use **expand → migrate → contract** across two releases.
- The health check after an update covers `/health/ready` (DB reachable, migrations at head, worker heartbeat).

## Backups

- **Nightly** automated, encrypted (age or GPG) `pg_dump` + an archive of the uploads volume.
- **Retention:** 7 daily, 4 weekly, 6 monthly.
- **Offsite:** the customer's own S3-compatible bucket (Backblaze B2, AWS S3, etc.) or a USB drive.
- **Restore test:** automated restore into a temporary container **monthly**; failures alert the owner and the maintainer.
- Backup failures show up in `status`, the heartbeat and an email alert.
- **Recovery promise:** RPO ≤ 24 h (nightly backup), **RTO ≤ 1 business day** on replacement hardware or a new cloud server. Rehearse a full recovery before the pilot and once a year after.

## Outages on the customer's side

The schedule must never exist only on the box ([DQ-9](10-design-questions.md#dq-9-resilience-when-an-on-prem-box-goes-down)):
- The PWA caches each employee's published shifts for viewing offline.
- Publishing emails each employee their shifts and updates their iCal feed.
- Recommend a UPS on-prem; Docker restart policies + the host restoring power automatically (BIOS setting) bring the stack back after a power cut.

## Monitoring

| Signal | How |
|---|---|
| Liveness / readiness | `/health/live`, `/health/ready`; Docker healthchecks; containers restart automatically |
| Heartbeat (opt-in) | Daily POST to the maintainer: install ID, version, uptime, free disk, last backup result. **No business data** |
| Errors (opt-in) | Sentry SDK → self-hosted GlitchTip; personal data removed before sending |
| Local alerts | Email to the business owner on backup failure, low disk, failed update |
| Logs | JSON to stdout → Docker `local` log driver with rotation (e.g. 10 × 20 MB) |
| Usage stats (opt-in, P7) | Weekly counts of feature use only (e.g. "schedules published: 4"). No names, no business data. Shows what on-prem customers actually use |

## Maintainer security

Your access to every customer is the biggest single risk ([DQ-8](10-design-questions.md#dq-8-maintainer-access-is-the-biggest-security-risk)):

| Control | Detail |
|---|---|
| Hardware security keys | FIDO2 on GitHub, GHCR, Tailscale, email, domain registrar, password manager, cloud consoles |
| Tailscale access rules | One tag per customer; access only from your device(s); SSH sessions logged; no always-on root |
| Signed releases | cosign signing in CI; key or keyless identity protected by the above |
| Laptop | Full-disk encryption, automatic screen lock, OS auto-updates, no customer data stored on it |
| Cloud accounts | Your own separate user in each customer's cloud account (never the root account), with MFA, limited to what you need |
| Business | LLC, support agreement + data processing agreement, cyber/E&O insurance, all **before the pilot** |
| Incident plan | One-page runbook: rotate keys, revoke Tailscale access, notify customers. Know your breach-notification obligations |

## Remote support

- Tailscale, with the customer's consent recorded in the support agreement.
- Always start with `punchedn support-bundle`; avoid poking around in production data.
- Keep a short **runbook** per common issue (disk full, tunnel down, SMTP failing, failed update).
- Keep a simple customer register: host, version, hosting type, backup destination, contact. Your heartbeat dashboard fills most of it in.

## Release process

1. Merge to `main` with Conventional Commits.
2. release-please opens a release PR (version + changelog).
3. Merging it tags the release → CI builds and publishes images for both processor types and the release notes.
4. Install on your own **staging host** (a home box or a cheap cloud server) → smoke test.
5. Roll out to customers: one pilot or friendly customer first, then the rest. Security fixes go out to everyone right away.
