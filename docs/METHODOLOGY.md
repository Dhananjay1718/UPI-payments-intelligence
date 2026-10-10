# Methods, decisions and limitations

## Reporting period and sources

National trends cover September 2022 through August 2026. Merchant, bank and state detail is a single August 2026 snapshot. The source register and extraction manifest preserve the 22 September 2026 retrieval date; the PDF was exported by the author on 7 October 2026. Publication does not update the reporting period.

The raw files contain transcribed/extracted aggregate table facts. S1 identifies the five official NPCI monthly overrides; S2 and S3 identify secondary tables attributing NPCI. Do not describe the whole dataset as a complete official transaction-level download.

## Metric definitions

| Metric | Calculation / denominator |
|---|---|
| Transactions, billions | `SUM(volume_mn) / 1000` |
| Payment value, lakh crore | `SUM(value_cr) / 100000` |
| Average payment, INR | `10 * SUM(value_cr) / SUM(volume_mn)` |
| Daily transactions, million | Monthly volume divided by calendar days; selected periods use the corresponding sum of days |
| Month-over-month growth | `current / previous - 1` on contiguous monthly observations |
| Top-five merchant share | Volume of the five largest categories in the current selection / volume of all categories in that selection |
| Weighted technical-decline rate | `SUM(volume_mn * td_rate) / SUM(volume_mn)` within one bank role |
| Estimated technical declines, million | Bank volume in millions multiplied by its reported TD fraction |
| Potential fewer declines, million | `volume_mn * MAX(td_rate - 0.005, 0) * 0.5`, summed across the selected sending banks |
| Dashboard Unclassified share | Unclassified state volume / total state-row volume for the snapshot |
| SQL Q12 Unclassified share | Unclassified state volume / official national volume for the same month |

Average payment is a ratio of totals, not an unweighted average of category averages. Percentages are stored as fractions: 0.0244 is 2.44%.

## Merchant segmentation

The median reported volume across the 29 categories is 149.6 million. A category at or above the median is "Larger"; below it is "Smaller". Nonnegative reported month-over-month growth is "growing" and negative growth is "contracting". The fixed snapshot produces 12 larger/growing, 8 smaller/growing, 6 smaller/contracting and 3 larger/contracting categories. Slicers select these precomputed segments; they do not recalculate the median.

The category table totals 12,534.3 million. Its top five total 8,410.7 million, or 67.10%. This denominator is the listed categories, not all national UPI activity or the entire P2M market.

## Bank scenario

Only six displayed sending banks are included in the page. Central Bank of India has 478.3 million reported attempts at a 2.34% TD rate, implying 11.19222 million estimated technical declines. The scenario is `478.3 * (0.0234 - 0.005) * 0.5 = 4.40036` million fewer declines. Across the selected sending sample it totals 6.741495 million.

Closing half the gap does not mean every bank reaches the 0.50% target. The effective modeled rate is `td_rate - MAX(td_rate - target, 0) * effectiveness`. This is a hypothetical planning exercise using rounded published inputs, not an implemented intervention.

Sending and receiving banks are two sides of potentially overlapping payments. Keep the role filter; do not add the two samples into one independent transaction count.

## Geographic reconciliation

There are 36 named states/UTs and one Unclassified row. Classified volume totals 13,629.4 million; Unclassified is 10,880 million. The row total is 24,509.4 million, compared with official national volume of 24,508.96 million. The 0.44 million residual is compatible with the displayed precision, but rounding has not been independently established as its sole cause.

The coverage donut and its KPI use the same row-total denominator and remain global when a state is selected. The state charts and state-dependent cards respond to the selection. Rankings do not control for population; they are not per-resident comparisons.

## Forecasting extension

The Python notebook includes a retrospective one-month-ahead comparison using the frozen snapshot: last-month daily rate, last-year daily rate and a 12-month log-linear trend. The first 30 months form initial history, the next six select the model, and the final 12 assess it. Each forecast uses only preceding observations.

The selected log-trend model has approximately 1.12% test WAPE on this data vintage. This does not establish future accuracy. The September 2026 baseline of about 23.99 billion uses only observations through August; it is a historical exercise, not a newly issued October forecast. The +/-10% range is an assumption, not a prediction interval. Forecast outputs are not shown on the final Power BI pages.

## Decision boundaries

The data support prioritizing investigations. Root causes require logs, incident times and other operational evidence. The aggregate facts cannot establish fraud, customer-level behavior, unique users, lost revenue, successful recoveries or causal improvements.
