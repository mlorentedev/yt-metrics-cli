# yt-metrics-cli

> Instructions for AI coding agents (Claude Code, Copilot, Cursor, Codex) operating in this repo.
>
> **This file is the agent SSOT for yt-metrics-cli.** The behavioural SSOT — Identity, Standing
> Orders, Decision Hierarchy, Knowledge Placement, Model Selection, the Neural Hive protocol —
> is the canonical dotfiles `AGENTS.md`; read that first. Everything below is what is specific
> to this repository. `.claude/CLAUDE.md` is a thin pointer to this file and carries only
> Claude Code-specific notes.

## What this is

CLI that analyzes YouTube channels and bulk-downloads video transcripts, computing engagement
metrics and emitting structured reports (CSV, text summaries, URL lists). It exists for the case
YouTube Studio does not cover: comparing *someone else's* channels.

Published to PyPI as `yt-metrics-cli` (console script `yt-metrics`). The Starlight documentation
site lives in `site/` and deploys to GitHub Pages; `docs/` is docs-as-code, not the published site.

## Architecture

| Layer | Module | Responsibility |
|---|---|---|
| CLI | `src/main.py` | Typer app — `channels` and `transcript` commands, exit codes, `--help` text |
| Config | `src/config.py` | pydantic-settings — env vars and `.env` |
| Core | `src/analyzer.py` | YouTube Data API v3 wrapper: channel resolution, batched video stats, exponential backoff on 403/429 |
| Metrics | `src/metrics.py` | Pure engagement math (view/like/comment rate, engagement rate, viral detection); no I/O |
| Transcript | `src/transcript.py` | 3-level fallback chain and video-ID validation |
| Export | `src/exporters/` | Report generators — `csv`, `text`, `readme` (index), `url` |

Two invariants worth knowing before editing:

1. **`src/metrics.py` stays pure.** All computation lives there so it can be table-tested without
   network or filesystem. I/O belongs in `analyzer`/`exporters`.
2. **Video ids reach the filesystem.** The validation regex in `src/transcript.py` is the contract
   that keeps them from becoming paths (lesson-003). A new code path that builds a path from a
   video id without going through that validation is a security finding, not a style nit.

## Technical standards

| Requirement | Tool |
|---|---|
| Python | 3.12+ (CI runs 3.12 and 3.13) |
| Type hints | `mypy --strict` (see `[tool.mypy]` in `pyproject.toml`) |
| Dependencies | `uv` (`pyproject.toml` + `uv.lock`; never edit the lock by hand) |
| Lint/format | `ruff` (`select = E,F,I,N,UP,B,A,SIM,TCH`, line length 100) |
| Tests | `pytest` + `pytest-cov`, table-driven where possible |
| CLI | Typer + Rich |
| Config | pydantic-settings |
| Build | hatchling |

## Commands

All development commands go through the Makefile:

```bash
make install    # uv venv + editable install with dev extras
make lint       # ruff
make typecheck  # mypy --strict
make test       # pytest with coverage
make check      # lint + typecheck + test  ← run before every PR
make build      # check + uv build
make site       # build the Starlight docs site (npm ci + build, needs Node)
```

`make check` is the same gate CI runs. As of 2026-09-22 the suite is 77 tests at 83% line
coverage (720 statements); treat the CI run as authoritative over any number written here.

## Key paths

| Path | Role |
|---|---|
| `src/main.py` | CLI entry point (Typer app) |
| `src/config.py` | Configuration via pydantic-settings |
| `src/analyzer.py` | YouTube API wrapper with retry/backoff |
| `src/metrics.py` | Pure engagement metric calculations |
| `src/transcript.py` | Transcript downloader with fallback chain + id validation |
| `src/exporters/` | Report generators (csv, text, readme, url) |
| `tests/` | pytest suite (one module per source module) |
| `scripts/check-lessons.sh` | Lesson numbering + index guard (CI and pre-commit) |
| `scripts/check-actions-pinned.sh` | Every `uses:` pinned to a commit SHA (CI and pre-commit) |
| `docs/lessons/` | One file per lesson + `docs/lessons/_index.md`; `docs/lessons.md` is a pointer stub |
| `specs/` | Per-feature SDD folders, created on demand by `dotf spec init` |
| `site/` | Astro Starlight docs site (published to GitHub Pages) |
| `.github/workflows/ci.yml` | lint, mypy, pytest+cov, `uv build` on 3.12 and 3.13 |
| `.github/workflows/repo-hygiene.yml` | lesson + action-pinning guards |
| `.pr_agent.toml` | PR-Agent (the `review` job) config and reviewer instructions |
| `harness/` | Review gates read by `dotf`: `review-attestation.json` (which output attests a review, the `## Review triage` heading) and `reviewer-pool.json` (models allowed to sign an adversarial review) |

## Knowledge placement

- Build/operate knowledge belongs **here**, in the repo: gotchas as `docs/lessons/lesson-NNN-*.md`
  (indexed in `docs/lessons/_index.md`, guarded by `scripts/check-lessons.sh`), decisions in
  `docs/adr/`, feature specs in `specs/<feature-id>/`. The vault holds no task state for this repo.
- Cross-project insight goes to the maintainer's store; session memory never lives in this repo
  (GUARD-001).
- A claim repeated in `README.md`, `AGENTS.md`, `site/src/content/docs/` and the CLI `--help`
  text drifts the moment one of them is edited. When you change a documented behaviour, grep for
  the other copies in the same PR.

## Review gates

`.github/workflows/pr-agent.yml` runs PR-Agent and then **fails closed** if it published no review.
Two things to know when reading that check:

- `harness/review-attestation.json` declares which reviewer output *attests* a review, which
  markers are *declines* (advisory, so they leave the item pending), and the `## Review triage`
  heading the triage dispositions are recorded under. Record the disposition even when there was
  nothing to dispose of.
- The `[ignore] glob` in `.pr_agent.toml` excludes **both lockfiles**. A Dependabot PR is therefore
  unreviewable by construction, and a human-driven rebase of one turns the `review` job red with a
  message that blames NaN concurrency — a wrong diagnosis. Declare such a merge with the
  `merged-unreviewed` label plus a `## Unreviewed merge rationale` section instead of reading the
  red check as a finding (lesson-011).

## Spec-Driven Development

This repo follows the **Spec-Driven Development per feature** pattern: non-trivial changes are specified before they are implemented.

When the user asks to **create, fill, or archive a spec**, follow this workflow. The `dotf` CLI (installed via dotfiles, on PATH) is the canonical, self-contained interface — run `dotf spec --help` for the full surface.

| Trigger phrase | Action |
|---|---|
| "create a spec for X", "scaffold spec X", "start working on X" | `dotf spec init <feature-id> --issue <N>` |
| "fill in the proposal for X", "help me write the proposal" | edit `specs/<feature-id>/proposal.md` — the Why + acceptance criteria — before writing implementation code |
| "archive spec X", "close spec X" | `dotf spec archive <feature-id> --pr <url>` |

Per-feature specs live at `specs/<feature-id>/` in this repo; archived at `specs/archive/<feature-id>/` (never deleted — audit trail).

**Skip SDD for**: typo fixes, comment-only edits, mechanical refactors, bug fixes <20 lines with obvious cause, doc-only changes.

`<feature-id>` format: `^([A-Z]+[0-9]*-[0-9]+[a-z]?(-[a-z0-9-]+)?|[0-9]{4}-[0-9]{2}-[0-9]{2}-[a-z0-9-]+)$` (e.g., `AI-001-ollama-public`, `ADR028-004`, `SDD-012b-guard`, `2026-05-13-cleanup`). This string is `idPattern` in dotfiles `cli/internal/spec/spec.go` verbatim; a drift test asserts every copy matches, so do not reword it.
