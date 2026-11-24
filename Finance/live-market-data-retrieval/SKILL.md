---
name: live-market-data-retrieval
description: Fetches current and historical market data from provider APIs with retries, rate-limit handling, timestamp and adjustment validation, staleness checks, and source lineage. Use for quotes, OHLCV bars, corporate actions, FX, and any workflow where prices must be current, correctly adjusted, and reproducible.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: finance
---

# Live Market Data Retrieval

## Overview

Market data is easy to fetch and hard to trust. Vendors differ on timestamps, adjustment conventions, symbology, and delayed versus real-time access. A retrieval skill must make those choices explicit, validate the response, and record where every number came from.

## When to use

- Getting a current quote or intraday bars for a trading or monitoring task.
- Building a historical price series for backtesting or analysis.
- Reconciling positions against market prices.
- Monitoring corporate actions or market status.

Do not use for order execution. This skill retrieves and validates data; it does not place trades.

## Inputs to pin before fetching

| Input | Why it matters |
| --- | --- |
| Symbol and exchange | Tickers are not globally unique; `AAPL` vs `AAPL.L` |
| Asset class | Equity, ETF, FX, crypto, futures have different calendars |
| Frequency | Tick, minute, hourly, daily, weekly |
| Adjustment | Raw, split-adjusted, total-return adjusted |
| Timezone | Exchange local versus UTC |
| Session | Pre-market, regular, after-hours |
| As-of time | Point-in-time versus latest |
| Currency | Quote currency versus reporting currency |

## Provider selection

Pick one primary provider and one fallback. Examples:

| Provider | Strength | Watch-outs |
| --- | --- | --- |
| Polygon.io | US equities, aggregates, trades | Paid tiers, rate limits |
| Finnhub | Quotes, fundamentals, news | Free tier limits |
| Alpha Vantage | Broad coverage, FX, crypto | Low free-tier throughput |
| Tiingo | Clean EOD data | Limited intraday |
| Exchange API | Authoritative | Per-exchange onboarding |
| Yahoo Finance | Convenient, unofficial | No SLA, schema changes |

Never scrape an unofficial endpoint for production without a fallback and a staleness check.

## Workflow

### 1. Load credentials from the environment

```python
import os
API_KEY = os.environ["POLYGON_API_KEY"]  # fail fast if missing
```

Never hardcode keys. Never print them in logs or error messages.

### 2. Fetch with bounded retries

```python
import time
import requests

RETRYABLE = {429, 500, 502, 503, 504}

def get_json(url, params, attempts=4, timeout=20):
    for attempt in range(attempts):
        response = requests.get(url, params=params, timeout=timeout)
        if response.status_code == 200:
            return response.json()
        if response.status_code not in RETRYABLE:
            response.raise_for_status()
        sleep = min(2 ** attempt, 30) + 0.1 * attempt
        time.sleep(sleep)
    raise RuntimeError(f"provider unavailable after {attempts} attempts")
```

Respect `Retry-After` when present. Do not retry authentication or validation errors.

### 3. Validate the payload

Check, in order:

1. Symbol matches the request exactly.
2. Timestamp is present, parseable, and not in the future.
3. Timestamp is within the expected session and timezone.
4. Open/high/low/close satisfy `low <= open, close <= high`.
5. Volume is non-negative and not absurd for the asset.
6. Currency and adjustment flags match the request.
7. The latest bar is not stale relative to the market calendar.
8. No duplicate timestamps; bars are sorted ascending.

### 4. Handle adjustments and corporate actions

- Raw prices are not comparable across splits and dividends.
- Split-adjusted prices preserve returns but change the price level.
- Total-return adjusted prices include dividends and are appropriate for performance analysis.
- Store the adjustment factor and the as-of date with the series.
- Re-fetch after a corporate action; do not patch prices manually.

### 5. Cache with a TTL

| Data | Suggested TTL |
| --- | --- |
| Real-time quote | 1–5 seconds |
| Intraday bar | Until the bar closes |
| Daily bar | Until the next session opens |
| Corporate actions | 24 hours |
| Reference data | 24 hours |

Cache keys include symbol, frequency, adjustment, session, and date range. Record the fetch time, not just the data time.

### 6. Cross-check against a second source

For material decisions, compare the close, volume, and timestamp against a fallback provider. Flag differences above a tolerance:

- Price: 0.5% or one tick, whichever is larger.
- Volume: 2%.
- Timestamp: one bar interval.

Do not average conflicting sources. Report the discrepancy and choose the primary according to a documented policy.

### 7. Record lineage

```json
{
  "symbol": "AAPL",
  "provider": "polygon",
  "endpoint": "/v2/aggs/ticker/AAPL/range/1/day/2026-11-01/2026-11-20",
  "fetched_at": "2026-11-24T15:04:05Z",
  "as_of": "2026-11-21T21:00:00Z",
  "frequency": "1d",
  "adjusted": true,
  "session": "regular",
  "currency": "USD",
  "row_count": 14,
  "checksum": "sha256:..."
}
```

## Gotchas

- A quote timestamp may be the exchange timestamp, the vendor timestamp, or the receipt timestamp. They differ.
- Free tiers often provide delayed data. Label it as delayed; never present it as real-time.
- Adjusted historical data changes after each corporate action. A backtest run last month may not reproduce today unless you snapshot the data.
- Survivorship bias: a universe built from today's index members excludes delisted companies.
- Ticker reuse: a symbol can refer to a different company after a delisting. Use a permanent identifier.
- FX pairs have no single consolidated price. State the venue and the fixing time.
- Market holidays and half-days differ by exchange. Use an exchange calendar, not a generic weekend rule.
- Crypto trades 24/7 but liquidity and timestamp conventions vary by venue.

## Output contract

Return a data frame or JSON with one row per bar plus a lineage envelope. Include `symbol`, `timestamp`, `open`, `high`, `low`, `close`, `volume`, `currency`, `adjusted`, `provider`, `fetched_at`, and `quality_flags`.

Quality flags:

- `stale`
- `delayed`
- `cross_source_mismatch`
- `outside_session`
- `corporate_action_pending`
- `insufficient_history`

## Checklist

- [ ] Symbol, venue, frequency, adjustment, and timezone pinned.
- [ ] Credentials loaded from environment.
- [ ] Retries bounded and non-retryable errors surfaced.
- [ ] Payload validated for ordering, range, duplicates, and staleness.
- [ ] Corporate actions considered.
- [ ] Cache TTL appropriate to the data.
- [ ] Material values cross-checked.
- [ ] Lineage recorded.

## Related skills

- `transaction-anomaly-flagging` when prices feed a transaction monitor.
- `portfolio-rebalancing-calculation` for using prices in rebalancing.
- `confidence-threshold-output-gating` before acting on a low-quality feed.
