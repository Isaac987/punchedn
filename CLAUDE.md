# CLAUDE.md

Guidance for Claude Code in this repository.

## Project

PunchedN: self-hosted employee scheduling for small businesses with student, volunteer and part-time staff. **Status: planning.** Application code starts with Phase 0.

- Planning docs: `docs/` (start at `docs/README.md`). They are the source of truth for scope, architecture and decisions.
- Current phase checklist: `docs/08-phase-0-plan.md`.

## Conventions (follow exactly)

All rules are in `CONTRIBUTING.md`. The ones that matter most:

- **Never commit to `main`.** Branch first: `<type>/<issue#>-<short-description>`.
- **Commit messages:** Conventional Commits. `type(scope): summary` in imperative mood, lowercase, no period, header ≤ 72 characters. Allowed types: `feat fix perf refactor test docs build ci chore revert style`. Scopes: `backend frontend rules auth ops ci docs deps`. Body explains why, wrapped at 72.
- End every commit with `Co-Authored-By: Claude <noreply@anthropic.com>` (or the exact trailer the session specifies).
- **PR titles** are Conventional Commit headers (they become the squash commit). Fill in `.github/pull_request_template.md`.
- `Closes #N` only works for PRs merged into `main`.
- Commit in small, logical steps on feature branches.
- Don't bypass hooks (`--no-verify`) unless the user asks.
- **Versions:** always the latest stable release (decision #029). Your training data may be out of date, so look up the current version (PyPI, npm, endoflife.date, Docker Hub) before writing any version number. Current targets are in `docs/02-tech-stack.md#versions`.

## Docs

- Update docs in the same change as the code they describe.
- Decisions in `docs/09-decisions.md` are append-only: add a new numbered record, mark the old one superseded. Never rewrite old records.
- Follow the ID and marker conventions in `docs/11-conventions.md` (P0–P8, M1–M14, DQ-N, #NNN).
- Plain, direct language; tables and short bullets; relative links.

## Ask before

- Changing a recorded decision or the roadmap's phase scope
- Adding a new service, dependency category or external integration
- Anything outward-facing: pushing, opening or merging PRs, creating releases, editing GitHub settings
