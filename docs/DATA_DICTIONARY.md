# Data dictionary and metric contract

## Table grain and keys

| Table | One row represents | Key |
|---|---|---|
| fact_monthly | National UPI activity for one month | month |
| fact_merchant | One displayed merchant category in one month | month + mcc |
| fact_bank | One displayed bank on one side of a payment | month + role + bank_id |
| fact_state | One state/territory or Unclassified row in one month | month + state |
| dim_month | One calendar month | month |
| dim_merchant | One four-digit merchant category code | mcc |
| dim_bank | One bank identity in the displayed snapshot | bank_id |
| sources | One publisher/coverage record | source_id |

Join dimensions to facts. Never join merchant, bank and state facts directly and then sum national volume: unrelated details create row multiplication. `fact_monthly` joins safely to state rows only when the national denominator is used once per month, as in SQL Q12.

## Fields and units

| Field | Meaning / calculation |
|---|---|
| month | First day of the reporting month; not the date of an individual transaction |
| volume_mn | Published payment volume or bank attempts in millions; read each table's definition |
| value_cr | Published transferred value in INR crore |
| banks_live | Official participating-bank count; missing outside April-August 2026 |
| daily_volume_mn | Monthly volume / calendar days in month |
| avg_ticket_inr | value_cr × 10 / volume_mn; ratio of totals when aggregated |
| mom_volume | current monthly volume / previous month - 1 |
| mom_daily_volume | current daily run rate / previous daily run rate - 1 |
| yoy_volume | current month / same month last year - 1; merchant growth is directly reported |
| six_month_volume | Merchant volume change over six months, as reported by S3 |
| rolling_3m_volume_mn | Three observed monthly volumes averaged; first two months missing |
| observed_volume_share | Merchant volume / sum of the 29 displayed category volumes |
| segment | Larger/smaller than the month's median observed category volume, crossed with nonnegative/negative MoM |
| role | Sending or Receiving; two views of potentially overlapping payments |
| td_rate | Published technical-decline percentage converted to a decimal fraction |
| estimated_td_mn | volume_mn × td_rate; approximate because inputs are rounded |
| target_td_rate | Analyst assumption; default 0.005 = 0.5% |
| effectiveness | Assumed fraction of excess declines reduced; default 0.5 |
| scenario_avoided_mn | volume_mn × max(td_rate - target_td_rate, 0) × effectiveness |
| national_volume_share | State volume / same-month official national volume |
| reported_volume_share | Source's displayed share converted to a fraction, except censored values |
| reported_volume_share_label | Original share text; preserves `<0.01%` |
| precision | `primary_verified` or `secondary_rounded` for national observations |
| source_id | Join to data/sources.csv |
| wape | Sum(abs(prediction - actual)) / sum(actual); lower is better |
| mae_mn | Mean absolute forecast error, million transactions |

One billion transactions = 1,000 million. One INR crore = 10,000,000 INR. One INR lakh crore = 100,000 crore = one trillion INR. These relationships explain the `×10` in average ticket. Never attach an INR symbol to a count.

## Missingness and rounding

Missing annual comparisons are unknown, not 0%. `<0.01%` is a bound, not exactly 0.01% or zero. The numeric reported-share field remains missing for that case while its label is preserved; a separate calculated share is available from rounded volume. Source numbers with two displayed decimals in billions/trillions have limited precision. Derived percentages and model errors should be reported to sensible precision.

## What this data cannot establish

Fraud, customer churn, unique active users, individual payment failure sequences, merchant revenue, company profit, actual recovered payments, bank root causes, and district-level market opportunity. No customer-level classification model or causal claim is supported. The bank table is a selected sample of six displayed banks per role and cannot estimate nationwide TD.
