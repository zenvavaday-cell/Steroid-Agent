---
name: semantic-codebase-search
description: Finds code by intent using hybrid lexical, structural, and embedding search, then returns file-and-line evidence with surrounding context. Use for onboarding, impact analysis, locating implementations, and answering "where is this handled?" across large or unfamiliar repositories.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: engineering
---

# Semantic Codebase Search

## Overview

Code search fails in two directions: keyword search misses renamed concepts, and embeddings miss exact identifiers, error strings, and config keys. Use both, plus syntax-aware chunking and symbol lookup. Then read the actual code before answering.

The output is evidence, not a vibe. Every claim cites `path:line`.

## When to use

- "Where is authentication enforced?"
- "Which code sends the welcome email?"
- "What calls this function?"
- Onboarding to an unfamiliar repository.
- Impact analysis before a change.
- Finding prior art for a new feature.

## Workflow

### 1. Map the repository

```bash
fd -t f -e py -e ts -e tsx -e go -e rs -e java | head -200
rg -n --hidden -g '!.git' -g '!node_modules' -g '!vendor' "^(package|module|import|from) " | head
```

Identify languages, build files, entry points, and generated or vendored directories. Exclude them from the index.

### 2. Run lexical search first for exact anchors

Use `rg` for identifiers, error messages, config keys, and route paths:

```bash
rg -n "send_welcome_email|welcome_email" --type py
rg -n -F "SMTPConnectionError" .
rg -n "POST /api/v1/users" .
```

Exact matches are high precision and cheap. Do not skip this step.

### 3. Run structural search for code shapes

```bash
sg run -p 'def $FUNC($$$ARGS): $$$BODY' -l python src/
sg run -p 'app.get($PATH, $HANDLER)' -l javascript src/
```

Use `abstract-syntax-tree-navigation` for complex queries, symbol resolution, and call graphs.

### 4. Build a semantic index

Chunk by symbol, not by fixed line count:

- One function or method per chunk.
- Include the file path, language, symbol name, signature, docstring, and imports.
- Keep a small overlap for long functions.
- Store the start and end line.

```python
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_chunks(chunks):
    texts = [f"{c['path']}\n{c['symbol']}\n{c['source']}" for c in chunks]
    vectors = model.encode(texts, normalize_embeddings=True)
    return vectors

def search(query, vectors, chunks, k=20):
    q = model.encode([query], normalize_embeddings=True)[0]
    scores = vectors @ q
    order = np.argsort(scores)[::-1][:k]
    return [(chunks[i], float(scores[i])) for i in order]
```

For a repository of moderate size, a local FAISS or numpy index is enough. Rebuild on commit or use incremental indexing.

### 5. Combine and rerank

Merge lexical, structural, and semantic results with reciprocal rank fusion:

```python
def rrf(rank_lists, k=60):
    scores = {}
    for ranks in rank_lists:
        for position, doc_id in enumerate(ranks, start=1):
            scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + position)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)
```

Then rerank the top 20 with a cross-encoder or by reading the code. Semantic similarity is a retrieval hint, not evidence.

### 6. Read the evidence

For each candidate:

- Open the file and read the full function plus callers.
- Confirm the symbol is the one used at runtime, not a duplicate or a test double.
- Check imports, aliases, and dynamic dispatch.
- Trace the call path from an entry point.
- Note version, branch, and commit.

### 7. Answer with citations

```markdown
Authentication is enforced in `src/api/middleware/auth.py:42`
(`require_user`), which is applied to the router in
`src/api/routes.py:18`. Token verification calls
`src/auth/tokens.py:77` (`verify_jwt`).
```

If evidence is incomplete, say so. Do not fill gaps with plausible architecture.

## Gotchas

- Embeddings miss exact identifiers, error codes, and rare terms. Always run lexical search too.
- Chunking by line count splits functions and loses context. Chunk by symbol.
- The index goes stale after a pull. Record the commit and rebuild or invalidate.
- Generated, vendored, and minified code pollutes results. Exclude by path.
- Test code often matches the query but is not the production path. Label it.
- Duplicate symbols across packages require import resolution.
- Monorepos need per-package indexes and cross-package dependency awareness.
- Secrets and sensitive code can leak into embeddings or logs. Use a local model and restrict access.
- Semantic similarity can rank a plausible but irrelevant function highly. Read before citing.
- Language-specific tokenizers matter for code. A general text model may underperform.

## Output contract

```json
{
  "query": "where is the welcome email sent",
  "commit": "abc123",
  "results": [
    {
      "path": "src/notifications/welcome.py",
      "symbol": "send_welcome_email",
      "lines": [18, 44],
      "evidence": "calls mailer.send with template 'welcome'",
      "callers": ["src/api/users.py:88"],
      "confidence": "high"
    }
  ],
  "excluded": ["tests/", "vendor/", "generated/"],
  "gaps": ["no coverage of the admin invite flow"]
}
```

## Checklist

- [ ] Repository mapped and exclusions defined.
- [ ] Lexical search run for exact anchors.
- [ ] Structural search run for code shapes.
- [ ] Semantic index built from symbol-level chunks.
- [ ] Results fused and reranked.
- [ ] Evidence read in full context.
- [ ] Call path traced from an entry point.
- [ ] Answer cites path and line.
- [ ] Index freshness recorded.

## Related skills

- `abstract-syntax-tree-navigation` for precise structural queries.
- `dead-code-elimination` for using search results to remove code.
- `automated-refactoring-execution` for acting on the findings.
