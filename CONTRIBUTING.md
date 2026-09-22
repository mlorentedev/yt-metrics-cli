# Contributing

## Setup

```bash
git clone https://github.com/mlorentedev/yt-metrics-cli.git
cd yt-metrics-cli
make install
```

## Development

```bash
make check    # lint + typecheck + test (run before every PR)
make lint     # ruff only
make typecheck # mypy --strict only
make test     # pytest only
make build    # full build (runs check first)
make run      # run channel analysis
make site     # build documentation site
make site-dev # start docs dev server
```

## Pre-commit hooks

`.pre-commit-config.yaml` runs gitleaks (never commit a credential), ruff lint, `mypy --strict`
and the two file-hygiene fixers (trailing whitespace, missing final newline) — the middle two
through `uv run`, so they are the same commands CI runs.

There is usually nothing to install. This machine dispatches git hooks machine-wide
(`core.hooksPath`, GUARD-001), and that dispatcher chains any repo-local
`.pre-commit-config.yaml` — so the hooks fire on `git commit` without `pre-commit install`.
On a machine without the dispatcher, run `pre-commit install` once per clone.

Bypass a hook only with explicit approval, and never for `gitleaks`:

```bash
SKIP=ruff-check git commit ...
```

## Pull Requests

1. Create a feature branch from `master`
2. Follow [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `docs:`, etc.)
3. Run `make check` — all gates must pass
4. Open a PR against `master`
5. CI runs automatically (Python 3.12 + 3.13)
6. Squash merge after CI passes

## Code Standards

- Python 3.12+, type hints everywhere (`mypy --strict`)
- Formatting: Ruff
- Tests: pytest, TDD preferred (write test first)
- Functions < 40 lines, nesting < 4 levels

## Release Process

Automated via [release-please](https://github.com/googleapis/release-please). Merging to `master` with conventional commits triggers:

1. Release PR with changelog (auto-created)
2. Merge Release PR → GitHub Release + PyPI publish (trusted publishing)
