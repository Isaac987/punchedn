# 10 — Design Questions

Areas that are harder than they look, with the approach we've chosen or proposed. Each entry lists which docs it affects and **the phase it must be settled by**. Items marked ⚠ shape the Phase 2 data model; changing them after the pilot means painful migrations.

> Labor-law points are things to research, not legal advice. Check each one for the jurisdictions of your first customers.

Status: **Decided** (recorded in [09](09-decisions.md)) · **Proposed** (direction chosen, details open) · **Open**.

---

## DQ-1 ⚠ Hour rules depend on age, calendar and jurisdiction
**Status:** Decided ([#011](09-decisions.md#011--rules-have-effective-dates-conditions-and-jurisdiction-presets)) · **Settle by:** P1

**Problem.** "Students can't work over 24 hrs/week" is one fixed rule. Real limits vary by:
- **Age.** Federal rules for 14–15-year-olds include 3 hrs on a school day, 18 hrs in a school week, and no work after 7pm during the school year. A rule's outcome can change on someone's birthday.
- **School in session vs. breaks.** Limits for minors and international students usually loosen during summer and breaks.
- **Daily vs. weekly overtime.** Some states (e.g. California) also have daily overtime.
- **The legal workweek.** For overtime it's a fixed 7-day window chosen by the employer, which may differ from the schedule period.

**Approach.**
- Rules live in **rule sets** made of rules with settings, **effective date ranges** and **conditions** (age range, school-calendar state, employee type).
- **School calendars** are data (in-session / break periods), so one calendar can serve several employee types.
- `date_of_birth` is stored (restricted access) so age-based rules can be checked on the shift date.
- Ship **jurisdiction presets** (US federal minors first, then the first customers' states) that admins clone and adjust.
- The workweek start day/time is a setting for each location.

**Affects:** [03](03-features.md) M2/M3, [05](05-architecture.md#rules-engine).

## DQ-2 ⚠ Time zones, overnight shifts and daylight saving
**Status:** Proposed ([#012](09-decisions.md#012--time-semantics-for-shifts-and-hour-totals)) · **Settle by:** P2

**Problem.** A 10pm–6am shift belongs to two days. On the night clocks fall back it's 9 hours long; on the night they spring forward it's 7. Which day, week and pay period does it count toward?

**Approach (proposed).**
- Store every moment in UTC; each location has an IANA time zone.
- **Display and day limits:** a shift belongs to the local day it **starts** on.
- **Hour totals (weekly limits, overtime):** count **actual elapsed hours**, split at workweek and pay-period boundaries. That's how hours worked are generally counted for overtime, and it handles DST correctly.
- Every hour calculation goes through one tested module (`core/timecalc.py`). Hypothesis tests cover DST transitions and shifts that cross a boundary.

**Open.** Check how daily-overtime states treat a shift that crosses midnight before building daily-overtime presets.

## DQ-3 ⚠ Pay rates per position; volunteers are unpaid
**Status:** Decided ([#013](09-decisions.md#013--pay-rates-belong-to-employee--position)) · **Settle by:** P1

**Problem.** Employees often earn different rates for different positions. Overtime across two rates may have to use a **blended (weighted-average) rate**. Volunteers have no pay at all.

**Approach.**
- `pay_rates` are keyed by **(employee, position)**, with effective dates and a default rate for the employee as a fallback.
- Each employee type has a `compensation` setting: `paid` | `volunteer`. Volunteers skip pay rates, overtime and payroll export, but appear in **service-hour reports**.
- Payroll export sends hours split by position and rate; the payroll provider calculates the blended overtime rate (we don't calculate payroll, see [#009](09-decisions.md#009--dont-calculate-payroll)).

## DQ-4 Sick leave and absence analytics carry legal risk
**Status:** Decided ([#016](09-decisions.md#016--absence-analytics-are-team-level-by-default)) · **Settle by:** P3 (leave), P8 (analytics)

**Problem.**
- Many states and cities **require paid sick leave**, often accrued per hours worked, with legal carry-over and usage rules.
- Some places **limit when an employer can require a doctor's note**, e.g. not for short absences.
- Flagging individual employees' "absence patterns" can lead to retaliation or discrimination claims when leave is protected (FMLA, ADA, sick-leave laws).

**Approach.**
- **Separate leave banks** (PTO, sick, custom), each with its own policy (accrual per hours worked or per period, cap, carry-over) in an append-only ledger.
- Doctor's-note upload is **optional and controlled by settings** (e.g. "only ask for absences longer than N days").
- Absence analytics show **team- and location-level totals** by default. Per-person views are HR-only, labeled "informational," and never trigger automatic discipline.

## DQ-5 "Don't schedule me with…" can be a harassment report
**Status:** Decided ([#015](09-decisions.md#015--employee-pairing-requests-go-confidentially-to-hr)) · **Settle by:** P2

**Problem.** An employee asking not to work with someone may really be reporting harassment, which needs HR follow-up. The other person must never find out, including indirectly. And enough restrictions can make a schedule **impossible to staff**.

**Approach.**
- Requests from employees go **confidentially to HR**, not the manager. Once HR approves, a restriction is created and shown to managers only as "constraint (confidential)," with no reason shown.
- The request form includes a link to the business's harassment-reporting policy (a setting).
- The rules engine reports **which restrictions are making a period impossible to staff** (to HR/admins only).
- Restrictions are never shown to either employee involved.

## DQ-6 ⚠ Changes after publishing, and predictive scheduling laws
**Status:** Decided ([#014](09-decisions.md#014--publishing-creates-versioned-snapshots)) · **Settle by:** P2

**Problem.** Several cities and Oregon require advance notice of schedules (roughly 14 days) and extra pay when a schedule changes late. Even elsewhere, changes after publishing need a reason, notifications and a history.

**Approach.**
- Publishing creates an **immutable, versioned snapshot**. Changes made afterward record `reason`, `changed_by` and **hours of notice given**.
- Only the employees affected by a change are notified.
- The data supports a later **compliance report** (notice given, changes, extra pay owed). Calculating the extra pay is a Phase 8 preset.

## DQ-7 Two managers editing the same schedule
**Status:** Decided ([#019](09-decisions.md#019--live-schedule-updates-via-postgres-listennotify--sse)) · **Settle by:** P2

**Approach.**
- **Baseline:** every write to a schedule period carries a version number (`If-Match`). If the schedule changed in the meantime, the server returns 409 and the UI asks the manager to reload.
- **Live updates:** Postgres `LISTEN/NOTIFY` → Server-Sent Events push grid changes to open browsers. No new services needed.
- Optional "someone else is editing this" indicator.

## DQ-8 Maintainer access is the biggest security risk
**Status:** Decided ([#018](09-decisions.md#018--maintainer-access-security)) · **Settle by:** P0 (accounts), P3 (contracts)

**Problem.** Remote access to every customer box makes the maintainer's laptop and accounts a single point of failure for all customers.

**Approach.**
- **Hardware security keys** (FIDO2) on GitHub, GHCR, Tailscale, email, the domain registrar and password manager.
- **Per-customer Tailscale access rules**, with access logged and time-limited where possible, and no always-on root.
- Images **signed with cosign**; `punchedn update` checks the signature before deploying.
- Full-disk encryption and automatic screen lock on the maintainer's laptop.
- Business: an **LLC**, a **support agreement + data processing agreement**, and **cyber/E&O insurance**, all in place **before the pilot**.

## DQ-9 Resilience when an on-prem box goes down
**Status:** Decided ([#020](09-decisions.md#020--the-schedule-is-never-stored-only-on-the-box)) · **Settle by:** P2 (offline), P3 (recovery promise)

**Approach.**
- The PWA **caches the employee's published schedule** for viewing offline.
- Publishing **emails each employee their schedule** and updates their **iCal feed**, so the schedule always exists somewhere other than the box.
- **Recovery promise (proposed):** RPO ≤ 24 h (nightly backup), RTO ≤ 1 business day on replacement hardware. Rehearse it before the pilot.
- Recommend a UPS for on-prem installs.

## DQ-10 Pay stubs and accounting integrations
**Status:** Open · **Settle by:** P5

**Problem.** Payroll APIs vary a lot. Some of the listed accounting tools have limited or no US payroll API. Many small businesses actually run payroll in **Gusto, Square, ADP or Paychex**.

**Approach.**
- **Ask pilot customers what they use** before building any integration.
- Payroll CSV export with configurable columns covers everyone in the meantime.
- **Pay stubs:** HR uploads the PDF each pay period (fallback); pull from provider APIs only where supported.

## DQ-11 License behavior when maintenance lapses
**Status:** Decided ([#017](09-decisions.md#017--perpetual-license-no-kill-switch)) · **Settle by:** P7 (before the first sale)

**Approach.** The license is **perpetual**: the software keeps working when maintenance lapses; updates and support stop. **No kill switch.** License checks only gate tier features, and a missing or invalid license falls back to Basic, never to locked out. Security fixes may still be offered to lapsed customers at your discretion.

## DQ-12 Time clock rules beyond punching in
**Status:** Proposed · **Settle by:** P5

**Approach.** **Punch policies** for each location:
- **Rounding** (off by default; neutral rounding only, since rounding is generally legal only if it doesn't systematically underpay)
- How early before a shift someone may clock in
- Missed-punch fixes, with manager approval and the reason recorded
- **Meal and rest break** rules with alerts (jurisdiction presets)
- **Preventing employees from punching in for each other** without biometrics: kiosk photo capture (no face recognition, since that counts as biometrics), geofencing, a check that the device is on the shop network

## DQ-13 Coverage needs must be data, not just shifts
**Status:** Decided ([#021](09-decisions.md#021--staffing-requirements-are-first-class)) · **Settle by:** P2

**Problem.** Shift templates describe slots, but the solver (and the manager) need to know **what coverage is needed**: "2 cashiers 9–12, at least one keyholder whenever the store is open, a trainee must work alongside a trainer."

**Approach.**
- **Staffing requirements:** per location/position, time window, min/max headcount, required skills.
- **Shift composition rules:** "≥1 person with skill X on every shift," "role A requires role B on the same shift" (trainee/trainer), "never more than N trainees."
- The rules engine checks both during manual scheduling; the solver uses the same definitions in P6.

## DQ-14 Explaining auto-generated schedules
**Status:** Proposed · **Settle by:** P6

Managers won't trust a black box.
- For **unfilled slots**, report the binding causes (e.g. "no available employee with skill Keyholder 6–10pm on Sat; 2 employees blocked by hour caps"). The solver can find these using assumption literals in CP-SAT.
- For **assignments**, show the top factors (availability preference, fairness, desired hours).

## DQ-15 Auto-scheduler goals: balance, locks, preferences
**Status:** Decided ([#025](09-decisions.md#025--auto-scheduler-tiered-objective-with-locks-and-soft-preferences), [#026](09-decisions.md#026--hour-balancing-and-lock-rules), [#027](09-decisions.md#027--first-preference-types-and-fallback-target)) · **Settle by:** P2 (data), P6 (tuning)

**Requirements.** Map available employees and their constraints onto the needed schedule; **balance hours** among employees; keep **locked shifts** (employees with fixed schedules); try to honor **schedule preferences** as a soft constraint.

**Approach.** Tiered objective (coverage → overtime → balance → preferences → stability); locks are fixed inputs; preferences are always soft. See [05 — Auto-scheduler](05-architecture.md#auto-scheduler-p6).

**Why this matters before P2:** fixed schedules, pins and preferences must be **captured in P1–P2** (recurring assignments with a lock flag, pinned assignments, a preferences table) so the solver has data to work with in P6.

**Decided**
- [x] **Balance toward desired hours.** Each employee's target is their own desired hours (capped by their rules), not equal hours for everyone.
- [x] **Carry-over over a rolling 4 weeks.** An employee who was short (or over) in the last 4 weeks gets a higher (or lower) target this period.
- [x] **Fixed-schedule employees aren't pushed toward a target.** Their locked hours count toward totals and coverage, but there's no balancing penalty for them. They only get extra shifts when coverage can't be met otherwise.
- [x] **The solver can never break a locked shift.** If a gap can't be covered without moving a lock, the slot is reported as unfilled for the manager to resolve.

- [x] **First preference types:** preferred days/times, preferred positions, avoid closing, max days/week. More types are added later based on pilot feedback.
- [x] **Fallback target when desired hours aren't set:** a fair share of the remaining pool demand. The employee is prompted to set desired hours, and the run report flags everyone who used the fallback.

---

## Deliberately not building

| Item | Why |
|---|---|
| Built-in chat | Big moderation and support burden; group chats already work. Announcements and shift notes cover the need |
| Payroll calculation | Legal and accuracy burden ([#009](09-decisions.md#009--dont-calculate-payroll)) |
| Windows hosts | Fragile; support load ([06](06-operations.md#support-matrix)) |
| Face recognition at kiosks | Counts as biometrics; see [#010](09-decisions.md#010--biometrics-deferred-pending-legal-review) |
