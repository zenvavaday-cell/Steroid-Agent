---
name: design-system-audit
description: Finds component drift, token inconsistencies, duplicated patterns, and accessibility gaps. Use for design-system health checks and migrations.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: product-design
---

# Design System Audit

## Overview

A design system decays through small, local decisions: a hardcoded hex value, a copied button, a variant that exists only in Figma. An audit measures that drift, quantifies adoption, and produces a migration plan with owners and guardrails.

The audit must compare design sources, code, and production. A library that looks correct in Storybook but is bypassed in the product is not healthy.

## When to use

- Before a redesign, rebrand, or token migration.
- After a merger or acquisition with multiple UI libraries.
- When inconsistency complaints rise across product teams.
- Before investing in documentation or new components.
- As a quarterly or semiannual design-system health check.
- When accessibility defects recur across similar components.

Do not use for visual QA of a single page, or as a substitute for a component-level accessibility test.

## Workflow

### 1. Inventory all sources

List the component library package, Storybook, the Figma library, and the production applications that consume them. Record versions and owners.

```bash
rg -n '"@acme/ui"' package.json apps/*/package.json
npx storybook build --output-dir .audit/storybook
```

Build a manifest with one row per component: name, package path, Figma node, variants, props, stories, owner, and last changed date.

### 2. Extract and compare tokens

Collect color, spacing, typography, radius, shadow, and motion values from code, design, and production CSS.

```bash
rg -o --no-filename '#[0-9a-fA-F]{3,8}\b' src apps --glob '*.{css,scss,ts,tsx}' \
  | tr 'A-F' 'a-f' | sort | uniq -c | sort -rn | head -40

rg -n --pcre2 '(padding|margin|gap):\s*\d+px' src apps --glob '*.{css,scss}' | wc -l
```

Map each raw value to a token. Classify: exact token match, near match within a documented tolerance, or unmatched. Near matches are still drift if a token exists.

| Raw value | Count | Nearest token | Delta | Verdict |
| --- | --- | --- | --- | --- |
| #1a73e8 | 37 | color.brand.600 (#1a73e8) | 0 | Match, replace with token reference |
| #1b74e9 | 9 | color.brand.600 | 1 per channel | Drift, replace |
| #f5f6f7 | 22 | color.surface.subtle (#f6f6f7) | 1 per channel | Drift or new token, decide |

### 3. Measure component adoption

Count imports and rendered usage, not just package installs. Include re-exports, dynamic imports, and wrapper packages.

```bash
rg -l "from ['\"]@acme/ui['\"]" apps --glob '*.{ts,tsx,js,jsx}' | wc -l
rg -n "<Button\b" apps --glob '*.{tsx,jsx}' | wc -l
rg -n "from ['\"]\./components/Button['\"]" apps --glob '*.{ts,tsx}' | wc -l
```

Define adoption as the share of audited screens or routes that use a design-system component for the pattern, not the share of files that import the package. State the denominator and the date.

### 4. Detect duplicates and variant drift

Flag components with similar names, props, or screenshots. Compare design variants to code variants and mark any variant that exists on only one side.

```bash
rg -n 'variant="(primary|secondary|tertiary)"' apps --glob '*.tsx' | wc -l
rg -n 'export (const|function) (Button|Btn|PrimaryButton)' packages/ui/src --glob '*.tsx'
```

Common drift patterns: a local `PrimaryButton` wrapping the system `Button`, a `size="large"` used only in marketing pages, and a Figma-only `danger` variant implemented with inline styles.

### 5. Audit accessibility at the component level

Run automated checks against every Storybook story, then verify keyboard and focus behavior manually.

```bash
npx @axe-core/cli http://localhost:6006/iframe.html?id=button--primary --exit
npx @axe-core/cli http://localhost:6006/iframe.html?id=select--open --exit
```

Check for each interactive component: accessible name, role, keyboard operation, focus visible, disabled semantics, error announcement, contrast in every variant, target size, and reduced-motion handling. Record the WCAG 2.2 criterion and the affected variant.

### 6. Score and classify findings

Rate each finding by user impact, reach (number of screens or variants), and migration cost. Use a simple 1 to 5 scale and a decision table.

| Impact | Reach | Cost | Class | Action |
| --- | --- | --- | --- | --- |
| 5 | 5 | 1 | Critical | Fix now, add lint guard |
| 4 | 4 | 3 | High | Next sprint, codemod if possible |
| 3 | 3 | 4 | Medium | Plan with deprecation window |
| 1 | 2 | 5 | Low | Document as accepted exception |

Accessibility defects cannot be downgraded below high if they block a core task.

### 7. Write the consolidation plan

For each duplicate or drifted element, name the target component or token, the migration path, the owner, and the deprecation date.

```json
{
  "finding_id": "DS-021",
  "current": "apps/billing/components/PrimaryButton.tsx",
  "target": "@acme/ui/Button variant=primary",
  "instances": 14,
  "migration": "codemod import rewrite, then manual review of size and loading props",
  "owner": "billing-web",
  "deprecation_date": "2026-07-01",
  "rollback": "revert codemod commit, keep wrapper for one release"
}
```

### 8. Add guardrails before migration

- Lint rule that rejects raw hex colors and arbitrary spacing in product code.
- Contract test that every documented variant has a story and a visual snapshot.
- CI check that fails on new local duplicates of core components.
- Visual regression baseline for all stories before any code change.
- Contribution path for exceptions, with an owner and expiry.

### 9. Publish and track

Report inventory coverage, adoption rate, top drift sources, accessibility gaps, and the migration burn-down. Re-run the same queries at a fixed interval so trends are comparable.

## Validation

- Inventory gate: 100% of shipped components covered, or a documented sample with a confidence statement.
- Token gate: every unmatched raw value has a target token, a new-token decision, or an accepted-exception owner.
- Adoption gate: metric states numerator, denominator, query, and date.
- Accessibility gate: every interactive component has an axe result and a manual keyboard result.
- Migration gate: target, owner, deprecation date, and rollback exist for every plan item.
- Safety gate: no component or token removed without a usage check and owner sign-off.
- Baseline gate: visual snapshots exist before migration starts.

```bash
python3 - <<'PY'
from pathlib import Path
report = Path(".audit/report.json").read_text()
for key in ["inventory", "tokens", "adoption", "accessibility", "migration"]:
    assert key in report, key
print("report complete")
PY
```

## Gotchas

- Auditing Figma only misses the code paths users actually see.
- Counting imports overstates adoption when a wrapper hides the system component.
- Treating every hex value as drift ignores brand, email, and third-party surfaces.
- Removing a variant without searching dynamic and string-based usage breaks production.
- Accessibility automation covers only part of WCAG. Keyboard and focus checks are mandatory.
- Legitimate one-off variants get flattened into the system and create prop sprawl.
- Duplicate components often have different names. Compare screenshots and props, not names alone.
- An audit with no owner becomes a slide deck. Assign migration owners up front.
- Migrating without visual regression invites silent layout breakage.
- Token naming churn adds migration cost with no user value. Freeze names before the sweep.
- Ignoring documentation and contribution guidelines means drift returns within a quarter.
- Measuring adoption once cannot show progress. Keep the query and rerun it.

## Output contract

```json
{
  "audit_id": "DS-2026-Q2",
  "scope": {"packages": ["@acme/ui@4.2.0"], "apps": ["billing", "admin"], "screens": 68},
  "inventory": {"components": 42, "documented": 37, "owned": 40},
  "tokens": {"raw_values": 214, "matched": 151, "drifted": 44, "unmatched": 19},
  "adoption": {"rate": 0.72, "numerator": 49, "denominator": 68, "query": "audit/adoption.sql", "date": "2026-05-30"},
  "duplicates": [{"name": "PrimaryButton", "instances": 14, "target": "Button variant=primary"}],
  "accessibility": [{"component": "Select", "criterion": "4.1.2", "variant": "open", "severity": "high"}],
  "migration": [{"finding_id": "DS-021", "owner": "billing-web", "deprecation_date": "2026-07-01"}],
  "trend": {"previous_adoption": 0.63, "previous_audit": "DS-2026-Q1"}
}
```

## Checklist

- [ ] Component, token, and app sources inventoried with versions.
- [ ] Raw color and spacing values extracted and mapped to tokens.
- [ ] Adoption measured with numerator, denominator, query, and date.
- [ ] Duplicates and variant drift detected across design and code.
- [ ] Every interactive component checked with axe and manual keyboard.
- [ ] Findings scored by impact, reach, and cost.
- [ ] Migration plan has target, owner, date, and rollback.
- [ ] Lint, contract, and visual regression guardrails specified.
- [ ] No removal without usage check and sign-off.
- [ ] Report published with trend against the prior audit.
- [ ] Accepted exceptions have owners and expiry.

## Related skills

- `ux-heuristic-evaluation` to connect component defects to task-level usability impact.
- `accessibility-format-conversion` when audit outputs must be delivered in accessible formats.
- `automated-refactoring-execution` to run codemods for component consolidation.
- `legacy-code-migration-planning` for sequencing a multi-release design-system migration.
