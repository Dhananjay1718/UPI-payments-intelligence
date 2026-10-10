-- Portable analysis: tested in SQLite; queries also use MySQL 8-compatible syntax.
-- Run each QUERY block separately in MySQL Workbench after import.

-- QUERY: Q01_latest_national_kpis
-- Topic: SELECT, ORDER BY, units. Question: What is the current network scale?
SELECT month, volume_mn/1000.0 AS volume_billion,
       value_cr/100000.0 AS value_lakh_crore,
       10.0*value_cr/NULLIF(volume_mn,0) AS avg_ticket_inr,
       precision, source_id
FROM fact_monthly ORDER BY month DESC LIMIT 1;

-- QUERY: Q02_month_over_month
-- Topic: LAG and CTE. Why: compare adjacent months without a self-join.
WITH x AS (
 SELECT month,volume_mn,daily_volume_mn,
        LAG(volume_mn) OVER(ORDER BY month) AS previous_volume,
        LAG(daily_volume_mn) OVER(ORDER BY month) AS previous_daily
 FROM fact_monthly
)
SELECT month,volume_mn,volume_mn/NULLIF(previous_volume,0)-1 AS mom_volume,
       daily_volume_mn/NULLIF(previous_daily,0)-1 AS mom_daily_volume
FROM x ORDER BY month;

-- QUERY: Q03_year_over_year
-- Topic: LAG offset. Why: separate annual growth from adjacent-month noise.
WITH x AS (SELECT month,volume_mn,LAG(volume_mn,12) OVER(ORDER BY month) AS last_year FROM fact_monthly)
SELECT month,volume_mn/NULLIF(last_year,0)-1 AS yoy_volume FROM x ORDER BY month;

-- QUERY: Q04_rolling_average
-- Topic: window frame. Why: smooth monthly variation; first two rows stay unavailable.
SELECT month,volume_mn,
 CASE WHEN COUNT(*) OVER(ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)=3
 THEN AVG(volume_mn) OVER(ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) END AS rolling_3m_volume
FROM fact_monthly ORDER BY month;

-- QUERY: Q05_annual_weighted_ticket
-- Topic: JOIN, GROUP BY. Why: a ratio of totals correctly weights payment size.
SELECT d.year,COUNT(*) AS observed_months,SUM(f.volume_mn) AS volume_mn,
       10.0*SUM(f.value_cr)/SUM(f.volume_mn) AS weighted_ticket_inr
FROM fact_monthly f JOIN dim_month d ON f.month=d.month
GROUP BY d.year ORDER BY d.year;

-- QUERY: Q06_merchant_priority
-- Topic: dimension join and ranking. Why: identify scale within observed categories.
SELECT f.month,d.merchant,f.volume_mn,f.mom_volume,f.segment,
       DENSE_RANK() OVER(PARTITION BY f.month ORDER BY f.volume_mn DESC) AS volume_rank
FROM fact_merchant f JOIN dim_merchant d ON f.mcc=d.mcc ORDER BY f.volume_mn DESC;

-- QUERY: Q07_merchant_pareto
-- Topic: cumulative SUM. Why: understand concentration; denominator is observed categories.
SELECT d.merchant,f.volume_mn,
 SUM(f.volume_mn) OVER(PARTITION BY f.month ORDER BY f.volume_mn DESC,f.mcc ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
 /SUM(f.volume_mn) OVER(PARTITION BY f.month) AS cumulative_observed_share
FROM fact_merchant f JOIN dim_merchant d ON f.mcc=d.mcc ORDER BY f.volume_mn DESC,f.mcc;

-- QUERY: Q08_contracting_categories
-- Topic: WHERE. Why: flag segments needing follow-up, without inventing root causes.
SELECT d.merchant,f.volume_mn,f.mom_volume,f.avg_ticket_inr
FROM fact_merchant f JOIN dim_merchant d ON f.mcc=d.mcc
WHERE f.mom_volume<0 ORDER BY f.volume_mn DESC;

-- QUERY: Q09_weighted_td_sample_only
-- Topic: weighted aggregation. Why: average percentages are misleading for unequal volumes.
-- These are selected high-decline samples, NOT estimates of national bank performance.
SELECT month,role,COUNT(*) AS displayed_banks,SUM(volume_mn) AS sample_attempts_mn,
       SUM(volume_mn*td_rate)/SUM(volume_mn) AS weighted_sample_td
FROM fact_bank GROUP BY month,role ORDER BY role;

-- QUERY: Q10_bank_investigation_queue
-- Topic: arithmetic, ranking. Why: a lower rate can still affect more attempts at higher volume.
-- Sending and receiving totals MUST NOT be added: one payment can appear on both sides.
SELECT f.month,f.role,b.bank,f.volume_mn,f.td_rate,
       f.volume_mn*f.td_rate AS estimated_td_mn,
       DENSE_RANK() OVER(PARTITION BY f.month,f.role ORDER BY f.volume_mn*f.td_rate DESC) AS review_rank
FROM fact_bank f JOIN dim_bank b ON f.bank_id=b.bank_id ORDER BY f.role,review_rank;

-- QUERY: Q11_scenario_reduction
-- Topic: CASE and explicit assumptions. Why: quantify a hypothetical investigation opportunity.
SELECT b.bank,f.role,f.target_td_rate,f.effectiveness,
       f.volume_mn*CASE WHEN f.td_rate>f.target_td_rate THEN f.td_rate-f.target_td_rate ELSE 0 END*f.effectiveness AS hypothetical_avoided_mn
FROM fact_bank f JOIN dim_bank b ON f.bank_id=b.bank_id
WHERE f.role='Sending' ORDER BY hypothetical_avoided_mn DESC;

-- QUERY: Q12_geography_coverage
-- Topic: conditional aggregation. Why: expose unclassified data before recommending territories.
SELECT s.month,SUM(s.volume_mn) AS rounded_state_rows_total_mn,
       MAX(n.volume_mn) AS official_national_volume_mn,
       SUM(CASE WHEN s.state='Unclassified' THEN s.volume_mn ELSE 0 END)/MAX(n.volume_mn) AS unclassified_share,
       SUM(s.volume_mn)-MAX(n.volume_mn) AS rounded_reconciliation_residual_mn
FROM fact_state s JOIN fact_monthly n ON s.month=n.month GROUP BY s.month;

-- QUERY: Q13_source_coverage
-- Topic: lineage join and COUNT. Why: distinguish official exact rows from rounded secondary rows.
SELECT f.source_id,s.publisher,f.precision,COUNT(*) AS observations,
       MIN(f.month) AS first_month,MAX(f.month) AS last_month
FROM fact_monthly f JOIN sources s ON f.source_id=s.source_id
GROUP BY f.source_id,s.publisher,f.precision;

-- QUERY: Q14_forecast_comparison
-- Topic: filtered ordering. Why: select on validation; report test performance separately.
SELECT split,model,months,mae_mn,wape FROM forecast_metrics ORDER BY split,wape;

-- QUERY: Q15_missing_comparisons
-- Topic: NULL and CASE. Why: missing YoY is not zero growth.
SELECT d.merchant,
 CASE WHEN f.yoy_volume IS NULL THEN 'Unavailable comparison' ELSE 'Available' END AS yoy_status
FROM fact_merchant f JOIN dim_merchant d ON f.mcc=d.mcc ORDER BY d.merchant;
