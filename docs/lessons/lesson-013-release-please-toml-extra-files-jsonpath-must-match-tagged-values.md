---
id: lesson-013-release-please-toml-extra-files-jsonpath-must-match-tagged-values
type: lesson
status: active
created: "2026-10-18"
owner: manu
tags: [yt-metrics-cli, lesson, ci, release-please, toml, uv, silent-failure]
---

# release-please's TOML `extra-files` jsonpath must match the *tagged* values it parses

**Context:** fixing BUG-001 (#81) — `uv.lock` records this project's own version and nothing
regenerated it after a release-please merge, so every release left a dirty tree behind it. The
chosen fix was `extra-files` with `"type": "toml"`, pointed at the lock's `[[package]]` entry for
`yt-metrics-cli`.
**Problem:** the jsonpath a careful person writes first matches **nothing**, and says so only as a
log warning:

```
⚠ No entries modified in $.package[?(@.name=='yt-metrics-cli')].version
```

`GenericToml.updateContent` then returns the content unchanged, release-please opens the release PR
without `uv.lock`, and the PR looks patched while the drift it was meant to end is still there. That
is a silent failure inside the fix for a silent failure — the worst place to keep one.

**Cause:** `GenericToml` does not parse the file with a plain TOML parser. It uses release-please's
`TaggedTOMLParser` (`src/util/toml-edit.ts`), which replaces every scalar with
`{[taggedValueMarker]: true, start, end, value}` so a replacement can be spliced by byte offset. A
filter expression therefore compares an **object** to a string: `@.name` is never `'yt-metrics-cli'`,
so the filter yields no pointers. Measured on release-please **17.11.2** and again on **17.6.0** (the
floor of `release-please-action@v5`'s `^17.6.0`), against this repo's own `uv.lock`:

| jsonpath | pointers matched | effect |
|---|---|---|
| `$.package[?(@.name=='yt-metrics-cli')].version` | 0 | file returned unchanged; warning only |
| `$.package[?(@.name.value=='yt-metrics-cli')].version` | 1 | line 999 rewritten, 0-byte length delta elsewhere |
| `$.package[*].version` | 55 | would rewrite every package's version |

The second form reaches the tag's `value` field, which is an implementation detail — but the
alternative guesses are worse, and the class docstring cannot be trusted either: it claims the
updater "does reformat the document and removes all comments", while `replaceTomlValue` in fact
splices the byte range and preserves formatting exactly (verified: the replacement changed one line
and left the other ~1000 untouched). **Read the code the fix depends on, not its summary.**

**Solution:** `"jsonpath": "$.package[?(@.name.value=='yt-metrics-cli')].version"`, proven against the
real updater class before merging rather than reasoned about:

```bash
npm i release-please@17.6.0     # the version the action can resolve
node -e "
  const {GenericToml} = require('release-please/build/src/updaters/generic-toml.js');
  const fs = require('fs'), original = fs.readFileSync('uv.lock', 'utf8');
  const out = new GenericToml(\"\$.package[?(@.name.value=='yt-metrics-cli')].version\", '9.9.9')
    .updateContent(original);
  const a = original.split('\n'), b = out.split('\n'), ch = [];
  a.forEach((line, i) => { if (line !== b[i]) ch.push(i + 1); });
  console.log(ch, out.length - original.length);
"
# [ 999 ] 0
```

…and pair it with a guard that fails closed, because "the updater logged a warning" is not a signal
anyone reads: `uv lock --check` in CI, which exits 1 with `The lockfile at uv.lock needs to be
updated` (measured by bumping a copy's `pyproject.toml` to 0.2.8 and watching it fail). A selector
that quietly stops matching then turns into a red build with the file and the command named, instead
of a release that ships a stale lock.
**Why:** this class recurs wherever release-please is pointed at a TOML file whose version is not at
`$.version` — the documented examples (`hive`, `pdf-modifier-mcp`) are all `type: json` on
`server.json`, where a filter on `name` *does* work, because the JSON updater does not tag its values.
Copying a working json config to a toml path silently changes the meaning of the filter.
**Second trap, same commit:** adding `uv.lock` to the release PR moves its diff signature from three
files to four, and `harness/review-attestation.json` matches exemptions by **set equality** — so the
same change would have quietly un-exempted every future release PR. Any automation that adds a file
to a known diff signature has to update the declaration that recognises it, in the same commit.
**Tags:** `#ci` `#release-please` `#toml` `#uv` `#silent-failure`
