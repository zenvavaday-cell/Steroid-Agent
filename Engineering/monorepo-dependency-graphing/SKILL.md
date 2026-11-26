---
name: monorepo-dependency-graphing
description: Maps package and target dependencies, detects cycles, and scopes affected builds and tests. Use for monorepo navigation, impact analysis, and CI optimization.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: engineering
---

# Monorepo Dependency Graphing

## Overview

A monorepo graph has two layers: what packages declare in manifests and build files, and what code actually imports. Divergence between them causes phantom dependencies, missed rebuilds, and CI jobs that pass while a clean install fails.

The deliverable is a deterministic graph plus three derived answers: cycles, the affected set for a change, and a topological build order.

## When to use

- Scoping CI to the packages a pull request actually touches.
- Investigating why a change broke an unrelated package.
- Planning a dependency upgrade across workspaces.
- Finding cycles before splitting or extracting a package.
- Onboarding onto a large repository with unclear ownership.
- Checking that a published package has no undeclared runtime dependency.

Do not use for single-package repositories, where a file-level import graph is sufficient.

## Workflow

### 1. Inventory workspace members

| Ecosystem | Command |
| --- | --- |
| npm, pnpm, yarn | `pnpm ls -r --depth -1 --json` or `yarn workspaces list --json` |
| Nx | `nx show projects --with-target build` |
| Bazel | `bazel query 'kind(".* rule", //...)' --output=label_kind` |
| Cargo | `cargo metadata --format-version 1 --no-deps` |
| Go | `go list -m -json all` |

Record name, path, manifest, publish flag, and owner for every member. Reconcile against the directories on disk; a workspace glob that silently matches nothing is a common failure.

### 2. Extract declared edges

Parse manifests with a script, not with grep. Classify every edge as `runtime`, `dev`, `peer`, or `build`. Resolve workspace protocols (`workspace:*`, `file:`, `portal:`) to local package names before treating anything as external.

For Bazel, use `bazel query 'deps(//pkg:target)' --output=label`. For Nx, read `nx.json` and each `project.json`, including `implicitDependencies`. For Go, `go list -deps ./...` follows build tags that a text scan misses.

### 3. Build the import graph

```bash
npx madge --extensions ts,tsx --ts-config tsconfig.json --json packages > /tmp/imports.json
npx dependency-cruiser --output-type json packages > /tmp/cruise.json
go list -f '{{.ImportPath}} {{join .Imports " "}}' ./...
cargo tree --workspace --edges normal,build
```

Collapse file edges into package edges and keep the strongest kind when several exist. Flag every import that resolves outside the importing package without a matching declared dependency. That is a phantom dependency, and hoisting hides it locally.

### 4. Reconcile declared against imported

Produce three lists: declared but unused, imported but undeclared, and declared only as dev but imported at runtime. Then prove the result in a clean environment:

```bash
pnpm install --frozen-lockfile
pnpm --filter <pkg> exec tsc --noEmit
```

A package that builds only because of the root `node_modules` will fail here.

### 5. Detect cycles

```bash
npx madge --circular --extensions ts,tsx packages
python3 scripts/scc.py graph.json  # Tarjan, prints SCCs with size > 1
```

Report package-level and file-level cycles separately. A file cycle inside one package is a refactor task. A package cycle blocks topological ordering and usually means a missing shared package or an inverted layer.

### 6. Compute the affected set

Mapping rules:

- A changed file belongs to the deepest enclosing package.
- Root files (`pnpm-lock.yaml`, `turbo.json`, `tsconfig.base.json`, CI config) mark every package affected.
- Take the reverse closure over runtime and build edges, transitively.
- Dev-only edges propagate to test and lint targets, not to production builds.

```bash
nx affected -t test build --files="$(git diff --name-only origin/main...HEAD | paste -sd, -)"
turbo run build --filter='...[origin/main]' --dry=json
```

If neither tool is available, run the reverse closure in a script and store the result as JSON. Prefer over-selection: a missed package is a broken main branch, an extra package is wasted minutes.

### 7. Emit build order and parallelism

Topologically sort the DAG and group nodes into levels. Level 0 has no internal dependencies. Every edge must point from a lower level to a higher one. Report the critical path (the longest chain) because it sets minimum wall-clock time regardless of worker count.

Commit the graph artifact so CI, reviewers, and new hires read the same structure.

## Validation

- Node count equals the member count from step 1; diff the name sets, not only the totals.
- Every internal import resolves to exactly one node, or is explicitly marked external.
- The cycle check exits 0, or every cycle is listed with an owner and a removal ticket.
- Topological order holds: for every edge A to B, `index(A) < index(B)`.
- The affected set contains the changed package and all transitive dependents; spot-check two known consumers.
- A no-op change to a leaf package affects only that package and its dependents.
- A clean-install build of each affected package succeeds with the lockfile frozen.

Fail the gate on any phantom dependency, unlisted cycle, or order violation.

## Gotchas

- `workspace:*` versions are not semver ranges; a naive parser treats them as external dependencies.
- Hoisted `node_modules` hides phantom dependencies. Only a clean install or an isolated build exposes them.
- Dynamic imports such as `await import(path)` or `require(name)` are invisible to static analyzers. Add manual edges or a runtime trace.
- Path aliases like `@/lib` cross package boundaries without appearing in imports. Resolve them through tsconfig paths and check the final file path.
- Peer dependencies are constraints, not install edges. Record them separately or the graph will overstate the build closure.
- Generated code creates real build edges that hand-written manifests miss. Include codegen outputs and the generator itself.
- Treating dev dependencies as runtime edges inflates CI by an order of magnitude and hides the true production closure.
- A lockfile change can alter every package through one shared transitive version. Mark it global rather than guessing.
- Duplicate versions of one package appear as separate nodes in file-level graphs. Normalize by package name at the package layer.
- TypeScript project references and package dependencies are different graphs. Keep both and reconcile them.
- Bazel visibility and Go build tags remove edges that a text scan reports. Trust the build tool's query output.

## Output contract

```json
{
  "generated_at": "2026-01-01T00:00:00Z",
  "packages": [
    {"name": "@acme/api", "path": "packages/api", "owner": "team-api"}
  ],
  "edges": [
    {"from": "@acme/api", "to": "@acme/core", "kind": "runtime", "source": "declared+imported"}
  ],
  "cycles": [
    {"members": ["@acme/a", "@acme/b"], "level": "package"}
  ],
  "affected": {
    "changed": ["packages/core/src/x.ts"],
    "packages": ["@acme/core", "@acme/api"],
    "reason": "reverse closure over runtime edges"
  },
  "build_order": [["@acme/core"], ["@acme/api"]],
  "violations": [
    {"type": "phantom", "package": "@acme/api", "dependency": "left-pad"}
  ]
}
```

## Checklist

- [ ] Workspace members inventoried from the package manager or build tool.
- [ ] Declared edges parsed and workspace protocols resolved.
- [ ] Import graph built and collapsed to package level.
- [ ] Declared and imported graphs reconciled.
- [ ] Cycles detected and classified by level.
- [ ] Affected set computed by reverse closure with root-file rules.
- [ ] Build order validated as topological.
- [ ] Phantom dependencies listed with an owner.
- [ ] Graph artifact committed for review.
- [ ] Clean-install verification run.

## Related skills

- `build-cache-optimization` for turning the graph into cache keys and hit-rate improvements.
- `code-ownership-mapping` for attaching owners and bus-factor risk to each node.
- `dependency-vulnerability-auditing` for scanning the resolved external edges.
- `ci-cd-failure-diagnosis` when a scoped pipeline still fails.
