from pathlib import Path
import sys,json,textwrap,html
import pandas as pd
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak,Preformatted,Table,TableStyle,Image
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from matplotlib import get_data_path
FONT_DIR=Path(get_data_path())/'fonts'/'ttf'
pdfmetrics.registerFont(TTFont("DejaVuMono", str(FONT_DIR/'DejaVuSansMono.ttf')))
R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'src'));import pipeline
m,mer,b,s=pipeline.clean_data(); send=b[b.role.eq('Sending')].sort_values('estimated_td_mn',ascending=False)
pdfmetrics.registerFont(TTFont('DV', str(FONT_DIR/'DejaVuSans.ttf')))
pdfmetrics.registerFont(TTFont('DV-Bold', str(FONT_DIR/'DejaVuSans-Bold.ttf')))
pdfmetrics.registerFontFamily('DV',normal='DV',bold='DV-Bold',italic='DV',boldItalic='DV-Bold')
styles=getSampleStyleSheet()
styles['Heading1'].fontName='DV-Bold'
styles['Heading2'].fontName='DV-Bold'
styles.add(ParagraphStyle(name='BodyX',fontName='DV',fontSize=10,leading=15,spaceAfter=9,textColor=colors.HexColor('#233449')))
styles.add(ParagraphStyle(name='CodeX',fontName='DejaVuMono',fontSize=7.3,leading=10,backColor=colors.HexColor('#F1F5F9'),borderPadding=8,spaceAfter=10))
styles['Heading1'].textColor=colors.HexColor('#123954');styles['Heading1'].fontSize=22;styles['Heading1'].leading=26
styles['Heading2'].textColor=colors.HexColor('#087F8C')
flow=[]
def p(t):flow.append(Paragraph(t,styles['BodyX']))
def h(t):flow.append(Paragraph(t,styles['Heading2']))
def page(t):
 if flow:flow.append(PageBreak())
 flow.append(Paragraph(t,styles['Heading1']));flow.append(Spacer(1,12))
def code(t):
 lines=[]
 for l in t.strip('\n').splitlines():
  lines.extend(textwrap.wrap(l,100,replace_whitespace=False,drop_whitespace=False,subsequent_indent='    ') or [''])
 flow.append(Preformatted('\n'.join(lines),styles['CodeX']))
def table(headers,rows,widths=None):
 data=[[Paragraph(html.escape(str(x)),styles['BodyX']) for x in row] for row in [headers]+rows]
 t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT');t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#DDEEF2')),('VALIGN',(0,0),(-1,-1),'TOP'),('BOTTOMPADDING',(0,0),(-1,-1),5),('TOPPADDING',(0,0),(-1,-1),5),('LINEBELOW',(0,0),(-1,0),.7,colors.HexColor('#087F8C')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F5F7FA')])]))
 flow.append(t);flow.append(Spacer(1,10))
page('UPI Payments Intelligence<br/>Python interview preparation')
p('<b>Prepared for Dhananjay Gupta</b> | Python phase study companion | 27 September 2026')
p('The business questions, Python programs, answers, explanations and limitations behind your completed practice. Use this guide to explain your reasoning, not just memorise outputs.')
h('What this guide is based on')
p('The original UPI_Payments_Intelligence_Project.zip, its Python pipeline, executed notebook, raw snapshots, processed data and tests, plus the lesson code and completion checkpoints visible in our conversation.')
p('<b>Verification:</b> the packaged pipeline was rerun for this guide; all nine tests passed and the learning-assets script executed nine notebook code cells. Numerical answers below are reproduced from that packaged snapshot. External source pages were not independently reverified for this PDF; primary_verified is the package\'s provenance label.')
h('A clear record of your progress')
p('You completed core Python cleaning, calculations, charts, merchant segmentation, bank analysis, location coverage and the pipeline/test commands. Forecasting was executed by the supplied pipeline, but its detailed study was deferred. Power BI has not yet been completed in this learning sequence.')
p('The separate lesson_01.py and lesson_02.py files are not in the archive and their exact original text is not visible here. Their cleaning and calculation topics are explained using the recovered pipeline; they are not presented as verbatim lesson files. The full recovered pipeline and notebook code are included in the appendices.')
h('How to study')
p('Read sections 1-10 first. Then practise the interview questions aloud and trace the code appendices. For every result, explain its unit, denominator, scope and limitation.')
page('1 | Project purpose and data')
p('<b>Decision:</b> where should a payments operations team investigate processing capacity, merchant activity and technical declines? Python transforms published aggregate snapshots into reproducible evidence for that decision.')
table(['Dataset','Rows / period','One row means'],[['Monthly','48; Sep 2022-Aug 2026','One national month'],['Merchants','29; Aug 2026','One merchant category-month'],['Banks','12; Aug 2026','One bank-role-month; six per role'],['Locations','37; Aug 2026','One state/UT or Unclassified entry']],[95,145,255])
p('<b>Grain</b> means what one row represents. These are aggregate data, not individual payments or customer records. They cannot reveal individual retry journeys, customer retention, fraud cases or technical root causes.')
h('Why each library was used')
table(['Library','Use in this project'],[['pandas','Read CSVs, clean columns, handle dates, calculate metrics, group and join tables.'],['NumPy','Conditional segments, weighted averages, numeric comparisons and supplied forecast maths.'],['Matplotlib','Two practice trend charts and the supplied dashboard image.'],['pathlib','Build readable file paths and create output directories.'],['sqlite3 / unittest','Persist the analytical database and verify important business rules.']],[115,380])
p('<b>Interview answer:</b> I used Python to standardise inconsistent published units, calculate comparable metrics and validate aggregate data before SQL and dashboard reporting.')
page('2 | Importing, cleaning and provenance')
h('Problem solved')
p('Published strings contain units such as million, billion and trillion. Dates need chronological ordering; some percentages contain a Unicode minus sign. Treating these fields as plain strings would make arithmetic or comparisons unreliable.')
code("""raw = pd.read_csv('data/raw/monthly_reported.csv')
raw['month'] = pd.to_datetime(raw['month_label'], format='%B %Y')
raw['volume_mn'] = raw['volume_reported'].map(pipeline.compact_number) / 1e6
raw['value_cr'] = raw['value_reported'].map(pipeline.compact_number) / 1e7
raw = raw.sort_values('month').reset_index(drop=True)""")
p('This explanatory extract uses the recovered pipeline helper; it is not the missing original lesson file. read_csv creates a DataFrame. to_datetime makes calendar operations possible. map applies a parser to each value. Sorting must happen before growth or rolling calculations.')
h('Unit conversions')
table(['Conversion','Reason'],[['Billion to million: × 1,000','All payment counts use millions.'],['Trillion rupees to crore: × 100,000','One crore is 10 million rupees.'],['2.34% to rate: ÷ 100 = 0.0234','Multiplication needs the decimal fraction.']],[240,255])
p('compact_number uses a regular expression to capture the first reported number and unit. This prevents a secondary US-dollar amount in the same source string from being mistaken for the rupee amount.')
p('The pipeline labels 43 older monthly rows secondary_rounded. Five April-August 2026 rows are replaced from official_monthly_overrides.csv and labelled primary_verified. It checks differences against the rounding tolerances before replacement, rather than silently accepting source conflicts.')
p('Missing comparisons and censored values such as &lt;0.01% remain missing numeric values; a true 0% stays zero. Keeping the original label preserves information that a numeric point estimate cannot represent.')
page('3 | Monthly questions and answers')
table(['Question','Calculation / answer'],[['What is the latest payment count?','24,508.96 million = 24.50896 billion.'],['What is the latest transferred value?','2,982,355.95 crore = 29.8235595 lakh crore.'],['What is the average payment?','10 × value_cr / volume_mn = INR 1,216.84.'],['How busy is an average day?','24,508.96 / 31 = 790.61 million payments/day.'],['How did volume change MoM?','(current / previous - 1) × 100 = 3.60%.'],['How did volume change YoY?','(current / 12 months earlier - 1) × 100 = approximately 22.48%.']],[220,275])
code("""m['days_in_month'] = m.month.dt.days_in_month
m['daily_volume_mn'] = m.volume_mn / m.days_in_month
m['avg_ticket_inr'] = 10 * m.value_cr / m.volume_mn
m['mom_volume'] = m.volume_mn.pct_change(fill_method=None)
m['mom_daily_volume'] = m.daily_volume_mn.pct_change(fill_method=None)
m['yoy_volume'] = m.volume_mn.pct_change(12, fill_method=None)
m['rolling_3m_volume_mn'] = m.volume_mn.rolling(3, min_periods=3).mean()""")
p('These are actual calculations in pipeline.py. pct_change returns a decimal fraction: multiply by 100 for percentage display. The first MoM value and first 12 YoY values are missing because no earlier comparison exists. min_periods=3 prevents a partial three-month average.')
p('<b>Important distinction:</b> this Python pipeline smooths monthly volume. Your later SQL Q7 smooths average daily volume. They are different measures and should not be expected to match.')
p('Average ticket is a ratio of total value to total count, not an unweighted mean of monthly averages. Transferred payment value is not company revenue or profit.')
page('4 | Lesson 3: charts and CSV export')
p('<b>Questions:</b> how has daily payment activity changed, and how has the typical payment amount changed? You saved and opened two line-chart PNGs. The conversation confirms an analysis CSV with 48 rows and 13 columns.')
code("""from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

chart_folder = Path('reports/practice')
chart_folder.mkdir(parents=True, exist_ok=True)

def save_chart(column, title, y_label, filename):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df['month'], df[column], linewidth=2)
    ax.set_title(title)
    ax.set_xlabel('Month (Sep 2022-Aug 2026)')
    ax.set_ylabel(y_label)
    ax.set_ylim(bottom=0)
    ax.set_xlim(df['month'].min(), df['month'].max())
    ax.grid(axis='y', alpha=0.25)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(chart_folder / filename, dpi=180)
    plt.close(fig)

save_chart('daily_volume_mn', 'UPI: average daily transactions',
           'Million transactions per day', '01_daily_transactions.png')
save_chart('avg_ticket_inr', 'UPI: average payment amount',
           'INR per payment', '02_average_payment.png')
df.to_csv('data/processed/monthly_analysis_practice.csv', index=False)""")
p('Compact reconstruction of the chart block shown in the conversation; df is the cleaned monthly analysis DataFrame. The original chart included a source/precision footer. The exact opening portion of lesson_03.py was not available.')
p('A reusable function avoids repeating chart instructions. fig is the whole figure; ax is its plotting area. DateFormatter makes readable dates, savefig writes the image, and close releases memory. index=False avoids exporting an extra DataFrame row-number column.')
p('<b>Finding:</b> daily activity trends upward overall, ending at 790.61 million/day; average ticket trends downward overall, ending at INR 1,216.84. Neither trend must be monotonic, and the charts alone do not establish why it occurred.')
page('5 | Lesson 4: merchant cleaning and shares')
p('<b>Question:</b> which merchant categories handle the most payments? We standardised count units, separated names from MCC codes and calculated each category\'s share of the observed sample.')
code("""raw = pd.read_csv('data/raw/merchants_reported.csv')
merchants = raw[['month', 'source_id']].copy()
merchants['month'] = pd.to_datetime(merchants['month'])
names = raw['merchant_reported'].str.rsplit('MCC ', n=1, expand=True)
merchants['merchant'] = names[0].str.strip()
merchants['mcc'] = names[1].str.strip()
volume = raw['volume_reported'].str.split(expand=True)
merchants['volume_mn'] = (
    volume[0].astype(float)
    * volume[1].map({'million': 1, 'billion': 1000})
)
merchants['mom_growth_pct'] = (
    raw['mom_reported'].str.replace('\u2212', '-', regex=False)
    .str.replace('%', '', regex=False).astype(float)
)
merchants['source_precision'] = 'secondary_rounded'
assert not merchants.isna().any().any()
assert not merchants.duplicated(['month', 'mcc']).any()
assert (merchants['volume_mn'] > 0).all()
latest_month = merchants['month'].max()
merchants = merchants.loc[merchants['month'] == latest_month].copy()
merchants['observed_share_pct'] = (
    merchants['volume_mn'] / merchants['volume_mn'].sum() * 100
)""")
p('rsplit separates at the last MCC marker; strip removes edge whitespace. MCC is an identifier and should stay text. astype(float) enables arithmetic. map performs a unit lookup; an unknown unit becomes missing and is caught by the check.')
p('<b>Denominator:</b> the combined volume of these 29 categories, 12,534.3 million. It is neither all national UPI nor necessarily all merchant payments. In the lesson, mom_growth_pct is in percentage points; the pipeline\'s mom_volume is a decimal fraction.')
page('6 | Lesson 4: segmentation and outputs')
code("""median_volume = merchants['volume_mn'].median()
large = merchants['volume_mn'] >= median_volume
growing = merchants['mom_growth_pct'] > 0
contracting = merchants['mom_growth_pct'] < 0
merchants['segment'] = np.select(
    [large & growing, large & contracting,
     ~large & growing, ~large & contracting],
    ['Larger and growing', 'Larger and contracting',
     'Smaller and growing', 'Smaller and contracting'],
    default='Flat'
)
summary = merchants.groupby('segment', as_index=False).agg(
    categories=('mcc', 'count'), volume_mn=('volume_mn', 'sum')
)
output_folder = Path('data/processed')
output_folder.mkdir(parents=True, exist_ok=True)
merchants.to_csv(output_folder / 'merchant_analysis_practice.csv', index=False)
summary.to_csv(output_folder / 'merchant_segments_practice.csv', index=False)""")
p('The median is 149.6 million payments. With 29 categories, it is the 15th sorted value. At or above the median is our definition of larger. & combines Boolean conditions; ~ reverses them. np.select is similar to SQL CASE WHEN. groupby().agg() creates one summary row per segment.')
table(['Segment','Categories','Volume, million'],[['Larger and contracting',3,1185.4],['Larger and growing',12,10012.7],['Smaller and contracting',6,565.2],['Smaller and growing',8,771.0]],[245,90,160])
p('<b>Finding:</b> three larger categories are contracting and warrant review. Volume and growth together provide more context than either alone. Negative growth does not prove a technical problem.')
p('<b>Code nuance:</b> the practice lesson labels zero growth Flat. The supplied pipeline groups zero growth with growing (>= 0). This snapshot has no zero-growth categories, so the segment counts agree here. Future data could produce different labels unless the rule is standardised.')
page('7 | Merchant findings to explain')
top=mer.nlargest(5,'volume_mn')
table(['Category','Million payments','Observed share'],[[r.merchant,f'{r.volume_mn:,.1f}',f'{r.observed_volume_share:.2%}'] for r in top.itertuples()],[255,120,120])
p('<b>Answer:</b> groceries and supermarkets rank first: 4,000 million payments and 31.91% of observed category volume. Together the top five represent about 67.10%; that concentration was subsequently calculated explicitly in SQL.')
h('Larger categories with declining volume')
contract=mer[mer.segment.eq('Larger and contracting')]
table(['Category','Million payments','Reported MoM'],[[r.merchant,f'{r.volume_mn:,.1f}',f'{r.mom_volume:.2%}'] for r in contract.itertuples()],[255,120,120])
p('<b>Recommended investigation:</b> compare category activity with earlier complete snapshots, seasonality and merchant operational logs before proposing a cause. This dataset supplies reported growth rates, not enough category-month history to independently reconstruct every growth figure.')
h('Interview answer')
p('I combined category size and reported growth using a median-based rule. I calculated shares within the observed 29 categories, clearly named the denominator, and identified larger shrinking categories for investigation. I did not claim that this sample represented the entire UPI merchant network.')
page('8 | Lesson 5: bank analysis')
code("""def to_millions(series):
    parts = series.str.split(expand=True)
    return parts[0].astype(float) * parts[1].map(
        {'million': 1, 'billion': 1000})

banks = pd.read_csv('data/raw/banks_reported.csv', parse_dates=['month'])
banks['bank'] = banks['bank'].str.strip()
banks['volume_mn'] = to_millions(banks['volume_reported'])
banks['td_pct'] = banks['td_reported'].str.replace(
    '%', '', regex=False).astype(float)
banks['td_rate'] = banks['td_pct'] / 100
assert banks['volume_mn'].gt(0).all()
assert banks['td_rate'].between(0, 1).all()
assert not banks.duplicated(['month', 'role', 'bank']).any()
banks['estimated_td_mn'] = banks['volume_mn'] * banks['td_rate']
latest_month = banks['month'].max()
sending = banks.loc[(banks['month'] == latest_month)
                    & (banks['role'] == 'Sending')].copy()
assert len(sending) > 0
sending = sending.sort_values('estimated_td_mn', ascending=False)
weighted_td_pct = (sending['estimated_td_mn'].sum()
                   / sending['volume_mn'].sum() * 100)""")
p('The helper is reused for banks and states. parse_dates loads a date column immediately. The compound bank key includes role because a bank may appear as both sender and receiver. Filtering before aggregation keeps the populations separate.')
p('<b>Answer:</b> Central Bank of India leads the investigation queue: 478.3 million attempts × 0.0234 = 11.19222 million estimated declines, displayed as 11.19 million.')
p('<b>Weighted sample rate:</b> approximately 2.04%. It is total estimated declines divided by total attempts. A simple mean would give small and large banks equal importance.')
p('Technical declines concern system/network issues; these aggregate counts cannot diagnose the specific root cause. Do not sum sending and receiving volumes into a national total: they are different sides of payment processing and the samples are incomplete.')
page('9 | Bank answers and what-if scenario')
table(['Sending bank','TD rate','Estimated declines (mn)'],[[r.bank,f'{r.td_rate:.2%}',f'{r.estimated_td_mn:.2f}'] for r in send.itertuples()],[270,85,140])
code("""benchmark_rate = 0.005
reduction_fraction = 0.50
sending['scenario_avoided_td_mn'] = (
    sending['volume_mn']
    * (sending['td_rate'] - benchmark_rate).clip(lower=0)
    * reduction_fraction
)""")
p('<b>Scenario question:</b> if the rate above a 0.5% benchmark were halved, how many declines might be avoided at unchanged volume? clip(lower=0) prevents negative reductions for banks already below target.')
p('For Central Bank: 2.34% - 0.50% = 1.84 percentage points of excess. Half is 0.92 percentage points. The scenario rate is therefore 1.42%, not 1.17% and not 0.5%.')
p('<b>Answer:</b> 6.741495 million, approximately 6.74 million, hypothetically avoided declines across the six selected sending banks. This is not an achieved result, a forecast of actual recovery or money saved.')
p('Saved practice outputs: bank_analysis_practice.csv contains all 12 bank-role rows. bank_sending_priority_practice.csv contains the six sending-bank rows with the scenario column. The pipeline uses scenario_avoided_mn for the corresponding metric.')
page('10 | Lesson 5: location coverage')
code("""states = pd.read_csv('data/raw/states_reported.csv', parse_dates=['month'])
states['state'] = states['state'].str.strip()
states['volume_mn'] = to_millions(states['volume_reported'])
assert states['volume_mn'].gt(0).all()
assert not states.duplicated(['month', 'state']).any()
national = pd.read_csv('data/processed/monthly_cleaned_practice.csv',
                       parse_dates=['month'])
states = states.merge(
    national[['month', 'volume_mn']].rename(
        columns={'volume_mn': 'national_volume_mn'}),
    on='month', how='left', validate='many_to_one')
assert states['national_volume_mn'].notna().all()
states['national_share_pct'] = (
    states['volume_mn'] / states['national_volume_mn'] * 100)
snapshot = states.loc[states['month'] == latest_month].copy()
unclassified = snapshot.loc[snapshot['state'] == 'Unclassified']
assert len(unclassified) == 1
unclassified_pct = unclassified['national_share_pct'].iloc[0]
states.to_csv('data/processed/state_coverage_practice.csv', index=False)""")
p('latest_month above comes from the bank section of the same lesson; both snapshots are August 2026. In a general refresh, check that their dates agree rather than assuming the bank and location snapshots always align.')
p('A left merge keeps every location row. many_to_one checks that many locations match only one national row for each month. Duplicate national months could otherwise multiply rows and corrupt totals. iloc[0] extracts the one expected Unclassified value.')
p('<b>Answer:</b> 10,880 / 24,508.96 × 100 = 44.39% unclassified. There are 37 location entries, including Unclassified. A substantial part of national volume cannot be assigned geographically in this snapshot.')
p('Unclassified is an explicit category, not a blank to delete. Rounded location rows need not sum exactly to the more precise national total. A residual is a reconciliation finding, not proof of lost payments. Recorded volume is not per-capita adoption.')
page('11 | Pipeline, files and execution')
code('python src/pipeline.py\npython -m unittest discover -s tests -v\npython src/build_learning_assets.py')
table(['Program / function','Responsibility'],[['clean_data()','Read raw snapshots, parse units, apply overrides, calculate metrics and validate grains.'],['forecasting()','Run supplied baselines and log-trend evaluation; detailed learning deferred.'],['warehouse()','Create nine SQLite tables; export bundled SQL results; reconcile average ticket.'],['figures()','Create reports/dashboard.png.'],['main()','Coordinate execution, CSV exports, summary, validation report and workbook payload.'],['build_learning_assets.py','Execute the guided notebook and generate sql/mysql_import.sql.']],[175,320])
p('pipeline.py uses Path(__file__).resolve().parents[1], so paths are anchored to the script\'s project root. The practice lesson files use relative paths and should be run from the project folder.')
p('The analytical SQLite database is rebuilt by the pipeline; raw CSV snapshots remain unchanged. The separate MySQL export is generated for later import. Rebuilding CSVs does not automatically refresh an existing Excel workbook or Power BI report.')
h('Outputs you should recognise')
p('Practice: monthly_cleaned_practice.csv; monthly_analysis_practice.csv; two practice PNGs; merchant_analysis_practice.csv; merchant_segments_practice.csv; bank_analysis_practice.csv; bank_sending_priority_practice.csv; state_coverage_practice.csv.')
p('Supplied pipeline: data/processed/*.csv; data/upi_intelligence.sqlite; reports/summary.json; reports/validation.json; reports/sql_results/*.csv; reports/dashboard.png; reports/workbook_data.json. Learning assets: notebooks/01_guided_analysis.ipynb and sql/mysql_import.sql.')
page('12 | What the nine tests protect')
table(['Test','Business risk prevented'],[['Units and secondary currency','Confusing rupees, crore, million or secondary USD text.'],['Duplicate keys','Double-counting through repeated records or joins.'],['Impossible rates','Treating 2.44 as a decimal fraction instead of 2.44%.'],['Missing / censored values','Replacing unknown or below-threshold values with zero.'],['Known snapshot control','Unexpected latest month, total volume or override count.'],['Forecast future isolation','Using future observations in a historical prediction.'],['Validation-only selection','Choosing a model using the held-out test result.'],['SQL rate and grain consistency','Different weighted rates in Python and SQL, or broken foreign keys.'],['Scenario bounds','Negative avoided declines or more avoided than estimated.']],[180,315])
p('<b>Verified result:</b> Ran 9 tests - OK. The learning-assets command also printed: Executed 9 notebook code cells; exported MySQL import.')
p('Tests support computational consistency; they do not prove that external source data are complete, that a scenario will happen, or that every conceivable edge case is covered.')
p('Practice assertions provide quick checks. For durable runtime validation, the pipeline uses explicit ValueError checks in several helpers; Python assertions can be disabled with optimisation. Keep this distinction in mind when explaining production robustness.')
h('Reproducibility')
p('The pipeline records raw-file SHA-256 hashes and library/runtime versions in validation.json. Hashes help identify exactly which input bytes produced a run. A reproducible offline pipeline can be rerun without downloading changing web pages.')
page('13 | Forecasting: supplied, not yet studied')
p('This section documents code you executed through the pipeline. Do not describe forecasting as independently developed or mastered until you can explain and reproduce it.')
table(['Model','Idea'],[['daily_naive','Last month\'s daily rate × next month\'s days.'],['seasonal_daily_naive','Same month last year\'s daily rate × target month\'s days.'],['log_trend_12m','Fit a straight line to log daily volume over the last 12 months, then exponentiate and convert to monthly volume.']],[160,335])
p('The first 30 months form initial history; the next six are validation; the last 12 are test. Each one-step prediction uses only earlier months. The winning model is chosen by validation WAPE, then evaluated on the test period.')
p('<b>MAE:</b> mean absolute error in million payments. <b>WAPE:</b> total absolute error / total actual volume. These measure prediction error, not guaranteed future accuracy.')
p('Reproduced packaged results: selected model log_trend_12m; test WAPE about 1.12%; September 2026 forecast about 23.99 billion. This is a model output from the historical snapshot, not an observed September result.')
p('The +/-10% range is an assumed planning scenario, not a statistically calibrated prediction interval. The evaluation is retrospective using the current data vintage, and much of its older history is rounded.')
h('Why no random split?')
p('Random splitting can let later observations influence predictions for earlier periods. Time-ordered evaluation better represents the information available at a forecast date. Pipeline tests check temporal cutoffs, but source-vintage revisions remain a separate limitation.')
page('14 | Interview questions: fundamentals')
qas=[('Explain your project in one minute.','I reproduced and studied a Python payments-analysis workflow using 48 national months and aggregate merchant, bank and location snapshots. I standardised dates and units, calculated daily activity and average ticket, segmented merchants, prioritised selected banks by estimated declines and measured unclassified geography. I validated outputs and reconciled Python with SQL. The next phase is Power BI.'),('What was your contribution?','I ran and practised the guided Python programs, checked the outputs, studied the business calculations and completed the verification steps. The project includes supplied pipeline code. I distinguish what I reproduced from what I independently designed, and I can explain the sections I have studied.'),('Why use vectorisation?','A column expression applies the operation across the Series without a manual Python row loop. It is concise and well suited to pandas numeric operations. I used it for ticket size, shares and estimated declines.'),('Why .copy() after filtering?','It creates a separate DataFrame for subsequent changes and makes the intended independence of the filtered result clear.'),('What is the difference between groupby and a window calculation?','groupby aggregation collapses rows into group summaries. A window-like transform can return group totals alongside each original row. The pipeline uses transform for merchant share denominators.'),('Why keep missing growth values?','No previous observation means growth is unavailable, not zero. Replacing it with zero would invent evidence of no change.')]
for q,a in qas:h(q);p(a)
page('15 | Interview questions: business reasoning')
qas=[('Why multiply by 10 for average ticket?','Value is in crore rupees and count is in million payments. One crore equals ten million, so the scale factor is 10. The result is rupees per payment.'),('Why compare daily activity?','Month lengths differ. Dividing by the number of days separates part of the calendar effect from changes in daily processing activity.'),('Why a weighted bank rate?','The correct combined rate is estimated declines divided by attempts. A simple average gives the same weight to a bank handling 100 attempts and one handling a million.'),('Why not combine sending and receiving banks?','They describe different roles in payment processing. Adding them can count two sides of activity, and both selected samples are incomplete.'),('Did your project save 6.74 million payments?','No. It estimated a hypothetical reduction under a 0.5% benchmark and 50% reduction of the excess rate, with unchanged attempt volumes. Actual impact would need an intervention and evaluation.'),('What does 44.39% unclassified mean?','That share of the national count is in an explicit Unclassified location row. Geographical conclusions are incomplete; it does not mean those transactions failed.'),('What would you improve next?','Verify and expand official history, obtain complete repeated bank snapshots, preserve source vintages, standardise segmentation edge cases and collect operational evidence to investigate causes.')]
for q,a in qas:h(q);p(a)
page('16 | Revision checklist and source notes')
h('Be able to reproduce these without copying')
p('1. Convert billion payments to millions.<br/>2. Derive average ticket from value and count.<br/>3. Explain the first missing growth values.<br/>4. Build a median-based np.select segment.<br/>5. Name the merchant-share denominator.<br/>6. Compute a weighted decline rate.<br/>7. Explain why clip(lower=0) is needed.<br/>8. Validate a many-to-one merge.<br/>9. Distinguish estimated, hypothetical and observed results.<br/>10. Explain one failing test and why it matters.')
h('Common errors and fixes')
table(['Error','First check'],[['FileNotFoundError','Run practice lessons from the extracted project root; confirm paths.'],['KeyError','Inspect df.columns; practice and pipeline names can differ.'],['astype(float) fails','Inspect spaces, commas, percent signs and the Unicode minus.'],['Unexpected NaN','Check unrecognised units, censored rates and missing comparison periods.'],['Merge multiplies rows','Check uniqueness of the right-hand join key and use merge validation.'],['Chart uses wrong dates','Convert dates, sort chronologically and check period coverage.']],[165,330])
h('Evidence and provenance')
p('Original archive: UPI_Payments_Intelligence_Project.zip. Internal references: src/pipeline.py, src/build_learning_assets.py, tests/test_pipeline.py, notebooks/01_guided_analysis.ipynb, data/sources.csv, raw/processed CSVs and reports/summary.json. Lesson explanations also use the visible conversation.')
p('The package lists NPCI product statistics (S1), India Dispatch UPI transactions (S2) and India Dispatch payments (S3), accessed 22 September 2026. This guide reproduces the stored data; it does not constitute a fresh audit of those publishers. Source URLs are recorded in data/sources.csv.')

# Append actual source, no invented replacements.
for title,file in [('Appendix A | Complete recovered pipeline','src/pipeline.py'),('Appendix B | The nine actual tests','tests/test_pipeline.py'),('Appendix C | Learning-assets generator','src/build_learning_assets.py')]:
 page(title);p('Source: '+file+' | Original program recovered from the archive. Line wrapping is for PDF readability.')
 # flowable chunks avoid oversized blocks and retain readable source
 lines=(R/file).read_text(encoding='utf-8').splitlines()
 for start in range(0,len(lines),32):
  code('\n'.join(lines[start:start+32]))
page('Appendix D | Executed notebook programs')
p('Source: notebooks/01_guided_analysis.ipynb. All nine code cells are reproduced below in execution order. The setup cell must run first; several later cells require pipeline outputs on disk.')
nb=json.loads((R/'notebooks/01_guided_analysis.ipynb').read_text(encoding='utf-8'));i=0
for c in nb['cells']:
 if c['cell_type']=='code':
  i+=1;h('Code cell '+str(i));code(''.join(c['source']))
def footer(canvas,doc):
 canvas.setStrokeColor(colors.HexColor('#D9E3EC'));canvas.line(42,39,553,39)
 canvas.setFont('DV',8);canvas.setFillColor(colors.HexColor('#52647A'))
 canvas.drawString(42,26,'UPI Python | Interview preparation | Dhananjay Gupta')
 canvas.drawRightString(553,26,str(doc.page))
path=str(R/'docs/UPI_Python_Interview_Preparation_Guide.pdf')
doc=SimpleDocTemplate(path,pagesize=(595.28,841.89),rightMargin=45,leftMargin=45,topMargin=44,bottomMargin=52,title='UPI Python Interview Preparation Guide',author='Prepared for Dhananjay Gupta')
doc.build(flow,onFirstPage=footer,onLaterPages=footer)
print(path)
