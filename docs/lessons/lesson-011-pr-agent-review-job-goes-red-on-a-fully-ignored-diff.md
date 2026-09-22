---
id: lesson-011-pr-agent-review-job-goes-red-on-a-fully-ignored-diff
type: lesson
status: active
created: "2026-09-22"
owner: manu
tags: [yt-metrics-cli, lesson, ci, pr-agent, review-gate, misdiagnosis]
---

# PR-Agent's review job goes red on a fully `[ignore]`d diff and blames the wrong cause

**Context:** Reading the red `review` check on Dependabot PR #74 (js-yaml 4.3.1 → 4.3.2), which had
been rebased by hand from the GitHub UI.
**Problem:** The `review` job failed with:

```
::error::PR-Agent reported success but published no review
::error::Most likely cause: NaN concurrency exhaustion — the cluster allows 5 simultaneous
::error::requests, shared with pi, qq and hive embeddings. See #1107.
```

Both halves of that are wrong. PR-Agent did not "report success and publish nothing because the
model was saturated"; it never had anything to review. The run log says so:

```
Tokens: 3068, total tokens under limit: 200000, returning full diff.
Empty diff for PR: https://api.github.com/repos/mlorentedev/yt-metrics-cli/pulls/74
Failed to generate prediction with openai/mimo-v2.5
  "error": "No PR diff fits the /review request for openai/mimo-v2.5"
Failed to generate prediction with openai/deepseek-v4-flash
```

Root cause: `site/package-lock.json` is in `.pr_agent.toml`'s `[ignore] glob` (the file lists both
lockfiles — thousands of resolved URLs that the bump PR already reviewed). `_get_diff_files` filters
the whole diff out, `_prepare_prediction` then finds an empty reviewable set, and both models "fail"
on an empty prompt. The guard correctly detects "no review landed" and then attaches the one cause it
knows, sending the reader to a closed issue about a different failure.

The trigger is worth as much as the cause: the job's Dependabot exclusion keys on `github.actor`, so
a **human-driven rebase** of a Dependabot branch runs the job (measured: `actor=mlorentedev` on the
failing run, `actor=dependabot[bot]` on the sibling runs that were skipped). Every Dependabot PR in
this repo is lockfile-only, so every hand-rebase of one reproduces it.

**Solution:** (1) Read the job's own log before believing its summary line — the guard's
"most likely cause" is a guess, the `Empty diff for PR` line is evidence. (2) Do not let the red
check block the bump: the diff is a lockfile, CI green is the whole verdict, so merge it with the
`merged-unreviewed` label plus a `## Unreviewed merge rationale` section rather than silently or by
pretending a review happened. (3) Prefer `@dependabot rebase` over the UI's "Update branch": the
Dependabot actor is what makes the job skip, and a skipped check is honest where a red one is a
false alarm. (4) Record the disposition under `## Review triage` even when it is "no reviewer could
run".
**Why:** Failing closed is right; guessing the cause in the failure message is not, because the
message is what the next reader trusts. This is a class, not an incident: `mlorentedev/dotfiles#1417`
(open) documents the same guard misfiring when an entire diff is `[ignore]`d for a different reason
(SOPS ciphertext), and asks for exactly this measurement. An `[ignore] glob` that covers a PR's whole
diff makes that PR unreviewable *by construction* — the fix belongs in the gate (detect it and
declare the PR unreviewed), not in the reader's patience.
**Tags:** `#ci` `#pr-agent` `#review-gate` `#misdiagnosis`
