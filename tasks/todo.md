# yt-metrics-cli — Backlog

> CLI for YouTube channel analysis and transcript downloading.

## P0 — High Priority

- [ ] **Add test suite**: Zero test coverage. Set up pytest + pytest-cov with unit tests for `metrics.py`, `analyzer.py`, and `exporters.py`. Mock YouTube API responses.
- [ ] **Add CI pipeline**: No GitHub Actions workflow. Add CI with lint + type check + tests on push/PR.
- [ ] **Add linting and formatting**: No ruff, mypy, or pre-commit config. Add `pyproject.toml` tool sections + `.pre-commit-config.yaml`.
- [ ] **Add `.env.example` and `channels.example.yml`**: No example config files committed — new users have to guess the format.

## P1 — Medium Priority

- [ ] **Split `exporters.py`**: 472 lines — too large. Split into `csv_exporter.py`, `text_exporter.py`, `readme_exporter.py`.
- [ ] **Add logging framework**: No structured logging. Uses `print()` for output. Add `logging` or `rich.console` for proper log levels.
- [ ] **API rate limiting / backoff**: No retry logic for YouTube API quota errors (HTTP 403). Add exponential backoff.
- [ ] **Batch transcript download**: Currently one video at a time. Add support for downloading transcripts for all videos in a channel.
- [ ] **Add `mypy --strict` compliance**: Type hints present but not validated. Fix issues and enforce in CI.

## P2 — Low Priority / Nice-to-Have

- [ ] **Output cleanup/archival**: Timestamped output folders accumulate without limit. Add `--clean` or rotation.
- [ ] **Data persistence**: No database — reports are one-shot files. Consider SQLite for trend tracking across runs.
- [ ] **Multiple export formats**: Only CSV/TXT. Add JSON and Markdown output options.
- [ ] **Configurable metric thresholds**: Performance distribution uses hardcoded 1.5x/0.5x multipliers. Make configurable.

## Done

_None yet._
