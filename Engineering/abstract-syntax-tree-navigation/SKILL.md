---
name: abstract-syntax-tree-navigation
description: Parses and queries source code as syntax trees using tree-sitter, ast-grep, and language-native ASTs to find and transform precise code patterns without regex false positives. Use for codemods, call-graph exploration, lint rules, symbol search, and structural refactors across large codebases.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: engineering
---

# Abstract Syntax Tree Navigation

## Overview

Regex matches text; an AST matches structure. Use an AST when the question is "find every call to this function with two arguments" or "rename this symbol but not the string with the same name." Use regex only for lexical tasks such as license headers or TODO comments.

This skill covers parsing, querying, resolving symbols, and editing trees while preserving formatting.

## When to use

- Finding call sites, imports, decorators, or specific node shapes.
- Writing a codemod or lint rule.
- Extracting a call graph or dependency structure.
- Refactoring across many files.
- Answering "where is this symbol used?" with structural accuracy.

## Tool selection

| Task | Tool |
| --- | --- |
| Multi-language structural search | `ast-grep` (`sg`) |
| Precise querying with a grammar | tree-sitter |
| Python analysis and transforms | `ast`, `libcst` |
| TypeScript/JavaScript transforms | `ts-morph`, `jscodeshift` |
| Java | JavaParser |
| C# | Roslyn |
| Go | `go/ast`, `golang.org/x/tools/go/packages` |
| Rust | `syn` |

## Workflow

### 1. Parse and confirm the grammar

```bash
# Inspect the tree for a file
tree-sitter parse src/service.py
```

For tree-sitter queries, inspect node types with the playground or `tree-sitter query`. Node names vary by grammar version; do not guess.

### 2. Write a structural query

tree-sitter query example (Python):

```scheme
(call
  function: (attribute
    object: (identifier) @obj
    attribute: (identifier) @method)
  arguments: (argument_list) @args
  (#eq? @obj "requests")
  (#eq? @method "get"))
```

ast-grep example:

```yaml
id: requests-get-without-timeout
language: python
rule:
  pattern: requests.get($URL, $$$REST)
constraints:
  REST:
    not:
      has:
        pattern: timeout=$T
message: requests.get called without a timeout
severity: warning
```

Run:

```bash
sg scan --rule no-timeout.yml src/
sg run -p 'requests.get($URL)' -l python src/
```

### 3. Resolve scope and symbols

A syntactic match is not a semantic one. Two functions can share a name. Resolve:

- Imports and aliases (`import numpy as np`).
- Local variables shadowing a name.
- Methods versus free functions.
- Overloads and generics.
- Dynamic dispatch and reflection.

Use the language server or type checker for semantic answers:

```bash
pyright --outputjson src/ | jq '.generalDiagnostics'
```

For Python, `ast` plus `symtable` can approximate scope. For TypeScript, `ts-morph` exposes the type checker.

### 4. Capture context

For each match, record:

- File and byte or line/column range.
- Enclosing function, class, and module.
- Import path and alias.
- Whether the match is in generated, vendored, or test code.

Filter generated code by path and header markers, not by guesswork.

### 5. Edit safely

Prefer a lossless CST for edits:

```python
import libcst as cst

class AddTimeout(cst.CSTTransformer):
    def leave_Call(self, original_node, updated_node):
        if isinstance(updated_node.func, cst.Attribute):
            if updated_node.func.attr.value == "get":
                return updated_node.with_changes(
                    arguments=updated_node.arguments
                    + [cst.Arg(keyword=cst.Name("timeout"), value=cst.Float("10"))]
                )
        return updated_node

source = open("client.py").read()
tree = cst.parse_module(source)
open("client.py", "w").write(tree.visit(AddTimeout()).code)
```

`ast` loses comments and formatting. `libcst`, `ts-morph`, and Roslyn preserve it.

### 6. Validate

- Re-parse every modified file.
- Run the formatter and linter.
- Run type checks.
- Run tests.
- Inspect the diff for unintended changes.

A codemod that parses but changes semantics is still broken.

## Gotchas

- Tree-sitter is error-tolerant. A parse with errors can still return matches; check for `ERROR` nodes.
- Grammar versions differ. A query working in one editor may fail in another.
- Byte offsets versus line/column versus UTF-16 columns cause off-by-one edits, especially with Unicode.
- Comments and formatting are not in the Python `ast`. Use `libcst` for rewrites.
- Macros, decorators, and generated code can hide the real definition.
- Dynamic imports and `eval` defeat static analysis. Search strings and runtime traces too.
- JSX/TSX and template languages need the right grammar variant.
- A rename must include re-exports, type-only imports, and documentation references.
- Do not rewrite vendored dependencies; patch at the dependency boundary.

## Output contract

```json
{
  "query": "requests.get without timeout",
  "language": "python",
  "matches": [
    {
      "file": "src/client.py",
      "range": {"start_line": 42, "start_col": 5, "end_line": 42, "end_col": 38},
      "enclosing": "fetch_user",
      "symbol_resolved": "requests.get",
      "in_generated": false,
      "snippet": "requests.get(url)"
    }
  ],
  "parse_errors": [],
  "excluded": ["vendor/", "generated/"]
}
```

## Checklist

- [ ] Grammar and node types confirmed.
- [ ] Structural query written and tested on a sample.
- [ ] Scope and symbol resolution checked.
- [ ] Generated and vendored code excluded.
- [ ] Lossless edit tool used where formatting matters.
- [ ] Every modified file re-parsed.
- [ ] Tests and type checks pass.
- [ ] Diff reviewed for unintended changes.

## Related skills

- `semantic-codebase-search` for intent-based retrieval beyond syntax.
- `automated-refactoring-execution` for the full refactor workflow.
- `static-code-analysis-remediation` for lint-driven fixes.
