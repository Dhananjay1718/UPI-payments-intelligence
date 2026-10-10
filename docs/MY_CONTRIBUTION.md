# Contribution and evidence

This is a guided portfolio project developed with AI assistance. The record describes work evidenced in the project and its build conversation; it does not claim that every code line was written independently.

| Work | Evidence / outcome |
|---|---|
| Worked through Python data preparation and analysis | Pipeline, guided notebook, processed CSVs and reconciled outputs; explanations used for interview preparation |
| Created/imported MySQL tables and ran analytical questions | User-reviewed query outputs through the core SQL work, including bank scenarios and geographic coverage; 15 reproducible query blocks included |
| Built the Power BI data model | Imported fact/dimension CSVs and created the report relationships |
| Built four analytical pages and the Home page | Native PBIX, five-page PDF and matching screenshots |
| Refined measures and formatting | Unscaled INR display, percentage formatting, weighted bank rate, Top N filters and category segments |
| Configured filter behavior | User-tested merchant and bank filters; state selection preserves global geographic coverage; trend-year selection preserves August KPI cards |
| Added navigation and visual styling | Four Home-page navigation buttons, return-Home buttons, consistent blue palette and decorative illustrations |
| Reviewed findings and limitations | Explicit snapshot periods, selected-bank scope, category-share denominator and hypothetical scenario labels |

AI helped with code, debugging, explanations, design examples, decorative illustrations and documentation. The author performed the local Power BI editing and reported test outcomes. The attached PDF proves report layout and visible results; the supplied native PBIX distributes the interactive report. Its report definitions were inspected for page destinations, filters and selected interactions; native DAX and refresh were not executed in this environment.

The release-preparation run regenerated the Python outputs and notebook, ran the original nine analytical tests; the later folder review also passed three extraction-date tests, rendered all five PDF pages and reconciled headline figures. See reports/release_validation.json for the recorded results.
