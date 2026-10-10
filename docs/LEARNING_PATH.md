# Learn by rebuilding

This study plan now accompanies the completed five-page report. The native PBIX, Excel workbook, 12-page project guide and 28-page Python interview guide are included. The original guide PDFs preserve the earlier learning-stage instructions; use the current Power BI build guide for the final page design.

Plan for roughly four weeks at 1.5-2 hours per study day. Move on when you can explain the result without reading the code. The schedule is adjustable, not a promise of mastery.

## Week 1: pandas and NumPy on a business problem

| Sessions | Learn | Execute | Proof of understanding |
|---|---|---|---|
| 1-2 | Business questions, grain, units | Read README and data dictionary; inspect four raw CSVs | Explain why a bank attempt and a national payment are not interchangeable |
| 3-4 | read_csv, dtypes, dates, missing values | Notebook sections 1-2 | Calculate INR 1,216.84 from the two official inputs |
| 5-6 | vectorization, np.select, groupby, merge validation | Rebuild merchant shares and segments | State the exact denominator and your segmentation rule |
| 7 | duplicates, validation, assertions | Run tests; deliberately duplicate a copy of one source row | Explain why the pipeline rejects the duplicate |

## Week 2: SQL and analytical reasoning

| Sessions | Learn | Execute | Proof |
|---|---|---|---|
| 8-9 | Fact/dimension model, primary/foreign keys | Import SQLite or MySQL; queries Q01-Q05 | Explain weighted ticket and partial calendar years |
| 10-11 | CTEs, LAG, window frames | Q02-Q04 without copying | First-year YoY remains missing |
| 12-13 | ranking, cumulative SUM, CASE | Q06-Q11 | Explain why the highest TD rate is not always first priority |
| 14 | coverage and reconciliation | Q12-Q15 | Explain Unclassified and the rounding residual |

## Week 3: Excel and Power BI

| Sessions | Learn | Execute | Proof |
|---|---|---|---|
| 15-16 | Ratios of totals, formula tracing, what-if drivers | Open Excel; change Scenario B5 to 0, then restore 50 | Avoided attempts becomes zero without changing actuals |
| 17-18 | Power Query, types, star schema | Follow powerbi/BUILD_GUIDE.md | No fact-to-fact joins; MCC remains text |
| 19-20 | DAX measures, CALCULATE, filter context and snapshot scope | Build Network and Merchant pages | National totals do not multiply when filtering merchants |
| 21 | Weighted measures, role filters, visual design | Build Bank Reliability, Geographic Distribution and Home pages | Clearing the bank role does not double-count two sides |

## Week 4: forecasting, communication and ownership

| Sessions | Learn | Execute | Proof |
|---|---|---|---|
| 22-23 | Baselines, rolling origin, temporal splits | Notebook section 7 | Explain why random train/test split is inappropriate |
| 24-25 | np.linalg.lstsq, log transformation, MAE, WAPE | Compare all three models | Choose on validation, evaluate on test |
| 26 | Sensitivity and limits | Change config target from 0.5% to 1%; rebuild | Report scenario change as hypothetical |
| 27 | Business writing | Write a one-page memo with two recommendations | Separate observation, inference, proposed action and evidence needed |
| 28 | Portfolio and interview | Record a three-minute walkthrough and update MY_CONTRIBUTION.md | Explain any selected line of code |

## Refresh and customization

- `python src/pipeline.py` rebuilds the analytical outputs from the packaged snapshots.
- To add a new release, verify its reporting month and source first. Run `extract_snapshot.py --refresh --observation-month YYYY-MM-01` only after that verification. This downloads public pages using curl and can fail if access or page structure changes. No automated recurring refresh is configured. When using saved HTML instead, supply `--retrieved-on YYYY-MM-DD` with the date those source pages were actually obtained; the extraction date is recorded separately.
- Review counts, duplicate keys, units, coverage and source hashes. Update config.as_of and data/sources.csv. Add exact official overrides only after verifying them. Never fill missing periods with guesses.
- Rebuild with the pipeline, run tests, then `python src/build_learning_assets.py` to refresh notebook/MySQL assets. The fixed August 2026 control in `test_known_official_control` must be updated deliberately when accepting a new release.
- The supplied Excel file is a snapshot with live formulas, not a connected refresh pipeline. For a new release, replace its input rows from processed CSVs, extend formulas/tables/charts, adjust latest-month references and scenario sample rows, and reconcile the headline controls. Do not assume it refreshes when a CSV changes.
- Power BI reads local CSVs. After rebuilding, Refresh in Desktop, review model relationships and update the snapshot page filters and labels. Then export all five pages, including Home, and update the PDF and five screenshots.
- Edit the business memo and PDF's dated figures when sources change. These documents do not update automatically.

## Strong extensions after the core works

1. Collect multiple months of complete bank tables from official published releases; retain bank identifiers and role. Compare bank trends on like-for-like coverage.
2. Replace all rounded history with verified official downloads, record publication vintages, and rerun the forecast comparison.
3. Add a constrained AI memo writer using `AI_EXTENSION_PROMPT.md`. Feed only validated metrics and source IDs, and check each numeric statement. Treat it as a writing feature, not a new source of evidence.
4. If you obtain a real, permitted transaction-level dataset later, add retry recovery and cohort analysis. The current aggregate tables do not support those analyses.

## Interview checkpoints

Be ready to explain: the business decision; grain; one-million versus crore units; missing versus zero; weighted averages; join fanout; filter context; selected bank samples; forecast leakage; and hypothetical versus achieved impact.

After you reproduce and extend it, a truthful resume bullet could describe: a reproducible payments analytics pipeline over 48 months, 15 SQL business queries, source validation, a forecast comparison and an operations dashboard. The native PBIX is now included. Explain the filters, navigation and measures you built, and distinguish your hands-on work from AI assistance. Do not claim the hypothetical 6.74 million attempts as an achieved saving.
