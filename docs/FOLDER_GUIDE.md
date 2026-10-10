# What each folder does

Start with `README.md` in the main `upi-payments-intelligence` folder. Extract the ZIP before opening or running the project. Keep the folder names and relative positions together so the programs can find their inputs.

Think of the project as a small analysis workshop. `data` holds the ingredients. `src` contains the Python instructions. `sql` contains the database questions. `powerbi` contains the interactive presentation. `reports` holds saved answers and exports. `notebooks` teaches the Python steps, `docs` explains the work, and `tests` checks selected mistakes.

## The eight main folders

| Folder | What it handles | Example | What you normally do |
|---|---|---|---|
| `data/` | The source numbers, cleaned tables and local database | Monthly payment volume and bank decline rates | Inspect the CSVs; use processed facts/dimensions for Power BI |
| `src/` | Reusable Python programs | `pipeline.py` cleans the data and rebuilds analytical outputs | Read the code; run the pipeline when you intentionally rebuild |
| `sql/` | Database setup and analytical questions | Q12 calculates geographic coverage | Open the SQL in your database tool and run the relevant question |
| `notebooks/` | A step-by-step Python lesson with saved answers | `01_guided_analysis.ipynb` | Open with a notebook editor and run from top to bottom |
| `powerbi/` | The native report and supporting build materials | `UPI_Payments_Intelligence.pbix` | Open the PBIX in Power BI Desktop |
| `reports/` | Saved results, visual exports and verification records | The five-page dashboard PDF and Excel workbook | View, compare or share outputs |
| `docs/` | Explanations, study materials and portfolio text | Data dictionary, methodology and interview PDF | Read these to understand and explain the project |
| `tests/` | Automated checks of important assumptions | Reject duplicate keys or invalid dates | Run the tests after changing the code or accepted data |

## Inside data

| Location | What is inside | Why it exists |
|---|---|---|
| `data/raw/` | Five CSV inputs: monthly history, official monthly overrides, merchants, banks and states; plus the extraction manifest | Preserves the source snapshot before Python transformations |
| `data/processed/` | Cleaned analysis tables, Power BI facts/dimensions and forecast outputs | Provides consistent dates, numeric units, identifiers and calculated columns |
| `data/sources.csv` | Source IDs, publishers, URLs, retrieval date and coverage notes | Explains where the numbers came from |
| `data/upi_intelligence.sqlite` | A local SQL database containing the analytical tables | Lets the Python workflow run the SQL questions without a database server |

`raw` means the packaged aggregate source facts, not individual payment records. The four subject files are supplemented by a fifth file containing official overrides for five national months.

Similar names have different purposes:

- `monthly.csv`, `merchants.csv` and `banks.csv` are convenient Python analysis tables. For example, `banks.csv` includes the readable bank name.
- `fact_monthly.csv`, `fact_merchant.csv`, `fact_bank.csv` and `fact_state.csv` are model tables. A fact table holds measurements at a defined level, such as one bank, role and month.
- `dim_month.csv`, `dim_merchant.csv` and `dim_bank.csv` hold descriptions and lookup keys. A dimension answers questions such as “Which bank does this ID represent?”
- `states.csv` and `fact_state.csv` currently have identical contents because there is no separate state dimension in this project. Both names are generated for their respective workflows.
- `data/processed/sources.csv` is the generated model copy of `data/sources.csv`.
- The three `forecast_*.csv` files belong to the optional Python forecasting exercise. They are not extra Power BI report pages.

For the Power BI rebuild, load the **four fact tables and three dimension tables** listed in `powerbi/BUILD_GUIDE.md`. Loading every similarly named CSV can create unnecessary duplicate tables.

## The three main Python programs

| File | Reads | Writes | When to use it |
|---|---|---|---|
| `src/pipeline.py` | Raw CSVs, source register, configuration and SQL files | Processed CSVs, SQLite database, SQL answers, metrics and the Python chart | The normal offline rebuild |
| `src/build_learning_assets.py` | The existing validated database, analytical code and chart | The executed notebook and MySQL import | After the pipeline, when refreshing those learning assets |
| `src/extract_snapshot.py` | Two saved HTML source pages, or the published pages with `--refresh` | Four raw CSVs and the extraction manifest | Only when deliberately collecting and reviewing another source snapshot |

The extractor is optional. It changes raw inputs and does not independently verify official overrides. For saved HTML, supply both the verified observation month and the actual retrieval date with `--retrieved-on YYYY-MM-DD`. A new extraction date is recorded separately. Do not run a refresh simply to view the existing dashboard.

## Inside SQL, Power BI and reports

| Location | Purpose |
|---|---|
| `sql/schema_sqlite.sql` | Creates the local SQLite table structure |
| `sql/mysql_import.sql` | Creates/populates the `upi_portfolio` database in MySQL; existing same-key rows are updated |
| `sql/analysis_queries.sql` | Contains Q01–Q15: the questions and SQL logic |
| `reports/sql_results/` | Contains Q01–Q15 answers saved as CSVs |
| `powerbi/Measures.dax` | Documents equivalent rebuild measures; it is not an extracted copy of the native PBIX model |
| `powerbi/LoadCSV.pq` | Optional Power Query function for importing the processed CSVs |
| `powerbi/theme.json` | Report theme settings |
| `powerbi/assets/` | The two decorative Home-page images, also embedded in the PBIX |
| `powerbi/reference/` | The earlier DAX starter kit, kept as a historical reference; use the current build guide for the completed report |
| `reports/screenshots/` | Five images rendered from the final Power BI PDF |
| `reports/excel_previews/` | Six saved images of the Excel sheets |
| `reports/UPI_Payments_Intelligence.xlsx` | The six-sheet Excel analysis and scenario workbook |
| `reports/UPI_Payments_Intelligence_Dashboard.pdf` | The final five-page Power BI export |
| `reports/dashboard.png` | A separate chart produced by Python; it is not the Power BI report |
| `reports/*validation*`, audit JSON and release logs | Evidence of checks, their results and their limits |
| `reports/summary.json` | Headline Python results in a program-readable format |
| `reports/workbook_data.json` | Structured values used for the original Excel build; this does not automatically refresh the workbook |

The **SQL files are the questions; the SQL result CSVs are the saved answers**. The **PBIX is interactive; the PDF and PNGs are pictures of a saved report state**.

## Inside docs

- `VIEWING_GUIDE.md` helps visitors view, download or reproduce the work, including common file-opening problems.
- `DATA_DICTIONARY.md` defines columns, units and row meanings.
- `METHODOLOGY.md` explains calculations, denominators, assumptions and limitations.
- `MY_CONTRIBUTION.md` records the hands-on work and AI assistance.
- `LEARNING_PATH.md` provides practice exercises and interview checkpoints.
- The two guide PDFs preserve the earlier project and Python learning stages. Statements such as “the next phase is Power BI” describe that earlier stage. Power BI is now included; use the current README and build guide for the finished report.
- `REPORT_REVIEW.md` records the visual and native-file review, including Desktop checks that still require attention.
- `FILE_INVENTORY.md` maps the complete deliverables.
- `PUBLISHING.md` and `LINKEDIN_POST.md` contain publishing instructions and the draft social post. Their presence does not mean the project has been published.
- `AI_EXTENSION_PROMPT.md` is an optional writing extension, not another data source.
- `docs/source/` contains the two Python programs that generate the study PDFs. These are optional documentation tools. Their `requirements.txt` adds ReportLab to the normal dependencies. Running a generator overwrites its corresponding guide, so use a copy while experimenting.

## Files at the top level

| File | Plain-language meaning |
|---|---|
| `README.md` | Start here: project purpose, findings, previews and run instructions |
| `config.json` | Adjustable analytical settings, including the 0.50% target and 50% effectiveness assumption |
| `requirements.txt` | Python packages needed by the analytical programs |
| `CHECKSUMS.sha256` | File fingerprints for this packaged release; intentional edits require new fingerprints |

The `as_of` value in `config.json` describes the snapshot's source-retrieval vintage. It is different from the reporting month, August 2026, and the later date on which the report was completed.

## Open the right file with the right application

| Extension | Use |
|---|---|
| `.pbix` | Power BI Desktop |
| `.xlsx` | Excel or a compatible spreadsheet application |
| `.pdf` / `.png` | PDF reader / image viewer |
| `.ipynb` | Jupyter or a notebook-capable editor |
| `.py` | A code editor; Python executes it |
| `.sql` | A database query editor, using the relevant database engine |
| `.csv` | A text/spreadsheet viewer or data-import tool |
| `.sqlite` | SQLite-compatible software or Python's `sqlite3` |
| `.md` / `.json` / `.dax` / `.pq` | A text or code editor; these are not dashboard files |

A file that Windows does not open automatically is not necessarily damaged. Its application may not be installed or associated with the extension.

## What was corrected in the folder review

On 9 October 2026, the guide generators were changed to locate Matplotlib's bundled fonts instead of requiring Linux system font paths. Text reads and writes in the affected scripts now explicitly use UTF-8. The optional extractor now records the actual retrieval date and rejects non-month-start observation dates before writing files. The existing August source snapshots are unchanged.

The final PBIX may still need its CSV source locations updated after moving the project to another computer. Native Desktop refresh and interaction testing cannot be completed by inspecting folders alone. This review also keeps the earlier geographic bar-click check visible in `REPORT_REVIEW.md`.

Rebuilding Python outputs does **not** automatically update the saved Power BI report, its PDF/screenshots, the Excel workbook or the study PDFs. Refresh or regenerate those deliberately, then reconcile them with the new outputs.
