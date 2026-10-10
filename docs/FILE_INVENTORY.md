# Complete deliverable inventory

The release contains every distinct final deliverable found in the project workspace, with the final native Power BI report added. Earlier duplicate archives, temporary inspection dumps and incomplete superseded copies are excluded. SHA-256 hashes for the packaged files appear in `../CHECKSUMS.sha256`.

| Work completed | Included files |
|---|---|
| Python programs | `src/pipeline.py`, `src/extract_snapshot.py`, `src/build_learning_assets.py` |
| Python walkthrough | `notebooks/01_guided_analysis.ipynb`, with nine executed code cells |
| Data inputs and provenance | Five raw CSV snapshots, extraction manifest and `data/sources.csv` |
| Cleaned analytical data | `data/processed/`, including facts, dimensions and forecast comparison outputs |
| Database and SQL work | `data/upi_intelligence.sqlite`; MySQL import, SQLite schema and 15 question blocks in `sql/` |
| Answers to the SQL questions | All 15 files in `reports/sql_results/` |
| Native interactive Power BI report | `powerbi/UPI_Payments_Intelligence.pbix`, preserved exactly as uploaded |
| Power BI visual export | `reports/UPI_Payments_Intelligence_Dashboard.pdf` and five matching PNGs in `reports/screenshots/` |
| Power BI supporting assets | Current build guide, documented DAX, original DAX reference, Power Query loader and theme |
| Home-page illustrations | Two original embedded images extracted to `powerbi/assets/` |
| Excel analysis | `reports/UPI_Payments_Intelligence.xlsx`, containing Overview, Scenario, Monthly, Merchants, Bank sample and Geography |
| Excel visual previews | Six original previews in `reports/excel_previews/` |
| Original project companion | `docs/UPI_Project_Guide.pdf`, 12 pages |
| Python interview preparation | `docs/UPI_Python_Interview_Preparation_Guide.pdf`, 28 pages |
| Study-guide generation programs | Two scripts and optional requirements in `docs/source/` |
| Learning and explanation | Learning path, data dictionary, methodology, contribution record and optional AI-extension prompt in `docs/` |
| Python visual and metrics | `reports/dashboard.png`, summary, validation and workbook-input JSON |
| Verification | Twelve tests, release logs, original Excel scenario check, native PBIX audit and release-validation JSON |
| Portfolio presentation | README, viewing/download guide, report review, publishing instructions and LinkedIn caption |

## Which version to use

The final Power BI report has five pages. The original learning PDFs were written before the report was completed and retain instructions from that stage. Use the current README and `powerbi/BUILD_GUIDE.md` for the final design. The current notebook contains the repaired, executed walkthrough. The latest release test log supersedes the earlier duplicate test-output file.

The Excel workbook and both study PDFs are copied from their complete original deliverables. They do not refresh automatically when Python outputs change. The PBIX is preserved rather than reconstructed from the documented DAX.

## Optional PDF regeneration

The original PDF-authoring source is included under `docs/source/`, with paths adapted to this repository. These are separate documentation tools, not pipeline dependencies. They require ReportLab and the project Python dependencies. The scripts now locate DejaVu fonts bundled with Matplotlib, so Linux system font paths are no longer required.

Running either script replaces its corresponding guide PDF. The existing PDFs are the reviewed original outputs. Both corrected scripts were executed successfully in an isolated project copy on 9 October and produced 12-page and 28-page PDFs. Review the dated narrative and render the resulting pages before distributing a regenerated guide.

## Verification limits

The Python pipeline, all 12 tests and nine notebook code cells were rerun on 9 October from a project path containing spaces. All 30 generated CSVs and the headline summary matched the packaged results. Both study-guide generators ran successfully in the isolated copy. The added workbook passed ZIP integrity and cached-error checks and retains its original scenario validation. PBIX checks cover report structure and recorded filters/navigation, without native Power BI execution. See `REPORT_REVIEW.md`, `FOLDER_GUIDE.md` and `../reports/release_validation.json` for the exact scope.
