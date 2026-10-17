# 07 — Engineering Standards

## Error handling

### Exception hierarchy (`core/errors.py`)

```
AppError                      (500, base)
├── NotFoundError             (404)
├── PermissionDeniedError     (403)
├── AuthenticationError       (401)
├── ValidationError           (422)  domain validation beyond Pydantic
├── ConflictError             (409)
│   └── ScheduleConflictError        overlap / double-booking
├── RuleViolationError        (422)  carries list[Violation]
└── ExternalServiceError      (502)  SMTP, integrations
```

- Services raise domain errors; **routers never build error responses themselves**.
- Global handlers turn them into **RFC 9457 Problem Details**:
  ```json
  {
    "type": "https://punchedn.app/errors/rule-violation",
    "title": "Schedule rule violated",
    "status": 422,
    "detail": "Assignment breaks 1 hard rule.",
    "code": "rule_violation",
    "request_id": "01J…",
    "violations": [{"rule": "max_weekly_hours", "severity": "hard", "message": "…"}]
  }
  ```
- Unhandled exceptions: logged with the stack trace and request ID; the client gets a generic 500 with the `request_id` and **no internal details**.
- DB integrity errors (e.g. the exclusion constraint) are caught in the repository and re-raised as domain errors.
- The frontend shows `title`/`detail`, maps `violations` onto the relevant fields or grid cells, and shows the `request_id` on unexpected errors so it can be included in support requests.
- Background jobs: retry with backoff for temporary errors; permanent failures are logged and stored as failed jobs.

## Logging

- **structlog**, JSON in production, readable console output in dev.
- Every log line includes: `timestamp`, `level`, `logger`, `event`, `request_id`, `user_id` (if known), `install_id`, `version`.
- Middleware assigns or passes through `X-Request-ID` and returns it on the response. Jobs carry the ID of the request that queued them.
- One **access log** line per request: method, route template, status, duration.
- **Never log:** passwords, tokens, pay rates, health data, full request bodies. A log processor masks known sensitive keys.
- Levels: `DEBUG` dev only; `INFO` business events (schedule published); `WARNING` handled problems; `ERROR` failures needing attention.
- The **audit log** is separate from application logs: a DB table, append-only, shown to admins in the UI.

## Testing

| Layer | Tooling | Scope |
|---|---|---|
| Unit | pytest | Services with fake repositories; rules engine; utilities |
| Integration | pytest + **testcontainers Postgres** | Repositories, migrations, constraints, API endpoints through `httpx.AsyncClient` |
| Property | **Hypothesis** | Rules engine; `timecalc` (DST, overnight, boundaries); later, "every solver output passes every hard rule" |
| Rule presets | pytest table tests | Each jurisdiction preset has a set of example cases (e.g. a 15-year-old in a school week) |
| Accessibility | **axe** in Playwright | No serious/critical violations on key pages; keyboard-only flow for the schedule grid |
| i18n | Script | No hard-coded UI text; every key exists in every shipped language |
| Frontend unit | **Vitest + RTL + MSW** | Components, hooks, forms |
| E2E | **Playwright** | Critical flows against the built Compose stack |
| Migration | pytest | Upgrade from an empty DB and from the previous release's schema; downgrade where supported |
| Upgrade (CI) | Shell + Compose | Install N-1 → load test data → update to N → smoke test |

Rules:
- **Coverage gate:** 80% backend overall, **95% for `rules/` and `core/`**. Frontend 70%.
- Every bug fix comes with a test that would have caught it.
- Test data comes from factories (polyfactory). No shared fixture database.
- Each test runs in a transaction that's rolled back afterward (fast, isolated).
- E2E critical flows (grow as phases land): login → create shift → assign → publish → employee sees it.

## CI/CD (GitHub Actions)

```
pull request:
  backend:  ruff check · ruff format --check · pyright · pytest (unit+integration) · coverage gate
  frontend: eslint · prettier --check · tsc · vitest · build
  api:      regenerate OpenAPI client → fail if it differs from what's committed
  security: gitleaks · CodeQL · pip-audit / pnpm audit
  image:    docker build (x86_64) · Trivy (fail on HIGH/CRITICAL with a fix available)
  e2e:      compose up · Playwright

main:
  all of the above + release-please PR

tag v*:
  buildx x86_64 + ARM64 → push GHCR (version tags) · SBOM · Trivy · cosign sign
  upgrade test (N-1 → N) · GitHub release with changelog + install bundle
```

- Branch protection on `main`: CI must pass; linear history; squash merges.
- Renovate: weekly, grouped; auto-merge patch updates for dev dependencies once CI passes.

## Git workflow

- Trunk-based: short-lived branches (`feat/…`, `fix/…`), squash-merged.
- **Conventional Commits** (`feat:`, `fix:`, `perf:`, `refactor:`, `test:`, `docs:`, `build:`, `ci:`, `chore:`, `revert:`, `style:`), checked by a `commit-msg` hook and a PR-title CI check. release-please builds versions and changelogs from these. Full rules and examples: [CONTRIBUTING.md](../CONTRIBUTING.md).
- Semantic versioning. `0.x` until the first paying customer; `1.0.0` at the commercial launch.
- Even solo, open PRs for the CI record, and review your own diff before merging.

## Code conventions

**Python**
- Type hints everywhere; pyright strict for `core/` and `rules/`.
- Async throughout the web layer; the solver runs synchronously inside a worker job.
- No business logic in routers or models.
- Times: always `datetime` with a time zone; never naive datetimes. **All hour/day/week calculations go through `core/timecalc.py`**; never subtract datetimes for hours elsewhere.
- Restricted fields (pay, date of birth, health data, pairing-request reasons) need explicit permission checks in the service and are masked in logs.
- User-facing text (violations, emails, PDFs) uses translation keys, never literal strings.
- Money: `Decimal`, stored as `numeric`.

**TypeScript**
- `strict: true`; no `any` without a comment.
- Server data only through TanStack Query hooks generated from the API client.
- Theme colors only from CSS variables (that's how branding works).
- No hard-coded UI text: everything goes through the translation layer; dates and numbers through `Intl`.
- Interactive components must work with a keyboard and have accessible names.

**API**
- Versioned prefix `/api/v1`.
- Plural resource nouns, cursor pagination, filtering through query params.
- `PATCH` for partial updates; `If-Match`/version field on schedules for optimistic locking.

## How we work

IDs, labels, issue format and terms are defined in [11 — Conventions](11-conventions.md).

### Tracking

| What | Where |
|---|---|
| Milestones | One GitHub milestone per roadmap phase (P0…P7). The description is that phase's **exit criteria** from [04](04-roadmap.md) |
| Tasks | One issue per task, sized to **one reviewable PR**. If an issue needs more than one PR or touches unrelated areas, split it. Acceptance criteria live in the issue (reuse [03](03-features.md)) |
| Labels | `area:*` (backend, frontend, ops, ci, auth, rules, docs) · `type:*` (feat, chore, spike) · `priority:must/should/could` · `data-model` (settle early) |
| Board | GitHub Projects: **Backlog** (sorted) → **Next** (max 5) → **Doing** (max 2) → **Done** |
| Decisions | When an issue changes a decision, update [09](09-decisions.md) in the same PR |

### Building features

- **Vertical slices, not layers.** A feature PR includes migration, model, service, API, generated client, screen, tests and audit entry together, so every merge leaves something that works and can be demoed.
- **Spikes** (`type:spike`) answer one question on a throwaway branch. The output is a short write-up in the issue (and a decision in 09 if it settles one), not merged code.
- Write each milestone's **end-to-end Playwright test early**, from its exit criteria. It is the milestone's definition of done.

### Prioritizing within a milestone

1. **Must:** exit criteria and `data-model` items. Do `data-model` items first; changing them later means migrations.
2. **Should:** what makes a real demo convincing.
3. **Could:** everything else. Draw a cut line; items below it move to a later milestone.

As a rule of thumb, prefer the work most likely to force a redesign if it's wrong: the riskiest unknown, or what a real user touches first.

### Review cadence

- **Weekly:** update the progress log, refill **Next** from the top of the backlog, check that the exit criteria are still realistic.
- **At each milestone boundary:** re-rank the next milestone using pilot feedback. After the pilot, its top pain points outrank the roadmap order.

## Documentation

- `docs/` (these files) is kept up to date in PRs.
- New major decisions are added to [09 — Decision Log](09-decisions.md).
- Runbooks live in `docs/runbooks/`.
- The OpenAPI spec is the API reference.
