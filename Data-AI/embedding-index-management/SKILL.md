---
name: embedding-index-management
description: Chooses, builds, and maintains vector indexes with recall, latency, cost, and refresh tradeoffs. Use for semantic search and RAG infrastructure.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: data-ai
---

# Embedding Index Management

## Overview

A vector index is a latency and recall budget traded against memory and money. The same corpus can be served by HNSW in RAM, IVF-PQ on a smaller footprint, or DiskANN on SSD, and each choice changes what users retrieve, what the p95 looks like, and what a rebuild costs.

The discipline is to measure recall against exact search on a labeled query set, tune parameters against that measurement, pin the embedding model to the index, and treat every model or schema change as a reindex event rather than an in-place mutation.

## When to use

- Standing up semantic search, RAG retrieval, deduplication, or recommendation candidate generation.
- Choosing between pgvector, FAISS, Qdrant, Weaviate, Milvus, or a managed vector service.
- Recall has dropped or latency has risen on an existing index.
- Changing embedding model, dimension, chunking strategy, or distance metric.
- Adding metadata filters or hybrid keyword-plus-vector retrieval.
- Planning index growth, sharding, or cost reduction.
- Do not use for exact nearest-neighbor needs on fewer than roughly 10,000 vectors where a brute-force scan already meets latency.

## Workflow

### 1. Set retrieval SLOs before choosing technology

Define these numbers with the product owner:

| Requirement | Example target | Why it constrains the index |
| --- | --- | --- |
| Recall@10 | `>= 0.95` of exact search | drives HNSW `ef_search` or IVF `nprobe` |
| p95 query latency | `<= 150 ms` server-side | drives index type and quantization |
| Peak QPS | 200 with 20 concurrent | drives replicas and memory |
| Freshness | new docs visible within 5 min | drives incremental upsert vs rebuild |
| Corpus size | 12M chunks, 8 KB average | drives memory and shard count |
| Cost ceiling | $0.40 per 1M queries | drives quantization and instance size |

Without a recall target, "fast" is unfalsifiable. Without a freshness target, a nightly rebuild may be acceptable or disqualifying.

### 2. Pin the embedding contract

Record for every vector: model ID, model version or commit, dimension, normalization, distance metric, chunker version, and source document hash. Store these as filterable metadata and in a sidecar table.

- Use cosine similarity for normalized text embeddings; if vectors are L2-normalized, inner product and cosine rank identically.
- Never mix vectors from two model versions in one index. Their spaces are not comparable even at the same dimension.
- Treat a model upgrade as a new collection with a new name, then cut over.
- Keep the raw text or a pointer to it. Re-embedding requires the original content.

### 3. Choose an index type from constraints

| Situation | Index | Starting parameters | Watch |
| --- | --- | --- | --- |
| `< 5M` vectors, memory fits | HNSW | `M=16`, `ef_construction=200`, `ef_search=64` | memory about `vectors * (dim * 4 + M * 2 * 4)` bytes |
| `5M` to `100M`, memory tight | IVF-PQ or scalar-quantized HNSW | `nlist ~ 4*sqrt(n)`, `nprobe=16`, `m=16` PQ subquantizers | recall loss from compression |
| `> 100M` or SSD budget | DiskANN / IVF on disk | `R=64`, `L=100` | SSD IOPS and cold-start latency |
| Heavy metadata filters | HNSW plus payload indexes | pre-filter when selectivity `< 10%` | filtered recall collapse |
| Keyword and vector mixed | hybrid BM25 + dense with fusion | reciprocal rank fusion, `k=60` | weight tuning per query class |

Postgres with pgvector:

```sql
CREATE INDEX docs_embedding_hnsw ON docs
  USING hnsw (embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 200);

SET hnsw.ef_search = 64;
SET hnsw.iterative_scan = relaxed_order;  -- pgvector 0.8+, helps filtered queries
```

FAISS:

```python
import faiss
index = faiss.IndexHNSWFlat(dim, 16, faiss.METRIC_INNER_PRODUCT)
index.hnsw.efConstruction = 200
index.add(vectors)
index.hnsw.efSearch = 64
```

IVF indexes require training on a representative sample before adding vectors. HNSW does not, which matters for incremental corpora.

### 4. Build a labeled query set and measure recall

Sample 200 to 1,000 real queries with known relevant chunk IDs from click logs, human judgments, or synthetic questions grounded in documents. Compute exact top-k by brute force as ground truth.

```python
def recall_at_k(approx_ids, exact_ids, k=10):
    return len(set(approx_ids[:k]) & set(exact_ids[:k])) / k

# Sweep the recall/latency curve rather than picking one point.
for ef in (32, 64, 128, 256):
    index.hnsw.efSearch = ef
    recall = mean_recall(index, queries, ground_truth, k=10)
    p95 = percentile_latency(index, queries, 95)
    print(ef, round(recall, 3), round(p95, 1))
```

Pick the smallest parameter that meets recall with headroom for growth. Report recall@1, recall@10, and MRR, not a single blended score. Measure against exact search, not against a previous ANN index.

### 5. Handle filters and hybrid retrieval deliberately

Filtering changes the search problem:

- **Pre-filter** when the filter keeps less than about 10 percent of the corpus. Use payload indexes on filtered fields so the search space shrinks before graph traversal.
- **Post-filter** only when the filter is broad; it can return fewer than `k` results when selective.
- Verify recall separately per filter class. A global recall of 0.96 can hide 0.55 on `tenant_id` filters.
- For hybrid search, fuse ranked lists with reciprocal rank fusion (`score = sum(1 / (60 + rank))`) and tune on the labeled set.
- Enforce tenant isolation in the query, not only in application code.

### 6. Define refresh, compaction, and reindex triggers

| Change | Action | Downtime |
| --- | --- | --- |
| New or edited document | upsert by deterministic chunk ID, delete stale chunk IDs | none |
| Deleted document | delete vectors and tombstones, then compact | none |
| Embedding model change | build new collection, backfill, evaluate, alias swap | none with blue-green |
| Distance metric change | new collection and full rebuild | none with alias |
| Chunker change | new collection; old chunk IDs are not comparable | none with alias |
| Index parameter change | rebuild in place or new collection depending on engine | planned |

Upserts must be idempotent. Use `chunk_id = sha256(doc_id + chunker_version + chunk_index)` so reruns do not duplicate. In pgvector, updates create dead tuples; schedule `VACUUM` and monitor table bloat. In Qdrant and Milvus, deletions leave tombstones until optimization or compaction.

Blue-green cutover with a Qdrant alias:

```bash
curl -s -X POST "$QDRANT/collections/docs_v2/aliases" \
  -H 'Content-Type: application/json' \
  -d '{"actions":[{"delete_alias":{"alias_name":"docs_current"}},
                  {"create_alias":{"collection_name":"docs_v2","alias_name":"docs_current"}}]}'
```

Keep the old collection for a rollback window, then delete it on a schedule.

### 7. Monitor recall, latency, freshness, and cost

Track per collection and per filter class:

- Canary recall@10 on 100 fixed queries, hourly. Alert on a drop greater than 0.03 from the build baseline.
- p50, p95, p99 latency and QPS. Alert on p95 above the SLO for 10 minutes.
- Index size, vector count, deleted-vector ratio, and memory headroom.
- Ingestion lag: time from source commit to searchable vector. Alert above the freshness SLO.
- Embedding cost per 1M tokens and query cost per 1M requests.
- Empty-result rate and zero-click rate as user-facing signals.

## Validation

Gates before serving traffic:

- [ ] Recall@10 on the labeled query set meets the SLO with at least 0.03 headroom.
- [ ] Recall reported per filter class and per tenant where applicable.
- [ ] p95 latency measured under expected concurrency, not single-threaded.
- [ ] Every vector carries model ID, model version, dimension, and chunker version.
- [ ] No collection contains vectors from more than one model version.
- [ ] Deterministic chunk IDs make re-ingestion idempotent.
- [ ] Delete and update path tested, including tombstone compaction.
- [ ] Blue-green cutover and rollback rehearsed on a staging collection.
- [ ] Memory and disk headroom sized for 30 percent corpus growth.

```bash
python scripts/eval_index.py --collection docs_current --queries eval/queries.jsonl \
  --k 10 --ef 64 --report recall.json --fail-under 0.95
```

## Gotchas

- Comparing recall against another ANN index hides shared errors. Ground truth must come from exact search.
- Cosine on unnormalized vectors is not the same as inner product. Normalize at write time and assert the norm.
- `ef_search` set in one session may not apply through a connection pooler. Set it per transaction or in the role default.
- Selective metadata filters can drop HNSW recall sharply because the graph is traversed without the filter. Pre-filter or use iterative scan.
- Deleted vectors can still surface until compaction. Filter on `deleted_at IS NULL` as a second guard.
- Re-embedding with a new model into the same collection silently corrupts similarity. Version the collection name.
- Chunk ID churn from a whitespace change creates duplicates. Hash normalized content and chunker version.
- pgvector updates bloat the table and slow scans. Monitor dead tuples and vacuum on a schedule.
- Quantization saves memory but shifts rankings. Rerank the top 100 with full-precision vectors when quality matters.
- Truncating long documents at the model limit drops the answer span. Chunk with overlap and keep the source offsets.
- Setting `M` too high raises memory and build time without proportional recall. Sweep it, do not default to the maximum.
- A global recall number can mask a tenant or language slice with near-zero recall. Slice the evaluation.

## Output contract

```json
{
  "collection": "docs_current",
  "embedding": {"model": "bge-m3", "version": "2025-09-01", "dim": 1024, "metric": "cosine", "normalized": true},
  "index": {"type": "hnsw", "m": 16, "ef_construction": 200, "ef_search": 64},
  "corpus": {"vectors": 12400000, "size_gb": 51.2, "deleted_ratio": 0.02},
  "evaluation": {
    "queries": 800,
    "recall_at_1": 0.71,
    "recall_at_10": 0.962,
    "mrr": 0.79,
    "p95_ms": 138,
    "by_filter": {"tenant": 0.951, "language=en": 0.966, "language=ja": 0.902}
  },
  "freshness": {"ingest_lag_p95_seconds": 180, "slo_seconds": 300},
  "cost": {"embedding_usd_per_1m_tokens": 0.09, "query_usd_per_1m": 0.31},
  "cutover": {"strategy": "alias_swap", "previous_collection": "docs_v1", "rollback_window_hours": 72},
  "decision": "serve"
}
```

## Checklist

- [ ] Recall, latency, QPS, freshness, and cost targets agreed.
- [ ] Embedding model, version, dimension, metric, and normalization pinned.
- [ ] Index type chosen from corpus size, memory, and filter behavior.
- [ ] Parameters swept against exact-search ground truth.
- [ ] Recall reported by filter class and tenant.
- [ ] Deterministic chunk IDs and idempotent upserts.
- [ ] Delete, update, and compaction paths tested.
- [ ] Blue-green rebuild and alias cutover rehearsed.
- [ ] Canary recall and latency monitoring live with alert thresholds.
- [ ] Memory and disk sized for expected growth.
- [ ] Rollback collection retained for the documented window.
- [ ] Quantization rerank tested when compression is enabled.

## Related skills

- `retrieval-augmented-generation-orchestration` for chunking, reranking, and context assembly above the index.
- `semantic-codebase-search` for an applied embedding index over repository code and symbols.
- `feature-store-engineering` for keeping embedding features consistent between offline builds and online serving.
- `data-quality-profiling` for source content checks before vectors are generated.
