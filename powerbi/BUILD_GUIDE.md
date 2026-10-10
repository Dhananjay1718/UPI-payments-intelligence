# Rebuild the completed five-page report

The final visual reference is `../reports/UPI_Payments_Intelligence_Dashboard.pdf`. The author built the report in Power BI Desktop. The native report is included as `UPI_Payments_Intelligence.pbix`. Open it in Power BI Desktop; before refreshing on a new computer, point its existing CSV sources to this repository's `data/processed` folder. Retain the current saved report while changing paths. `Measures.dax` documents equivalent rebuild logic; it is not an export of the native model.

## 1. Import

Import these seven CSVs from `data/processed`: `fact_monthly`, `fact_merchant`, `fact_bank`, `fact_state`, `dim_month`, `dim_merchant`, `dim_bank`. `sources.csv` is an optional disconnected reference table.

Set `month` to Date, numeric analytical fields to Decimal Number, and identifier fields including MCC to Text. Dates are month-start observations. Percentages are decimal fractions.

You can use Get data > Text/CSV, or the provided `LoadCSV.pq` function with a Text parameter called `ProjectFolder` pointing at the extracted repository. For each table create a query calling `LoadCSV("table_name")`.

## 2. Relationships

Use active one-to-many relationships with single direction from dimensions to facts:

| One side | Many side |
|---|---|
| dim_month[month] | fact_monthly[month] |
| dim_month[month] | fact_merchant[month] |
| dim_month[month] | fact_bank[month] |
| dim_month[month] | fact_state[month] |
| dim_merchant[mcc] | fact_merchant[mcc] |
| dim_bank[bank_id] | fact_bank[bank_id] |

The completed design uses `dim_month`, not the optional daily `DimDate` from the initial build kit in `reference/initial_measures.dax`. Do not combine the two approaches by adding a second active date-filter path.

## 3. Pages and metrics

| Page | Main visuals and scope |
|---|---|
| Home | Four page-navigation buttons, one for each analytical page; decorative images |
| Network Overview | Four August snapshot cards; volume, value and average-payment lines over the 48-month history; Trend Year slicer |
| Merchant Activity | Category count, selected category volume, top-five share of selection, larger-contracting count; Top 10 volume chart, segment counts and size/growth scatter |
| Bank Reliability | Keep the Sending and August 2026 scope; selected bank count, weighted TD, scenario target and potential fewer declines; three bank rankings |
| Geographic Distribution | Classified state count/volume, global Unclassified share, leading state; Top 10 volume, Top 10 average payment and global coverage donut |

The supplied Bank Reliability page applies `fact_bank[role] = Sending` and August 2026 as filters on each of its eight data visuals, including the slicer. A rebuild may use page filters for the same scope, after checking every visual.

Merchant, bank and geographic pages describe August 2026 only. Do not sync the historical year slicer to those pages. Use dimension names where available on axes. Put the Top N condition on the category/state field and rank by the appropriate measure.

Use a plain Card visual for snapshot values. The KPI visual's trend-axis behavior is unnecessary here. Format INR with Display units None and two decimals; rates as percentages with two decimals. Use the blue/navy/pale-blue theme and explicit units.

## 4. Slicers and interactions

| Slicer | Should filter | Should stay fixed |
|---|---|---|
| Trend Year | The three national line charts | August snapshot cards and August findings |
| Merchant Segment | Merchant charts and cards | The findings text labeled All Categories |
| Select Bank | Bank charts and cards, retaining Sending scope | The findings text labeled All Selected Sending Banks |
| Select State/UT | Two state bar charts and state-dependent cards | Global coverage donut and Unclassified Share (All Data) |

Exclude the Unclassified row from the State/UT slicer using a slicer-level Geographic Status filter. Use Edit interactions to disable state-slicer filtering of the coverage donut. The documented global Unclassified DAX measure also removes the state/status selection. When rebuilding, also check bar-chart selections: the native file explicitly disables slicer-to-donut filtering, but does not record equivalent overrides for bar-chart clicks.

All-data findings are static text and explicitly labeled. Use a dynamic title or "Monthly trend for selected years" on the national charts to keep titles accurate when filtering.

## 5. Navigation

Configure each Home-page button with Action On, Type Page navigation, and its corresponding page as Destination. Add a return-Home button on every analytical page. In Desktop, Ctrl+click tests navigation. Return all dropdown slicers to All before saving the portfolio snapshot.

## 6. Reconciliation controls

| Page | Expected All-view values |
|---|---|
| Network | 24.51 Bn; ₹29.82 lakh Cr; ₹1,216.84; 790.61 Mn/day |
| Merchant | 29; 12.53 Bn; 67.10%; 3 |
| Bank, Sending | 6; 2.04%; 0.50%; 6.74 Mn |
| Geography | 36; 13.63 Bn; 44.39%; Maharashtra |

Native interaction checks from the build included: choosing 2025 leaves August cards fixed; Larger and contracting produces three merchant categories; selecting Central Bank of India yields 2.34% TD and 4.40 Mn scenario reduction; choosing Maharashtra leaves the global donut unchanged. Recheck these when reproducing the report.
