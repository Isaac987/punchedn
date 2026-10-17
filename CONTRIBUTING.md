# Contributing to PunchedN

PunchedN is built by one maintainer and isn't accepting outside code contributions yet. This guide is the working agreement for everyone who does commit, including AI assistants, so the history stays consistent and the release tooling works.

The background behind these rules is in [07 — Engineering Standards](docs/07-engineering-standards.md) and [11 — Conventions](docs/11-conventions.md).

## Contents

- [Set up your clone](#set-up-your-clone)
- [Workflow](#workflow)
- [Branches](#branches)
- [Commit messages](#commit-messages)
- [Pull requests](#pull-requests)
- [Issues](#issues)
- [Code style](#code-style)
- [Dependencies and versions](#dependencies-and-versions)
- [Documentation](#documentation)
- [Versioning and releases](#versioning-and-releases)

## Set up your clone

```bash
# Git hooks: formatting, secret scanning, commit message check
uv tool install pre-commit
pre-commit install

# Commit message template (shows the format in your editor)
git config commit.template .gitmessage
```

The hooks run on every commit. To check the whole repo at once, run `pre-commit run --all-files`.

Common tasks run through [just](https://just.systems/). Install it, then run `just` to list the recipes:

```bash
uv tool install rust-just
```

Language tooling (uv for Python, pnpm for the frontend) arrives with [Phase 0](docs/08-phase-0-plan.md). This section will be updated then.

## Workflow

PunchedN uses **trunk-based development**:

1. Pick or open an issue. One issue is one reviewable PR.
2. Branch from an up-to-date `main`.
3. Commit in small, logical steps.
4. Open a PR, let CI pass, and review your own diff.
5. **Squash-merge** into `main`. The PR title becomes the commit on `main`.
6. Delete the branch.

Nobody commits directly to `main`. The `no-commit-to-branch` hook blocks it locally, and branch protection blocks it on GitHub.

## Branches

```
<type>/<short-description>
```

| Prefix | Use for |
|---|---|
| `feat/` | New capability |
| `fix/` | Bug fix |
| `chore/` | Tooling, CI, dependencies, maintenance |
| `docs/` | Documentation only |
| `refactor/` | Code changes that don't change behavior |
| `spike/` | Throwaway experiment. **Never merged**; delete it after the write-up is posted |

Use lowercase words joined by hyphens, and add the issue number when there is one: `feat/12-timecalc-module`, `fix/31-dst-hour-total`.

To create a branch for an issue, use the GitHub CLI. It creates the branch, links it to the issue, and checks it out:

```bash
gh issue develop 12 --name feat/12-timecalc-module --base main --checkout
```

GitHub's "Create a branch" button on an issue suggests a name like `12-add-timecalc-module`, which doesn't follow this format. If you use the button, rename the branch in the dialog before you create it.

## Commit messages

Commits follow [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/). A `commit-msg` hook rejects anything else, and release-please builds version numbers and the changelog from these messages.

```
<type>(<scope>): <summary>

<body>

<footer>
```

### Type (required)

| Type | Use for | Shown in changelog |
|---|---|---|
| `feat` | A new capability for users or for the ops tooling | ✔ Features |
| `fix` | A bug fix | ✔ Bug fixes |
| `perf` | A performance improvement | ✔ |
| `revert` | Reverting an earlier commit | ✔ |
| `refactor` | A code change that doesn't fix a bug or add a feature | |
| `test` | Adding or fixing tests only | |
| `docs` | Documentation only | |
| `build` | Build system, Dockerfile, dependencies | |
| `ci` | GitHub Actions and other CI config | |
| `chore` | Anything else that doesn't touch production code | |
| `style` | Formatting only, no change in meaning | |

### Scope (optional)

Use a scope when it helps someone scanning the log. Scopes match the `area:*` labels:

`backend` · `frontend` · `rules` · `auth` · `ops` · `ci` · `docs` · `deps`

### Summary (required)

- **Imperative mood**, as if finishing the sentence "This commit will…": `add`, not `added` or `adds`
- Lowercase first letter, no period at the end
- The whole header is **72 characters or fewer**
- Say what changed, not which files were touched

### Body (optional)

Separate it from the header with a blank line and wrap at 72 characters. Explain **what and why**, not how. The diff already shows how. Include it whenever the reason isn't obvious from the summary.

### Footer (optional)

One trailer per line, after a blank line:

| Trailer | When |
|---|---|
| `Closes #12` | The commit or PR finishes an issue (only works for PRs merged into `main`) |
| `Refs #12` | Related to an issue without closing it |
| `Refs: docs/09-decisions.md #028` | Implements or changes a recorded decision |
| `BREAKING CHANGE: <description>` | Anything that breaks an existing install, API or config. You can also add `!` after the type: `feat(api)!: …` |
| `Co-Authored-By: Name <email>` | Someone else (or an AI assistant) helped write the change |

### Examples

```
feat(rules): add school-week hour cap for minors
```

```
fix(backend): count DST fall-back night as nine hours

Hour totals subtracted local wall-clock times, so a 10pm–6am shift on
the fall-back night came out as 8 hours instead of 9. Totals now go
through core/timecalc.py, which uses elapsed UTC time.

Closes #31
```

```
feat(ops)!: move install directory to /opt/punchedn

BREAKING CHANGE: existing installs must run `punchedn migrate-install`
before updating to this version.
```

```
docs: record decision to use built-in authentication

Refs: docs/09-decisions.md #028
```

**Avoid:** `update stuff`, `fix bug`, `WIP`, `Added new feature.`, `feat: Add Login Page`.

### Commits made with AI help

Commits written with Claude's help end with a co-author trailer:

```
Co-Authored-By: Claude <noreply@anthropic.com>
```

The maintainer reviews every AI-assisted change before it is merged. [CLAUDE.md](CLAUDE.md) gives Claude Code these same rules.

## Pull requests

- **The title must be a valid Conventional Commit header**, because it becomes the squashed commit on `main`. A CI check enforces this.
- Fill in the [PR template](.github/pull_request_template.md): what changed, why, and how it was tested.
- Keep PRs small: one issue, one concern. Split anything that touches unrelated areas.
- Build features as **vertical slices** (migration, model, service, API, generated client, screen and tests together) so every merge leaves something that works.
- CI must be green before merging. Review your own diff before you merge, even when working solo.
- `Closes #N` only closes the issue when the PR is merged into `main`. For stacked PRs that target another branch, close the issue by hand after the stack lands.

## Issues

Use the issue forms on GitHub. Each task issue has the same sections (**Goal**, **Tasks**, **Done when**, **Depends on**, **Refs**) and a title prefix that matches the commit types (`feat:`, `fix:`, `chore:`, `docs:`, `spike:`). Labels are described in [11 — Conventions](docs/11-conventions.md#labels).

## Code style

Formatting is automated. Don't argue with the formatter, and don't hand-format.

| Area | Standard | Enforced by |
|---|---|---|
| All files | UTF-8, LF line endings, final newline, no trailing whitespace | `.editorconfig`, `.gitattributes`, pre-commit |
| Python | [PEP 8](https://peps.python.org/pep-0008/) via ruff, 100-character lines, type hints everywhere, [Google-style docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) | ruff, ruff format, pyright (strict on `core/` and `rules/`) |
| TypeScript | `strict: true`, no `any` without a comment | ESLint, Prettier, `tsc --noEmit` |
| SQL / migrations | Lowercase `snake_case` names, plural table names, one Alembic migration per schema change | Review |
| API | `/api/v1` prefix, plural nouns, `snake_case` JSON fields, [RFC 9457](https://www.rfc-editor.org/rfc/rfc9457) error responses | Review, generated client check in CI |
| Secrets | Never committed. Use `.env` (ignored) and document new variables in `deploy/.env.example` | gitleaks |

Naming:

| Thing | Convention | Example |
|---|---|---|
| Python modules, functions, variables | `snake_case` | `split_at_week_boundary()` |
| Python classes | `PascalCase` | `ScheduleContext` |
| Constants | `UPPER_SNAKE_CASE` | `MAX_SOLVER_SECONDS` |
| React components and their files | `PascalCase` | `ScheduleGrid.tsx` |
| Hooks | `use` + `camelCase` | `useSchedulePeriod` |
| Other TypeScript files | `kebab-case` | `format-hours.ts` |
| Permissions | `resource.action`, dotted lowercase | `schedule.publish` |
| Environment variables | `UPPER_SNAKE_CASE` | `SOLVER_TIME_LIMIT_SECONDS` |

Project-specific rules (time handling, restricted fields, translations, money) are in [07 — Engineering Standards](docs/07-engineering-standards.md#code-conventions).

## Dependencies and versions

- Use the **latest stable release** of every language, runtime, framework and tool. No alpha, beta or RC versions. Node.js uses the newest LTS line. See [decision #029](docs/09-decisions.md#029--use-the-latest-stable-versions).
- Before adding a dependency, check its current version on PyPI or npm. Don't copy a version number from an old example or from memory.
- Pin exact versions through the lockfiles (`uv.lock`, `pnpm-lock.yaml`) and pin Docker images by version tag, never `latest`.
- Renovate opens update PRs. Use `chore(deps):` for tooling and `fix(deps):` for runtime dependencies. Major upgrades get a manual review and update the [versions table](docs/02-tech-stack.md#versions) in the same PR.

## Documentation

- Update the docs in the **same PR** as the change they describe.
- A change to a recorded decision gets a **new** entry in the [Decision Log](docs/09-decisions.md). Old entries are never rewritten.
- Write in plain, direct language. Prefer tables and short bullets over long paragraphs.
- Use relative links (`[DQ-2](10-design-questions.md#…)`) so they work on GitHub and in Obsidian.

## Versioning and releases

- [Semantic Versioning](https://semver.org/): `0.x` until the first paying customer, `1.0.0` at commercial launch.
- release-please opens a release PR from the commits on `main`. Merging it tags the version, updates `CHANGELOG.md`, and triggers the image build.
- `CHANGELOG.md` is generated from commit messages: `feat`, `fix`, `perf` and `revert` commits appear under their own headings, and other types are left out. The commit messages are the changelog, so write them for a reader.
- Never edit `CHANGELOG.md` by hand; release-please overwrites it. Write a better commit message instead.
