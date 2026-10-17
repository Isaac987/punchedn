# 05 — Architecture

## System overview

```
                 Internet
                    │
     ┌──────────────┴───────────────┐
     │  Cloudflare Tunnel (on-prem) │  or public IP (cloud)
     └──────────────┬───────────────┘
                    │ HTTPS
┌───────────────────▼─────────────────────────────────────────┐
│  Host (customer hardware or customer-owned cloud server)    │
│                                                             │
│  ┌─────────┐   ┌──────────────────────┐   ┌──────────────┐  │
│  │  caddy  │──►│ app (FastAPI + SPA)  │──►│   postgres   │  │
│  └─────────┘   └──────────────────────┘   │  (data +     │  │
│                ┌──────────────────────┐   │   job queue) │  │
│                │ worker (Procrastinate│──►│              │  │
│                │  jobs, PDFs, solver) │   └──────────────┘  │
│                └──────────────────────┘                     │
│  volumes: pgdata, uploads, backups      tailscale (ssh)     │
└─────────────────────────────────────────────────────────────┘
        ▲                                   │ opt-in heartbeat
  time clock devices (P8)                   ▼
                                    maintainer monitoring
```

- **app** and **worker** run the same image with different commands.
- The **SPA** is built into the image and served by FastAPI under `/`. The API lives under `/api/v1`.
- **No outside services are required at runtime** except SMTP. Everything else (heartbeat, GlitchTip, Cloudflare) is optional.

## Repository layout (monorepo)

```
punchedn/
├── backend/
│   ├── pyproject.toml / uv.lock
│   ├── alembic/                    # migrations
│   ├── src/punchedn/
│   │   ├── main.py                 # app factory
│   │   ├── worker.py               # Procrastinate app
│   │   ├── cli.py                  # management commands (create-admin, etc.)
│   │   ├── core/
│   │   │   ├── config.py           # pydantic-settings
│   │   │   ├── logging.py          # structlog setup
│   │   │   ├── errors.py           # domain exceptions + handlers
│   │   │   ├── db.py               # engine, session, Base
│   │   │   ├── middleware.py       # request ID, access log
│   │   │   ├── security.py         # hashing, tokens
│   │   │   ├── permissions.py      # permission registry + dependency
│   │   │   ├── storage.py          # Storage interface (local / S3)
│   │   │   ├── timecalc.py         # the one place hours/days/weeks are computed
│   │   │   ├── events.py           # LISTEN/NOTIFY → SSE live updates
│   │   │   ├── i18n.py             # translations for emails/PDFs
│   │   │   └── audit.py
│   │   ├── rules/                  # rules engine (shared with solver)
│   │   ├── solver/                 # P6: CP-SAT model builder
│   │   └── features/
│   │       └── <feature>/
│   │           ├── router.py       # HTTP layer only
│   │           ├── schemas.py      # Pydantic request/response models
│   │           ├── service.py      # business logic
│   │           ├── repository.py   # DB access
│   │           ├── models.py       # SQLAlchemy models
│   │           └── tasks.py        # background jobs (optional)
│   └── tests/
│       ├── unit/  integration/  property/
├── frontend/
│   ├── src/
│   │   ├── api/                    # generated client
│   │   ├── features/<feature>/     # mirrors backend features
│   │   ├── components/ui/          # shadcn components
│   │   ├── locales/                # translation files (en, es, …)
│   │   └── theme/                  # CSS variable tokens
│   └── e2e/                        # Playwright
├── clock-agent/                    # P8
├── deploy/
│   ├── compose.yaml
│   ├── Caddyfile
│   ├── .env.example
│   ├── bin/punchedn                # admin command
│   └── ansible/
├── docs/                           # these documents
├── Dockerfile                      # multi-stage: frontend build → python runtime
└── .github/workflows/
```

## Backend layering

```
router  →  service  →  repository  →  database
  │          │
schemas    rules engine / domain exceptions
```

| Layer | Responsibility | Must not |
|---|---|---|
| **router** | Parse requests, check permissions, call the service, map results to schemas | Contain business logic or touch the DB |
| **service** | Business rules, transactions, audit logging, starting background jobs | Know about HTTP |
| **repository** | Queries; returns models | Make business decisions |
| **models / schemas** | DB shape / API shape (kept separate) | Leak DB models straight into responses |

Dependency injection uses FastAPI `Depends`: `get_session → Repository → Service`. Tests swap in fakes at the service boundary, or use a real DB for integration tests.

## Core data model (initial sketch)

```
# Identity & access
users (email or phone, locale) ─┬─ user_roles ── roles ── role_permissions
                                ├─ user_groups ── group_roles
                                ├─ user_totp (secret encrypted, recovery code hashes)
                                ├─ auth_sessions (refresh token hash, device, revoked_at)
                                └─ identities (provider, subject)   # future OIDC SSO
# Org & rules
locations (tz, workweek_start, hours) ── departments
positions ── position_skills ── skills (expires)
rule_sets ── rules (code, params JSONB, effective_from/to, conditions JSONB)
jurisdiction_presets (read-only rule_set templates)
school_calendars ── calendar_periods (in_session | break | exams, date range)
employee_types (compensation: paid|volunteer, rule_set, calendar)
# People
employees (date_of_birth*, hire_date, desired_hours_min/max)
  ── employee_skills, employee_positions
  ── pay_rates (employee, position NULL=default, rate, effective_from)*
availability_patterns, availability_exceptions
pair_restrictions (a, b, source: manager|employee, status, confidential)
pair_requests (requester, other, reason*, hr_status)   ← HR-only
# Scheduling
staffing_requirements (location, position, weekday|date, window, min, max, skills)
composition_rules (scope, kind: requires_skill|requires_role|max_role, params)
schedule_periods (status, version, availability_deadline, publish_by)
schedule_versions (period, version_no, snapshot JSONB, published_at/by)  ← immutable
schedule_changes (period, version_no, diff, reason, notice_hours, changed_by)
shift_templates ── template_slots
shifts (location, position, starts_at, ends_at, headcount, required skills, notes)
shift_assignments (shift, employee, starts_at, ends_at)   ← EXCLUDE constraint
recurring_assignments (locked flag, effective_from/to)
shift_assignments.pinned (draft-only lock)
schedule_preferences (employee, kind, params JSONB, strength: strong|mild)
preference_satisfaction (employee, period, score)        ← fairness history
solver_runs (period, mode, settings, status, report JSONB, duration)
# Time off
leave_banks (kind: pto|sick|custom, policy JSONB)
leave_ledger (employee, bank, delta_hours, reason, ref)   ← append-only
time_off_requests, time_off_limits, blackout_dates
absences (sick calls) ── attachments*
# Marketplace & comms
swap_requests, open_shift_claims
notifications, notification_preferences, announcements, announcement_reads
# Time & attendance
punch_policies, break_rules (location)
time_punches, punch_corrections, timesheets, devices
# Platform
webhook_subscriptions, webhook_deliveries          (P8)
import_jobs (CSV imports: mapping, preview, errors)
audit_log (append-only)
settings (key/value, typed)

* = restricted fields: separate permission, never in list endpoints, masked in logs
```

Conventions:
- Primary keys are UUIDv7 (sort by time, safe to expose).
- All timestamps are `timestamptz` stored in UTC; each location has a time zone used for display and rules.
- Soft delete (`archived_at`) for anything that appears in history; balances and audit records are append-only ledgers.

## Rules engine

The bridge between manual scheduling (P2) and auto-scheduling (P6).

```python
class Rule(Protocol):
    code: str                     # "max_weekly_hours"
    severity: Severity            # HARD | SOFT

    def check(self, ctx: ScheduleContext, change: Assignment) -> list[Violation]:
        """P2: validate a proposed assignment against the current schedule."""

    def to_constraints(self, model: CpModel, vars: SolverVars, ctx: ScheduleContext) -> None:
        """P6: express the same rule as CP-SAT constraints / objective terms."""
```

- `ScheduleContext` is a **read-only snapshot** (employees with ages on the relevant dates, availability, approved time off, existing assignments, pair restrictions, staffing requirements, composition rules, the rules that apply, calendar state) loaded once per request or solver run.
- Rule settings come from data, not code. **Picking which rules apply** happens before rules run: for each employee and date, take the employee type's rule set → keep rules whose effective dates include the date → keep rules whose conditions match (age on that date, calendar period). Rules never look up dates or ages themselves.
- Rule kinds:
  - **Per-employee:** hour caps (daily/weekly/school-week), rest between shifts, time-of-day windows, availability, skills
  - **Per-shift composition:** required skill present, role requires role (trainee/trainer), max per role
  - **Per-time-window coverage:** staffing requirement min/max
  - **Pairwise:** do-not-pair (confidential ones are reported as "confidential constraint" except to HR)
- All hour totals go through `core/timecalc.py` (see [Time semantics](#time-semantics)).
- **Explanations:** each `Violation` carries the rule code, the people/shifts involved and a translatable message. In P6 the solver adds an assumption literal per rule group, so it can report the binding constraints behind each unfilled slot.
- **Every rule ships with tests for both methods.** A property test checks that any schedule the solver produces passes `check()` for every rule. That's how we know the two paths agree.
- Overriding a soft rule records `(rule_code, reason, user)` in the audit log.

## Auto-scheduler (P6)

Runs as a worker job: `generate_schedule(period_id, mode: full | fill_remaining)`.

**Inputs** (from `ScheduleContext`): staffing requirements / open slots, eligible employees (skills, positions, availability, approved time off), the rules that apply, **locked assignments** (fixed schedules + pins), **target hours**, **schedule preferences**, recent preference-satisfaction history, last period's schedule.

**Model (CP-SAT)**
- Boolean `x[e, s]` = employee *e* works slot *s*, created only for **eligible** pairs (skills, availability, time off) to keep the model small.
- Locked assignments: `x[e, s] == 1`, after checking them against hard rules and time off (conflicts are skipped and reported). **The solver never breaks a lock to cover a gap**; the gap goes into `unfilled[s]` instead.
- Hard rules: each `Rule.to_constraints()`, including no overlaps, hour caps, rest, composition and do-not-pair.
- Coverage: `sum(x[·, s]) + unfilled[s] >= min[s]`, with `unfilled[s]` heavily penalized, so the solver always returns a schedule plus a list of unfilled slots, never just "impossible."

**Objective** (minimize; weights per tier so a higher tier always beats any lower one):

| Tier | Term |
|---|---|
| 1 Coverage | Σ unfilled slots |
| 2 Overtime | Σ hours over the overtime limit |
| 3 Balance | Σ \|hours[e] − target[e]\| over **flexible** employees, plus a small max-deviation term so no one is an outlier. Fixed-schedule employees are left out of this term |
| 4 Preferences | Σ preference violations × strength × fairness factor (higher for employees whose preferences went unmet recently) |
| 5 Stability | Σ changes vs. last period / recurring pattern; clopens |

- **Target hours (balance toward desired hours, 4-week carry-over):**
  ```
  carry[e]  = Σ over the previous 4 weeks (desired[e] − actual[e])     # + if short, − if over
  target[e] = clamp(desired[e] × weeks_in_period + carry[e],
                    0, max hours allowed by e's rules this period)
  ```
  `actual` comes from published schedules (from timesheets once P5 exists). If an employee hasn't set desired hours, the fallback is a fair share:
  ```
  fair_share[e] = (pool demand − locked hours in pool − Σ targets of members with desired hours)
                  / members without desired hours        # weighted by each one's available hours
  ```
  clamped by the employee's rules. They're prompted to set desired hours, and the run report flags everyone who got the fallback.
- **Preference types (first release):** `preferred_times` (days + time windows), `preferred_positions`, `avoid_closing`, `max_days_per_week`. Each is strong or mild and adds a penalty in tier 4 when it's not met.
- **Fixed-schedule employees** (all of their shifts in the period are locked) have no target and no balance penalty. Assigning them an extra shift costs a penalty in the overtime/stability tier, so it only happens when coverage can't be met otherwise.
- Tier 3 vs. 4 weighting is the business's "fairness vs. preferences" slider; tiers 1–2 are fixed.
- Hours are measured in whole minutes, because CP-SAT only works with integers.

**Output:** a draft (never published automatically) + a run report: unfilled slots with their binding causes, skipped locks, per-employee hours vs. target, preference satisfaction, solver status (optimal / feasible within the time limit).

**Guarantees, tested:** every output passes every hard rule's `check()`; locks are kept (unless reported); results are the same for the same inputs and seed.

## Time semantics

Per [DQ-2](10-design-questions.md#dq-2--time-zones-overnight-shifts-and-daylight-saving) (proposed):

| Question | Answer |
|---|---|
| Storage | `timestamptz` in UTC; location has an IANA time zone |
| Which day a shift belongs to (display, daily limits) | The local date the shift **starts** on |
| Hours counted toward a week or pay period | **Actual elapsed hours**, split at workweek/pay-period boundaries (local time) |
| DST | Elapsed time is what counts: fall-back night 10pm–6am = 9 h, spring-forward = 7 h |
| Age on a date | Computed from `date_of_birth` at the shift's local start date |

`core/timecalc.py` is the only place these are computed, and it has Hypothesis tests around DST changes and shifts that cross a boundary.

## Publishing & versions

- `schedule_periods.version` goes up with every write (used for version checks).
- **Publish** writes an immutable `schedule_versions` row (a full snapshot of the assignments) and notifies everyone on the schedule.
- **Edits after publishing** must include a `reason`. The system records the diff and `notice_hours` (time between the change and the affected shift's start) in `schedule_changes`, and notifies only the affected employees.
- Employee views always show the latest published version, never drafts.

## Concurrency & live updates

- **Version checks:** writes send `If-Match: <version>`; a mismatch returns `409 ConflictError`; the UI reloads and highlights what changed.
- **Live updates:** after a write is committed, the service runs `NOTIFY schedule_period_<id>`. An SSE endpoint (`/api/v1/schedule-periods/{id}/events`) relays these to open grids. No new services; Caddy proxies SSE as is.
- The SSE stream only notifies clients that something changed. Clients refetch through the normal API, so permission checks stay in one place.

## Resilience

- The PWA service worker caches the employee's **published** shifts (only theirs) for viewing offline; it shows a "last updated" timestamp.
- Publishing emails each employee their shifts; the iCal feed updates. The schedule never exists only on the box.
- Targets: **RPO ≤ 24 h, RTO ≤ 1 business day** (see [06](06-operations.md#backups)).

## Internationalization & accessibility

- Frontend: all text in `locales/*.json` from P0 (e.g. react-i18next or Lingui); dates and numbers formatted with `Intl` in the location's time zone and the user's language.
- Backend: emails, PDFs and violation messages are translated (`core/i18n.py`); API error `code`s stay stable and untranslated.
- WCAG 2.2 AA; the schedule grid has a keyboard-only assignment mode and announces changes to screen readers; axe checks in Playwright.

## Permissions

- Permission names are registered in code (`core/permissions.py`) so they can't be misspelled and can be listed in the admin UI.
- Endpoints declare what they need: `Depends(require("schedule.publish", scope="location"))`.
- Scopes: global, or limited to specific locations.
- Field-level checks (pay rate, date of birth, doctor's notes, pairing request reasons) happen in the service layer, not only the UI.
- **Confidential pairing data:** `pair_requests` is visible only to `hr.pair_requests.manage`. Managers see an approved restriction only as "constraint (confidential)," and neither employee ever sees it, including in rule-violation messages.
- Employees without email sign in with a phone number + one-time code or a kiosk PIN; terminating an employee revokes all their sessions and tokens immediately.

## Configuration

All configuration comes from environment variables (12-factor), validated at startup. A bad config means the app **refuses to start** with a clear message.

Examples: `DATABASE_URL`, `SECRET_KEY`, `PUBLIC_URL`, `SMTP_*`, `STORAGE_BACKEND`, `HEARTBEAT_URL` (empty = off), `SENTRY_DSN` (empty = off), `WORKER_CONCURRENCY`, `SOLVER_TIME_LIMIT_SECONDS`.

## Security baseline

- HTTPS only; HSTS; secure, HttpOnly, SameSite cookies for refresh tokens
- CSRF protection for cookie-authenticated requests; CORS locked to `PUBLIC_URL`
- Rate limiting on auth endpoints
- Authentication is built in; no bundled IdP ([#028](09-decisions.md#028--built-in-authentication-no-bundled-identity-provider)). TOTP 2FA is enforced for users holding sensitive permissions; granting such a permission to a user without 2FA forces enrollment at their next login
- Secrets generated at install time, stored in `.env` with `0600` permissions
- Uploads: size/type allow-list, served only through a permission-checked endpoint, encrypted at rest
- Dependency and image scanning in CI; host hardening via Ansible (see [06](06-operations.md))
- Images signed with **cosign**; `punchedn update` refuses images whose signature doesn't check out
- Webhooks (P8) are signed with HMAC and include a timestamp so they can't be replayed; API tokens have limited permissions and can be revoked
