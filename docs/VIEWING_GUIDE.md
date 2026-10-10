# View, download or reproduce the project

[Back to the project](../README.md)

You can understand the completed analysis without installing Python, a database or Power BI. Start with the [five-page dashboard PDF](../reports/UPI_Payments_Intelligence_Dashboard.pdf), then follow the route that interests you.

## A two-minute tour

1. **Network Overview:** look at the August snapshot cards, then the 48-month trend charts. Payment volume grew while the average payment amount fell.
2. **Merchant Activity:** compare the largest categories and their growth segments. The top five categories account for 67.10% of the volume across the 29 listed categories.
3. **Bank Reliability:** compare decline rates with estimated decline counts. In the selected sending-bank sample, the highest rate and the largest affected volume belong to different banks.
4. **Geographic Distribution:** read the coverage donut before comparing states. The 44.39% Unclassified share limits geographic conclusions.

The Home page provides navigation in the interactive report. PDF pages and PNG screenshots show a saved state; their slicers do not operate.

## View it in a browser

- Open the [dashboard PDF](../reports/UPI_Payments_Intelligence_Dashboard.pdf). If the preview fails, download the file and open it in a PDF reader.
- For a single page, open [Home](../reports/screenshots/01-home.png), [Network Overview](../reports/screenshots/02-network-overview.png), [Merchant Activity](../reports/screenshots/03-merchant-activity.png), [Bank Reliability](../reports/screenshots/04-bank-reliability.png) or [Geographic Distribution](../reports/screenshots/05-geographic-distribution.png).
- Read the [saved notebook](../notebooks/01_guided_analysis.ipynb), [SQL queries](../sql/analysis_queries.sql) and [CSV answers](../reports/sql_results/) directly in the repository.

A hosted interactive Power BI report has not yet been deployed. No sign-in to Power BI is needed to view the public repository's PDF or screenshots.

## Use the interactive Power BI report

1. On a Windows computer with [Power BI Desktop](https://learn.microsoft.com/en-us/power-bi/fundamentals/desktop-get-the-desktop), [download the PBIX](../powerbi/UPI_Payments_Intelligence.pbix?raw=true).
2. Open the downloaded file in Power BI Desktop. Use the Home page to choose an analysis page; hold Ctrl while clicking navigation buttons in Desktop's editing view.
3. Try the Trend Year, Merchant Segment, Select Bank and Select State/UT slicers. The August network cards remain fixed; the year selection changes the historical charts.
4. To refresh from the packaged CSVs, download and extract the complete repository first, then update the saved source paths to your own `data/processed` folder. The [build guide](../powerbi/BUILD_GUIDE.md) documents the seven required tables and expected filters.

GitHub stores the PBIX for download; it does not run its slicers in a browser. The original saved report is included. Opening and refreshing it on another computer is a separate native Power BI check.

## Download the complete project

From the [repository](https://github.com/Dhananjay1718/UPI-payments-intelligence), choose **Code → Download ZIP**, then extract the ZIP. Keep the folders together. For a Git checkout, use the clone command in the [README](../README.md#run-locally).

The [folder guide](FOLDER_GUIDE.md) explains each directory. The [file inventory](FILE_INVENTORY.md) maps the Python, SQL, Power BI, Excel and study materials.

## Reproduce the analysis

Follow [Run locally](../README.md#run-locally) to create a Python environment, install dependencies, rebuild the analytical outputs and run the 12 checks. The normal pipeline uses the included source snapshots offline.

For MySQL, use the dedicated import script as described in the README. For Power BI, follow the build guide. The Python run does not automatically update the saved PBIX, report PDF, screenshots, Excel workbook or study guides.

## Common opening problems

| What you see | What to do |
|---|---|
| The PBIX is not previewed on GitHub | Download it and open it with Power BI Desktop; use the PDF if you only want to view the work |
| A PDF preview does not load | Download the PDF or open the individual page PNGs |
| Power BI cannot find a CSV | Extract the full project and update the source paths to your local `data/processed` folder |
| An image looks small | Open the linked PNG and zoom in; each page is also available in the PDF |
| The notebook preview does not load | Download it and open it with a notebook-capable editor |
| Numbers differ from the all-data snapshot | Check the current filters, month and bank role against the build guide's reconciliation table |

## What the numbers represent

The analytical snapshot is August 2026; the national history runs from September 2022 through August 2026. These are published aggregate tables, not individual payment records. Merchant shares use the 29 listed categories, bank results use selected banks, and the decline-reduction scenario is hypothetical. See [methodology](METHODOLOGY.md) for the full definitions and limitations.
