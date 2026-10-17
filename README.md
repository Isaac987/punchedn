<p align="center">
  <img src="resources/banner.png" alt="PunchedN banner" width="100%" />
</p>

<h3 align="center">Shift scheduling for teams that change every week</h3>

<p align="center">
  <img alt="Status: planning" src="https://img.shields.io/badge/status-planning-lightgrey">
  <a href="https://github.com/Isaac987/punchedn/pulls"><img alt="Pull requests" src="https://img.shields.io/github/issues-pr/isaac987/punchedn"></a>
  <a href="https://github.com/Isaac987/punchedn/issues"><img alt="Issues" src="https://img.shields.io/github/issues/isaac987/punchedn"></a>
  <a href="https://discord.gg/2bgWhtCHbb"><img alt="Discord" src="https://img.shields.io/discord/1526075110543462410"></a>
</p>

**PunchedN** is an employee scheduling and time-tracking system for small businesses that rely on students, volunteers and part-time staff: cafés, campus shops, nonprofits, recreation centers and small retail. These teams' shifts change often and unpredictably, and many of them still schedule on paper, in spreadsheets or in group chats.

PunchedN lets managers build schedules quickly while the system catches conflicts and rule breaks. Employees see their schedule, request time off, call in sick and swap shifts from their phones. Each business runs its own install, on its own hardware or in a cloud account it owns, so its data stays in its hands.

> [!NOTE]
> **PunchedN is in the planning stage.** The design, roadmap and decisions are documented in [`docs/`](docs/README.md). Application code starts with [Phase 0](docs/08-phase-0-plan.md). Nothing here is ready to install yet.

## Table of contents

- [Why PunchedN](#why-punchedn)
- [Features](#features)
- [How it works](#how-it-works)
- [Tech stack](#tech-stack)
- [Deployment](#deployment)
- [Roadmap](#roadmap)
- [Development](#development)
- [Documentation](#documentation)
- [Use of AI](#use-of-ai)
- [Contributing](#contributing)
- [Security](#security)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## Why PunchedN

Tools like When I Work and Deel are built for larger companies. PunchedN is built for small teams:

- **Your data stays with you.** Each install runs on hardware or a cloud account the business owns. There is no shared multi-customer database.
- **Built-in hour rules for students and minors.** Hour limits follow age and the school calendar (school week vs. breaks), using jurisdiction presets that admins can clone and adjust.
- **Volunteer support.** Volunteers are tracked as unpaid staff, with service-hour reports and printable certificates.
- **Conflicts are caught as you schedule.** Double-booking is blocked at the database level. Hour caps, missing skills, availability and do-not-pair rules show live warnings.
- **Explainable auto-scheduling (planned).** When the solver can't fill a shift, it says why.
- **Perpetual license.** If the maintenance plan lapses, the software keeps working. There is no kill switch.
- **Accessible and translated.** Targets WCAG 2.2 AA, including a keyboard-only schedule grid. English first, then Spanish.

## Features

Features are grouped into modules and delivered in phases. Full acceptance criteria are in [03 — Feature Breakdown](docs/03-features.md).

| Role | Highlights |
|---|---|
| **Admin** | Branding (logo and colors), fine-grained roles and permissions, user groups, global policy toggles, audit log, time clock devices |
| **Manager** | Staffing requirements, shift templates, rule-checked manual scheduling, copy last period, versioned publishing, time-off and swap approvals, printable schedules |
| **HR** | Hire and remove employees, pay rates per position, CSV import, confidential handling of do-not-pair requests, sick-leave records |
| **Employee** | Mobile schedule (works offline), availability and preferences, time-off requests, sick call-outs, shift swaps and open shifts, iCal feed |

Admin, Manager, HR and Employee are **presets**, not hard-coded roles. Permissions can be set up so that managers schedule but can't see pay, and HR changes pay but can't publish schedules.

**Planned for later phases:** web and kiosk clock-in, timesheets and break rules, payroll CSV export, fairness and labor-law reports, automatic schedule generation with Google OR-Tools, payroll/accounting integrations, and RFID/NFC time clocks.

**Deliberately not building:** built-in chat, payroll calculation, Windows hosts, and face recognition. The reasons are in [10 — Design Questions](docs/10-design-questions.md#deliberately-not-building).

## How it works

```
caddy (HTTPS) ──► app (FastAPI + React SPA) ──► postgres (data + job queue)
                  worker (jobs, PDFs, solver) ──┘
```

- **One Docker Compose bundle** runs everywhere, configured only through environment variables.
- **PostgreSQL is the only stateful service.** It also holds the background job queue, so there is one thing to back up.
- **A shared rules engine.** Each rule (hour caps, rest between shifts, required skills, do-not-pair, and so on) can both validate a manual edit and become a constraint for the auto-scheduler, so both paths enforce the same rules.
- **The schedule is never stored only on the box.** Publishing emails each employee their shifts and updates their iCal feed, and the PWA caches each employee's shifts for offline viewing.

Details are in [05 — Architecture](docs/05-architecture.md).

## Tech stack

| Layer | Technologies |
|---|---|
| Backend | Python 3.15, FastAPI, Pydantic 2, SQLAlchemy 2.1 + Alembic, Procrastinate |
| Database | PostgreSQL 18 |
| Frontend | React 19, TypeScript 7, Vite 8, Tailwind CSS + shadcn/ui, TanStack Query, installable PWA |
| Scheduling engine | Google OR-Tools CP-SAT (Phase 6) |
| Infrastructure | Docker Compose, Caddy, Tailscale, Cloudflare Tunnel, images for x86_64 and ARM64 |
| Tooling | uv, pnpm, ruff, pyright, pytest + Hypothesis, Vitest, Playwright, GitHub Actions, release-please, cosign |

The project uses the latest stable version of everything; the current versions are listed in [02 — Versions](docs/02-tech-stack.md#versions). The reasons for each choice, and the options that were rejected (including MongoDB, Celery and Keycloak), are in [02 — Tech Stack](docs/02-tech-stack.md) and the [Decision Log](docs/09-decisions.md).

## Deployment

PunchedN is **single-tenant**: one install per business. The same bundle supports two hosting options:

| | On-prem | Cloud |
|---|---|---|
| Runs on | The customer's own hardware | A server in the customer's own cloud account |
| Infrastructure paid by | Customer | Customer, billed directly by the provider |
| Internet access | Cloudflare Tunnel (default) or port forwarding | Public IP with automatic TLS |

The maintainer installs, configures and maintains every deployment. The `punchedn` admin command handles installs (with a preflight check), signed updates with automatic rollback, encrypted backups and restores, and support bundles.

**Minimum hardware:** 2 cores, 4 GB RAM, 40 GB SSD, running Ubuntu 26.04 LTS or Debian 13. See the [support matrix](docs/06-operations.md#support-matrix) and [06 — Operations](docs/06-operations.md).

## Roadmap

Phases 0–3 are the MVP: enough for a real business to stop scheduling by hand.

| Phase | Focus | Status |
|---|---|---|
| P0 | Foundation: skeleton, CI/CD, installer, update/backup/restore | Next |
| P1 | Core data: permissions, locations, positions, rule sets, employees, CSV import | Planned |
| P2 | Manual scheduling ⭐: rules engine, staffing requirements, publishing, mobile schedule | Planned |
| P3 | Time off and notifications → **first pilot business** | Planned |
| P4 | Shift marketplace: swaps, give-aways, open shifts | Planned |
| P5 | Time and attendance, basic reports, payroll CSV | Planned |
| P6 | Auto-scheduling with OR-Tools | Planned |
| P7 | Commercial release: licensing, EULA, documentation site | Planned |
| P8 | Expansion based on what customers ask for | Planned |

Each phase has exit criteria in [04 — Roadmap](docs/04-roadmap.md) and is tracked as a [GitHub milestone](https://github.com/Isaac987/punchedn/milestones).

## Development

There is no application code yet. Phase 0 sets up the monorepo (`backend/`, `frontend/`, `deploy/`), a task runner for `dev`, `test`, `lint` and `build`, and a local Compose environment. This section will be filled in with real setup steps once those exist.

Until then, the standards that new code will follow are already written down:

- [CONTRIBUTING.md](CONTRIBUTING.md): clone setup, branch names, commit messages (Conventional Commits), pull requests and code style
- [07 — Engineering Standards](docs/07-engineering-standards.md): error handling, logging, testing and coverage gates, CI/CD and git workflow
- [11 — Conventions](docs/11-conventions.md): issue format, labels, branch names and Conventional Commits

## Documentation

The planning docs in [`docs/`](docs/README.md) are numbered in reading order and also work as an [Obsidian](https://obsidian.md/) vault.

| # | Document | What it covers |
|---|---|---|
| 01 | [Product Overview](docs/01-overview.md) | The problem, users, deployment and business model |
| 02 | [Tech Stack](docs/02-tech-stack.md) | Which technologies, and why |
| 03 | [Feature Breakdown](docs/03-features.md) | Every feature, with acceptance criteria |
| 04 | [Roadmap](docs/04-roadmap.md) | Phases and exit criteria |
| 05 | [Architecture](docs/05-architecture.md) | System design, data model, rules engine, auto-scheduler |
| 06 | [Operations](docs/06-operations.md) | Install, update, backup, monitoring, maintainer security |
| 07 | [Engineering Standards](docs/07-engineering-standards.md) | Errors, logging, testing, CI/CD |
| 08 | [Phase 0 Plan](docs/08-phase-0-plan.md) | Foundation task checklist |
| 09 | [Decision Log](docs/09-decisions.md) | Key decisions and the reasons for them |
| 10 | [Design Questions](docs/10-design-questions.md) | Hard problems and the approaches chosen for them |
| 11 | [Conventions](docs/11-conventions.md) | IDs, labels, issue format, glossary |

## Use of AI

PunchedN is built by one developer, with help from [Claude](https://www.anthropic.com/claude), Anthropic's AI model, used through [Claude Code](https://claude.com/claude-code). Claude helps with:

- **Documentation:** drafting and editing the planning docs and this README
- **Research:** comparing technologies and looking into labor-law topics such as minor hour limits, sick leave and predictive scheduling laws
- **Planning:** breaking the roadmap into phases, issues and acceptance criteria, and working through design questions

The maintainer makes all decisions and reviews everything before it is merged. Commits written with Claude's help carry a `Co-Authored-By` trailer. Research on legal topics is a starting point for further checking, not legal advice.

## Contributing

PunchedN is currently built and maintained by one person, and outside contributions aren't being accepted yet. Feedback is welcome:

- **Bugs and ideas:** open an [issue](https://github.com/Isaac987/punchedn/issues)
- **Questions and discussion:** join the [Discord](https://discord.gg/2bgWhtCHbb)

The development workflow and commit conventions are in [CONTRIBUTING.md](CONTRIBUTING.md).

If you're interested in running a pilot at your business, get in touch on Discord.

## Security

PunchedN will handle sensitive data such as pay rates and health information. If you find a security issue, **please don't open a public issue.** Report it privately through [GitHub's private vulnerability reporting](https://github.com/Isaac987/punchedn/security/advisories/new) instead.

## License

The license has not been decided yet. A proprietary EULA is expected; an open-core model is still being considered (see [01 — Product Overview](docs/01-overview.md#open-questions)). Until a license is published, all rights are reserved.

## Acknowledgments

- [Google OR-Tools](https://developers.google.com/optimization) for schedule optimization
- [FastAPI](https://fastapi.tiangolo.com/), [React](https://react.dev/), [PostgreSQL](https://www.postgresql.org/), [Procrastinate](https://procrastinate.readthedocs.io/) and [shadcn/ui](https://ui.shadcn.com/)
- [Claude](https://www.anthropic.com/claude) for help with documentation, research and planning
