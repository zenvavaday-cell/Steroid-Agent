---
name: tool-result-caching
description: Caches tool outputs with stable keys, TTL, invalidation, and correctness checks. Use for expensive or rate-limited tools and repeated agent runs.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: agentic
---

# Tool Result Caching

## Overview

Agents repeat themselves: the same search, the same document fetch, the same FX quote, the same enrichment call. Caching tool results cuts latency and spend, but a wrong cache is worse than no cache, because a stale or cross-tenant value looks like a successful tool call.

The discipline is a correct key, a justified TTL, explicit invalidation, protection against stampedes, and a way to prove cached values still match the source.

## When to use

- A read-only tool is slow, metered, or rate-limited.
- The same request repeats within a run, across runs, or across users.
- A tool returns slowly changing reference data (docs, catalog, FX, geocoding).
- Evaluation or replay reruns identical tool sequences.
- An upstream dependency has outages and stale reads are acceptable.
- Fan-out causes duplicate calls for the same key.

Do not use for side-effecting calls (payments, sends, writes) or for per-user confidential responses without strict partitioning.

## Workflow

1. **Classify each tool.** Mark it cacheable read, cacheable with tenant scope, stale-tolerant read, or never cache (writes, secrets, real-time pricing). Record the owner and the freshness requirement for each tool.

2. **Build a canonical cache key.** Hash a canonical object, not a raw JSON string:

```python
import hashlib, json, unicodedata

def cache_key(tool, version, args, scope):
    canonical = {
        "tool": tool,
        "tool_version": version,
        "args": normalize(args),          # sort keys, NFKC, trim, drop None
        "tenant": scope.tenant_id,
        "principal": scope.principal_hash, # hash of auth context, not the token
        "locale": scope.locale,
    }
    blob = json.dumps(canonical, sort_keys=True, separators=(",", ":"))
    return "tres:v3:" + hashlib.sha256(blob.encode()).hexdigest()
```

Include every input that changes the answer: auth scope, locale, units, feature flags, and API version. Exclude request ids and timestamps.

3. **Store a bounded envelope.** Keep payload, `created_at`, `expires_at`, `source_etag`, `key_version`, `sensitivity`, and a checksum. Cap value size (for example 256 KB) and refuse to cache larger responses; store a reference instead.

4. **Set TTL by volatility, not by convenience.** Example policy:

| Data class | TTL | Revalidation | Notes |
| --- | --- | --- | --- |
| Static docs | 24 h | ETag | Invalidate on publish event |
| Catalog and prices | 15 min | ETag | Per-tenant currency |
| FX and market quotes | 30 s | none | Label timestamp in answer |
| User profile lookup | 5 min | none | Per-user partition |
| Search results | 10 min | none | Query normalization matters |
| Anything personalized | 0 (no shared cache) | n/a | Per-session only |

Add 0 to 20% random jitter to TTLs to avoid synchronized expiry.

5. **Invalidate on writes and deploys.** Publish invalidation events tagged by resource id when the source changes. Bump the key namespace on tool schema or prompt changes. Treat TTL as a backstop, not the primary consistency mechanism.

6. **Control stampedes.** Use single-flight per key so 100 concurrent misses produce one backend call. Serve stale within a grace window when the backend errors, and mark the response `stale: true`. Apply a per-tool concurrency limit and a circuit breaker.

7. **Partition for privacy, prove correctness, and measure value.** Never share entries across tenants or principals unless the tool is explicitly public. Encrypt values, exclude secrets, and honor deletion. Sample 0.5 to 1% of hits and re-fetch to measure the mismatch rate; alert above 1%. Emit hit rate, stale serves, evictions, backend calls avoided, latency saved, and cost saved.

## Validation

| Gate | Test | Pass |
| --- | --- | --- |
| Key stability | Same logical args in different key order | Identical key |
| Scope isolation | Tenant A reads tenant B key | Miss or denial, never a hit |
| Expiry | Advance a fake clock past TTL | Refetch occurs |
| Invalidation | Write resource, then read | Fresh value within 1 s |
| Stampede | 100 concurrent misses | Exactly 1 backend call |
| Corruption | Inject malformed envelope | Treated as miss, no crash |
| Deletion | Delete a subject's data | Entries and derived values removed |
| Correctness | Sampled re-fetch comparison | Mismatch rate under 1% |

A failed gate blocks enabling the cache for that tool.

## Gotchas

- A key that omits auth scope leaks one user's data to another. Include tenant and principal.
- One TTL for all data serves stale prices or evicts static docs too early. Set per class.
- Caching errors and empty results turns a blip into a long outage. Negative-cache briefly or not at all.
- Caching a write can report success for an effect that never happened. Never cache side effects.
- TTL without invalidation serves stale data for the full window after a write.
- Expiry without jitter or single-flight causes a thundering herd.
- Unbounded payloads exhaust memory. Cap size and compress.
- Reusing keys after a schema change feeds old values to a new parser. Version the namespace.
- Per-process caches in an autoscaled fleet give inconsistent hits and low global hit rate. Use a shared cache.
- Personal data cached past a deletion request violates policy. Tag sensitivity and purge.
- Clock skew between nodes changes effective expiry. Use server-side TTL.
- Hit rate alone hides incorrect hits. Sample and verify against the source.

## Output contract

```json
{
  "key": "tres:v3:5f1c...",
  "tool": "catalog.lookup",
  "status": "hit",
  "age_s": 412,
  "ttl_s": 900,
  "stale": false,
  "source_etag": "W/\"a91f\"",
  "value_bytes": 18240,
  "backend_calls_avoided": 1,
  "latency_saved_ms": 640,
  "cost_saved_usd": 0.002,
  "verification": {"sampled": false, "mismatch": null}
}
```

## Checklist

- [ ] Every tool classified as cacheable or never-cache.
- [ ] Cache key canonical and includes scope and version.
- [ ] Envelope has TTL, checksum, source etag, and sensitivity label.
- [ ] TTL set per data class with jitter.
- [ ] Invalidation events wired for writes and deploys.
- [ ] Single-flight prevents stampedes.
- [ ] Stale serving is bounded and labeled.
- [ ] Tenant and principal isolation tested.
- [ ] Size cap and eviction policy configured.
- [ ] Deletion purges cached personal data.
- [ ] Hit rate, stale rate, and mismatch rate monitored.
- [ ] Sampled re-fetch correctness check running.

## Related skills

- `bounded-multi-tool-orchestration` for idempotency keys and retry rules that caching must not bypass.
- `latency-budget-orchestration` for using stale or cached results in the degradation ladder.
- `cost-aware-model-routing` for including cache hit rates in cost per successful task.
- `agent-observability-tracing` for cache hit and miss spans that explain latency and spend.
