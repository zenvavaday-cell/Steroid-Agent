---
name: code-ownership-mapping
description: Infers ownership from repository history and CODEOWNERS, and flags orphaned or overloaded areas. Use for review routing and maintenance planning.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: engineering
---

# Code Ownership Mapping

## Overview

Ownership has two sources that often disagree. CODEOWNERS declares who must review a path. Repository history shows who actually changes and understands it. Review routing based only on the declaration sends changes to teams that no longer maintain the code, while routing based only on history ignores accountability and on-call responsibility.

The discipline is to build both views, reconcile them path by path, and expose three risks: orphaned code with no active maintainer, concentrated code where one person holds all context, and overloaded reviewers who become the bottleneck. The result is an evidence-backed map with confidence levels, not an org chart.

## When to use

- Setting or repairing review routing for a repository or monorepo.
- Planning maintenance after a reorganization, acquisition, or team change.
- Finding orphaned services, packages, or directories before a release or audit.
- Measuring bus factor and reviewer load for critical systems.
- Preparing a handover or maintenance budget.
- Do not use for individual performance evaluation; commit counts are a poor and privacy-sensitive proxy for contribution.

## Workflow

### 1. Collect declared ownership

Find the active CODEOWNERS file. GitHub uses the first file found in this order: `.github/CODEOWNERS`, `CODEOWNERS`, `docs/CODEOWNERS`. GitLab uses a similar location configured per project.

```bash
for f in .github/CODEOWNERS CODEOWNERS docs/CODEOWNERS; do
  [ -f "$f" ] && echo "$f" && wc -l "$f"
done
gh api "repos/$OWNER/$REPO/codeowners/errors" --jq '.errors'
```

Record each rule, its pattern, owners, and the section comment. Note that the last matching pattern wins, not the first, and that negation patterns are not supported on GitHub.

### 2. Build the path inventory

List tracked paths, grouped at a useful granularity: top-level package, service, or deployable unit. Exclude vendored code, generated files, and build output.

```bash
git ls-files \
  | rg -v '(^vendor/|^node_modules/|\.pb\.go$|^dist/|^build/|lock\.json$)' \
  | awk -F/ '{print $1"/"$2}' | sort | uniq -c | sort -rn
```

For a monorepo, use the package manifest list as the unit of ownership. For a service repository, use directories that map to deployables. The mapping unit should match how work is assigned, not the folder nesting depth.

### 3. Mine recent history per path

Use a window that reflects the current team, typically 12 to 18 months. Exclude merge commits, bots, and mechanical commits. Recency matters: a contributor who left two years ago should not own the path today.

```bash
git log --since='18 months ago' --no-merges --format='%ae' -- src/checkout \
  | sort | uniq -c | sort -rn | head -10
```

For a full matrix, aggregate commits and changed lines per path and author with a script:

```python
import collections, subprocess

since = "18 months ago"
out = subprocess.check_output([
    "git", "log", f"--since={since}", "--no-merges", "--numstat",
    "--format=commit\t%ae", "--", "src/",
], text=True)

counts = collections.defaultdict(collections.Counter)
author = None
for line in out.splitlines():
    if line.startswith("commit\t"):
        author = line.split("\t", 1)[1]
    elif line and author and not line.startswith("commit"):
        parts = line.split("\t")
        if len(parts) == 3:
            path = parts[2].rsplit("/", 1)[0]
            counts[path][author] += 1

for path, authors in sorted(counts.items()):
    total = sum(authors.values())
    top, n = authors.most_common(1)[0]
    print(f"{path}\t{total}\t{top}\t{n / total:.0%}")
```

Map emails to people with `.mailmap` before aggregating, and drop known bot addresses such as `dependabot[bot]` and `renovate[bot]`.

### 4. Score ownership and confidence

Compute a recency-weighted share, not a raw lifetime count. A practical rule: weight commits by half-life of 6 months, then take the top contributor's share and the number of contributors with at least 10% share.

| Signal | High confidence | Medium | Low |
| --- | --- | --- | --- |
| Top contributor share, 18 months | 50% or more | 25% to 49% | below 25% |
| Contributors with 10% or more | 2 or more | 2 with one dominant | 1 |
| Last change | within 90 days | within 12 months | older than 12 months |
| Declared owner matches history | yes | partial path | no |

A path can be well owned but still risky if only one person has context. Treat "single owner on a Tier 1 service" as a finding regardless of confidence.

### 5. Compare declared and actual ownership

Build a matrix with one row per path: declared owners, top historical contributors, last change date, commit count, service tier, and findings.

Findings to flag:

- **Orphaned**: no declared owner and no commits in 12 months, or declared team no longer exists.
- **Misrouted**: declared owner accounts for less than 10% of recent changes while another team does most of the work.
- **Concentrated**: one person accounts for 80% or more of recent changes on a Tier 1 path.
- **Overloaded**: a team or reviewer is in the top decile of review requests, or median review latency is more than twice the repository median.
- **Uncovered**: a tracked source path matches no CODEOWNERS rule.

### 6. Validate with team leads

Send each team its slice with the evidence and ask for three decisions: confirm, reassign, or split ownership. Resolve conflicts by naming one accountable team and, optionally, secondary reviewers. Record exceptions with a reason and review date.

Do not publish individual commit rankings. Share aggregates by team and flag concentration privately with the manager, because the data is incomplete and can be misread.

### 7. Update routing and review cadence

Write CODEOWNERS with the most specific patterns first and a final broad rule, because the last match wins. Prefer teams over individuals so routing survives staff changes. Add a non-code ownership file for infrastructure, dashboards, and data assets.

```text
# .github/CODEOWNERS
/src/checkout/          @org/checkout-team
/src/payments/          @org/payments-team @org/security-reviewers
/infra/terraform/       @org/platform-team
/                     @org/engineering-leads
```

Open a pull request with the map, the risk register, and the updated CODEOWNERS. Schedule a quarterly refresh because ownership drifts after reorganizations and departures.

## Validation

| Gate | Pass criterion | Evidence |
| --- | --- | --- |
| CODEOWNERS syntax | API reports zero errors | `gh api repos/$OWNER/$REPO/codeowners/errors` |
| Coverage | Every tracked source path matches a rule | Coverage script reports zero uncovered |
| Owners valid | Every user and team has write access | `gh api` permission checks |
| Team exists | No reference to archived or deleted teams | Org team list |
| Orphans | Zero orphaned Tier 1 paths, others have an exception | Risk register |
| Concentration | Zero single-owner Tier 1 paths without a documented plan | Risk register |
| Review load | No team above 1.5x the median review request volume | Review analytics |
| Freshness | Map generated within 30 days, CODEOWNERS reviewed quarterly | Report metadata |
| Privacy | Output aggregates by team, no individual ranking published | Review of shared artifact |

A path with a declared owner that has not touched it in 12 months is still orphaned for practical purposes. Do not mark the gate green on declaration alone.

## Gotchas

- CODEOWNERS uses last-match-wins. A broad rule at the bottom overrides specific rules above it.
- Patterns without a leading slash match at any depth, so `docs/` also matches `src/docs/`. Anchor with `/docs/` when that is the intent.
- Teams must have explicit write access or review requests fail silently. Check permissions, not just team names.
- GitHub does not support negation patterns. Excluding a subdirectory requires a more specific later rule.
- Renamed or moved files break per-path history. Use `git log --follow` for individual files, and treat the result as approximate.
- Bots, formatters, and codemods inflate one author's share. Exclude known bot accounts and commits that touch hundreds of files.
- `--since` uses commit date, which can be rewritten by rebases. For recent work, cross-check author date and merge date.
- A top committer may be the newest maintainer rather than the domain expert. Combine with review history and incident ownership.
- Ownership by acquisition or reorg is stale within days. Date the report and refresh after org changes.
- Generated and vendored paths create noise and false orphans. Exclude them from the mapping unit.
- Publishing individual commit counts invites gaming and privacy complaints. Keep the analysis at team and path level.
- A single team owning every path is not ownership. Cap the number of paths per team and escalate the overflow.

## Output contract

```markdown
| Path | Tier | Declared owners | Top recent contributors | Top share | Last change | Coverage | Finding |
| --- | --- | --- | --- | --- | --- | --- | --- |
| src/checkout | 1 | @org/checkout-team | A. Rivera, J. Chen | 58% | 2026-11-18 | yes | none |
| src/legacy-billing | 1 | @org/payments-team | M. Okafor | 91% | 2026-02-03 | yes | concentrated, stale |

## Risk register
- Orphaned: <path>, <evidence>, <recommended owner>, <deadline>
- Misrouted: <path>, declared <team>, actual <team>, <decision>
- Overloaded: <team>, <review volume vs median>, <rebalance action>

## Changes
- CODEOWNERS: <rules added, changed, removed>
- Non-code ownership: <dashboards, infra, data assets>
- Follow-up: <owner, date>
```

```yaml
report:
  generated_at: YYYY-MM-DD
  window_months: 18
  repository: string
  commit: string
  units: integer
  findings:
    orphaned: integer
    misrouted: integer
    concentrated: integer
    overloaded: integer
  reviewers: [string]
```

## Checklist

- [ ] Active CODEOWNERS file located and parsed.
- [ ] Path inventory built at the deployable or package level.
- [ ] Generated and vendored paths excluded.
- [ ] History window reflects the current team.
- [ ] Bots, merges, and mechanical commits excluded.
- [ ] Recency-weighted ownership computed.
- [ ] Declared and actual ownership compared per path.
- [ ] Orphaned, misrouted, concentrated, and overloaded paths flagged.
- [ ] Team leads confirmed or reassigned each finding.
- [ ] CODEOWNERS updated with last-match-wins ordering.
- [ ] Risk register and exceptions recorded with owners and dates.
- [ ] Quarterly refresh scheduled.

## Related skills

- `automated-pull-request-review` for enforcing review policy once routing is correct.
- `monorepo-dependency-graphing` for mapping ownership across package boundaries and affected targets.
- `dead-code-elimination` for removing orphaned paths that no team maintains.
- `incident-postmortem-generation` for connecting incident ownership to the code map.
