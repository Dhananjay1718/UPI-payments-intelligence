# Monthly investigation flags

These optional queries add two monitoring questions to the original 15 SQL analyses. They operate on national aggregates, not transaction-level fraud labels.

| Query | Metric | Saved output |
|---|---|---|
| A01 | Month-over-month daily transaction-volume change | [48 monthly rows](../reports/sql_results/A01_daily_volume_change.csv) |
| A02 | Month-over-month average payment-size change | [48 monthly rows](../reports/sql_results/A02_average_payment_change.csv) |

## Rule and interpretation

For each change, use the six preceding changes to calculate a mean and population variance. Exclude the current month. Require six non-null baseline changes; the first seven observations are `insufficient_history`.

Flag a month only when its change differs from the preceding mean by at least five percentage points and more than three baseline standard deviations. The SQL compares squared deviations with nine times the variance, avoiding a dialect-specific square-root function. With a flat zero-variance baseline, the five-percentage-point minimum still applies. `within_rule` means the screening rule did not trigger, not that the month is proven normal.

The six-month window and thresholds are explicit analyst choices. They have not been calibrated against labeled incidents or false-alert costs. Monthly changes may be seasonal or serially correlated; three standard deviations is not a claimed probability or confidence level. The rules assume contiguous month-start dates, which the existing pipeline validates. Daily normalization accounts for month length, but not holidays or changing payment mix.

## Results on the included snapshot

A01 flags **November 2024**. A02 flags no months. First verify source consistency, then review calendar effects, incidents and payment mix before deciding whether any action is justified. Neither result establishes fraud or a root cause.

## Reproduce

From the project root, run `python src/pipeline.py` and then `python src/run_monitoring.py`. The latter uses Python's standard library and rewrites the two saved CSVs. For MySQL 8, import `sql/mysql_import.sql`, then run each named block in `sql/anomaly_monitoring.sql` separately.

Validation: both queries ran against all 48 SQLite observations. Their means, variances and flags were independently checked against Python calculations using prior-only windows. Synthetic checks covered insufficient history, a stable zero-variance baseline and a doubled final observation. All 12 existing tests also passed. MySQL server execution was not performed in this update.
