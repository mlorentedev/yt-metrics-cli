---
id: lesson-012-graphql-quota-is-per-user-so-one-session-can-block-ci-releases
type: lesson
status: active
created: "2026-09-22"
owner: manu
tags: [yt-metrics-cli, lesson, github, graphql, rate-limit, ci, release-please]
---

# The GraphQL quota is per *user*, so one session's board queries can block a CI release

**Context:** A housekeeping session on 2026-09-22 read the bitácora board to reconcile it, then verified a rotated `RELEASE_TOKEN` by watching the `release-please` job.

**Problem:** The release run that followed a merge failed — and the failure had nothing to do with the credential being tested:

```
2026-09-22T02:54:15Z ##[error]release-please failed: Request failed due to following response errors:
 - API rate limit already exceeded for user ID 13562150.
```

That is the *same* GraphQL quota the session itself had exhausted twenty minutes earlier, from the same account:

```
$ gh project item-list 1 --owner mlorentedev --limit 1200 --format json   # 02:20, twice
$ gh api graphql -f query=…                                              # 02:41, 02:43, 02:47
{"errors":[{"type":"RATE_LIMIT","code":"graphql_rate_limit",
 "message":"API rate limit already exceeded for user ID 13562150."}]}
```

GitHub's GraphQL limit is 5000 points/hour **per user**, and every credential belonging to that user draws on the same bucket: the `gh` CLI running locally with `mlorentedev`'s OAuth token, and the `RELEASE_TOKEN` (also `mlorentedev`'s PAT) that `release-please-action` uses inside CI. So the local session's queries did not merely slow the session down — they blocked the repository's release path, and the CI log blamed a token that was in fact healthy. That is the trap: the symptom (`release-please failed`) points at the credential, while the cause is a quota the credential's *owner* spent elsewhere.

Also note where the quota was spent. `gh project item-list --limit 1200` against a 3206-item project is a paginating GraphQL drain: two of those calls are enough to matter, and the second one bought nothing (the first had already returned what was needed, and only the first 200 items had been filtered on).

**Solution:** (1) Treat the GraphQL quota as a shared, per-user budget: before spending it on board reads, ask whether a release is pending or a CI run is about to need it. (2) Use the narrowest possible query — `gh api repos/…/issues/<n>` (REST) for a single item, a `node(id:)` lookup for one project item, or `--query` to filter server-side — instead of listing a 3206-item project to find one row. REST and GraphQL bills are separate pools, so REST is the fallback when one is exhausted (lesson-009). (3) When a token-verification run fails, read the error body before believing the headline: `Bad credentials` (401) is the credential, `API rate limit exceeded for user ID …` is the quota, and the two arrive under the same job name. (4) Wait for the reset (hourly, from first consumption) and re-run; nothing needs fixing in the secret.

**Why:** A quota is not local to the process that spends it. Here the session was verifying a rotated PAT — the one moment where "did the fix work?" has to be answered by a CI run — and it spent, minutes earlier, the exact budget that run needed to answer. Correction without a clean measurement window is indistinguishable from a failed fix, which is why the first reading of that log was "the new token is also broken" until the error body was read.

**Tags:** `#github` `#graphql` `#rate-limit` `#ci` `#release-please` `#gotcha`
