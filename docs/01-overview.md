# 01 — Product Overview

## Problem

Small businesses that hire many students or volunteers (cafés, campus shops, nonprofits, recreation centers, small retail) see shifts change often and unpredictably. Large companies pay for tools like When I Work or Deel. Many small businesses still schedule by hand on paper, in spreadsheets or in group chats.

## Product

**PunchedN** is an employee scheduling and time-tracking system that:

- lets managers build schedules quickly, with the system catching conflicts and rule breaks (overlaps, hour caps, missing skills, people who shouldn't work together)
- lets employees see their schedule, request time off, call in sick and swap shifts from their phone
- later, **generates schedules automatically** using Google OR-Tools
- keeps the business's data on infrastructure the business controls

## Users

| Role | Main goals |
|---|---|
| **Admin** (often the owner) | Configure the system: branding, permissions, user groups, integrations, time clock devices, global policies |
| **Manager** | Build and publish schedules; handle sick calls, time off and swaps; see patterns |
| **HR** | Hire and remove employees; manage pay rates and employment records (kept separate from managers) |
| **Employee** | See schedule and coworkers; manage availability; request time off; call in sick; swap or pick up shifts; see PTO, pay rate and pay stubs |

The permission system must be flexible enough to support **separation of duties**. Admin/Manager/HR/Employee are presets, not hard-coded roles.

## Deployment model

- **Single-tenant:** one installation per business. No shared multi-customer database.
- **Two hosting options, one software bundle:**
  1. **On-prem:** runs on the customer's own hardware (which varies).
  2. **Cloud:** runs on a cloud server in the **customer's own cloud account**, which the customer pays for.
- The **maintainer installs, configures and maintains** every deployment, remotely after the initial setup.

## Business model (proposed)

| Item | On-prem | Cloud |
|---|---|---|
| Setup fee | ✔ (optionally includes hardware) | ✔ |
| Software license | One-time, tiered (Basic / Advanced) | Same |
| **Annual maintenance plan** | Updates, backup monitoring, remote support | Same |
| Infrastructure cost | Customer's hardware | Customer pays cloud provider directly |

> **Why a maintenance plan:** with a one-time price only, every new customer adds permanent support work but no ongoing income. On-prem software usually charges an annual maintenance fee for this reason. Decide before the first sale.

**License behavior:** perpetual. If maintenance lapses, the software keeps working; updates and support stop. No kill switch ([#017](09-decisions.md#017--perpetual-license-no-kill-switch)).
**Support policy:** the latest two minor versions are supported.
**Before the first install:** LLC, a support agreement + data processing agreement, and cyber/E&O insurance ([DQ-8](10-design-questions.md#dq-8-maintainer-access-is-the-biggest-security-risk)).

**Tiers** (from the idea doc): *Basic* limits the management tools; *Advanced* includes the full suite. Exact split TBD (see [03](03-features.md#tier-split-draft)).

## Competitors

When I Work, Deel, Productive. Our differences:
- data stays on hardware or cloud accounts the customer owns
- a perpetual license, pricing aimed at small businesses
- **built-in rules for student/minor hour limits** that follow age and school calendars
- **volunteer service-hour tracking and certificates**
- a fairness dashboard and explainable auto-scheduling (later)
- Spanish-language support for staff

## Product name

**PunchedN.** The domain has been purchased for one year (renew before it lapses).

## Constraints

- Built and maintained by **one person**. Prefer fewer moving parts and boring technology.
- Must run on modest, varied hardware (see [06 — Operations](06-operations.md#support-matrix)).
- Handles sensitive data: pay rates, doctor's notes, and possibly biometrics. See the legal flags in [03](03-features.md#legal--compliance-flags).

## Open questions

- [ ] Who is the first pilot business?
- [ ] Price points for the license, setup fee and maintenance plan
- [ ] Exactly which features go in the Basic vs. Advanced tiers
- [ ] Source license: proprietary EULA (expected) vs. open-core
- [ ] Which state's or country's labor rules to build in first
- [ ] Which payroll/accounting tools the pilot customers use ([DQ-10](10-design-questions.md#dq-10-pay-stubs-and-accounting-integrations))
- [ ] How daily-overtime states treat shifts that cross midnight ([DQ-2](10-design-questions.md#dq-2--time-zones-overnight-shifts-and-daylight-saving))
- [ ] Who pays per-message SMS costs, if SMS is offered
- [ ] Legal entity, insurance and contract templates (support agreement, DPA, EULA)

See [10 — Design Questions](10-design-questions.md) for the full list of hard problems and their status.
