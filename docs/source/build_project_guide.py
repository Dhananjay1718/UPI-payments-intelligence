from pathlib import Path
import json
import csv
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, Preformatted
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from matplotlib import get_data_path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/UPI_Project_Guide.pdf'
s=json.loads((ROOT/'reports/summary.json').read_text(encoding='utf-8'))
metrics=list(csv.DictReader((ROOT/'data/processed/forecast_metrics.csv').open(encoding='utf-8')))
FONT_DIR=Path(get_data_path())/'fonts'/'ttf'
pdfmetrics.registerFont(TTFont('DejaVu',str(FONT_DIR/'DejaVuSans.ttf')))
pdfmetrics.registerFont(TTFont('DejaVuBold',str(FONT_DIR/'DejaVuSans-Bold.ttf')))
pdfmetrics.registerFontFamily('DejaVu',normal='DejaVu',bold='DejaVuBold')
navy=colors.HexColor('#142B45');blue=colors.HexColor('#2A70B8');light=colors.HexColor('#EDF3F9');gray=colors.HexColor('#52647A')
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='BodyCustom',fontName='DejaVu',fontSize=10.2,leading=15.5,textColor=navy,spaceAfter=9))
styles.add(ParagraphStyle(name='SmallCustom',fontName='DejaVu',fontSize=8.5,leading=12,textColor=gray,spaceAfter=7))
styles.add(ParagraphStyle(name='HeadCustom',fontName='DejaVuBold',fontSize=22,leading=27,textColor=navy,spaceAfter=18))
styles.add(ParagraphStyle(name='SubCustom',fontName='DejaVuBold',fontSize=12,leading=17,textColor=blue,spaceBefore=10,spaceAfter=8))
styles.add(ParagraphStyle(name='CoverCustom',fontName='DejaVuBold',fontSize=34,leading=41,textColor=navy,spaceAfter=20))
styles.add(ParagraphStyle(name='TableCustom',fontName='DejaVu',fontSize=8.6,leading=12,textColor=navy))
styles.add(ParagraphStyle(name='TableHeadCustom',fontName='DejaVuBold',fontSize=8.6,leading=12,textColor=colors.white))
styles.add(ParagraphStyle(name='CodeCustom',fontName='Courier',fontSize=8.7,leading=12,textColor=navy,backColor=light,borderPadding=9,spaceBefore=8,spaceAfter=12))
story=[]
def p(text,style='BodyCustom'):story.append(Paragraph(text,styles[style]))
def heading(k,title):
 if story:story.append(PageBreak())
 p(k.upper(),'SmallCustom');p(title,'HeadCustom')
def sub(t):p(t,'SubCustom')
def table(headers,rows,widths):
 data=[[Paragraph(escape(str(x)),styles['TableHeadCustom']) for x in headers]]+[[Paragraph(escape(str(x)),styles['TableCustom']) for x in row] for row in rows]
 tb=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
 tb.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),navy),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,light]),('LINEBELOW',(0,0),(-1,0),.6,navy)]))
 story.append(tb);story.append(Spacer(1,10))
def code(t):story.append(Preformatted(t,styles['CodeCustom']))
def footer(c,doc):
 c.saveState();w,h=A4;c.setStrokeColor(colors.HexColor('#D9E2EC'));c.line(45,42,w-45,42);c.setFont('DejaVu',8);c.setFillColor(gray);c.drawString(45,28,'UPI Payments Intelligence  |  Dhananjay Gupta');c.drawRightString(w-45,28,str(doc.page));c.restoreState()

p('PORTFOLIO PROJECT AND LEARNING GUIDE','SmallCustom')
story.append(Spacer(1,25))
p('UPI Payments<br/>Intelligence','CoverCustom')
p('Growth, merchant activity and operational investigation','SubCustom')
p('Prepared for Dhananjay Gupta. Build on your SQL, Excel, Power BI and business fundamentals while learning pandas, NumPy and more advanced analytical methods.')
story.append(Spacer(1,15))
table(['The decision','The evidence'],[
 ['Where should a payments team investigate capacity, activity and technical declines?','48 national months, 29 merchant categories, 12 bank-role observations and 37 geography rows.'],
 ['Latest observed month','August 2026. Research snapshot: 22 September 2026.'],
 ['Published data, clearly labelled','Latest five national months verified against NPCI. Remaining detail is published, rounded NPCI-attributed data from India Dispatch Research.'],
 ['What you receive','Executable Python, an executed notebook, a populated SQL database, 15 business queries, Excel analysis, dashboard and Power BI build kit.'],
 ],[220,285])
p('Start with the business question. Then run the pipeline. Learn each technique when it solves a question in this project.','SubCustom')
p('A native Power BI PBIX is a local build step. The supplied Power Query, DAX and page instructions make that step concrete. This package does not claim that your Power BI report has already been built.','SmallCustom')

heading('01 / Business output','What the analysis found')
story.append(Image(str(ROOT/'reports/dashboard.png'),width=505,height=315.6))
story.append(Spacer(1,12))
table(['Observation','Proposed investigation'],[
 [f"{s['latest_volume_bn']:.2f} billion transactions in August; about {s['latest_yoy']:.1%} annual volume growth.",'Review daily processing capacity and peak-period behavior. Monthly totals alone cannot size peak infrastructure.'],
 ['Groceries lead the displayed merchant categories at about 4 billion payments.','Review checkout success and service capacity for this high-volume category.'],
 [f"About {s['unclassified_share']:.1%} of national volume is unclassified by state.",'Improve location attribution before using this dataset to choose expansion territories.'],
 ],[245,260])
p('These are proposed actions. The source does not prove the cause of payment failures or any achieved commercial benefit.','SmallCustom')

heading('02 / Data design','Understand what one row means')
table(['Dataset','Grain','Coverage'],[
 ['National monthly','One national month','48 months: Sep 2022-Aug 2026'],
 ['Merchants','One category-month','29 displayed categories, Aug 2026'],
 ['Banks','One bank-role-month','Six displayed banks on each side, Aug 2026'],
 ['Geography','One state/territory-month','36 state/territory rows + Unclassified'],
 ],[118,166,221])
sub('Four rules that prevent misleading results')
p('<b>Keep denominators explicit.</b> A category share uses the 29 observed categories. It must not be labelled as a share of all merchant payments.')
p('<b>Separate bank roles.</b> A payment can be represented on both the sending and receiving sides. Adding their attempt or decline totals double-counts overlapping activity.')
p('<b>Retain uncertainty.</b> Secondary tables display rounded values. Unavailable comparisons remain missing. A reported value below 0.01% is a bound, not zero.')
p('<b>Do not confuse value with revenue.</b> National UPI value is money transferred. It includes transfers between people and repeated movements of funds.')
sub('Core units')
table(['Conversion','Use'],[['1 billion = 1,000 million','Convert volume_mn to dashboard billions.'],['1 crore INR = 10 million INR','Average ticket = value_cr x 10 / volume_mn.'],['1 lakh crore = 100,000 crore','Display large national values in Indian units.']],[245,260])
p('Detailed definitions and every important metric contract are in docs/DATA_DICTIONARY.md.','SmallCustom')

heading('03 / Python workflow','Run it, then read it')
p('Open a terminal in the extracted UPI_Payments_Intelligence folder. Use Python 3.10 or newer. Create a virtual environment if you want to keep project dependencies separate.')
code('python -m pip install -r requirements.txt\npython src/pipeline.py\npython -m unittest discover -s tests -v')
table(['Stage','Code technique','Why it is used'],[
 ['Read','pd.read_csv','Load snapshots with their original reporting labels.'],
 ['Clean','Dates, regex, unit conversion','Make comparable numeric fields from published strings.'],
 ['Validate','Key and range checks','Catch duplicate grains, invalid rates and source conflicts.'],
 ['Transform','groupby, merge, rolling, pct_change','Calculate growth, ratios and category context.'],
 ['Model','np.select and np.linalg.lstsq','Build explainable segments and a basic trend model.'],
 ['Publish','SQLite, CSV, matplotlib','Produce results reusable by SQL, Excel and Power BI.'],
 ],[83,151,271])
sub('Your first calculation')
code('ticket_inr = 10 * value_cr / volume_mn\n# August 2026 inputs:\n# value_cr = 2982355.95\n# volume_mn = 24508.96\n# Result: about INR 1216.84')
p('The project works offline after dependencies are installed. You do not need an API key or a database server for the first successful run. The included notebook contains nine executed code cells and explanations.','SmallCustom')

heading('04 / SQL practice','15 business questions, with purpose')
table(['Query','Question','Topic and reason'],[
 ['Q01','What is the latest national scale?','SELECT and units; publish interpretable KPIs.'],
 ['Q02','How did activity change monthly?','CTE + LAG; compare adjacent observations.'],
 ['Q03','How did activity change annually?','LAG(...,12); compare the same month last year.'],
 ['Q04','What does a smoothed trend show?','Window frame; average three complete months.'],
 ['Q05','What is the annual average ticket?','JOIN + GROUP BY; calculate ratio of totals.'],
 ['Q06','Which categories carry volume?','Dimension join + DENSE_RANK; ordered comparison.'],
 ['Q07','How concentrated is observed activity?','Cumulative SUM; category Pareto analysis.'],
 ['Q08','Which categories contracted?','WHERE on negative growth; investigation candidates.'],
 ['Q09','What is the sample TD rate?','Weighted aggregation; volumes differ across banks.'],
 ['Q10','Which banks affect most attempts?','Rate x volume, rank within each role.'],
 ['Q11','What might an improvement change?','CASE + explicit assumptions; scenario arithmetic.'],
 ['Q12','How much geography is missing?','Conditional aggregation and denominator join.'],
 ['Q13','Which rows have official verification?','Source join; data lineage and coverage.'],
 ['Q14','Which forecast performs better?','Filter and order; distinguish validation from test.'],
 ['Q15','Where are annual comparisons absent?','NULL handling; missing growth is not zero.'],
 ],[45,188,272])
p('Every query is saved with comments in sql/analysis_queries.sql. Its executed result is in reports/sql_results. Query blocks are designed for MySQL 8 and were executed using SQLite.','SmallCustom')

heading('05 / Advanced reasoning','Choose the right operational priority')
p('Among the six displayed sending banks, Baroda U.P. Bank has a 2.44% technical-decline rate on about 109.7 million attempts. Central Bank of India has a slightly lower 2.34% rate on about 478.3 million attempts. [S3]')
table(['Bank','Approx. rate','Estimated affected attempts'],[['Baroda U.P. Bank','2.44%','2.677 million'],['Central Bank of India','2.34%','11.192 million']],[192,96,217])
p('Central Bank affects more attempts in this sample. That supports an investigation priority, not a conclusion about root cause or the bank as a whole.')
sub('Why weighted rates matter')
code('weighted_td = sum(attempts * td_rate) / sum(attempts)\n# Not: mean(td_rate)')
p('An unweighted mean gives a small bank the same influence as a large bank. Weighting answers the rate across the displayed attempts. It still does not correct the bias created by a selected high-decline sample.')
sub('An explicit what-if scenario')
p('Assume a target TD of 0.5%, and assume half of the excess declines could be prevented. Those are analyst choices, not NPCI standards.')
code('avoided = attempts * max(td_rate - 0.005, 0) * 0.50')
p(f"Across the displayed sending sample this gives about <b>{s['sending_scenario_avoided_mn']:.2f} million hypothetical avoided attempts</b>. There is no evidence that the intervention was implemented, that all affected payments were permanently lost, or that these attempts translate into revenue.")

heading('06 / Excel','A workbook you can change')
table(['Sheet','Use'],[['Overview','Latest KPIs, national trend and selected merchant comparisons.'],['Scenario','Editable target and effectiveness; formula-driven hypothetical outcome.'],['Monthly','48 months of source inputs, daily rates, ticket, MoM and YoY formulas.'],['Merchants','Source magnitudes, weighted ticket, observed shares and reported growth.'],['Bank sample','Sending and receiving rows labelled separately; estimated decline counts.'],['Geography','States, Unclassified, calculated share and a rounding reconciliation.']],[115,390])
sub('Three short exercises')
p('<b>1.</b> Open Scenario. B4 is the TD target in basis points: 50 means 0.5%. B5 is the assumed reduction of excess declines in percent: 50 means half. Change B5 to 0. The hypothetical avoided total must become 0 while actual attempts stay unchanged.')
p('<b>2.</b> Restore B5 to 50. Change B4 to 100, meaning a 1% TD target. Explain why the hypothetical opportunity shrinks. Restore the default before comparing to the PDF.')
p('<b>3.</b> On Monthly, trace the latest ticket formula to its two input cells. Recalculate it on your calculator. Then compare total-month growth with daily-rate growth.')
sub('Refresh behavior')
p('The workbook is an editable snapshot. Rebuilding CSVs does not automatically refresh it. For a new source release, update input rows, extend formulas and charts, adjust the latest-month references and reconcile headline figures. The pipeline and Power BI CSV imports have separate refresh steps.')
p('The workbook was recalculated, scanned for formula errors and visually inspected in the authoring engine. Native Excel behavior should be checked on your device.','SmallCustom')

heading('07 / Power BI','Create the four-page report')
p('Use powerbi/BUILD_GUIDE.md for exact steps. LoadCSV.pq imports typed CSVs, Measures.dax defines measures and a full date table, and theme.json supplies the report colors.')
table(['Page','Decision and visuals'],[['1. Network','Latest cards, historical volume, growth and source precision.'],['2. Merchants','Category scale, reported growth, ticket size and analyst segments.'],['3. Operations','Single-select bank role, affected-volume ranking and scenario table.'],['4. Coverage','Unclassified share, geographic comparison and source notes.']],[115,390])
sub('Model relationships')
p('Connect DimDate to the month field in each fact table. Connect dim_merchant to fact_merchant by MCC, and dim_bank to fact_bank by bank_id. Use one-to-many, single-direction relationships. The monthly dimension in SQLite is replaced by a full daily calendar for DAX time intelligence.')
sub('Filter behavior to verify')
p('Selecting a merchant must not multiply or redefine national volume. Bank metrics must require one role. Snapshot pages must remain labelled August 2026; selecting another month should not silently reuse August detail. Format rates as percentages and IDs as text.')
table(['Reconciliation','Expected snapshot result'],[['National volume','24,508.96 million'],['Average ticket','INR 1,216.84'],['MoM volume','3.5954%'],['Unclassified share','About 44.39%'],['Sending-bank hypothetical avoided','About 6.7415 million']],[260,245])
p('<b>Completion boundary:</b> a native PBIX has not been generated or tested. Build it in Desktop, reconcile these controls and add your screenshots to the portfolio.','SmallCustom')

heading('08 / Forecasting','Test a model before trusting it')
table(['Candidate','How it predicts next month'],[['Daily naive','Use the last observed daily rate x days in the target month.'],['Seasonal daily naive','Use the same month last year, normalized to the target month length.'],['12-month log trend','Fit a straight line to log daily volume across the previous 12 months, then convert back and multiply by target days.']],[150,355])
p('The first 30 months provide initial history. The next six months are validation for model selection. The final 12 months are a test period. Each one-month prediction uses only earlier observations, with the selected model fixed before the test period.')
rows=[]
for name in ['daily_naive','seasonal_daily_naive','log_trend_12m']:
 val=next(x for x in metrics if x['model']==name and x['split']=='validation');test=next(x for x in metrics if x['model']==name and x['split']=='test')
 rows.append([name,f"{float(val['wape']):.2%}",f"{float(test['wape']):.2%}"])
table(['Model','Validation WAPE','Test WAPE'],rows,[235,135,135])
p(f"The selected log-trend model has about <b>{s['test_wape']:.2%} test WAPE</b> here. WAPE is total absolute error divided by total actual volume. The test contains only 12 months, and much of the source history is rounded.")
p(f"Using observations through August, the September 2026 full-month baseline is about <b>{s['forecast_bn']:.2f} billion transactions</b>. The +/-10% range in the output is an assumed planning scenario, not a statistical prediction interval.")
p('This is a retrospective evaluation using the data vintage retrieved now. It does not reproduce historical publication delays or revisions. September has 30 days while August has 31, so monthly volume can fall even if the daily rate rises.','SmallCustom')

heading('09 / Learning plan','Build your understanding in four weeks')
table(['Week','Learn while executing','What you must explain'],[
 ['1. Python','pandas inputs, dtypes, date handling, missing values, NumPy vectorization, groupby and validated joins.','The grain; INR units; source precision; one calculated column without copying.'],
 ['2. SQL','Fact/dimension design, JOIN, CTE, LAG, ranking, cumulative SUM and CASE.','Weighted ticket, weighted TD, join fanout and missing YoY.'],
 ['3. Reporting','Excel scenario controls; Power Query; DAX measures, filter context and four Power BI pages.','Why filters change some metrics and must leave others intact.'],
 ['4. Advanced work','Three forecast baselines, temporal splits, MAE/WAPE, sensitivity and a business memo.','Why the scenario is hypothetical, why the forecast may fail and what evidence to request next.'],
 ],[80,222,203])
p('Allow roughly 1.5-2 hours per study day. The full session-by-session plan is in docs/LEARNING_PATH.md. Do not rush ahead simply because a script runs.')
sub('Your first session')
p('Read the business question and data dictionary. Open monthly_reported.csv and official_monthly_overrides.csv. Run pipeline.py. Independently reproduce the August average ticket. Write two sentences explaining why volume and transferred value are different.')
sub('Your first independent improvement')
p('Choose one: improve a chart label; add a SQL question about daily growth; compare a second target in the scenario; or write a better data-quality check. Record the reason and result in MY_CONTRIBUTION.md.')
sub('AI extension, after the core works')
p('The optional prompt can draft a memo from validated metrics. It is not an implemented API feature. Check every number and source ID. Reject invented root causes, national claims from the bank sample and supposed achieved savings.')

heading('10 / Interview preparation','Explain the choices behind the result')
table(['Likely question','A defensible answer'],[
 ['What problem does it solve?','It helps a payments team review growth, merchant mix, selected bank failures and data coverage before choosing investigations.'],
 ['Why this dataset?','It is current, published and relevant to Indian payments. I distinguish official verification from rounded secondary detail.'],
 ['What did pandas add?','Type cleaning, unit conversion, validated joins, group operations, rolling growth and repeatable outputs.'],
 ['Where did NumPy help?','Vectorized segmentation, weighted averages and least-squares fitting for an explainable forecast baseline.'],
 ['Why not average TD percentages?','Volumes differ. Use sum(volume x rate) / sum(volume), and state the sample coverage.'],
 ['How did you prevent leakage?','Each forecast uses only prior months. Model selection uses validation; test results are reported separately.'],
 ['Did you reduce failures by 6.74 million?','No. That is a scenario under explicit target/effectiveness assumptions, not measured impact.'],
 ['What would you improve next?','Full official bank history, verified unrounded monthly data and real error/retry logs for root-cause work.'],
 ],[160,345])
sub('A three-minute walkthrough')
p('Spend 30 seconds on the business question, 40 on sources and cleaning, 40 on two findings, 40 on one technical choice and 30 on limitations and the next evidence needed. Show one query and one chart you can explain from memory.')
p('Use the contribution log honestly. Describe AI assistance and your own verification and changes. List Power BI as completed only after you build the native report.','SmallCustom')

heading('11 / Verification and sources','What is checked, and what remains')
table(['Component','Status'],[['Python pipeline and SQL','Executed. All 15 query outputs saved.'],['Validation tests','Nine tests passed: units, keys, rates, missingness, known source control, temporal leakage, model selection, SQL rates and scenario bounds.'],['Notebook','Nine code cells executed and saved with outputs.'],['Excel','Recalculated; formula error scan passed; scenario changes and headline values reconciled; sheet previews inspected.'],['Power BI Desktop / MySQL server','Kit/import supplied. Native application execution not performed.'],['Publication','Files packaged. No GitHub upload or public deployment.']],[145,360])
sub('Source register')
p('<b>S1. NPCI:</b> official UPI product statistics. April-August 2026 national volume/value/bank counts. Retrieved 22 September 2026.','SmallCustom')
p('<link href="https://www.npci.org.in/product/upi/product-statistics" color="#2A70B8">https://www.npci.org.in/product/upi/product-statistics</link>','SmallCustom')
p('<b>S2. India Dispatch Research:</b> monthly UPI table, attributing NPCI. September 2022-August 2026 at displayed rounded precision. Latest five months reconciled and replaced with S1.','SmallCustom')
p('<link href="https://data.indiadispatch.com/payments/upi-transactions" color="#2A70B8">https://data.indiadispatch.com/payments/upi-transactions</link>','SmallCustom')
p('<b>S3. India Dispatch Research:</b> August 2026 merchant, selected bank and geography tables, attributing NPCI. No full-bank national conclusions are drawn.','SmallCustom')
p('<link href="https://data.indiadispatch.com/payments" color="#2A70B8">https://data.indiadispatch.com/payments</link>','SmallCustom')
p('Implementation references: Microsoft Learn star-schema, date-table and DATEADD documentation, linked in the Power BI build guide. Full source metadata and input hashes are retained with the code.','SmallCustom')

doc=SimpleDocTemplate(str(OUT),pagesize=A4,rightMargin=45,leftMargin=45,topMargin=42,bottomMargin=58,title='UPI Payments Intelligence - Project and Learning Guide',author='Prepared for Dhananjay Gupta')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print(OUT)
