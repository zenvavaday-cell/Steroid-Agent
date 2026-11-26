---
name: journal-entry-fraud-testing
description: Tests journal entries for Benford, round-number, timing, unusual-pairing, and segregation-of-duties anomalies. Use for audit analytics and internal controls testing.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: finance
---

# Journal Entry Fraud Testing

## Overview

Journal entries are the most direct way to move profit between periods, hide a liability, or extract cash. Fraud testing looks for statistical and behavioral patterns that are rare in legitimate postings but common in manipulation: amounts just under approval limits, entries dated on weekends, rare account pairings, and users who can both create and approve.

An anomaly is a lead, not a conclusion. The output of this skill is a ranked, evidence-backed population for investigation, with false positives explained and the audit trail preserved.

## When to use

- Annual or interim audit analytics over the general ledger.
- Internal controls testing of manual journal entries and approvals.
- Investigating a whistleblower allegation or an unexplained margin shift.
- Pre-close review of high-risk entities, accounts, or users.
- Designing continuous monitoring rules for the finance function.
- Supporting a forensic accounting engagement with a documented method.

Do not use to accuse an individual, to monitor employees outside an approved audit scope, or on data you are not authorized to access.

## Workflow

### 1. Acquire a read-only, complete extract

Pull header and line data for the full period plus a prior comparison period. Minimum fields:

| Field | Why it matters |
| --- | --- |
| journal_id, line_no | Unique key and line integrity |
| entity, ledger, source_system | Scope and system-generated versus manual |
| entry_type, reversal_flag | Manual, top-side, accrual, reversal |
| entered_by, approved_by, entered_at, posted_at | SoD and timing tests |
| accounting_period, document_date | Cut-off and backdating |
| account_code, cost_center, counterparty | Pairing and concentration |
| debit, credit, currency, amount_reporting | Value tests and normalization |
| description, attachment_ref | Text screening and evidence |

Hash the extract (`sha256sum`) and store the hash with the workpaper. Reconcile row counts, total debits, total credits, and net movement to the trial balance before running any test.

### 2. Normalize and classify the population

- Convert all amounts to one reporting currency at a documented rate.
- Use `abs(debit - credit)` as the entry amount and keep the sign.
- Separate system-generated postings from manual entries. Most statistical tests belong on manual entries, or on manual entries plus top-side consolidation entries.
- Pair accruals with reversals within the period so the same amount is not counted twice.
- Exclude assigned or sequential numbers (invoice IDs, check numbers, account codes) from Benford tests.

### 3. Run Benford and digit tests

First-digit expected probability is `log10(1 + 1/d)`.

```python
import math
from collections import Counter

def benford(amounts):
    amounts = [abs(a) for a in amounts if a and abs(a) >= 1]
    n = len(amounts)
    if n < 300:
        return {"n": n, "warning": "sample too small for reliable first-digit test"}
    counts = Counter(int(str(int(a))[0]) for a in amounts)
    rows = []
    mad = 0.0
    for d in range(1, 10):
        expected = math.log10(1 + 1 / d)
        actual = counts[d] / n
        mad += abs(actual - expected)
        rows.append({"digit": d, "expected": expected, "actual": actual})
    return {"n": n, "mad": mad / 9, "rows": rows}
```

Commonly cited first-digit MAD bands (Nigrini) are: below 0.006 close conformity, 0.006 to 0.012 acceptable, 0.012 to 0.015 marginal, above 0.015 nonconformity. Treat these as calibration starting points, not proof. Report chi-square with 8 degrees of freedom and the 0.05 critical value of 15.507, and always report sample size.

### 4. Test round numbers and approval thresholds

Flag amounts divisible by 1,000, 10,000, or 100,000, and amounts in the 90% to 100% band below a known approval limit. Join to the approval matrix:

```sql
SELECT j.journal_id, j.entered_by, j.approved_by,
       l.account_code, l.amount_reporting, a.limit_amount
FROM je_lines l
JOIN je_header j ON j.journal_id = l.journal_id
JOIN approval_matrix a
  ON a.entity = j.entity AND a.role = j.entered_by_role
WHERE l.amount_reporting >= 0.90 * a.limit_amount
  AND l.amount_reporting <  a.limit_amount
  AND j.entry_type = 'manual';
```

Legitimate accruals often land on round numbers, so rank these by user, account, and period rather than flagging every occurrence.

### 5. Test timing and cut-off

| Test | Rule | Interpretation |
| --- | --- | --- |
| Weekend or holiday | Posted on non-business day | Manual override or batch job, check source |
| Backdating | document_date in a prior period, posted in current period | Possible cut-off manipulation |
| Late posting | posted_at more than 30 days after document_date | Weak close discipline or concealment |
| Period-end spike | Share of entries in last 2 days above 2x the daily average | Earnings management risk |
| Odd hour | Posted between 00:00 and 05:00 local time | Investigate with user context |
| Reversal abuse | Accrual reversed through a different account or entity | Income statement shift |

Compare the current period to at least one prior period. A single weekend entry is noise; a user with a persistent weekend pattern is a lead.

### 6. Test unusual account pairings and access conflicts

Build debit-credit account pairs and compute lift:

```
lift = observed_pair_frequency / (debit_frequency * credit_frequency)
```

Flag pairs with low historical frequency, high value, or first appearance in the current period (for example, debit revenue and credit cash). Also flag new user-account combinations and users posting to entities or cost centers outside their normal profile.

For segregation of duties, define conflict rules before querying:

```yaml
conflicts:
  - id: SOD-01
    rule: entered_by == approved_by
  - id: SOD-02
    rule: user has both vendor_master_maintain and payment_approve
  - id: SOD-03
    rule: user has both je_post and je_approve for the same entity
  - id: SOD-04
    rule: user has both customer_master_maintain and credit_limit_approve
```

Join role assignments to the HR or identity system, then confirm whether a compensating control exists before reporting a deficiency.

### 7. Score, sample, and investigate

Assign weights to each indicator, for example: threshold proximity 25, SoD conflict 20, unusual pairing 20, timing 15, round number 10, Benford deviation 10. Score at the journal level, then sample:

- 100% of entries above the monetary top-stratum threshold.
- 100% of entries with two or more high-weight indicators.
- A random sample of the remainder, with a documented seed and sample size.

For each selected item, obtain the supporting document, the business rationale, the approver, and the accounting treatment. Record a disposition: explained, control deficiency, or referred for investigation.

## Validation

| Gate | Test | Fail action |
| --- | --- | --- |
| Completeness | Extract row count and totals tie to GL control totals | Re-extract before testing |
| Balance | Total debits equal total credits within each journal | Fix extract or query |
| Period coverage | Every day in scope present, including zero-entry days | Fill gaps or document |
| Normalization | FX conversion rate and date documented per currency | Reconvert |
| Benford suitability | Sample size, exclusions, and digit level reported | Do not conclude |
| Threshold join | Approval matrix version and effective dates match the period | Rejoin |
| SoD evidence | Role data sourced from the identity system, not guessed | Requery |
| Sample integrity | Population, seed, and selection method reproducible | Redraw |
| Evidence chain | Hash, extract timestamp, and custodian recorded | Recreate workpaper |
| Review | Second reviewer signs off on conclusions | Hold report |

## Gotchas

- Benford does not apply to assigned, sequential, or bounded numbers. Invoice IDs, account codes, and fixed-fee amounts will fail by construction.
- Small samples produce large random deviations. Below roughly 300 amounts, report the test as inconclusive rather than a finding.
- Round-number flags catch legitimate accruals, rent, and payroll. Calibrate to the approval matrix and rank by repetition.
- Automated batch postings often run at night or on weekends. Classify source system before treating timing as suspicious.
- Period 13, adjustment periods, and late-close entries distort period-end comparisons. Align the calendar first.
- A user posting and approving the same entry may be a small-team compensating control, not a fraud. Test whether review evidence exists.
- Mixing currencies in one amount distribution creates artificial digit patterns. Convert or test per currency.
- Reversals double-count amounts and inflate both Benford and round-number results. Pair them before scoring.
- Top-side consolidation entries may have no line-level detail. Request the consolidation workpaper instead of assuming absence of detail means no risk.
- Sampling only flagged items guarantees confirmation bias. Keep a random control sample.
- An indicator score is not a probability of fraud. Do not put scores in performance reviews or disciplinary files.
- User IDs are personal data. Restrict access, retain only what the engagement needs, and follow the audit data retention policy.

## Output contract

```json
{
  "engagement": "FY2026 interim audit",
  "scope": {"entities": ["USCo", "UKCo"], "period_start": "2025-10-01", "period_end": "2026-09-30"},
  "population": {"journals": 184220, "manual_journals": 9120, "amount_reporting": 4120000000},
  "control_totals": {"debits": 4120000000, "credits": 4120000000, "tie": true},
  "tests": [
    {"name": "benford_first_digit", "sample": 8420, "mad": 0.009, "chi_square": 21.4, "result": "deviation"},
    {"name": "round_number", "flagged": 412, "rate": 0.045},
    {"name": "weekend_posting", "flagged": 88, "rate": 0.0096},
    {"name": "threshold_proximity", "flagged": 37, "rate": 0.0041},
    {"name": "unusual_pairing", "flagged": 64, "rate": 0.007},
    {"name": "sod_conflict", "flagged": 12, "rate": 0.0013}
  ],
  "findings": [
    {
      "journal_id": "JE-2026-091842",
      "score": 70,
      "indicators": ["threshold_proximity", "weekend_posting", "entered_approved_same_user"],
      "amount_reporting": 49850,
      "entities": ["USCo"],
      "disposition": "referred",
      "evidence": ["approval_matrix_v4", "JE PDF", "role_export_2026-10-02"],
      "owner": "internal-audit-lead"
    }
  ],
  "false_positive_themes": ["monthly rent accrual at round amount", "batch payroll on Saturday"],
  "limitations": ["role data lag of 5 days", "two entities on a different ERP"],
  "prepared_by": "audit.analytics",
  "reviewed_by": "audit.manager",
  "extract_hash": "sha256:..."
}
```

## Checklist

- [ ] Authorization and scope documented before extraction.
- [ ] Read-only extract hashed and reconciled to control totals.
- [ ] Manual versus system-generated entries classified.
- [ ] FX normalization rate and date recorded.
- [ ] Benford sample size, digit level, and exclusions reported.
- [ ] Round-number and approval-threshold tests joined to the correct matrix version.
- [ ] Timing tests compare against a prior period.
- [ ] Unusual pairing lift calculated on a stable baseline.
- [ ] SoD rules defined before querying role data.
- [ ] High-risk population fully tested plus a random control sample.
- [ ] Every finding has evidence, disposition, and owner.
- [ ] Second reviewer signs off before distribution.

## Related skills

- `automated-ledger-reconciliation` for tie-outs that establish the population is complete.
- `transaction-anomaly-flagging` for transaction-level detection beyond journals.
- `anti-money-laundering-screening` when the concern extends to counterparties and flows.
- `confidence-threshold-output-gating` before escalating a finding to legal or HR.
