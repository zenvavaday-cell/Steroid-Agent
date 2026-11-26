---
name: release-notes-generation
description: Builds user-facing release notes from commits, pull requests, and issue trackers with accurate categorization. Use for product releases and changelog maintenance.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: engineering
---

# Release Notes Generation

## Overview

Release notes are a product artifact built from engineering evidence. The failure mode is not a missing section, it is a confident claim that the release does not support: a fix that did not ship, a breaking change buried under "improvements", or an internal ticket ID exposed to customers.

The discipline is traceability. Every published bullet maps to a merged pull request, commit, or issue, and every breaking change has a migration path. Draft from evidence, classify by user impact, then verify the rendered notes against the release diff.

## When to use

- Publishing a product, API, SDK, mobile app, or platform release.
- Maintaining `CHANGELOG.md` under a consistent format.
- Preparing internal release summaries for support, sales, or leadership.
- Documenting breaking changes and upgrade steps for a major version.
- Reconstructing notes for a release that shipped without them.
- Do not use for incident communication or postmortems; use `incident-postmortem-generation`, which has different timing, audience, and legal constraints.

## Workflow

### 1. Pin the release boundary and version

Identify the previous published tag, the target commit, and the version. Confirm the tag points at the intended commit and that the branch is the release branch, not a feature branch.

```bash
git describe --tags --abbrev=0
git log --no-merges --date=short \
  --pretty=format:'%h%x09%ad%x09%s' v1.4.0..HEAD
git rev-parse v1.5.0^{commit}
```

Apply semantic versioning deliberately:

| Change content | Version bump |
| --- | --- |
| Removed or renamed public API, changed default behavior | Major |
| New user-facing capability, backward compatible | Minor |
| Bug fix, performance improvement, security patch | Patch |
| Internal only, no user-visible behavior | Patch or no release |

### 2. Collect evidence from every source

Merge commits alone miss context. Pull requests carry the description, labels, linked issues, and review discussion. Issues carry user impact and reproduction details.

```bash
gh pr list --state merged --limit 200 \
  --search "merged:>=2026-11-01" \
  --json number,title,labels,author,url,mergeCommit,body

gh issue list --state closed --limit 200 \
  --search "closed:>=2026-11-01" \
  --json number,title,labels,url
```

For repositories without GitHub, export the equivalent from GitLab, Jira, or the tracker API. Record the query and date so the note set is reproducible.

### 3. Normalize and dedupe

- Collapse a pull request and its commits into one entry.
- Drop merge commits, version bumps, and pure formatting changes.
- Detect revert pairs: if a commit is reverted before the tag, neither belongs in the notes.
- Merge duplicate fixes for the same issue.
- Exclude cherry-picks already listed under another release.
- Keep backports only in the release that actually contains them.

```bash
# Commits on the release side that are not already in the previous tag
git log --cherry-pick --right-only --no-merges v1.4.0...v1.5.0
```

### 4. Classify by user impact

Use a fixed taxonomy, and make the classification depend on observable behavior, not on the commit prefix alone. Commit types are hints, not truth.

| Section | Include | Example |
| --- | --- | --- |
| Breaking changes | Removed APIs, changed defaults, required migrations | Auth token lifetime reduced from 24 h to 1 h |
| Added | New capability users can invoke | Bulk export for audit logs |
| Changed | Behavior changes that are not breaking | Default page size increased to 50 |
| Fixed | Defects with observable wrong behavior | Retry no longer duplicates charges |
| Security | Patched vulnerabilities and hardening | Updated TLS cipher policy |
| Deprecated | Still works, removal scheduled | `v1/search` endpoint |
| Removed | No longer available | Legacy CSV import |
| Performance | Measured latency, throughput, or cost change | Report query p95 reduced by 40% |
| Internal | Build, CI, dependencies, refactors | Usually excluded from user notes |

If a commit marked `chore` changes a user-visible default, it is a change. If a commit marked `feat` is unreachable behind a disabled flag, it is not in this release's user notes.

### 5. Write each entry for its audience

Lead with the user outcome, then the action if one is required. Keep one sentence per entry, past tense, no internal jargon. Link to documentation for anything that needs a migration.

Bad: `PAY-1842 refactor token refresh path`
Good: `Sessions now refresh access tokens five minutes before expiry, reducing mid-session sign-outs. No action required.`

Bad: `Breaking: auth changes`
Good: `Breaking: personal access tokens now expire after 90 days. Existing tokens expire on their current schedule. Create a replacement token before 2027-01-15. See the migration guide.`

Produce targeted variants from the same source data:

- End users: outcomes, no endpoint names or schema details.
- Administrators: configuration changes, permissions, quotas, migration deadlines.
- Developers: API changes, SDK versions, deprecations, code samples.

### 6. Verify claims against the release

For every bullet, confirm the change is present in the tagged commit and reachable by users. Check breaking changes against both the marker scan and the diff. Verify that migration documentation exists and is published before the notes go live.

```bash
# Breaking-change markers in the release range
git log v1.4.0..v1.5.0 --pretty=format:'%h %s' \
  | rg '!:|BREAKING[ -]CHANGE'

# Public surface diff for an API or library
git diff --stat v1.4.0..v1.5.0 -- api/ openapi.yaml
```

Redact internal ticket IDs, customer names, hostnames, and exploit details. Coordinate security items with the security owner so disclosure does not precede the fix.

### 7. Publish, link, and archive

Write `CHANGELOG.md` with an `Unreleased` section, one heading per version, and ISO dates. Publish the same content to the release page and documentation, then verify every link and code sample.

```bash
markdownlint-cli2 "CHANGELOG.md"
lychee --no-progress "CHANGELOG.md"
gitleaks detect --source . --no-git
```

Tag the release only after the notes and artifacts agree. Store the source range, query, and reviewer in the release record.

## Validation

| Gate | Pass criterion | Evidence |
| --- | --- | --- |
| Traceability | Every bullet maps to a PR, commit, or issue | ID column in the draft |
| Completeness | Every user-visible merged change appears once | Diff of release range against draft |
| No phantom entries | No bullet without a shipped change | Spot-check commit and deployed behavior |
| Breaking changes | Count matches marker scan and public surface diff | `rg` output plus API diff |
| Migration path | Every breaking change links to tested upgrade steps | Doc link and review |
| Version correctness | Bump matches the semver table | Release record |
| Link integrity | All links return 200 | `lychee` output |
| Redaction | No secrets, customer data, or embargoed details | `gitleaks` plus manual review |
| Rendering | Markdown lint passes and headings render | `markdownlint-cli2` |
| Audience review | Product and support approve the user-facing copy | Approval record |

Block publication if a breaking change lacks migration steps or if any bullet cannot be traced to a shipped change.

## Gotchas

- Squash merges replace individual commit messages with the PR title, which may be vague. Read the PR body and labels before writing the bullet.
- A revert and its original commit cancel out but both appear in the range. Remove the pair.
- Commit prefixes lie. A `fix:` can be a refactor and a `chore:` can change behavior. Verify against the diff.
- Dependency bumps are often security fixes in disguise. Check the advisory and classify them under Security when users are affected.
- Auto-generated notes list every pull request, including chores and tests. Curate instead of pasting the generated list.
- Maintenance branches contain backports that already shipped elsewhere. Compare cherry-picks before listing them.
- Internal ticket IDs and customer names leak through commit messages and PR titles. Strip them during drafting, not after publishing.
- Security embargoes break if notes mention the fix before the patch is available to users. Coordinate the disclosure time.
- The version bump commit and the notes commit itself are not user changes. Exclude them.
- Timezone differences make the release date ambiguous. Use the date of the published artifact and state the timezone if it matters.
- A release with no user-visible changes should say so, not manufacture improvement language.
- Links to unreleased documentation return 404 on publish day. Publish docs first or use a stable versioned URL.

## Output contract

```markdown
# Release v1.5.0 (2026-11-26)

## Breaking changes
- <change>. Migration: <link>.

## Added
- <user outcome>. (<PR link>)

## Changed
- <behavior change>. (<PR link>)

## Fixed
- <defect fixed>. (<PR link>)

## Security
- <advisory or hardening>. (<link>)

## Deprecated
- <surface> will be removed on <date>. Use <replacement>.

## Performance
- <metric> improved from <baseline> to <result> in <environment>.

## Internal
- <excluded from user-facing distribution>
```

```yaml
release:
  version: string
  date: YYYY-MM-DD
  previous_tag: string
  target_commit: string
  source_query: string
  reviewer: string
  traceability:
    - entry: string
      source: string
  redactions:
    - item: string
      reason: string
```

## Checklist

- [ ] Previous tag and target commit pinned.
- [ ] Version bump matches the semver table.
- [ ] Commits, pull requests, and issues collected with reproducible queries.
- [ ] Duplicates, reverts, and backports removed.
- [ ] Every entry classified by user impact.
- [ ] User, admin, and developer variants considered.
- [ ] Every bullet traced to a shipped change.
- [ ] Breaking changes include tested migration steps.
- [ ] Security disclosure coordinated.
- [ ] Internal identifiers and customer data redacted.
- [ ] Links, Markdown, and secret scans pass.
- [ ] Notes archived in the changelog and release page.

## Related skills

- `feature-flag-lifecycle-management` for launches whose visibility depends on rollout state.
- `automated-pull-request-review` for consistent PR descriptions and labels that feed the notes.
- `technical-documentation-writing` for migration guides linked from breaking changes.
- `semantic-codebase-search` for locating user-facing strings and deprecated surfaces.
