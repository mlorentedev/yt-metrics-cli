# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> **Read [`AGENTS.md`](../AGENTS.md) first.** It is the agent SSOT for this repo and carries the
> content that used to live here: the architecture layer map and its two invariants, the technical
> standards table, the Makefile command set, the key-paths table, knowledge placement and the
> review-gate notes. `AGENTS.md` in turn delegates the behavioural SSOT (Identity, Standing Orders,
> Decision Hierarchy, Model Selection, Neural Hive protocol) to the canonical dotfiles `AGENTS.md`.
>
> This file overlays only Claude Code-specific notes on top of `AGENTS.md`. Keep it a thin pointer —
> durable rules belong in `AGENTS.md` so every agent (Claude, Copilot, Cursor, Codex) sees them.

## Claude Code-specific notes

- **Model tier** (per `AGENTS.md` "Model Selection" in the dotfiles canon): Top tier for hard
  debugging, root-cause work and architecture; Mid for mechanical refactors, docs and test
  scaffolding; Low for syntax lookups. Propose a tier change, never switch silently.
- **MEMORY.md and session memory never live in this repo** — they belong in the vault (GUARD-001).
  Use Hive as the memory API over the vault, not committed files here.
- **Reviewer context:** `.pr_agent.toml` names `AGENTS.md` as `repo_context_files`. If this file
  ever grows back into a second source of truth, the reviewer is reading the stale one.
