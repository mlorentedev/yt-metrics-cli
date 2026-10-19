.PHONY: help install lint lock typecheck test check build clean run site site-dev site-preview
.DEFAULT_GOAL := help

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

install: ## Create venv and install deps
	uv venv && uv pip install -e ".[dev]"

lint: ## Run ruff linter
	uv run ruff check src/ tests/

# Same check CI runs (ci.yml, "Lockfile matches pyproject"): the lock must agree with
# pyproject.toml, so a version bump that skipped `uv lock` fails locally first instead of
# on the 3.12 leg after a push. BUG-001 (#81), lesson-013.
#
# IT MUST STAY FIRST IN `check`. Every `uv run` below synchronises the project first and
# rewrites uv.lock when it is stale, so `lint` would repair the drift and hand `lock` an
# already-synced file: a green `make check` over an uncommitted lock diff -- the exact
# symptom this target exists to prevent (PR-Agent on #102, measured in #81).
lock: ## Fail if uv.lock is out of sync with pyproject.toml
	uv lock --check

typecheck: ## Run mypy --strict
	uv run mypy src/

test: ## Run tests with coverage
	uv run pytest tests/ -v --cov=src --cov-report=term-missing

check: lock lint typecheck test ## Lock + lint + typecheck + test

build: check ## Check + build package
	uv build

clean: ## Remove build artifacts
	rm -rf dist/ .venv/ *.egg-info/ .ruff_cache/ .mypy_cache/ .pytest_cache/ htmlcov/ .coverage coverage.xml site/dist/ site/node_modules/

run: ## Run channel analysis (requires .env)
	uv run yt-metrics channels

site: ## Build documentation site (requires Node.js)
	cd site && npm ci && npm run build

site-dev: ## Start documentation dev server
	cd site && npm run dev

site-preview: ## Preview documentation production build
	cd site && npm run preview
