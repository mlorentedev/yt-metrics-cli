# yt-metrics-cli

> CLI for YouTube channel analysis and transcript downloading.

## Architecture

- **CLI Layer:** `src/main.py` — Entry point with `channels` and `transcript` commands
- **Config:** `src/config.py` — pydantic-settings based configuration
- **Core:** `src/analyzer.py` — YouTube API wrapper (channel resolution, batch video stats, exponential backoff)
- **Metrics:** `src/metrics.py` — Pure engagement calculations (6 computed fields)
- **Transcript:** `src/transcript.py` — Transcript download with 3-level fallback and video ID validation
- **Export:** `src/exporters/` — Report generators package (CSV, TXT, README, URL)

## Technical Standards

| Requirement | Tool/Pattern |
|---|---|
| Python | 3.12+ |
| Type hints | mypy --strict |
| Dependencies | uv |
| Formatting | Ruff |
| Testing | pytest + pytest-cov |
| CLI | Typer + Rich |
| Config | pydantic-settings |
| Build | hatchling |

## Key Paths

| Path | Role |
|---|---|
| `src/main.py` | CLI entry point (Typer app) |
| `src/config.py` | Configuration via pydantic-settings |
| `src/analyzer.py` | YouTube API wrapper with retry logic |
| `src/metrics.py` | Engagement metric calculations |
| `src/transcript.py` | Transcript downloader with fallback chain |
| `src/exporters/` | Report generators (csv, text, readme, url) |
| `tests/` | pytest suite (77 tests, 83% coverage) |
| `site/` | Astro Starlight documentation |

## Verification Commands

All commands go through the Makefile:

```bash
make install    # Create venv + install deps
make lint       # Ruff linter
make typecheck  # mypy --strict
make test       # pytest with coverage
make check      # lint + typecheck + test
make build      # check + uv build
make run        # Run channel analysis
make clean      # Remove build artifacts
```
