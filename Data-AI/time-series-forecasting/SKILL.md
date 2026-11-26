---
name: time-series-forecasting
description: Builds backtested forecasts with seasonality, covariates, prediction intervals, and drift monitoring. Use for demand, capacity, and financial planning.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: data-ai
---

# Time-Series Forecasting

## Overview

A forecast is a decision input, not a curve. The useful questions are: at what horizon, at what aggregation, with what cost of error, and does the model beat a seasonal naive baseline out of sample. Everything else is secondary.

The discipline is chronological backtesting with no future leakage, scale-free metrics, honest prediction intervals, and monitoring that separates a bad week from a broken model.

## When to use

- Demand, inventory, staffing, capacity, or revenue planning.
- Setting safety stock or reorder points from forecast error.
- Forecasting a metric with weekly, monthly, or annual seasonality.
- Adding known-future drivers such as promotions, holidays, price changes, or weather.
- Choosing between statistical, gradient-boosted, and foundation time-series models.
- Deciding whether a retrain improved the forecast or only fit history better.
- Do not use for a one-off scenario with no history; use driver-based modeling or judgment instead.

## Workflow

### 1. Define the forecast object and the decision

Write down:

- Target and unit (`units_sold`, `orders`, `hours`).
- Grain: series ID, geography, product, channel.
- Frequency and horizon: daily for 28 days, weekly for 13 weeks, monthly for 18 months.
- Aggregation used by the decision (sum over horizon, peak week, end-of-month level).
- Error cost: asymmetric stockout versus holding cost, or planner tolerance.
- Refresh cadence and the cutoff time for actuals.

Forecast at the grain where the decision is made, or forecast the bottom and reconcile upward. Do not forecast a total and divide it by history shares when mix changes.

### 2. Establish baselines before modeling

Every candidate must beat these on the same backtest:

| Baseline | Implementation | Use |
| --- | --- | --- |
| Naive | last observed value | level-only series |
| Seasonal naive | value from `m` periods ago | strong seasonality |
| Moving average | trailing 4 or 8 periods | noisy series |
| ETS | `statsmodels` Holt-Winters | trend plus seasonality |
| Linear regression on calendar | trend plus Fourier terms | simple, explainable |

```python
from statsmodels.tsa.holtwinters import ExponentialSmoothing

model = ExponentialSmoothing(train, trend="add", seasonal="add", seasonal_periods=7).fit()
forecast = model.forecast(horizon)
```

If a complex model does not beat seasonal naive by at least 5 percent MASE on the backtest (example gate), keep the baseline. Complexity must pay for its operational cost.

### 3. Profile the series and fix the time axis

Check, per series:

- Missing timestamps and duplicates; reindex to a complete regular grid before modeling.
- Frequency changes, timezone shifts, and daylight-saving transitions.
- Outliers and level shifts with dates and causes (system outage, price change, pandemic).
- Zero-inflation and intermittent demand; these need Croston or Tweedie-style models, not log-transformed ARIMA.
- Multiple seasonality: hour-of-day, day-of-week, week-of-year, holiday effects.
- Censoring: stockouts hide demand. Exclude censored periods or model latent demand explicitly.

Record which dates are excluded and why. Do not silently interpolate a month of missing sales.

### 4. Build a rolling-origin backtest

Use only information available at each forecast origin. Expanding or sliding window, step by the decision cadence, with at least 5 folds or 2 full seasonal cycles, whichever is longer.

```python
import numpy as np

def mase(y_true, y_pred, y_train, seasonality=7):
    scale = np.mean(np.abs(y_train[seasonality:] - y_train[:-seasonality]))
    return np.mean(np.abs(y_true - y_pred)) / scale

def pinball(y_true, q_pred, q):
    diff = y_true - q_pred
    return np.mean(np.maximum(q * diff, (q - 1) * diff))
```

Report:

- MASE per series and horizon, then weighted by volume.
- RMSE or MAE only when series share a scale.
- Bias: mean error as a percentage of mean actual, per horizon.
- Pinball loss and empirical coverage for each interval level.
- Worst 10 series by MASE, not only the average.

A model that wins on average but loses on the top 20 revenue series is not a win.

### 5. Add covariates without leaking the future

Classify each driver:

- **Known future**: calendar, holidays, planned promotions, contracted price, weather forecast. Safe at forecast time if the vintage is recorded.
- **Lag-only**: competitor price, search volume, prior sales. Use lags of at least the data publication delay.
- **Unknown future**: actual competitor actions, realized demand. Exclude from the forecast or simulate scenarios.

For each covariate, measure the release lag and align by `available_at`, not by event date. A promotion table backfilled after the fact is a leakage source.

### 6. Produce calibrated intervals and reconcile hierarchies

Generate predictive distributions, not only point forecasts:

- Statistical models: use model-based intervals (`get_forecast(...).summary_frame(alpha=0.05)`).
- Gradient boosting: train quantile objectives (`objective="quantile"`, `alpha=0.1` and `0.9`) or use conformal prediction on backtest residuals.
- Evaluate empirical coverage on the backtest. If a nominal 90 percent interval covers 78 percent, widen it or fix the model.
- For hierarchical forecasts, reconcile with MinT or bottom-up and verify that parent totals equal child sums.

```python
from sktime.split import ExpandingWindowSplitter

cv = ExpandingWindowSplitter(fh=range(1, 29), initial_window=365, step_length=7)
for train_idx, test_idx in cv.split(y):
    ...
```

### 7. Monitor drift and retrain on evidence

Track per series and in aggregate:

| Signal | Definition | Example trigger |
| --- | --- | --- |
| Bias drift | mean error over trailing 4 weeks | abs > 5 percent of mean actual |
| Coverage drift | share of actuals inside 90 percent interval | outside 85 to 95 percent |
| MASE drift | trailing MASE vs backtest baseline | ratio > 1.25 |
| Input drift | PSI on volume, price, promo share | PSI > 0.2 |
| Residual autocorrelation | lag-1 autocorrelation of errors | abs > 0.3 |

Retrain on a fixed cadence (weekly or monthly) and on triggers. Keep a champion/challenger comparison on identical folds. Log the data cutoff, code version, and model artifact for every run.

## Validation

Release gates:

- [ ] Forecast grain, frequency, horizon, and decision aggregation documented.
- [ ] At least two baselines, including seasonal naive, evaluated on identical folds.
- [ ] Backtest is chronological with no shuffled splits and no future covariates.
- [ ] MASE reported per series and weighted by decision-relevant volume.
- [ ] Bias reported by horizon; systematic under-forecast is flagged.
- [ ] Interval coverage measured empirically and within 5 percentage points of nominal.
- [ ] Hierarchy reconciliation checked (parent equals sum of children).
- [ ] Censored and missing periods handled explicitly.
- [ ] Retraining cadence, owner, and drift triggers recorded.

```bash
python -m pytest tests/test_forecast_pipeline.py -q
python scripts/backtest.py --config configs/demand_weekly.yaml --folds 8 --out backtest.json --fail-mase 1.0
```

## Gotchas

- Random cross-validation on time series leaks the future. Use rolling origin only.
- Fitting a scaler or imputer on the full history leaks test-period statistics. Fit inside each fold.
- Future covariates backfilled after the event inflate accuracy. Align on `available_at`.
- MASE below 1 is good only relative to the naive scale used. State the seasonality and the window.
- Aggregate forecasts rarely equal the sum of item forecasts. Reconcile and publish one consistent set.
- Stockouts censor demand, so the model learns low sales. Flag and adjust censored periods.
- Log transforms bias retransformed means. Use a bias correction or model on the original scale.
- Multiplicative seasonality breaks with zeros or negatives. Switch to additive or a count model.
- In-sample residual intervals are too narrow. Calibrate on out-of-sample errors.
- Promotions and price changes create level shifts that a smooth model absorbs slowly. Add event regressors or intervene.
- Retraining weekly on revised actuals can chase revisions. Freeze the vintage used for evaluation.
- A single global model can hide failing segments. Slice metrics by series cluster and check the tail.
- Horizon-specific seasonality matters: a 90-day forecast needs day-of-year effects, not just day-of-week.

## Output contract

```json
{
  "forecast_id": "demand-weekly-2026-11-24",
  "target": "units_sold",
  "grain": "sku x region",
  "frequency": "weekly",
  "horizon": 13,
  "cutoff": "2026-11-22T23:59:59Z",
  "model": {"family": "lightgbm_quantile", "version": "4.5.0", "artifact": "gs://models/demand/2026-11-24"},
  "baselines": {"seasonal_naive_mase": 0.92, "ets_mase": 0.84, "selected_mase": 0.71},
  "metrics": {
    "mase_weighted": 0.71,
    "bias_pct_by_horizon": [0.8, 1.2, 2.1],
    "coverage": {"0.8": 0.79, "0.9": 0.88},
    "worst_series": [{"id": "sku-1042", "mase": 1.31}]
  },
  "folds": 8,
  "reconciliation": {"method": "mint", "parent_child_check": "pass"},
  "drift": {"bias_status": "ok", "coverage_status": "ok", "psi_max": 0.14},
  "retrain": {"cadence": "weekly", "next_review": "2026-12-01", "owner": "demand-planning"},
  "decision": "publish"
}
```

## Checklist

- [ ] Target, grain, frequency, horizon, and decision aggregation defined.
- [ ] Baselines including seasonal naive evaluated on identical folds.
- [ ] Time axis regularized; duplicates, gaps, and DST handled.
- [ ] Outliers and censored periods flagged with causes.
- [ ] Rolling-origin backtest with at least 5 folds.
- [ ] Scale-free metrics plus bias reported by horizon.
- [ ] Covariates classified by availability and aligned on `available_at`.
- [ ] Prediction intervals calibrated on out-of-sample residuals.
- [ ] Hierarchy reconciliation verified.
- [ ] Drift monitors and retraining triggers configured.
- [ ] Champion/challenger comparison on fixed folds.
- [ ] Artifact, cutoff, and code version logged for reproducibility.

## Related skills

- `model-evaluation-benchmarking` for holdout discipline, uncertainty, and slice reporting.
- `data-quality-profiling` for missing timestamps, duplicates, and freshness before modeling.
- `feature-store-engineering` for point-in-time correct lags and covariates.
- `causal-inference-analysis` when a price or promotion change needs an effect estimate rather than a forecast.
