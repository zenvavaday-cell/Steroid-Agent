---
name: sec-filing-extraction
description: Retrieves and extracts SEC filings and XBRL facts from EDGAR, including 10-K, 10-Q, 8-K, S-1, and proxy statements, with accession numbers, periods, units, and paragraph citations. Use for financial statement analysis, due diligence, filing monitoring, or any task requiring authoritative US public-company disclosures.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: finance
---

# SEC Filing Extraction

## Overview

EDGAR is the authoritative source for US public-company disclosures. It exposes submissions, XBRL company facts, and full-text search. The hard part is not downloading a filing; it is selecting the right filing, period, unit, and tag, and preserving a citation that a reviewer can reproduce.

## When to use

- Pulling revenue, margins, debt, or guidance from 10-K/10-Q filings.
- Monitoring 8-K events, insider transactions, or activist stakes.
- Extracting risk factors, MD&A, or exhibit lists.
- Building a comparable-company dataset from XBRL.
- Due diligence on a newly public company via S-1.

## EDGAR endpoints

| Purpose | Endpoint |
| --- | --- |
| Submissions by CIK | `https://data.sec.gov/submissions/CIK##########.json` |
| Company facts (XBRL) | `https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json` |
| Concept facts | `https://data.sec.gov/api/xbrl/companyconcept/CIK##########/us-gaap/Revenues.json` |
| Frames | `https://data.sec.gov/api/xbrl/frames/us-gaap/Revenues/USD/CY2025.json` |
| Filing index | `https://www.sec.gov/Archives/edgar/data/<CIK>/<ACCESSION-NO-DASHES>/index.json` |
| Full-text search | `https://efts.sec.gov/LATEST/search-index?q=%22...%22` |

Rules:

- Send a descriptive `User-Agent` with a contact email. Requests without one may be blocked.
- Stay at or below 10 requests per second.
- Cache responses. EDGAR data is stable for filed documents.
- Use the accession number without dashes in archive paths.

## Workflow

### 1. Resolve the entity

```python
import requests

HEADERS = {"User-Agent": "research-agent contact@example.com"}
CIK = "0000320193"  # Apple
url = f"https://data.sec.gov/submissions/CIK{CIK}.json"
data = requests.get(url, headers=HEADERS, timeout=30).json()
print(data["name"], data["tickers"], data["sicDescription"])
```

CIKs are zero-padded to 10 digits. Ticker-to-CIK mapping is available from `https://www.sec.gov/files/company_tickers.json`.

### 2. Select filings

Filter `data["filings"]["recent"]` by form type, filing date, and report date. Handle pagination in `filings["files"]` for older filings.

Selection rules:

- Use the latest amendment (`10-K/A`, `10-Q/A`) only when it explicitly restates the period.
- Distinguish fiscal period from filing date.
- For 8-K, read the item numbers; not every 8-K is material.
- For proxy statements, use DEF 14A, not the annual report exhibit.

### 3. Fetch the primary document and exhibits

```python
accession = "0000320193-25-000079"
base = f"https://www.sec.gov/Archives/edgar/data/{int(CIK)}/{accession.replace('-', '')}"
index = requests.get(f"{base}/index.json", headers=HEADERS, timeout=30).json()
for item in index["directory"]["item"]:
    print(item["name"], item.get("size"))
```

Prefer the primary `.htm` document for narrative extraction. Use the XBRL instance for numeric facts. Exhibits 10.x contain material contracts; exhibit 99.x often contains earnings releases.

### 4. Extract XBRL facts

```python
facts = requests.get(
    f"https://data.sec.gov/api/xbrl/companyfacts/CIK{CIK}.json",
    headers=HEADERS, timeout=60,
).json()

gaap = facts["facts"]["us-gaap"]
revenue = (
    gaap.get("RevenueFromContractWithCustomerExcludingAssessedTax")
    or gaap.get("Revenues")
)
if revenue is None:
    raise KeyError("no revenue concept found; inspect the company's tags")
for unit, entries in revenue["units"].items():
    for e in entries:
        if e.get("form") == "10-K" and e.get("fp") == "FY":
            print(unit, e["end"], e["val"], e["accn"], e.get("frame"))
```

Every fact carries `start`, `end`, `val`, `accn`, `fy`, `fp`, `form`, `filed`, and sometimes `frame`. Preserve all of them.

### 5. Normalize

- Convert all monetary values to one currency and scale, stating the scale.
- Use the period end, not the filing date.
- For flow concepts, use the duration (`start` to `end`), not the instant.
- For balance-sheet concepts, use the instant at period end.
- Keep the original tag and unit alongside the normalized value.
- Do not sum quarterly facts unless the durations are contiguous and non-overlapping.

### 6. Validate

- Recompute gross profit = revenue − cost of revenue.
- Recompute margins from raw values, not from rounded percentages.
- Check that assets = liabilities + equity.
- Compare the XBRL value to the value in the primary document.
- Flag restatements and amended periods.
- Confirm the fiscal year end.

### 7. Cite

Use a citation that includes company, form, period, accession number, and section or tag:

```
Apple Inc., Form 10-K for fiscal year ended 2025-09-27,
accession 0000320193-25-000079, Item 7 (MD&A), XBRL tag
us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax.
```

## Gotchas

- XBRL tags are not consistent across companies or years. `Revenues` and `RevenueFromContractWithCustomerExcludingAssessedTax` may both appear.
- Units matter: USD, USD/shares, shares, pure. A value of 1,000 could be thousands or millions depending on the fact's decimals.
- `frame` values can be restated. Use the latest filing for the same period unless doing point-in-time analysis.
- 10-K/A filings may amend only part of the original. Read the amendment cover page.
- Inline XBRL in the primary document can differ from the extracted instance due to rounding.
- Full-text search covers 2001 onward and has syntax limits. Quote phrases and filter by form.
- Earnings releases in exhibit 99.1 are not audited and may use non-GAAP measures.
- Fiscal years are not calendar years. Do not map FY2025 to CY2025 without checking.

## Output contract

```json
{
  "company": "Apple Inc.",
  "cik": "0000320193",
  "form": "10-K",
  "period_end": "2025-09-27",
  "filed": "2025-10-31",
  "accession": "0000320193-25-000079",
  "source_url": "https://www.sec.gov/Archives/...",
  "facts": [
    {
      "concept": "us-gaap:Revenues",
      "value": 416161000000,
      "unit": "USD",
      "start": "2024-09-29",
      "end": "2025-09-27",
      "citation": "Item 8, Consolidated Statements of Operations"
    }
  ],
  "checks": {"assets_equal_liabilities_equity": true},
  "warnings": []
}
```

## Checklist

- [ ] CIK resolved and confirmed by name and ticker.
- [ ] Correct form and period selected, amendments checked.
- [ ] Primary document and XBRL instance both retained.
- [ ] Units, scale, and duration recorded for every fact.
- [ ] Arithmetic and balance checks passed.
- [ ] Citation includes accession and section.
- [ ] Restatements and non-GAAP measures flagged.

## Related skills

- `deterministic-financial-modeling` to feed extracted financials into a model.
- `source-grounded-citation-verification` to verify narrative claims.
- `schema-enforced-json-extraction` to enforce the output schema.
