# 09 — Decision Log

Short decision records. Add new ones at the bottom; don't rewrite old ones. If a decision is replaced, mark it **Superseded by #N**.

Format: **Context** → **Decision** → **Consequences**.

---

### 001 — Python + FastAPI backend
*2026-10-16 · Accepted*
- **Context:** Auto-scheduling will use Google OR-Tools, whose best API is in Python. Solo developer.
- **Decision:** Python backend with FastAPI.
- **Consequences:** one language for the API, worker and solver. Django's built-in admin is given up (admin screens will be built in React).

### 002 — PostgreSQL as the only stateful service
*2026-10-16 · Accepted*
- **Context:** relational domain; overlap protection; self-hosted installs need few moving parts.
- **Decision:** PostgreSQL for data **and** the job queue (Procrastinate). No Redis, no MongoDB.
- **Consequences:** one thing to back up and monitor. Revisit if the job volume grows a lot (unlikely for single-tenant installs).

### 003 — Single-tenant deployments
*2026-10-16 · Accepted*
- **Context:** the data-ownership pitch; the customer hosts.
- **Decision:** one installation per business; multiple locations are supported inside one install.
- **Consequences:** no tenant-isolation bugs; simpler security. Updates must be rolled out to each install, so update tooling is essential (see 006).

### 004 — Customer hosts: on-prem or a cloud account they own
*2026-10-16 · Accepted*
- **Context:** the maintainer wants to avoid paying hosting costs; some customers will want cloud hosting.
- **Decision:** two targets for the same bundle: customer hardware, or a cloud server in the **customer's own** cloud account, billed to them. The maintainer installs and maintains both.
- **Consequences:** no billing or payment risk for the maintainer, and data ownership is clear. Hardware varies, so a support matrix, a preflight check and images for both processor types are needed.

### 005 — Docker Compose, configured only through environment variables
*2026-10-16 · Accepted*
- **Context:** varied hosts; solo maintainer.
- **Decision:** Docker Compose bundle (caddy, app, worker, postgres); images for x86_64 and ARM64; all config from environment variables.
- **Consequences:** the same artifact runs everywhere. Kubernetes isn't needed.

### 006 — Ops tooling built in Phase 0, not at the end
*2026-10-16 · Accepted*
- **Context:** the first pilot runs on customer infrastructure; one person maintains every install.
- **Decision:** installer, update with automatic rollback, backup/restore and support bundle are Phase 0–3 work.
- **Consequences:** slower start on features, but the pilot is safe to operate.

### 007 — Shared rules engine for manual and automatic scheduling
*2026-10-16 · Accepted*
- **Context:** auto-scheduling is planned for later; manual scheduling needs the same rules.
- **Decision:** each rule has both `check()` (validation) and `to_constraints()` (CP-SAT). Rule settings come from data.
- **Consequences:** auto-scheduling plugs into what's already there instead of needing a rewrite; property tests keep the two paths in agreement.

### 008 — PWA before native mobile
*2026-10-16 · Accepted*
- **Context:** solo developer; employees need mobile access.
- **Decision:** an installable PWA with web push. Expo/React Native only when needed (iPhone NFC, app-store presence).
- **Consequences:** one frontend codebase. iPhone web push requires adding the app to the home screen.

### 009 — Don't calculate payroll
*2026-10-16 · Accepted*
- **Context:** pay stubs and accounting integrations were requested.
- **Decision:** export hours and pull pay stubs from payroll providers; never calculate taxes or net pay.
- **Consequences:** avoids a huge legal and accuracy burden. Pay stub features depend on what each provider's API offers.

### 010 — Biometrics deferred pending legal review
*2026-10-16 · Accepted*
- **Context:** BIPA and similar laws carry lawsuit risk.
- **Decision:** no biometric features until a legal review; RFID/NFC/PIN come first.
- **Consequences:** possibly fewer hardware options at first.

### 011 — Rules have effective dates, conditions and jurisdiction presets
*2026-10-16 · Accepted* · [DQ-1](10-design-questions.md#dq-1--hour-rules-depend-on-age-calendar-and-jurisdiction)
- **Context:** hour limits depend on age, school calendar, jurisdiction and daily vs. weekly overtime; one fixed limit per employee type can't express them.
- **Decision:** employee types link to rule sets; rules have settings, effective date ranges and conditions (age, calendar state). School calendars are data. Ship cloneable jurisdiction presets. Store date of birth (restricted access). Workweek start is a per-location setting.
- **Consequences:** more complex P1 data model; correct handling of the core target market (students and minors).

### 012 — Time semantics for shifts and hour totals
*2026-10-16 · Proposed* · [DQ-2](10-design-questions.md#dq-2--time-zones-overnight-shifts-and-daylight-saving)
- **Context:** overnight shifts and DST make "hours per day/week" ambiguous.
- **Decision:** UTC storage; a shift belongs to the local day it starts on; hour totals use actual elapsed time split at workweek/pay-period boundaries; one `core/timecalc.py` module with property tests.
- **Consequences:** consistent results everywhere. **Open:** check how daily-overtime states treat shifts that cross midnight.

### 013 — Pay rates belong to employee + position
*2026-10-16 · Accepted* · [DQ-3](10-design-questions.md#dq-3--pay-rates-per-position-volunteers-are-unpaid)
- **Context:** different rates per position; blended overtime; unpaid volunteers.
- **Decision:** `pay_rates` keyed by (employee, position) with a default fallback and effective dates; employee types have `compensation: paid | volunteer`. Payroll export splits hours by rate; the provider calculates the blended rate.
- **Consequences:** correct exports; volunteers get service-hour reports instead of payroll.

### 014 — Publishing creates versioned snapshots
*2026-10-16 · Accepted* · [DQ-6](10-design-questions.md#dq-6--changes-after-publishing-and-predictive-scheduling-laws)
- **Context:** predictive scheduling laws; employees need to trust that published schedules are stable.
- **Decision:** publish writes an immutable snapshot; edits afterward require a reason and record notice hours and a diff; only affected employees are notified.
- **Consequences:** makes compliance reports possible later; slightly more storage.

### 015 — Employee pairing requests go confidentially to HR
*2026-10-16 · Accepted* · [DQ-5](10-design-questions.md#dq-5-dont-schedule-me-with-can-be-a-harassment-report)
- **Context:** a "don't schedule me with" request may be a harassment report.
- **Decision:** requests go to HR, not managers; approved restrictions appear to managers as "constraint (confidential)" with no reason; never shown to either employee; link to the business's harassment policy.
- **Consequences:** protects employees and the business; HR must actually review the queue (notifications + dashboard).

### 016 — Absence analytics are team-level by default
*2026-10-16 · Accepted* · [DQ-4](10-design-questions.md#dq-4-sick-leave-and-absence-analytics-carry-legal-risk)
- **Context:** per-employee absence pattern flags create retaliation/discrimination risk around protected leave.
- **Decision:** team/location-level totals by default; per-person views HR-only, labeled informational, never linked to automatic discipline. Sick leave gets its own leave bank with statutory accrual presets; doctor's notes are optional and controlled by settings.
- **Consequences:** a less flashy analytics feature, but much lower legal risk for customers.

### 017 — Perpetual license, no kill switch
*2026-10-16 · Accepted* · [DQ-11](10-design-questions.md#dq-11-license-behavior-when-maintenance-lapses)
- **Context:** self-hosting customers value control; a surprise lockout destroys trust.
- **Decision:** the software keeps working after maintenance lapses; updates and support stop. An invalid or missing license falls back to Basic tier features, never to locked out.
- **Consequences:** income depends on the maintenance plan being worth renewing, not on locking customers in.

### 018 — Maintainer access security
*2026-10-16 · Accepted* · [DQ-8](10-design-questions.md#dq-8-maintainer-access-is-the-biggest-security-risk)
- **Context:** remote access to every customer makes the maintainer a single point of compromise.
- **Decision:** hardware security keys on all critical accounts; per-customer Tailscale access rules with access logged; cosign-signed images checked on update; encrypted laptop. LLC, support agreement + DPA, and cyber/E&O insurance before the pilot.
- **Consequences:** small upfront cost and setup; essential for a product sold on data security.

### 019 — Live schedule updates via Postgres LISTEN/NOTIFY + SSE
*2026-10-16 · Accepted* · [DQ-7](10-design-questions.md#dq-7-two-managers-editing-the-same-schedule)
- **Context:** several managers may edit one schedule; no new services wanted.
- **Decision:** version checks (409 on conflict) as the baseline; LISTEN/NOTIFY → SSE notifies open grids, which refetch through the API.
- **Consequences:** live collaboration without Redis or WebSocket infrastructure.

### 020 — The schedule is never stored only on the box
*2026-10-16 · Accepted* · [DQ-9](10-design-questions.md#dq-9-resilience-when-an-on-prem-box-goes-down)
- **Context:** an on-prem box or internet connection will eventually fail.
- **Decision:** the PWA caches the employee's published shifts offline; publishing emails each employee their shifts and updates their iCal feed. Recovery targets: RPO ≤ 24 h, RTO ≤ 1 business day.
- **Consequences:** employees still know when to work during an outage.

### 021 — Staffing requirements are first-class
*2026-10-16 · Accepted* · [DQ-13](10-design-questions.md#dq-13-coverage-needs-must-be-data-not-just-shifts)
- **Context:** the solver needs to know what coverage is needed; managers need understaffing warnings.
- **Decision:** staffing requirements (headcount per position and time window) and shift composition rules (required skill, role requires role, max per role) are data, checked by the rules engine in P2 and used by the solver in P6.
- **Consequences:** P2 grows a little; P6 gets much simpler.

### 022 — Translations and accessibility from the start
*2026-10-16 · Accepted*
- **Context:** many hourly staff prefer Spanish or another language; adding translations or accessibility later is expensive.
- **Decision:** all UI and email text in translation files from P0; WCAG 2.2 AA, including a keyboard-only schedule grid; axe checks in CI.
- **Consequences:** small ongoing cost per feature.

### 023 — No built-in chat
*2026-10-16 · Accepted*
- **Context:** competitors offer chat; it brings a big moderation and support burden.
- **Decision:** announcements and shift notes only.
- **Consequences:** less to build and support; businesses keep using their existing group chats.

### 024 — Support the last two minor versions
*2026-10-16 · Accepted*
- **Context:** one maintainer can't test and support every release across many installs.
- **Decision:** support policy covers the latest two minor versions; upgrade tests cover the oldest supported → latest.
- **Consequences:** customers must update at least every couple of releases (`punchedn update` makes that easy).

### 025 — Auto-scheduler: tiered objective with locks and soft preferences
*2026-10-16 · Accepted* · [DQ-15](10-design-questions.md#dq-15-auto-scheduler-goals-balance-locks-preferences)
- **Context:** the auto-scheduler must map available employees and their constraints onto the needed schedule, balance hours, keep employees' fixed schedules, and try to honor schedule preferences.
- **Decision:** CP-SAT model with hard rules from the rules engine; **locked shifts** (fixed schedules + manager pins) are fixed inputs, skipped and reported only if they conflict with time off or a hard rule; objective tiers: coverage → overtime → **hour balance (deviation from target hours)** → **preferences (soft, weighted by strength and recent fairness)** → stability. The business adjusts the balance-vs-preference weighting. Output is always a draft plus an explanation report.
- **Consequences:** predictable, explainable results; fixed schedules, pins and preferences must exist in the data model from P2.

### 026 — Hour balancing and lock rules
*2026-10-16 · Accepted* · [DQ-15](10-design-questions.md#dq-15-auto-scheduler-goals-balance-locks-preferences)
- **Context:** #025 left open what "balanced" means, how long balance carries over, how fixed-schedule employees are treated, and whether locks can be broken.
- **Decision:**
  - Balance **toward each employee's desired hours** (capped by their rules), not equal hours.
  - **Rolling 4-week carry-over:** target = desired × weeks + Σ(desired − actual) over the previous 4 weeks.
  - **Fixed-schedule employees** have no target and no balance penalty; extra shifts for them only when coverage requires it.
  - **Locks are never broken** by the solver; uncoverable gaps are reported as unfilled.
- **Consequences:** needs a record of hours actually worked per employee per week (from published schedules, later from timesheets). Managers resolve gaps caused by locks manually.

### 027 — First preference types and fallback target
*2026-10-16 · Accepted* · [DQ-15](10-design-questions.md#dq-15-auto-scheduler-goals-balance-locks-preferences)
- **Context:** the last open items from DQ-15.
- **Decision:**
  - First preference types: **preferred days/times, preferred positions, avoid closing, max days/week**, each strong or mild, always soft.
  - Employees with no desired hours get a **fair share of the remaining pool demand** (after locked hours and other members' targets), weighted by availability and capped by their rules. They're prompted to set desired hours and flagged in the run report.
- **Consequences:** DQ-15 is fully decided. The preferences table and desired-hours prompt ship in P2; the solver uses them in P6.

### 028 — Built-in authentication; no bundled identity provider
*2026-10-16 · Accepted*
- **Context:** Keycloak was considered for password management. Installs run on modest hardware (minimum 4 GB RAM), one maintainer supports every host, and Postgres is the only stateful service (#002). The hardest login flows (phone + one-time code, kiosk PIN, per-customer branding, Spanish) would need custom Keycloak extensions and themes in Java. Authorization (permission-based RBAC, separation of duties) lives in the app either way. Target customers rarely run SAML/LDAP; when they want SSO it's usually Google Workspace or Microsoft 365.
- **Decision:**
  - Authentication stays in the app, built on proven libraries: Argon2id (`argon2-cffi`), rate limiting + lockout, server-side session/refresh-token records so sessions can be revoked.
  - **TOTP 2FA (`pyotp`) is required for users holding sensitive permissions** (pay rates, health data, roles/permissions); optional for everyone else. Recovery codes are issued at enrollment.
  - Passkeys/WebAuthn later.
  - SSO is added later as an **OIDC client** (Authlib) pointing at the customer's existing IdP. An `identities (user_id, provider, subject)` table exists from P1 so external logins attach to existing users without a migration.
  - Authorization always comes from PunchedN's permission tables, never from IdP roles or claims.
  - No IdP ships in the bundle. If a customer requires one on the box, it's an optional Compose profile (evaluate lighter options such as Zitadel or Authentik before Keycloak).
- **Consequences:** no JVM service, extra upgrade path or extra backup on each host; auth code must be well tested (it's security-critical and owned by us). Revisit if customers need AD/LDAP federation or SAML, or if PunchedN becomes several apps sharing one login.

### 029 — Use the latest stable versions
*2026-10-16 · Accepted*
- **Context:** the project starts from scratch, so there's no upgrade cost yet. Starting on older versions means an early migration and a shorter support window. Python 3.15 was released on 2026-10-09; OR-Tools doesn't publish 3.15 wheels yet but isn't needed until P6.
- **Decision:**
  - Use the latest **stable** release of every language, runtime, framework, tool and host OS. No pre-releases. Node.js uses the newest LTS line.
  - If a *required* dependency doesn't support the newest version, use the newest version all required dependencies support, and move up when they catch up.
  - Starting versions: Python 3.15, PostgreSQL 18, Node.js 26 LTS, Ubuntu 26.04 LTS / Debian 13 hosts. The full table is in [02 — Versions](02-tech-stack.md#versions).
  - Renovate keeps versions current; major upgrades are reviewed by hand and update the versions table in the same PR.
- **Consequences:** fewest forced upgrades over the product's life, and longest security support. Newer releases sometimes lack wheels or plugin support at first. **Open:** confirm OR-Tools ships Python 3.15 wheels before P6; if not, decide then between waiting and running the solver on 3.14.
