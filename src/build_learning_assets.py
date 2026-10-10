"""Create the executed teaching notebook and a MySQL import from the validated DB."""
from pathlib import Path
import contextlib
import io
import json
import sqlite3
import base64
import os

ROOT=Path(__file__).resolve().parents[1]

def mysql_export():
    # Tested source is SQLite. This export targets MySQL 8; no MySQL server is used here.
    keys={'sources':['source_id'],'dim_month':['month'],'dim_merchant':['mcc'],'dim_bank':['bank_id'],
          'fact_monthly':['month'],'fact_merchant':['month','mcc'],'fact_bank':['month','role','bank_id'],
          'fact_state':['month','state'],'forecast_metrics':['split','model']}
    def quote(v):
        if v is None:return 'NULL'
        if isinstance(v,(int,float)):return repr(v)
        return "'"+str(v).replace('\\','\\\\').replace("'","''")+"'"
    parts=['-- Generated from the validated SQLite snapshot. MySQL 8 import; not server-tested.',
      '-- Dedicated database. Existing same-key rows are refreshed; unrelated rows are retained.',
      'CREATE DATABASE IF NOT EXISTS upi_portfolio CHARACTER SET utf8mb4;','USE upi_portfolio;']
    with sqlite3.connect(ROOT/'data/upi_intelligence.sqlite') as con:
        for table,pk in keys.items():
            info=con.execute(f'PRAGMA table_info({table})').fetchall()
            fields=[]
            for _,name,typ,*_ in info:
                t='DOUBLE' if typ=='REAL' else 'INT' if typ=='INTEGER' else 'VARCHAR(1024)' if name in ('url','precision_note','coverage') else 'VARCHAR(255)'
                if name=='month':t='DATE'
                fields.append(f'  `{name}` {t}'+(' NOT NULL' if name in pk else ''))
            fields.append('  PRIMARY KEY ('+','.join('`'+k+'`' for k in pk)+')')
            parts.append('CREATE TABLE IF NOT EXISTS `'+table+'` (\n'+',\n'.join(fields)+'\n);')
            cols=[r[1] for r in info];rows=con.execute(f'SELECT * FROM {table}').fetchall()
            assignments=','.join(f'`{c}`=VALUES(`{c}`)' for c in cols if c not in pk)
            parts.append('INSERT INTO `'+table+'` ('+','.join('`'+c+'`' for c in cols)+') VALUES\n'+',\n'.join('('+','.join(quote(v) for v in row)+')' for row in rows)+'\nON DUPLICATE KEY UPDATE '+assignments+';')
    (ROOT/'sql/mysql_import.sql').write_text('\n\n'.join(parts),encoding='utf-8')

def notebook():
    cells=[]
    def md(text):cells.append({'cell_type':'markdown','metadata':{},'source':text.splitlines(True)})
    def code(text):cells.append({'cell_type':'code','metadata':{},'source':text.splitlines(True),'execution_count':None,'outputs':[]})
    md('# UPI Payments Intelligence\nA guided notebook for Dhananjay. Run from top to bottom. The included outputs were executed against the packaged CSV snapshot. Source dates and limitations are part of the analysis.\n\n**Decision:** Where should a payments operations team investigate capacity, merchant activity and technical declines?\n\n**Grain:** one national month, one merchant category-month, one bank-role-month, one state-month. There are no individual customer transactions.')
    code("from pathlib import Path\nimport sys\nimport pandas as pd\nimport numpy as np\nimport sqlite3\nROOT = Path.cwd()\nif ROOT.name == 'notebooks': ROOT = ROOT.parent\nif not (ROOT / 'src' / 'pipeline.py').exists():\n    raise FileNotFoundError('Open this notebook inside the extracted project folder.')\nsys.path.insert(0, str(ROOT / 'src'))\nimport pipeline\nprint('Project:', ROOT.name)\n")
    md('## 1. Read and validate\n`read_csv` brings the snapshots into DataFrames. Cleaning standardizes dates and units. Validation checks uniqueness before joins, so a repeated key cannot silently multiply totals. Five recent national months override rounded values with official NPCI figures.')
    code("monthly, merchants, banks, states = pipeline.clean_data()\nprint('Shapes:', {k: v.shape for k,v in [('monthly',monthly),('merchants',merchants),('banks',banks),('states',states)]})\nprint(monthly.tail(5).to_string(index=False))\n")
    md('## 2. Understand NumPy and vectorization\nA crore is 10 million. Therefore average ticket in INR is `10 * value_cr / volume_mn`. Vectorized operations calculate a whole column. `np.select` assigns merchant segments using median observed volume and whether reported growth is negative. These segments are analyst rules, not source classifications.')
    code("manual_ticket = 10 * monthly.iloc[-1]['value_cr'] / monthly.iloc[-1]['volume_mn']\nprint('Latest average ticket:', round(manual_ticket, 2))\nprint(merchants.groupby('segment').agg(categories=('mcc','count'), volume_mn=('volume_mn','sum')).to_string())\n")
    md('## 3. Ask better growth questions\n`pct_change()` calculates month-over-month change. A 30-day month has fewer processing days than a 31-day month, so compare the daily run rate too. `pct_change(12)` requires a complete monthly index. Missing first-year comparisons remain missing.')
    code("print(monthly[['month','volume_mn','mom_volume','mom_daily_volume','yoy_volume']].tail(8).to_string(index=False))\n")
    md('## 4. Rank operational review by affected volume\nTechnical decline is a failure associated with system/network issues. Estimated declines = attempts × TD rate. Use a weighted rate for a selected sample. The two displayed bank samples are selected and incomplete: neither is a national estimate, and sending plus receiving must not be added.')
    code("sending = banks[banks['role'].eq('Sending')].copy()\nsending = sending.sort_values('estimated_td_mn', ascending=False)\nprint(sending[['bank','volume_mn','td_rate','estimated_td_mn','scenario_avoided_mn']].to_string(index=False))\nprint('Weighted sample TD:', np.average(sending['td_rate'], weights=sending['volume_mn']))\n")
    md('## 5. Join with SQL\nThe pipeline writes a local SQLite database automatically. A bank dimension holds its name once; fact rows contain its key and measures. MySQL users can import `sql/mysql_import.sql` into the dedicated `upi_portfolio` database and run the same analysis queries.')
    code("with sqlite3.connect(ROOT / 'data' / 'upi_intelligence.sqlite') as con:\n    q = '''SELECT b.bank, f.role, f.volume_mn*f.td_rate AS estimated_td_mn\n           FROM fact_bank f JOIN dim_bank b ON f.bank_id=b.bank_id\n           WHERE f.role='Sending' ORDER BY estimated_td_mn DESC'''\n    result = pd.read_sql_query(q, con)\nprint(result.to_string(index=False))\n")
    md('## 6. Treat missing geography as a finding\nCompare each state row to the same month’s national total. Preserve Unclassified. Rounded rows may not add perfectly to the official total; a residual is not proof that the network lost transactions.')
    code("print(states[states['state'].isin(['Uttar Pradesh','Unclassified'])][['state','volume_mn','national_volume_share']].to_string(index=False))\nprint('Rounding residual, million:', round(states['volume_mn'].sum()-monthly.iloc[-1]['volume_mn'], 3))\n")
    md('## 7. Forecast without using future observations\nThree candidates: last-month daily rate, last-year daily rate, and a 12-month log-linear trend. The first 30 months form the initial history; the next six select the model; the final 12 evaluate it. Each prediction refits using earlier months only. WAPE = total absolute error / total actual volume. The ±10% next-month range is an assumption, not a confidence interval. This is a retrospective exercise using the current data vintage.')
    code("predictions, metrics, next_month = pipeline.forecasting(monthly)\nprint(metrics[['split','model','months','mae_mn','wape']].to_string(index=False))\nprint(next_month.to_string(index=False))\n")
    md('## 8. Turn findings into actions\nWrite an observation, implication, recommended investigation and evidence needed. Example: high estimated bank declines justify investigation of that bank’s error logs. Aggregate data cannot reveal the root cause or prove recoverable revenue.\n\n**Exercises:** (1) Reproduce the latest ticket without copying the answer. (2) Explain why a simple average TD is wrong. (3) Change the hypothetical target to 1% and rerun. (4) Rebuild SQL Q07 yourself. (5) Explain why merchant totals cannot be called total UPI. (6) Make a baseline forecast manually before reading the trend code.')
    code("from matplotlib import pyplot as plt\nimg = plt.imread(ROOT / 'reports' / 'dashboard.png')\nplt.figure(figsize=(16,10))\nplt.imshow(img)\nplt.axis('off')\nplt.tight_layout()\nplt.show()\n")
    # Execute code cells with standard Python. Capture real text/figure outputs.
    namespace={};count=0
    import matplotlib.pyplot as plt
    previous_cwd=Path.cwd();os.chdir(ROOT)
    try:
        for cell in cells:
            if cell['cell_type']!='code':continue
            count+=1;out=io.StringIO();images=[]
            def show(*args,**kwargs):
                buf=io.BytesIO();plt.gcf().savefig(buf,format='png',dpi=90,bbox_inches='tight');images.append(base64.b64encode(buf.getvalue()).decode());plt.close('all')
            old_show=plt.show;plt.show=show
            try:
                with contextlib.redirect_stdout(out):exec(''.join(cell['source']),namespace)
            finally:plt.show=old_show
            cell['execution_count']=count
            if out.getvalue():cell['outputs'].append({'output_type':'stream','name':'stdout','text':out.getvalue().splitlines(True)})
            for im in images:cell['outputs'].append({'output_type':'display_data','metadata':{},'data':{'image/png':im,'text/plain':['<executed matplotlib figure>']}})
    finally:os.chdir(previous_cwd)
    nb={'cells':cells,'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python','version':'3'}},'nbformat':4,'nbformat_minor':4}
    (ROOT/'notebooks/01_guided_analysis.ipynb').write_text(json.dumps(nb,indent=1),encoding='utf-8')
    print(f'Executed {count} notebook code cells; exported MySQL import.')

if __name__=='__main__':mysql_export();notebook()
