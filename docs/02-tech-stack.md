# 02 — Tech Stack

## What drives these choices

1. **OR-Tools.** Its best API is in Python, so the backend is Python. The solver, the app and the tests share one language and one set of models.
2. **Self-hosted on varied hardware, by one maintainer.** Every extra service is one more thing to break on a box you don't control. Prefer fewer parts.
3. **Same bundle everywhere.** On-prem and cloud run the identical Docker Compose bundle, configured only through environment variables.
4. **Production grade.** Typed code, tests, structured logs, CI/CD and safe upgrades.

## Stack

### Backend

| Concern | Choice | Notes |
|---|---|---|
| Language | **Python 3.15** | Latest stable; pinned in `.python-version`. OR-Tools has no 3.15 wheels yet; re-check before P6 (see [Versions](#versions)) |
| Web framework | **FastAPI** | Async, typed, generates its OpenAPI spec automatically |
| Validation / settings | **Pydantic 2**, pydantic-settings | All config comes from environment variables |
| ORM / migrations | **SQLAlchemy 2.1** (async) + **Alembic** | |
| Background jobs | **Procrastinate** | Job queue that runs inside Postgres, so no Redis needed. Used for notifications, PDFs, solver runs and scheduled jobs |
| Auth | Argon2 password hashing (argon2-cffi), short-lived JWT access tokens + rotating refresh tokens, TOTP 2FA (pyotp) | Built in, no bundled IdP ([#028](09-decisions.md#028--built-in-authentication-no-bundled-identity-provider)). SSO later as an OIDC client (Authlib) |
| Solver (Phase 6) | **Google OR-Tools CP-SAT** | Runs inside the worker with a time limit |
| PDF generation | WeasyPrint (HTML → PDF) | For printed schedules, volunteer certificates |
| Live updates | Postgres `LISTEN/NOTIFY` → **Server-Sent Events** | Live schedule grid with no new services ([#019](09-decisions.md#019--live-schedule-updates-via-postgres-listennotify--sse)) |
| Backend translations | Babel / gettext | Emails, PDFs, rule-violation messages |
| Time handling | stdlib `zoneinfo` + one `core/timecalc.py` module | DST-safe hour calculations ([DQ-2](10-design-questions.md#dq-2--time-zones-overnight-shifts-and-daylight-saving)) |
| Package / env manager | **uv** | Lockfile committed |
| Lint / format / types | **ruff**, **pyright** (strict on `core/`) | |

### Database

**PostgreSQL 18** (the current major version).

- Very relational data: shifts ↔ positions ↔ skills ↔ employees ↔ permissions.
- **Exclusion constraints** block double-booking at the database level (needs the `btree_gist` extension):
  ```sql
  EXCLUDE USING gist (employee_id WITH =, tstzrange(starts_at, ends_at) WITH &&)
  ```
- Also stores the job queue (Procrastinate), so there's one service to back up.

### Frontend

| Concern | Choice | Notes |
|---|---|---|
| Framework | **React + TypeScript + Vite** | Single-page app, served by the API container |
| UI kit | **shadcn/ui + Tailwind CSS** | Themed with CSS variables, so company colors are a runtime setting |
| Data fetching | **TanStack Query** | |
| Routing | **TanStack Router** (or React Router) | |
| Forms | React Hook Form + Zod | |
| Translations | react-i18next (or Lingui) | Text in `locales/*.json` from P0 |
| Accessibility | eslint-plugin-jsx-a11y, axe (Playwright) | WCAG 2.2 AA target |
| Offline | Service worker (e.g. Workbox via vite-plugin-pwa) | Caches the employee's published schedule |
| API client | **Generated from OpenAPI** (orval or openapi-typescript) | Frontend and backend types can't drift apart |
| Schedule UI | Custom grid built on shadcn (FullCalendar as a fallback; check its license) | The schedule grid is the product's core screen |
| Mobile | **PWA** (installable, web push) | Expo/React Native only when needed (iPhone NFC, app-store presence) |
| Package manager | **pnpm** | |
| Lint / format | ESLint + Prettier, `tsc --noEmit` | |

### Infrastructure & ops

| Concern | Choice |
|---|---|
| Packaging | Docker images for **x86_64 and ARM64** (`docker buildx`), published to GHCR |
| Orchestration | **Docker Compose**: `caddy`, `app`, `worker`, `postgres` |
| Reverse proxy / TLS | **Caddy** (automatic HTTPS) |
| Remote access | **Tailscale** on every host |
| Internet exposure (on-prem) | **Cloudflare Tunnel** by default; port forwarding + Caddy as an option |
| File storage | Local Docker volume behind a `Storage` interface (S3 option later) |
| Email | Customer-provided SMTP or a transactional email account |
| Provisioning | Ansible playbook + cloud-init for cloud servers |
| Error tracking | Sentry SDK pointing at self-hosted **GlitchTip** (opt-in) |
| Logs | structlog JSON → Docker log driver with rotation |
| Metrics / tracing | OpenTelemetry instrumentation, exporter off by default |

### Tooling & CI

| Concern | Choice |
|---|---|
| CI/CD | **GitHub Actions** |
| Dependency updates | **Renovate** (grouped, scheduled weekly) |
| Image scanning | **Trivy** |
| Image signing | **cosign** (Sigstore); checked by `punchedn update` |
| Code scanning | **CodeQL** |
| Releases | **release-please** (Conventional Commits → semver tags + changelog) |
| Local hooks | **pre-commit** (ruff, prettier, eslint, gitleaks) |
| Backend tests | pytest, pytest-asyncio, **testcontainers** (real Postgres), polyfactory, **Hypothesis** |
| Frontend tests | **Vitest**, React Testing Library, **MSW** |
| End-to-end tests | **Playwright** |
| Load testing (later) | Locust or k6 |

## Versions

**Policy ([#029](09-decisions.md#029--use-the-latest-stable-versions)):** use the latest **stable** release of every language, runtime, framework and tool. Never use pre-releases (alpha, beta, RC). For Node.js, use the newest **LTS** line. If a required dependency doesn't support the newest version yet, use the newest version that all required dependencies support, and move up as soon as they do. Renovate keeps versions current. Once code exists, the lockfiles and `.python-version` are the source of truth, and this table is updated in the same PR as any major upgrade.

Checked 2026-10-16:

| Component | Version | Notes |
|---|---|---|
| Python | 3.15 | Docker base `python:3.15-slim-trixie` |
| PostgreSQL | 18 | Docker image `postgres:18-trixie` |
| Node.js | 26 LTS | Build stage only; not shipped in the runtime image |
| pnpm | 12 | |
| FastAPI | 0.143 | |
| Pydantic | 2.14 | |
| SQLAlchemy | 2.1 | |
| Alembic | 1.20 | |
| Procrastinate | 3.10 | |
| OR-Tools | 9.15 | ⚠ Wheels only up to Python 3.14 so far. Needed in P6; check for 3.15 wheels before P6 starts |
| React | 19 | |
| TypeScript | 7.0 | |
| Vite | 8 | |
| Tailwind CSS | 4 | |
| TanStack Query / Router | 5 / 1 | |
| Host OS | Ubuntu 26.04 LTS, Debian 13 | See [06 — Support matrix](06-operations.md#support-matrix) |

## Considered and rejected

| Option | Why not |
|---|---|
| **Frappe** | Productive for CRUD, but opinionated. The custom schedule UI and solver integration would fight the framework |
| **Next.js + Prisma** | Splits the codebase into two languages; OR-Tools would end up in a separate Python service anyway |
| **Django** | A good alternative: built-in admin and auth. FastAPI fits a separate React frontend and typed async APIs better. Revisit if admin screens become a burden |
| **Flask** | Less built in than FastAPI, with no gain |
| **MongoDB** | Data is strongly relational; overlap protection and reporting are much easier in SQL |
| **Celery + Redis** | Extra service to run on every box. Procrastinate covers the workload |
| **Keycloak (bundled)** | A JVM service on every box, its own upgrades and backups, and custom Java extensions for phone/PIN login. Customers' own IdPs are supported later through OIDC ([#028](09-decisions.md#028--built-in-authentication-no-bundled-identity-provider)) |
| **Kubernetes** | Too much operational load for single-box, single-tenant installs |
| **Multi-tenant SaaS** | Conflicts with the data-ownership pitch, and it's harder to secure solo |
