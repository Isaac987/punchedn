# 03 — Feature Breakdown

Features from `PunchedN.pdf`, plus additions from [10 — Design Questions](10-design-questions.md), grouped into modules. **P** = the phase it's planned for (see [04 — Roadmap](04-roadmap.md)). 🆕 = added after the original idea doc.

**Key design principle:** the **rules engine** (M5) is shared by manual scheduling and the future auto-scheduler. The rule that warns a manager ("student over 18 hrs in a school week") is the same rule the OR-Tools solver turns into a constraint. See [05 — Architecture](05-architecture.md#rules-engine).

---

## M1 — Platform core · P0–P1

| Feature | Acceptance criteria |
|---|---|
| Login / logout / password reset | Argon2 hashes; reset by emailed link; failed logins rate-limited and logged |
| 🆕 Two-factor authentication | TOTP (authenticator app) with recovery codes. **Required** for anyone holding sensitive permissions (pay rates, health data, roles/permissions); optional for others. Admin can reset a user's 2FA (audited) ([#028](09-decisions.md#028--built-in-authentication-no-bundled-identity-provider)) |
| Invite users | Admin/HR sends an invite email; the invite link expires; the user sets their own password |
| **Permission-based RBAC** | Permissions are fine-grained strings (`schedule.publish`, `employee.pay_rate.view`). Roles are named sets of permissions. Each assignment can be limited to specific locations |
| Role presets | Admin, Manager, HR and Employee presets ship with the product; they can be cloned and edited, but presets can't be deleted |
| User groups | Create, edit and delete groups; assign roles to groups |
| Promote users | Admin can assign Manager/HR roles; every change is audited |
| Separation of duties | It's possible to configure a setup where managers schedule but can't change pay, and HR changes pay but can't publish schedules |
| Global policies | Toggles such as "shift swapping enabled," "employees can see coworkers," and the harassment-policy link |
| Branding | Upload a logo; choose primary/accent colors; applied app-wide through CSS variables; contrast checked |
| Audit log | Records who changed what and when, with before/after values, for permissions, pay, schedules and employee records. Can't be edited from the app |
| Advanced config | Time zone and **workweek start** per location, pay period, default shift lengths |
| 🆕 **Translations** | All UI text in translation files from P0; English first, then Spanish; each user picks a language; emails translated too |
| 🆕 **Accessibility** | Meets WCAG 2.2 AA; everything works with a keyboard alone, including the schedule grid |

## M2 — Org structure & rules · P1

| Feature | Acceptance criteria |
|---|---|
| Locations | A business can have one or more locations, each with its own time zone, hours and workweek |
| Departments | Optional grouping inside a location |
| Positions / tasks | CRUD (Cashier, Stocker, Cleaner); a color for the schedule grid; can require skills |
| Skills / qualifications | CRUD; optional expiry date (e.g. food-handler certificate); warning before it expires |
| **Employee types** | CRUD (Student, Volunteer, Part-time, Full-time); `compensation: paid / volunteer`; linked to a **rule set** |
| 🆕 **Rule sets** | Rules with settings, **effective date ranges** and **conditions** (age range, school calendar state). See [DQ-1](10-design-questions.md#dq-1--hour-rules-depend-on-age-calendar-and-jurisdiction) |
| 🆕 **Jurisdiction presets** | US federal minors, then the pilot customers' states; admins clone and edit them |
| 🆕 **School calendars** | Named calendars with in-session / break / exam periods; rules can depend on them |

## M3 — Employee management (HR) · P1

| Feature | Acceptance criteria |
|---|---|
| Add / edit / terminate employee | HR permission only; terminating revokes access immediately and keeps the history (soft delete) |
| Profile | Name, contact details, hire date, **date of birth** (restricted access), employee type, positions, skills |
| 🆕 **Pay rate per position** | Rates keyed by employee + position with effective dates; default-rate fallback; viewing and editing need separate permissions |
| 🆕 **Desired hours** | Min/max hours the employee wants per week; used for fairness and by the solver |
| Employee self-view | Own hire date, pay rates, leave balances |
| 🆕 **CSV import** | Import employees, positions and skills from a spreadsheet, with column mapping, a preview, row-level errors and an all-or-nothing commit |
| 🆕 Employees without email | Login with a phone number + one-time code or a kiosk PIN, for staff who don't have email |

## M4 — Availability & preferences · P2

| Feature | Acceptance criteria |
|---|---|
| Recurring availability | Weekly pattern per employee (available / preferred / unavailable) |
| Date exceptions | One-off changes ("unavailable Dec 20–Jan 5") |
| Self-service availability | Employee edits their own; optionally needs manager approval; **deadline per scheduling cycle** |
| Availability by role | Manager limits which positions an employee can fill and when |
| 🆕 **Schedule preferences** | Employee states the schedule they'd like. **First release:** preferred days/times, preferred positions, avoid closing, max days/week (more types later, e.g. preferred shift length). Each can be marked strong or mild. **Always soft:** used by the auto-scheduler (M12) and shown as hints in manual scheduling; never blocks an assignment. Unlike *unavailable* (hard), *preferred* only affects how well a schedule scores |
| **Do-not-pair (manager)** | Manager-defined restriction, enforced by the rules engine |
| 🆕 **Do-not-pair (employee request)** | Sent **confidentially to HR**; once approved, managers see it only as "constraint (confidential)" with no reason; never shown to either employee. See [DQ-5](10-design-questions.md#dq-5-dont-schedule-me-with-can-be-a-harassment-report) |
| 🆕 CSV import | Import existing availability |

## M5 — Scheduling (manual) · P2

| Feature | Acceptance criteria |
|---|---|
| Schedule periods | Weekly / biweekly / monthly; status **Draft → Published → Archived** |
| 🆕 **Scheduling cycle workflow** | Per period: availability deadline → reminders → draft → publish-by date (with notice-period warnings). Dashboard shows where each period stands |
| 🆕 **Staffing requirements** | Per location/position/time window: min/max headcount, required skills. The grid shows understaffed and overstaffed times |
| 🆕 **Shift composition rules** | "≥1 keyholder on every shift," "trainee requires a trainer on the same shift," "max N trainees" |
| Shift templates | A reusable layout of shift slots (time, position, required skills, headcount), with no one assigned |
| Create shifts | From a template, from staffing requirements, or by hand |
| Assign employees | Drag-and-drop **and** a keyboard-only alternative |
| **Overlap protection** | Double-booking is impossible (database constraint + friendly UI message) |
| **Rule validation** | Live warnings/blocks: hour caps (age/calendar aware), skill mismatch, outside availability, do-not-pair, minimum rest, overtime, staffing requirements, composition rules. Hard rules block; soft rules warn, and a manager can override with a reason |
| 🆕 **Overnight / DST correctness** | Shifts crossing midnight and DST changes are counted the way [DQ-2](10-design-questions.md#dq-2--time-zones-overnight-shifts-and-daylight-saving) defines |
| Copy previous schedule | Copy period N to N+1; whatever conflicts with time off or rules is flagged |
| Recurring assignments / **fixed schedules** | "Alex works Mon 9–1 every week" automatically fills new periods. Can be marked **locked**: the auto-scheduler keeps it (M12). Has effective dates (e.g. one semester) |
| 🆕 **Pin assignments** | In a draft, a manager can pin any assignment so the auto-scheduler won't move it |
| 🆕 **Versioned publishing** | Publishing creates an immutable snapshot; changes afterward require a reason and record the hours of notice given; only affected employees are notified |
| 🆕 **Concurrent editing** | Version checks (409 on conflict) + live grid updates for other managers viewing the schedule |
| Print / export | PDF for 1 week, 2 weeks or 1 month, filtered by location or position |
| My schedule (employee) | Mobile-first list and calendar; optionally shows coworkers on the same shift |
| 🆕 **Offline schedule** | The PWA caches the employee's published schedule for viewing offline |
| 🆕 **Schedule by email** | On publish, each employee is emailed their shifts |
| Calendar feed | Personal iCal link (can be revoked) |
| 🆕 CSV import | Import an existing schedule (for onboarding) |

## M6 — Time off & absences · P3

| Feature | Acceptance criteria |
|---|---|
| 🆕 **Leave banks** | Separate banks (PTO, sick, custom), each with a policy: accrual per hours worked or per period, cap, carry-over, waiting period. Append-only ledger |
| 🆕 **Sick-leave presets** | Accrual and usage rules matching the pilot's jurisdiction |
| Time-off request | Choose a bank, or unpaid; full or partial day; reason optional |
| 🆕 **Time-off limits** | Blackout dates; max N people off per location/position per day; shown before an employee submits |
| Approve / deny | The manager sees which shifts are affected and how they'll be covered before deciding |
| Sick call-out | Employee taps "call in sick" for a shift; manager is notified; the shift becomes an **open shift** |
| Mark sick (manager) | Manager can record a sick call on the employee's behalf |
| Doctor's note upload | **Optional, set in settings** (e.g. only for absences > N days). Stored encrypted; HR/permitted roles only; retention period setting |

## M7 — Shift marketplace · P4

| Feature | Acceptance criteria |
|---|---|
| Global toggle | Admin can turn swapping on or off |
| Swap request | A offers → B accepts → manager approves (approval is a setting). **Both sides** are checked against the rules engine (hours, skills, overtime, composition) |
| Give away / partial | Give a shift away without taking one back; partial-shift handoffs (a setting) |
| Open shifts | Shifts left open by sick calls or extra staffing needs; only qualified, eligible employees are notified; first come or manager picks |
| Spare capacity | Offer shifts first to people under their desired hours, to keep overtime low |
| Notifications | Everyone involved is notified at each step |

## M8 — Notifications & communication · P3

| Feature | Acceptance criteria |
|---|---|
| Channels | In-app, email, web push. SMS later (who pays the per-message costs is decided per customer) |
| Events | Schedule published/changed, time-off decision, sick call, swap and open-shift events, availability deadline |
| 🆕 **Shift reminders** | Configurable reminder N hours before a shift |
| 🆕 **Announcements** | Manager posts to a location/position/everyone; read receipts optional. **No chat** |
| 🆕 **Shift notes** | Notes attached to a shift ("bring the cash bag key") |
| Preferences | Per user, per event type, per channel |
| Delivery | Sent by background jobs with retries; failures logged |

## M9 — Time & attendance · P5

| Feature | Acceptance criteria |
|---|---|
| Web clock-in/out | From the employee's phone; geofence and/or a business-network check (settings) |
| Kiosk mode | A shared tablet with PIN login; optional photo capture at punch (**no face recognition**) |
| 🆕 **Punch policies** | Rounding (off by default, neutral only), how early someone may clock in, missed-punch fixes with approval and a reason |
| 🆕 **Break rules** | Meal/rest break requirements (jurisdiction presets) with alerts and timesheet flags |
| Timesheets | Scheduled vs. actual hours; manager edits with a reason; approve each pay period |
| Overtime tracking | Live alerts when someone is approaching overtime (weekly and daily) |
| Device registration | Each time clock device gets its own **token** and can be revoked |

## M10 — Reporting & analytics · P5 (basic) / P8 (advanced)

| Feature | Acceptance criteria |
|---|---|
| Hours reports | By employee, employee type, position, location; scheduled vs. actual |
| Labor cost | Hours × rate per position (needs a permission) |
| 🆕 **Volunteer service hours** | Report and printable **certificate** per volunteer for a date range (P5) |
| 🆕 **Fairness dashboard** | How hours, weekends, closing shifts and holidays are spread vs. desired hours (P5) |
| Absence patterns | Trends by weekday, month and holiday; **team-level by default**; per-person views HR-only and labeled informational (P8). See [DQ-4](10-design-questions.md#dq-4-sick-leave-and-absence-analytics-carry-legal-risk) |
| 🆕 **Labor-law report pack** | Schedule notice given, post-publish changes, sick-leave balances, hours worked by minors, break compliance (P8) |
| **Export all data** | Full CSV/JSON export (admin), also serves as data portability |

## M11 — Integrations · P5 (CSV) / P8 (APIs)

| Feature | Acceptance criteria |
|---|---|
| Payroll CSV export | Approved timesheets split by position/rate; configurable column layout; presets for common providers |
| 🆕 **Provider survey** | Ask pilot customers which payroll/accounting tools they use before building integrations ([DQ-10](10-design-questions.md#dq-10-pay-stubs-and-accounting-integrations)) |
| Accounting/payroll APIs | Candidates: QuickBooks, Xero, FreshBooks, Wave, **Gusto, Square, ADP, Paychex**. Check each provider's API and terms first |
| Pay stubs | **HR uploads the PDF** (fallback); pull from provider APIs where supported. **We do not calculate payroll** |
| 🆕 **Webhooks + documented API** | Webhooks on key events (signed, retried); API tokens with limited permissions; lets customers build integrations themselves (P8) |
| 🆕 POS sales data | Square / Toast sales history → suggested staffing requirements (P8) |

## M12 — Auto-scheduling · P6

| Feature | Acceptance criteria |
|---|---|
| Generate schedule | Looks at available employees and their constraints and **maps them to the needed schedule** (staffing requirements / open slots) in a draft period using CP-SAT |
| **Locked shifts** | Locked assignments are fixed inputs the solver must keep: (1) **fixed schedules**, employees whose recurring schedule is locked (M5), and (2) **pinned** assignments a manager locks in a draft before running the solver. Locked hours count toward hour totals and balancing. If a lock conflicts with approved time off or a hard rule, the solver skips that one occurrence and reports it; time off always wins. **The solver can never break a lock to cover a gap**; the gap is reported as unfilled |
| Hard constraints | All M5 hard rules + composition rules + availability + approved time off + locked shifts |
| **Hour balancing** | Balance **toward each employee's desired hours** (capped by their rules), with a **rolling 4-week carry-over**: anyone short or over in the last 4 weeks gets their target adjusted this period. **Fixed-schedule employees aren't pushed toward a target**; they only get extra shifts when coverage can't be met otherwise. Fallback when desired hours aren't set: a fair share of the remaining pool demand, weighted by availability; the employee is prompted to set desired hours and flagged in the run report |
| **Schedule preferences (soft)** | Try to give employees the schedule they asked for (M4 preferences). Never overrides a hard constraint or coverage |
| Other soft goals | Keep overtime low, consistency with last period, avoid "clopens" (a closing shift followed by an opening shift) |
| **Priority order** | 1) fill required coverage → 2) avoid overtime → 3) balance hours → 4) preferences → 5) stability. Weighted so a higher tier always beats a lower one; the business can adjust the balance-vs-preference weighting with a simple slider |
| **Preference fairness** | Track each employee's preference satisfaction over recent periods and prioritize those who got less, so the same people don't always win |
| Re-run / partial | Re-running keeps locks and pins; "fill remaining" mode only fills empty slots, leaving manual edits untouched |
| 🆕 **Explanations** | Why each slot is unfilled (the binding constraints); top factors behind each assignment ([DQ-14](10-design-questions.md#dq-14-explaining-auto-generated-schedules)) |
| Result | Always a **draft** for the manager to review |
| Runtime | Background job with a time limit and progress; runs well on the minimum hardware spec |

## M13 — Hardware time clocks · P8

| Feature | Acceptance criteria |
|---|---|
| RFID/NFC reader | Raspberry Pi + PN532 reader running the `clock-agent` program |
| Offline buffering | Punches are stored locally and synced later; duplicate punches are ignored |
| Phone NFC | Android through Web NFC; iPhone needs the native app |
| Biometrics | **Only after a legal review** |

## M14 — Commercial & ops · P0 / P1 / P3 / P7

| Feature | Phase |
|---|---|
| Installer + preflight check, `punchedn` admin command (update/backup/restore/support-bundle) | P0–P3 |
| 🆕 **Signed images** (cosign) checked by `punchedn update` | P0 |
| 🆕 **Demo data generator**: realistic fake businesses for demos, screenshots, E2E tests and solver benchmarks | P1 |
| Opt-in heartbeat | P3 |
| 🆕 Opt-in anonymous usage stats (feature usage counts only) | P7 |
| Offline license file (Ed25519-signed), **perpetual, no kill switch**; tier feature flags fall back to Basic | P7 |
| 🆕 Support policy: last 2 minor versions supported | P7 |
| EULA, documentation site | P7 |

---

## Tier split (draft)

| Basic | Advanced (adds) |
|---|---|
| M1–M6, M8, payroll CSV, CSV import, volunteer service hours | M7 marketplace, M9 time clock, fairness dashboard, absence and labor-law reports, M11 API integrations + webhooks, M12 auto-scheduling, M13 hardware, SSO |

## Legal & compliance flags

Things to research per jurisdiction, not legal advice:

- **Biometrics:** Illinois BIPA, Texas CUBI, Washington and others. Requires consent, retention policies; real lawsuit exposure. Leave until last and get legal advice first. Includes face recognition on kiosk photos.
- **Minors / students:** federal and state child-labor hour and time-of-day limits; international student work-hour limits. Rule presets ([DQ-1](10-design-questions.md#dq-1--hour-rules-depend-on-age-calendar-and-jurisdiction)).
- **Paid sick leave:** many states and cities mandate accrual and usage rules ([DQ-4](10-design-questions.md#dq-4-sick-leave-and-absence-analytics-carry-legal-risk)).
- **Doctor's notes:** health information. Some jurisdictions limit when they can be required. Encrypt, restrict access, set a retention policy.
- **Absence analytics:** protected leave (FMLA, ADA, sick-leave laws) means retaliation/discrimination risk. Team-level by default.
- **Harassment:** pairing requests may be reports; route them to HR ([DQ-5](10-design-questions.md#dq-5-dont-schedule-me-with-can-be-a-harassment-report)).
- **Predictive scheduling laws:** advance notice and extra pay for late changes in several cities and Oregon ([DQ-6](10-design-questions.md#dq-6--changes-after-publishing-and-predictive-scheduling-laws)).
- **Overtime:** weekly and, in some states, daily; blended rate across positions ([DQ-3](10-design-questions.md#dq-3--pay-rates-per-position-volunteers-are-unpaid)).
- **Time clock rounding and breaks:** rounding only if neutral; state meal/rest break rules ([DQ-12](10-design-questions.md#dq-12-time-clock-rules-beyond-punching-in)).
- **Records retention:** time and pay records have legally required retention periods. Don't hard-delete them.
- **Privacy:** CCPA/GDPR-style export and deletion requests.

## Not building

See [10 — Design Questions](10-design-questions.md#deliberately-not-building): built-in chat, payroll calculation, Windows hosts, face recognition.
