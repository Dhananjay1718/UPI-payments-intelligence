-- SQLite and MySQL 8-compatible. Run each named block separately.
-- Investigation flags on monthly aggregates, not fraud detection.
-- Requires contiguous monthly observations (validated by the pipeline).
-- Tune 3.0 standard deviations and 0.05 (5 percentage points) to alert costs.

-- QUERY: A01_daily_volume_change
-- Daily normalization reduces differences caused by month length.
WITH changes AS (
 SELECT month, daily_volume_mn,
        daily_volume_mn / NULLIF(LAG(daily_volume_mn) OVER (ORDER BY month), 0) - 1 AS change_rate
 FROM fact_monthly
), baseline AS (
 SELECT *, COUNT(change_rate) OVER w AS baseline_months,
        AVG(change_rate) OVER w AS baseline_mean,
        AVG(change_rate * change_rate) OVER w AS baseline_mean_square
 FROM changes
 WINDOW w AS (ORDER BY month ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING)
), scored AS (
 SELECT *, CASE WHEN baseline_mean_square - baseline_mean * baseline_mean > 0
          THEN baseline_mean_square - baseline_mean * baseline_mean ELSE 0 END AS baseline_variance
 FROM baseline
)
SELECT month, daily_volume_mn, change_rate, baseline_months, baseline_mean,
       baseline_variance, change_rate - baseline_mean AS deviation,
       CASE WHEN baseline_months < 6 OR change_rate IS NULL THEN 'insufficient_history'
            WHEN ABS(change_rate - baseline_mean) >= 0.05
             AND (change_rate - baseline_mean) * (change_rate - baseline_mean) > 9.0 * baseline_variance
            THEN 'investigate' ELSE 'within_rule' END AS monitoring_status
FROM scored ORDER BY month;

-- QUERY: A02_average_payment_change
-- Flags changes in average amount, which may reflect payment mix or source issues.
WITH changes AS (
 SELECT month, avg_ticket_inr,
        avg_ticket_inr / NULLIF(LAG(avg_ticket_inr) OVER (ORDER BY month), 0) - 1 AS change_rate
 FROM fact_monthly
), baseline AS (
 SELECT *, COUNT(change_rate) OVER w AS baseline_months,
        AVG(change_rate) OVER w AS baseline_mean,
        AVG(change_rate * change_rate) OVER w AS baseline_mean_square
 FROM changes
 WINDOW w AS (ORDER BY month ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING)
), scored AS (
 SELECT *, CASE WHEN baseline_mean_square - baseline_mean * baseline_mean > 0
          THEN baseline_mean_square - baseline_mean * baseline_mean ELSE 0 END AS baseline_variance
 FROM baseline
)
SELECT month, avg_ticket_inr, change_rate, baseline_months, baseline_mean,
       baseline_variance, change_rate - baseline_mean AS deviation,
       CASE WHEN baseline_months < 6 OR change_rate IS NULL THEN 'insufficient_history'
            WHEN ABS(change_rate - baseline_mean) >= 0.05
             AND (change_rate - baseline_mean) * (change_rate - baseline_mean) > 9.0 * baseline_variance
            THEN 'investigate' ELSE 'within_rule' END AS monitoring_status
FROM scored ORDER BY month;
