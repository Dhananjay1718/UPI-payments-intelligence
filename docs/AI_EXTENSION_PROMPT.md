# Optional AI writing extension

This prompt is an extension exercise. No LLM API integration or paid API call is included in the completed core project.

Give an AI assistant `reports/summary.json`, `reports/validation.json`, `data/sources.csv` and the relevant saved SQL outputs, followed by:

> Write a 200-word payments operations memo using only the supplied evidence. Every numerical claim must name its metric and source ID. Divide statements into observed findings, analyst inference and proposed action. Preserve the reporting date, rounded-source limits and selected bank sample. Do not describe transferred value as revenue, scenario reductions as achieved savings, or forecast scenarios as confidence intervals. If evidence is missing, say what data is needed. Do not invent causes, transactions or recommendations attributed to NPCI.

Acceptance checks: all numbers match the supplied files; sample size and reporting month are correct; bank roles are not combined; no customer-level claims; scenario wording is hypothetical; each action follows from a supplied finding. An unsupported statement fails the review even if the prose sounds convincing.
