---
name: process-mining-analysis
description: Reconstructs processes from event logs and finds bottlenecks, rework, and automation opportunities. Use for operations improvement and compliance.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: business-ops
---

# Process Mining Analysis

## Overview

Process mining reconstructs what actually happens from system event logs, rather than what the process diagram says should happen. The value comes from three questions: which paths do cases take, where does time accumulate, and which steps repeat because of errors or missing information.

The discipline is to validate the event log before trusting any model, separate waiting time from touch time, quantify variants and rework, and confirm findings with the people who run the process. An unvalidated log produces a confident and wrong story.

## When to use

- A process is slow, inconsistent, or expensive and the cause is disputed.
- Auditing whether a documented process is followed in practice.
- Quantifying rework, handoffs, and exception rates before automation.
- Comparing cycle time across regions, teams, systems, or time periods.
- Preparing evidence for a compliance or internal-control review.

Do not use when no system records timestamps and case identifiers, or when the process is fully manual and unlogged; use observation and time studies instead.

## Workflow

### 1. Define the event log schema

One row per event. The minimum columns are case identifier, activity, timestamp, and resource. Add lifecycle transition, attributes, and a source system.

| Column | Example | Rule |
| --- | --- | --- |
| case_id | ORD-10482 | Stable across the case lifetime |
| activity | Credit check | Controlled vocabulary, verb plus object |
| timestamp | 2026-11-03T14:22:05Z | ISO 8601 with timezone, UTC preferred |
| resource | agent_017 | Pseudonymized before analysis |
| lifecycle | complete | start, complete, schedule, suspend |
| attributes | region=EMEA, amount=4200 | Typed and documented |

### 2. Extract and normalize

Pull events from the systems of record (ERP, CRM, ticketing, workflow). Normalize activity names, map local timestamps to UTC, deduplicate retries, and drop test cases. Keep a raw snapshot and a versioned transformed table so the analysis is reproducible.

```python
import pandas as pd

cols = ["case_id", "activity", "timestamp", "resource"]
df = pd.read_csv("events_raw.csv", usecols=cols, parse_dates=["timestamp"])
df = (
    df.drop_duplicates()
      .dropna(subset=cols)
      .sort_values(["case_id", "timestamp"])
)
df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
print(df.groupby("case_id").size().describe())
```

### 3. Validate the log before discovery

Report coverage, completeness, and monotonicity. Stop and fix the extraction if the log fails the gates; do not tune the model around bad data.

| Check | Method | Threshold |
| --- | --- | --- |
| Case coverage | Cases with at least one event | 100% |
| Start and end | Cases with both boundaries | At least 95% |
| Monotonic time | No negative gap within a case | 100% |
| Duplicates | Exact duplicate event rows | Below 1% |
| Activity vocabulary | Share of labels outside the approved list | Below 2% |
| Window coverage | Events per week versus source counts | Within 5% |

### 4. Discover variants

A variant is the ordered sequence of activities for one case. Count variants and their share. The top variant is the happy path; the tail is where cost and risk live.

```python
variants = (
    df.groupby("case_id")["activity"]
      .agg(" -> ".join)
      .value_counts(normalize=True)
)
print(variants.head(10))
print("variants:", variants.size)
print("top 5 share:", variants.head(5).sum().round(3))
```

Use PM4Py for a process model and conformance metrics when the log is XES or convertible:

```python
import pm4py

log = pm4py.read_xes("events.xes")
net, im, fm = pm4py.discover_petri_net_inductive(log)
fitness = pm4py.fitness_token_based_replay(log, net, im, fm)
precision = pm4py.precision_token_based_replay(log, net, im, fm)
print(fitness, precision)
```

A fitness of 1.0 with a model that allows every behavior is useless. Report fitness and precision together and inspect the model for over-generalization.

### 5. Analyze time by activity and transition

Compute case cycle time from first to last event. Split it into touch time and waiting time. Waiting time is the gap between the completion of the previous activity and the start of the next; it is usually where the delay is.

```python
df["prev_end"] = df.groupby("case_id")["timestamp"].shift(1)
df["wait_min"] = (df["timestamp"] - df["prev_end"]).dt.total_seconds() / 60
print(df.groupby("activity")["wait_min"].describe(percentiles=[0.5, 0.9, 0.95]))
```

Report p50, p90, and p95 rather than the mean; a few extreme cases usually drive the average. Rank bottlenecks by total waiting time, not by average per case.

### 6. Quantify rework and loops

Detect repeated activities within a case, backward transitions, reopens, and cancelled-then-restarted steps. Quantify the share of cases affected and the added cycle time. Distinguish legitimate loops (review cycles defined by policy) from defects.

| Pattern | Detection | Metric |
| --- | --- | --- |
| Repeat step | Same activity appears more than once | Share of cases, extra hours |
| Reopen | Status returns to an earlier state | Count per 100 cases |
| Backward transition | Activity order reverses versus the norm | Share of cases |
| Rework loop | Sequence A-B-A repeats | Mean loop count |

### 7. Identify automation candidates

Score candidate activities on volume, rule determinism, exception rate, data availability, and system API access. High volume with high exception rates is usually a policy problem, not an automation opportunity.

| Activity | Volume/month | Rule-based | Exception rate | API available | Priority |
| --- | --- | --- | --- | --- | --- |
| Address validation | 8,400 | Yes | 3% | Yes | High |
| Manual credit review | 1,200 | No | 38% | Partial | Low |
| Invoice coding | 6,000 | Yes | 12% | Yes | Medium |

### 8. Confirm findings with process owners

Present the top variants, the three largest waiting-time contributors, the rework rate, and the proposed automation list. Ask owners to explain each deviation. Record disagreements and adjust the analysis if the log is incomplete. Never publish individual performance rankings from resource-level data.

### 9. Handle privacy and retention

Pseudonymize resource identifiers at extraction, aggregate before sharing outside the analysis team, restrict access to case-level data, and delete raw extracts at the end of the retention period. Document the lawful basis if personal data is involved.

## Validation

| Gate | Pass criterion | Fail action |
| --- | --- | --- |
| Log completeness | At least 95% of cases have start and end events | Fix extraction |
| Timestamp integrity | No negative durations or missing timezones | Normalize and rerun |
| Variant stability | Findings hold in a second time period | Report drift |
| Conformance | Fitness and precision both reported | Add precision |
| Bottleneck evidence | Top delays confirmed by owners and raw timestamps | Re-inspect |
| Rework definition | Legitimate loops excluded from defect count | Reclassify |
| Automation case | Volume, rules, exceptions, and API access evidenced | Defer |
| Privacy | Resource IDs pseudonymized and access restricted | Block release |

## Gotchas

- Batch jobs write midnight timestamps, creating fake overnight delays. Check timestamp distribution by hour and use source event time where possible.
- Coarse timestamps (day granularity) hide queue time. Do not report minute-level bottlenecks from date-only data.
- Case identifiers can change across systems, splitting one journey into several. Build an identity map and validate it on a sample.
- Missing events look like fast steps. Compare log counts with source transaction counts per activity.
- Parallel work appears sequential in a single-resource log. Use lifecycle transitions or overlapping timestamps before calling it a delay.
- Legitimate review loops get counted as rework. Confirm the policy definition with the process owner.
- Process drift across months makes pooled averages misleading. Segment by period and report trends.
- A model with fitness 1.0 may simply allow every path. Always report precision and inspect the model.
- Activity names vary by team or language. Normalize with a mapping table and keep the raw label.
- Timezone mistakes shift events across days and reorder cases. Convert to UTC at extraction and record the source timezone.
- Resource-level analysis can become performance surveillance. Aggregate and pseudonymize unless there is a clear, approved purpose.
- The log records system events, not business intent. A cancelled order and a corrected order may look identical.

## Output contract

```json
{
  "dataset": {
    "source": "order_management",
    "window": "2026-01-01/2026-09-30",
    "cases": 18420,
    "events": 147360,
    "completeness": 0.972
  },
  "variants": {
    "count": 214,
    "top_variant_share": 0.41,
    "top_5_share": 0.68
  },
  "conformance": {
    "fitness": 0.91,
    "precision": 0.74,
    "main_deviation": "Credit check skipped for existing customers"
  },
  "cycle_time": {
    "p50_hours": 31.2,
    "p90_hours": 96.4,
    "p95_hours": 141.0,
    "touch_share": 0.18
  },
  "bottlenecks": [
    {
      "activity": "Manual credit review",
      "median_wait_hours": 19.5,
      "total_wait_hours": 1840,
      "owner": "Credit Operations"
    }
  ],
  "rework": {
    "cases_affected_share": 0.23,
    "extra_hours_median": 11.0,
    "top_loop": "Credit check -> Document request -> Credit check"
  },
  "automation_candidates": [
    {
      "activity": "Address validation",
      "monthly_volume": 8400,
      "exception_rate": 0.03,
      "priority": "high"
    }
  ],
  "caveats": ["Resource IDs pseudonymized", "Two regions excluded due to missing events"]
}
```

## Checklist

- [ ] Event log schema documented and controlled vocabulary applied.
- [ ] Raw and transformed snapshots versioned.
- [ ] Completeness, monotonicity, and duplicate checks passed.
- [ ] Variants counted with top-variant and top-5 share.
- [ ] Fitness and precision reported together.
- [ ] Cycle time split into touch and waiting time at p50, p90, p95.
- [ ] Rework patterns defined and legitimate loops excluded.
- [ ] Automation candidates scored on rules, volume, and exceptions.
- [ ] Findings reviewed with process owners.
- [ ] Privacy controls applied and retention set.
- [ ] Caveats and excluded populations documented.

## Related skills

- `etl-pipeline-generation` for reproducible extraction and transformation of event data.
- `warehouse-schema-design` for the event table grain, keys, and partitioning.
- `operational-runbook-generation` for turning confirmed bottlenecks into operational fixes.
- `causal-inference-analysis` before claiming that a process change caused a cycle-time improvement.
