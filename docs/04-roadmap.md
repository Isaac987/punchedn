# 04 — Roadmap

Built solo. Every phase ends with a version that works, can be demoed, is tagged and can be installed. **Phases 0–3 are the MVP**: enough for a real business to stop scheduling by hand.

Effort is in relative sizes (S/M/L/XL), not dates. Adjust once Phase 0 gives you a sense of your pace. ⚠ marks items that shape the data model; see [10 — Design Questions](10-design-questions.md).

```
P0 Foundation ─► P1 Core data ─► P2 Manual scheduling ─► P3 Time off + notifications ─► [PILOT]
                                                                                            │
       P8 Expansion ◄─ P7 Commercial ◄─ P6 Auto-scheduling ◄─ P5 Time & attendance ◄─ P4 Marketplace
```

---

## P0 — Foundation · L

**Goal:** the production basics and the deploy/upgrade path work before any features exist.

- Monorepo, dev environment, pre-commit, Renovate
- Backend skeleton: config, structured logging, error handling, DB session, health endpoints
- `core/timecalc.py` skeleton with DST/boundary property tests ([DQ-2](10-design-questions.md#dq-2--time-zones-overnight-shifts-and-daylight-saving))
- Frontend skeleton: Vite + React + Tailwind/shadcn theme tokens, generated API client, **translation files**, accessibility linting
- Background worker skeleton (Procrastinate)
- CI: lint, type check, tests, builds for both processor types, Trivy, CodeQL, release-please, **cosign signing**
- Docker Compose bundle, installer with preflight check, `punchedn update/backup/restore/status` (update **checks the image signature**)
- **Maintainer account security:** hardware keys on GitHub/GHCR/Tailscale/email/registrar/password manager ([DQ-8](10-design-questions.md#dq-8-maintainer-access-is-the-biggest-security-risk))
- Upgrade test in CI (once a previous release exists)

**Exit criteria:** a tagged `v0.1.0` installs on a clean Ubuntu VM *and* an ARM64 machine with one command, shows a branded "hello" page over HTTPS, survives `punchedn update` to `v0.1.1`, refuses an unsigned image, and restores from a backup.
Detailed checklist: [08 — Phase 0 Plan](08-phase-0-plan.md).

## P1 — Core data · L

**Goal:** an admin can set up a business, including importing it from a spreadsheet.
Modules: **M1** platform core, **M2** org structure & rules, **M3** employee management.

- ⚠ Rule sets with effective dates and conditions, school calendars, first jurisdiction preset (US federal minors) ([DQ-1](10-design-questions.md#dq-1--hour-rules-depend-on-age-calendar-and-jurisdiction))
- ⚠ Pay rates per employee + position; volunteer compensation type ([DQ-3](10-design-questions.md#dq-3--pay-rates-per-position-volunteers-are-unpaid))
- Date of birth (restricted access), desired hours
- **CSV import** for employees, positions and skills
- **Demo data generator**
- Phone + one-time-code login for employees without email
- **TOTP 2FA**, required for sensitive permissions; `identities` table ready for future SSO ([#028](09-decisions.md#028--built-in-authentication-no-bundled-identity-provider))

**Exit:** set up a business with 2 locations, 5 positions, skills, rule sets with a school calendar, 20 employees imported from CSV, and custom roles showing separation of duties. Everything audited.

## P2 — Manual scheduling ⭐ · XL

**Goal:** managers build and publish schedules; employees see them on their phones.
Modules: **M4** availability, **M5** scheduling, PWA "My Schedule".

- Rules engine with age/calendar-aware hour rules
- ⚠ **Staffing requirements** + **shift composition rules** ([DQ-13](10-design-questions.md#dq-13-coverage-needs-must-be-data-not-just-shifts))
- ⚠ **Versioned publishing** with change reasons and notice hours ([DQ-6](10-design-questions.md#dq-6--changes-after-publishing-and-predictive-scheduling-laws))
- **Scheduling cycle workflow** (availability deadline → draft → publish-by)
- Concurrent editing: version checks + live updates via LISTEN/NOTIFY → SSE ([DQ-7](10-design-questions.md#dq-7-two-managers-editing-the-same-schedule))
- Data the auto-scheduler will need: **fixed (locked) schedules**, **pinned assignments**, **schedule preferences**
- Confidential HR routing for employee pairing requests ([DQ-5](10-design-questions.md#dq-5-dont-schedule-me-with-can-be-a-harassment-report))
- Keyboard-accessible grid; overnight/DST correctness
- **Offline schedule** in the PWA, **schedule email** on publish, iCal feed ([DQ-9](10-design-questions.md#dq-9-resilience-when-an-on-prem-box-goes-down))
- CSV import of availability and existing schedules
- Ops: network access setup (Cloudflare Tunnel) documented and scripted

**Exit:** a manager builds a week from staffing requirements in under 10 minutes with live rule warnings (including a minor's school-week limit), publishes it, and employees receive it by email and on their phones, readable offline. Overlaps are impossible; edits after publishing are versioned with reasons.

## P3 — Time off & notifications · L → PILOT

**Goal:** fully replaces the paper process.
Modules: **M6** time off & absences, **M8** notifications & communication.

- Leave banks (PTO, sick, custom), sick-leave preset for the pilot's jurisdiction, optional doctor's notes
- Time-off limits and blackout dates
- Shift reminders, announcements, shift notes
- **Spanish translation** (if the pilot needs it)

**Before the pilot install:**
- Ops: opt-in heartbeat, `support-bundle`, a **tested restore** that meets the recovery promise (RPO ≤ 24 h, RTO ≤ 1 business day), install tested on one on-prem box *and* one cloud server, a basic runbook
- Business: **LLC**, **support agreement + data processing agreement**, **cyber/E&O insurance**, per-customer Tailscale access rules
- Ask the pilot which payroll and accounting tools they use ([DQ-10](10-design-questions.md#dq-10-pay-stubs-and-accounting-integrations))

**Exit / milestone:** **install at the first pilot business.** Run it for at least one full schedule cycle before starting P4, and fix the pilot's top pain points first.

## P4 — Shift marketplace · M

Module **M7**. Swaps (both sides checked against the rules engine), give-aways, open shifts limited to eligible employees, spare-capacity offers, global toggle.

## P5 — Time & attendance · L

- **M9:** web + kiosk clock-in, **punch policies** (rounding, early clock-in, missed punches), **break rules**, timesheets ([DQ-12](10-design-questions.md#dq-12-time-clock-rules-beyond-punching-in))
- **M10 basics:** hours and labor-cost reports, **volunteer service-hour certificates**, **fairness dashboard**
- **M11:** payroll CSV split by position/rate with provider presets; HR pay stub upload

## P6 — Auto-scheduling · XL

Module **M12**. CP-SAT solver in the worker maps available employees onto the needed schedule; constraints come from the rules engine, staffing requirements and composition rules ([DQ-15](10-design-questions.md#dq-15-auto-scheduler-goals-balance-locks-preferences)).
- Keeps **locked shifts** (fixed schedules + pins); **balances hours** toward target hours; honors **schedule preferences** as soft goals; full and fill-remaining modes
- **Explanations** for unfilled slots and assignments ([DQ-14](10-design-questions.md#dq-14-explaining-auto-generated-schedules))
- Property-based tests (every generated schedule passes every hard rule)
- Benchmarks on the minimum hardware spec using demo-generator data and anonymized pilot data

**Exit:** generates a usable draft for a 50-employee, 1-week schedule within the time limit on minimum-spec hardware, with an explanation for every unfilled slot, every locked shift kept, and hours within an agreed tolerance of target for each pool.

## P7 — Commercialization · M

- **Perpetual** offline license file + tier feature flags, no kill switch ([DQ-11](10-design-questions.md#dq-11-license-behavior-when-maintenance-lapses))
- Support policy (last 2 minor versions), EULA
- Opt-in anonymous usage stats
- Documentation site, pricing page, a repeatable onboarding checklist

## P8 — Expansion · ongoing, driven by customers

Pick based on what paying customers ask for:
- Payroll/accounting API integrations, chosen from the provider survey
- **Webhooks + documented API**
- **Labor-law report pack**; predictive-scheduling extra-pay calculation
- Absence-pattern analytics, team-level by default (needs months of data)
- POS sales data → suggested staffing requirements
- Raspberry Pi RFID/NFC time clock (`clock-agent`)
- Native app with Expo (iPhone NFC, app stores)
- SSO as an OIDC client to the customer's IdP (Google Workspace, Microsoft 365); passkeys/WebAuthn; SMS notifications
- Optional managed hosting on your own infrastructure
- Biometrics, **only after legal review**

---

## Solo-dev guardrails

- **Each extra platform adds a lot of ongoing work:** native app, hardware and integrations. Build them only for a paying customer.
- **Don't start P4 until a pilot has used P3** for at least one full schedule cycle.
- Settle the ⚠ data-model items in P1–P2. Changing them after the pilot means painful migrations.
- Write commit messages worth reading (release-please turns them into the `CHANGELOG`) and keep a short weekly log of your own progress; with no team, they're your memory.
- Stop adding features at least 1–2 weeks before a pilot install; spend that time on ops and fixes.
