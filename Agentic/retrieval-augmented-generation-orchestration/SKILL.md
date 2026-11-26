---
name: retrieval-augmented-generation-orchestration
description: Plans chunking, retrieval, reranking, and grounded answer assembly with citation and fallback. Use for knowledge assistants and document Q&A.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: agentic
---

# Retrieval-Augmented Generation Orchestration

## Overview

A RAG system is an assembly line: parse, chunk, index, retrieve, rerank, pack, generate, and verify. Most failures blamed on the model originate earlier in the line: a table split across chunks, an ACL filter applied after retrieval, a reranker threshold never calibrated, or a context packed with near-duplicates.

Treat each stage as measurable. A good answer requires the right evidence to survive every stage and arrive in the context with enough provenance to cite it.

## When to use

- Building a knowledge assistant over documents, tickets, policies, or contracts.
- Document Q&A where answers must cite sources.
- Support or internal search that needs abstention instead of confident guessing.
- Adding retrieval to an agent that already has tools.
- Diagnosing wrong, stale, or uncited answers in an existing RAG pipeline.
- Evaluating a retrieval or reranking change before rollout.

Do not use for questions that require a live transactional lookup (query the database directly) or for a corpus small enough to include in full on every request.

## Workflow

### 1. Define the answer contract and evidence policy

Before choosing a vector database, decide what a valid answer looks like.

| Question type | Evidence rule | Allowed behavior |
| --- | --- | --- |
| Single-fact lookup | One span that states the fact | Answer with citation |
| Multi-hop | Spans covering each hop | Answer with one citation per hop |
| Comparative | Comparable sources for both sides | Answer, note any asymmetry |
| Procedural | Current authoritative procedure | Answer, cite version and date |
| Unanswerable | No supporting span exists | Abstain with reason |
| Conflicting sources | Sources disagree | Present both, prefer newer or higher authority |
| Out of scope | Not covered by corpus | Refuse and route |

Set freshness rules per document class. A policy from 2023 may not answer a 2026 question.

### 2. Chunk with structure and metadata

Chunk boundaries should follow document structure, not a fixed character count.

| Content | Chunking rule | Target size |
| --- | --- | --- |
| Prose and reports | Heading-aware paragraphs | 400 to 800 tokens, 10 to 15% overlap |
| Policies and contracts | One clause or section per chunk | 150 to 600 tokens |
| Tables | Header repeated with each row group | 5 to 20 rows |
| Code | Function or method boundaries | One definition |
| FAQs | One question and answer | As short as the pair |
| Transcripts | Speaker turns with timestamps | 300 to 600 tokens |

Use parent-child retrieval: embed small children (200 to 300 tokens) and return the larger parent (800 to 1200 tokens) to the generator. Every chunk carries `doc_id`, `chunk_id`, `parent_id`, `source_uri`, `title`, `section`, `page`, `effective_date`, `version_hash`, `tenant_id`, and `acl_groups`.

Reject chunks that are only navigation, headers, or boilerplate. Keep the raw extraction so you can re-chunk without re-parsing.

### 3. Retrieve with hybrid search and pre-filters

Run lexical and dense retrieval in parallel, then fuse. Apply security and scope filters inside the query, never after the results arrive.

```yaml
retrieval:
  lexical:
    enabled: true
    top_k: 50
  dense:
    model: "bge-m3"
    top_k: 50
    metric: cosine
  fusion: rrf
  rrf_k: 60
  filters:
    required: [tenant_id, acl_groups, doc_type]
    effective_before: query_date
  rerank:
    model: "bge-reranker-v2-m3"
    top_n: 12
    min_score: 0.30
  diversity:
    method: mmr
    lambda: 0.7
  context:
    max_tokens: 6000
    reserve_for_answer: 1200
```

Reciprocal rank fusion combines lists without score calibration:

```text
rrf_score(d) = sum over retrievers of 1 / (k + rank_i(d)), k = 60
```

Rewrite vague or conversational queries before retrieval. Decompose multi-hop questions into sub-questions and retrieve for each. Do not let the rewrite add facts that were not in the question.

### 4. Rerank, deduplicate, and select

A cross-encoder reranker on the top 50 usually improves precision more than raising top-k. After reranking:

- Drop chunks below the calibrated relevance threshold.
- Deduplicate exact hashes and near-duplicates with shingle overlap above 0.85.
- Prefer the newest version when the same document appears twice.
- Apply MMR if the top results are near-identical.
- Keep at least one chunk per required sub-question for multi-hop queries.

Calibrate `min_score` on labeled pairs. A threshold copied from another corpus is usually wrong.

### 5. Pack context under a token budget

```python
def pack_context(chunks, max_tokens, count_tokens):
    ordered = sorted(chunks, key=lambda c: c["rerank_score"], reverse=True)
    selected, used, seen = [], 0, set()
    for chunk in ordered:
        key = (chunk["doc_id"], chunk["version_hash"], chunk["text"][:200])
        if key in seen:
            continue
        cost = count_tokens(chunk["text"]) + 25
        if used + cost > max_tokens:
            continue
        selected.append(chunk)
        seen.add(key)
        used += cost
    if len(selected) > 2:
        selected = [selected[0]] + selected[1:-1] + [selected[-1]]
    return selected, used
```

Number chunks as `[S1]`, `[S2]` in the prompt and keep the mapping outside the model. Put the strongest evidence first and second strongest last; models attend less reliably to the middle of long contexts. Reserve tokens for instructions, the answer, and citation markers.

### 6. Generate with grounding constraints

The generation prompt must state:

- Answer only from the numbered sources.
- Cite the source number after each claim: `Revenue grew 12% [S3].`
- If sources conflict, say so and cite both.
- If the sources do not contain the answer, return `insufficient_evidence` and list what is missing.
- Do not use parametric knowledge unless explicitly allowed and labeled.
- Quote numbers exactly; do not recompute unless asked.

Prefer extractive spans for high-stakes answers, then paraphrase around them.

### 7. Verify and follow the fallback ladder

Check every citation against the chunk text and every number against its source. A citation that points to the right document but the wrong span is a failure.

Fallback order:

1. Retry retrieval with rewritten or decomposed queries.
2. Broaden filters only within the user's ACL.
3. Ask one clarifying question if the request is ambiguous.
4. Abstain with `insufficient_evidence` and list the missing information.
5. Escalate to a human or a different tool.

Never relax ACL or freshness rules to avoid abstaining.

## Validation

Build a golden set of at least 100 questions across intents, including 20% unanswerable and 10% with conflicting or stale sources. Label the supporting spans, not just the document.

```bash
python -m evals.rag run --dataset evals/rag_golden.jsonl --config config/rag.yaml
python -m evals.rag report --run runs/rag-latest --slices intent,freshness,tenant
```

Gates (example targets, calibrate to domain risk):

- [ ] Recall@20 is at least 0.85 and nDCG@10 at least 0.70.
- [ ] Citation precision is at least 0.95; every citation resolves to a real span.
- [ ] Unsupported claim rate is at most 2% on answerable questions.
- [ ] Abstention recall is at least 0.90 on unanswerable questions.
- [ ] Cross-tenant ACL leak count is zero (hard gate).
- [ ] Stale-source answers cite the effective date and do not present old policy as current.
- [ ] p95 end-to-end latency is within the product budget, for example 3 seconds for interactive chat.
- [ ] A document containing injected instructions does not alter tool calls or output format.
- [ ] Reindexing the corpus reproduces the same chunk IDs and metadata hashes.

## Gotchas

- Fixed-size chunking splits tables, clauses, and code blocks. Chunk on structure and keep headers with rows.
- Changing the embedding model without reindexing mixes incompatible vector spaces. Version the index and rebuild.
- Filtering ACLs after retrieval leaks snippets through logs, reranker scores, or error messages. Filter inside the query.
- Raising top-k adds distractors and cost. Rerank and threshold instead.
- A reranker threshold from another corpus causes over-abstention or noise. Calibrate on labeled pairs.
- Near-duplicate chunks crowd out coverage. Deduplicate and diversify.
- Long contexts suffer from middle-position loss. Place strong evidence at the start and end.
- A stale index answers yesterday's question. Track document versions and reindex on change.
- Citing a document is weaker than citing a span. Store offsets and verify them.
- Questions and documents use different language. Query rewriting helps, but rewriting can invent constraints.
- Over-strict grounding refuses answerable questions. Measure abstention on both answerable and unanswerable sets.
- Metadata often disappears during reindexing. Treat it as part of the chunk contract and test it.
- Multi-hop questions fail with single-shot retrieval. Decompose and retrieve per hop.
- Eval questions leaked into prompts inflate scores. Keep a held-out set and check contamination.

## Output contract

```json
{
  "answer": "Revenue grew 12% in fiscal 2025 [S2].",
  "status": "answered",
  "citations": [
    {"marker": "S2", "doc_id": "10k-fy2025", "chunk_id": "c-014", "page": 42, "span": "Net sales increased 12% ..."}
  ],
  "sources_used": 4,
  "context_tokens": 5120,
  "retrieval": {"query": "fiscal 2025 revenue growth", "candidates": 96, "reranked": 12, "selected": 4},
  "confidence": 0.93,
  "fallback": null,
  "trace_id": "rag-2026-11-26-0042"
}
```

For abstention, set `status` to `insufficient_evidence`, keep `answer` empty or explanatory, and populate `fallback` with the attempted steps.

## Checklist

- [ ] Answer contract and evidence policy defined per question type.
- [ ] Chunking follows document structure and preserves metadata.
- [ ] Parent-child retrieval keeps context coherent.
- [ ] Hybrid retrieval with pre-filters, including ACL and tenant.
- [ ] Reranker threshold calibrated on labeled data.
- [ ] Deduplication and diversity applied.
- [ ] Context packed within budget with citation markers.
- [ ] Generation prompt requires per-claim citations and abstention.
- [ ] Citations verified against exact spans.
- [ ] Fallback ladder defined and ACL-safe.
- [ ] Golden set includes unanswerable, stale, and conflicting cases.
- [ ] Retrieval and answer metrics tracked per slice.

## Related skills

- `source-grounded-citation-verification` for checking each claim against its cited span.
- `embedding-index-management` for index type, recall, refresh, and cost tradeoffs.
- `prompt-injection-defense` for treating retrieved documents as untrusted data.
- `confidence-threshold-output-gating` for routing low-confidence answers to review.
