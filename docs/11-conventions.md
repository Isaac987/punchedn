# 11 — Conventions

A reference for the IDs, markers, labels and terms used across these docs and the GitHub repo. The working process itself (how tasks are tracked, prioritized and reviewed) is in [07 — Engineering Standards](07-engineering-standards.md#how-we-work).

---

## IDs and cross-references

| ID | Means | Defined in | Example |
|---|---|---|---|
| **P0–P8** | Roadmap phase. Each is one GitHub milestone | [04](04-roadmap.md) | P2 — Manual scheduling |
| **M1–M12** | Feature module (a group of related features) | [03](03-features.md) | M5 — scheduling |
| **DQ-N** | Design question: a hard problem and its chosen approach | [10](10-design-questions.md) | DQ-2 (time zones, DST) |
| **#NNN** (three digits) | Decision record | [09](09-decisions.md) | #028 (built-in auth) |
| **#N** (on GitHub) | GitHub issue or PR | [repo](https://github.com/Isaac987/punchedn/issues) | #14 (timecalc spike) |
| **NN —** | Doc number; files are read in this order | [README](README.md) | `05-architecture.md` |

> **#NNN vs #N:** in these docs, a three-digit `#028` always means a decision. In GitHub issues and PRs, `#28` means issue 28. When an issue refers to a decision, write it as `docs/09-decisions.md #028`.

Link to sections with relative Markdown links (`[DQ-2](10-design-questions.md#dq-2--time-zones-overnight-shifts-and-daylight-saving)`) so they work on GitHub and in Obsidian.

## Markers in the docs

| Marker | Means |
|---|---|
| ⚠ | Shapes the data model. Settle it early (by P1–P2); changing it after the pilot means painful migrations. On GitHub this is the `data-model` label |
| 🆕 | A feature added after the original idea doc (`PunchedN.pdf`) |
| ⭐ | The phase or feature that is the product's core (P2 manual scheduling) |
| **S / M / L / XL** | Relative effort for a phase. Not tied to dates |
| `- [ ]` / `- [x]` | A task checklist item, open / done |

## Status values

**Design questions** ([10](10-design-questions.md)):
- **Open:** no direction chosen yet.
- **Proposed:** direction chosen, details still open.
- **Decided:** recorded as a decision in [09](09-decisions.md).

Each DQ also has **Settle by: P*N***, the phase by which it must be Decided.

**Decisions** ([09](09-decisions.md)):
- **Accepted:** in effect.
- **Superseded by #NNN:** replaced by a later decision. The old record stays as it is.

## Writing a decision record

Decisions are **append-only**: add new ones at the bottom with the next number, and never rewrite an old one. To change a decision, add a new record and mark the old one *Superseded by #NNN*.

```markdown
### 029 — Short title stating the decision
*YYYY-MM-DD · Accepted* · [DQ-N](10-design-questions.md#...)   ← link only if it settles a DQ
- **Context:** the situation and constraints that forced a choice.
- **Decision:** what we chose (bullets if several parts).
- **Consequences:** what this costs, what it enables, and when to revisit.
```

## GitHub

### Milestones

One milestone per phase, titled `P<N> — <Name>`. The milestone description is that phase's **exit criteria**, copied from [04](04-roadmap.md). A milestone is done when every exit criterion is met, not when every issue is closed.

### Issues

**Size:** one issue = one reviewable PR. If it needs more than one PR, or touches unrelated areas, split it.

**Title:** starts with a type prefix that matches Conventional Commits, then a short lowercase description.

| Prefix | Use for |
|---|---|
| `feat:` | New capability for users or the ops tooling |
| `fix:` | Bug fix |
| `chore:` | Setup, tooling, CI, maintenance, non-code tasks |
| `docs:` | Documentation or runbooks only |
| `spike:` | A spike (see below) |

**Body:** every issue uses the same sections.

```markdown
## Goal
One or two sentences: why this exists.

## Tasks
- [ ] Concrete step
- [ ] Concrete step

## Done when
- Observable check that proves it works (a test, a command, a page)

## Depends on
#7, #12          ← omit if none

## Refs
- docs/08-phase-0-plan.md §0.2
- docs/09-decisions.md #028
```

### Labels

Every issue gets one `type:*`, one `priority:*` and at least one `area:*` label.

| Label | Means |
|---|---|
| `type:feat` | New capability |
| `type:chore` | Setup, tooling, maintenance, non-code work |
| `type:spike` | Throwaway experiment that answers one question |
| `priority:must` | Needed for the milestone's exit criteria, or a `data-model` item |
| `priority:should` | Makes a real demo convincing |
| `priority:could` | Below the cut line; may move to a later milestone |
| `data-model` | Shapes the data model; do these first in a milestone (the ⚠ marker in docs) |
| `area:backend` | FastAPI, services, database |
| `area:frontend` | React SPA |
| `area:ops` | Install, update, backup, hosts |
| `area:ci` | GitHub Actions, releases |
| `area:auth` | Authentication and permissions |
| `area:rules` | Rules engine and `core/timecalc.py` |
| `area:docs` | Documentation and runbooks |
| `area:business` | Non-code work: pilot, legal, accounts |

### Board

GitHub Projects with four columns: **Backlog** (sorted by priority) → **Next** (max 5) → **Doing** (max 2) → **Done**. Limits on Next and Doing keep focus; finish something before starting something new.

### Branches, commits and versions

The full rules, with examples, are in [CONTRIBUTING.md](../CONTRIBUTING.md). In short:

- Branches: `<type>/<issue#>-<short-name>` (`feat/`, `fix/`, `chore/`, `docs/`, `refactor/`, `spike/`). Short-lived; squash-merged into `main`.
- Spike branches are **never merged**; delete them once the write-up is posted.
- Commits and PR titles follow **Conventional Commits**: `type(scope): summary`. Types: `feat`, `fix`, `perf`, `refactor`, `test`, `docs`, `build`, `ci`, `chore`, `revert`, `style`. Optional scopes match the `area:*` labels plus `deps`. A pre-commit hook checks commit messages and a CI check validates PR titles. release-please builds versions and the changelog from them.
- PRs that close an issue say `Closes #N` in the description (only works for PRs merged into `main`).
- Versions are semver: `0.x` until the first paying customer, `1.0.0` at commercial launch.

## Glossary

| Term | Meaning |
|---|---|
| **Exit criteria** | The checks that mark a phase/milestone as done. They define the scope; anything not needed for them is negotiable |
| **Walking skeleton** | The thinnest end-to-end version of the system that actually runs on a real host (P0 issues #1–#13): every layer exists, almost nothing is implemented |
| **Vertical slice** | One feature built through every layer at once (migration, model, service, API, client, screen, tests) in one PR, so each merge leaves something working. The opposite of building all models, then all endpoints, then all screens |
| **Spike** | A short, deliberately rough experiment on a throwaway branch that answers one question. Its output is a write-up and recommendation in the issue (and a decision in 09 if it settles one), not merged code |
| **Cut line** | The point in a milestone's priority-sorted list below which items are allowed to slip to a later milestone |
| **Definition of done** | For a milestone: its end-to-end Playwright test, written early from the exit criteria, passes. For an issue: its *Done when* checks pass and CI is green |
| **Pilot** | The first real business running PunchedN (end of P3). After the pilot, its top pain points outrank the roadmap order |
| **Preset** | A shipped default (a role, a jurisdiction's rule set) that admins clone and adjust, never a hard-coded behavior |
| **IdP** | Identity provider (Google Workspace, Microsoft 365, Keycloak…). PunchedN doesn't bundle one; it may sign in through a customer's IdP later ([#028](09-decisions.md#028--built-in-authentication-no-bundled-identity-provider)) |
| **RPO / RTO** | Recovery point / time objective: how much data can be lost (≤ 24 h) and how long recovery may take (≤ 1 business day) |
