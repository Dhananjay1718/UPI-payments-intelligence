"""Rebuild clean data, a SQL warehouse, forecasts and figures from real snapshots.

Run from any directory: python /path/to/project/src/pipeline.py
No network, account, database server or API key is needed for an offline run.
"""
from pathlib import Path
import hashlib
import json
import re
import sqlite3
import sys
import platform

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

ROOT = Path(__file__).resolve().parents[1]
RAW, CLEAN, REPORTS = ROOT/'data/raw', ROOT/'data/processed', ROOT/'reports'
CONFIG = json.loads((ROOT/'config.json').read_text(encoding='utf-8'))

def compact_number(value):
    """Parse the first number with its published unit; ignore secondary USD text."""
    match = re.search(r'([0-9][0-9,.]*)\s*(million|billion|trillion)', str(value))
    if not match: raise ValueError(f'Cannot parse a compact number: {value}')
    number = float(match.group(1).replace(',',''))
    return number * {'million':1e6,'billion':1e9,'trillion':1e12}[match.group(2)]

def rate(value):
    text = str(value).strip().replace('−','-').replace(',','')
    if text == 'Not comparable': return np.nan
    if text.startswith('<'): return np.nan  # preserve censoring, never make up a point value
    if not text.endswith('%'): raise ValueError(f'Not a reported percentage: {value}')
    return float(text[:-1])/100

def validate_unique(frame, columns):
    if frame[columns].isna().any().any() or frame.duplicated(columns).any():
        raise ValueError(f'Missing or duplicated key: {columns}')

def validate_rate(values, name):
    if values.isna().any() or not values.between(0,1).all():
        raise ValueError(f'{name} must be a decimal fraction between 0 and 1.')

def clean_data():
    m = pd.read_csv(RAW/'monthly_reported.csv')
    m['month'] = pd.to_datetime(m.month_label,format='%B %Y')
    m['volume_mn'] = m.volume_reported.map(compact_number)/1e6
    m['value_cr'] = m.value_reported.map(compact_number)/1e7
    m['precision'] = 'secondary_rounded'
    m['banks_live'] = np.nan
    m = m[['month','volume_mn','value_cr','banks_live','source_id','precision']].sort_values('month').reset_index(drop=True)
    official = pd.read_csv(RAW/'official_monthly_overrides.csv',parse_dates=['month'])
    validate_unique(official,['month'])
    for r in official.itertuples():
        mask=m.month.eq(r.month)
        if mask.sum()!=1: raise ValueError('Official override month absent from reported history.')
        original=m.loc[mask].iloc[0]
        # Published two-decimal billion / trillion display has rounding tolerance.
        if abs(original.volume_mn-r.volume_mn)>5.01 or abs(original.value_cr-r.value_cr)>500.01:
            raise ValueError(f'Source conflict at {r.month.date()}; review rather than silently overwrite.')
        m.loc[mask,['volume_mn','value_cr','banks_live','source_id','precision']] = [r.volume_mn,r.value_cr,r.banks_live,r.source_id,'primary_verified']
    validate_unique(m,['month'])
    expected=pd.date_range(m.month.min(),m.month.max(),freq='MS')
    if not m.month.equals(pd.Series(expected,name='month')): raise ValueError('Monthly series is not contiguous.')
    if (m[['volume_mn','value_cr']]<=0).any().any(): raise ValueError('Nonpositive monthly totals.')
    m['days_in_month']=m.month.dt.days_in_month
    m['daily_volume_mn']=m.volume_mn/m.days_in_month
    m['avg_ticket_inr']=10*m.value_cr/m.volume_mn
    m['mom_volume']=m.volume_mn.pct_change(fill_method=None)
    m['mom_daily_volume']=m.daily_volume_mn.pct_change(fill_method=None)
    m['yoy_volume']=m.volume_mn.pct_change(12,fill_method=None)
    m['rolling_3m_volume_mn']=m.volume_mn.rolling(3,min_periods=3).mean()

    raw=pd.read_csv(RAW/'merchants_reported.csv')
    d=raw.merchant_reported.str.extract(r'^(.*)MCC (\d{4})$')
    merchants=pd.DataFrame({'month':pd.to_datetime(raw.month),'mcc':d[1],'merchant':d[0],
        'volume_mn':raw.volume_reported.map(compact_number)/1e6,
        'value_cr':raw.value_reported.map(compact_number)/1e7,
        'mom_volume':raw.mom_reported.map(rate),'six_month_volume':raw.six_month_reported.map(rate),
        'yoy_volume':raw.yoy_reported.map(rate),'source_id':raw.source_id})
    validate_unique(merchants,['month','mcc'])
    merchants['avg_ticket_inr']=10*merchants.value_cr/merchants.volume_mn
    # The denominator is ONLY the categories in this dataset, not all P2M.
    merchants['observed_volume_share']=merchants.volume_mn/merchants.groupby('month').volume_mn.transform('sum')
    median=merchants.groupby('month').volume_mn.transform('median')
    merchants['segment']=np.select([
        (merchants.volume_mn>=median)&(merchants.mom_volume>=0),
        (merchants.volume_mn>=median)&(merchants.mom_volume<0),
        (merchants.volume_mn<median)&(merchants.mom_volume>=0)],
        ['Larger and growing','Larger and contracting','Smaller and growing'],default='Smaller and contracting')

    raw=pd.read_csv(RAW/'banks_reported.csv')
    banks=pd.DataFrame({'month':pd.to_datetime(raw.month),'role':raw.role,'bank':raw.bank,
        'volume_mn':raw.volume_reported.map(compact_number)/1e6,'td_rate':raw.td_reported.map(rate),'source_id':raw.source_id})
    banks['bank_id']=banks.bank.str.lower().str.replace(r'[^a-z0-9]+','_',regex=True).str.strip('_')
    validate_unique(banks,['month','role','bank_id']);validate_rate(banks.td_rate,'Technical decline rate')
    banks['estimated_td_mn']=banks.volume_mn*banks.td_rate
    banks['target_td_rate']=CONFIG['scenario_td_target']
    banks['effectiveness']=CONFIG['scenario_effectiveness']
    banks['scenario_avoided_mn']=banks.volume_mn*(banks.td_rate-banks.target_td_rate).clip(lower=0)*banks.effectiveness

    raw=pd.read_csv(RAW/'states_reported.csv')
    states=pd.DataFrame({'month':pd.to_datetime(raw.month),'state':raw.state,
        'volume_mn':raw.volume_reported.map(compact_number)/1e6,
        'value_cr':raw.value_reported.map(compact_number)/1e7,
        'reported_volume_share':raw.volume_share_reported.map(rate),
        'reported_volume_share_label':raw.volume_share_reported,'source_id':raw.source_id})
    validate_unique(states,['month','state'])
    states=states.merge(m[['month','volume_mn']].rename(columns={'volume_mn':'national_volume_mn'}),on='month',validate='many_to_one')
    states['national_volume_share']=states.volume_mn/states.national_volume_mn
    for frame in (merchants,banks,states):
        if not frame.month.isin(m.month).all(): raise ValueError('Fact month missing from monthly dimension.')
        if (frame.volume_mn<=0).any(): raise ValueError('Nonpositive fact volume.')
    return m,merchants,banks,states

def predict_one(history, target_month, model):
    """Only past observations enter any prediction; target month must follow history."""
    h=history.sort_values('month').reset_index(drop=True)
    target=pd.Timestamp(target_month)
    if target!=h.month.iloc[-1]+pd.offsets.MonthBegin(1): raise ValueError('Expected next contiguous month.')
    days=target.days_in_month
    if model=='daily_naive': return float(h.daily_volume_mn.iloc[-1]*days)
    if model=='seasonal_daily_naive':
        row=h[h.month.eq(target-pd.DateOffset(years=1))]
        if len(row)!=1: raise ValueError('Seasonal baseline needs last year.')
        return float(row.daily_volume_mn.iloc[0]*days)
    if model=='log_trend_12m':
        y=np.log(h.daily_volume_mn.tail(CONFIG['trend_lookback_months']).to_numpy())
        x=np.arange(len(y),dtype=float)
        slope,intercept=np.linalg.lstsq(np.column_stack([x,np.ones(len(x))]),y,rcond=None)[0]
        return float(np.exp(intercept+slope*len(y))*days)
    raise ValueError(f'Unknown model: {model}')

def forecasting(m):
    if len(m)<CONFIG['minimum_months_for_forecasting']:raise ValueError('Insufficient forecasting history.')
    ntest,nval=CONFIG['forecast_test_months'],CONFIG['forecast_validation_months']
    val_start,test_start=len(m)-ntest-nval,len(m)-ntest
    records=[]
    for model in ['daily_naive','seasonal_daily_naive','log_trend_12m']:
        for i in range(val_start,len(m)):
            pred=predict_one(m.iloc[:i],m.month.iloc[i],model)
            records.append({'month':m.month.iloc[i],'model':model,'split':'validation' if i<test_start else 'test',
                'actual_mn':float(m.volume_mn.iloc[i]),'predicted_mn':pred,'train_last_month':m.month.iloc[i-1]})
    pred=pd.DataFrame(records)
    pred['absolute_error_mn']=(pred.predicted_mn-pred.actual_mn).abs()
    metrics=pred.groupby(['split','model'],as_index=False).agg(mae_mn=('absolute_error_mn','mean'),absolute_error_total=('absolute_error_mn','sum'),actual_total=('actual_mn','sum'),months=('month','count'))
    metrics['wape']=metrics.absolute_error_total/metrics.actual_total
    selected=metrics[metrics.split.eq('validation')].sort_values(['wape','model']).iloc[0]['model']
    target=m.month.iloc[-1]+pd.offsets.MonthBegin(1)
    estimate=predict_one(m,target,selected)
    next_month=pd.DataFrame([{'month':target,'model':selected,'forecast_mn':estimate,
        'assumed_minus_10pct_mn':estimate*.9,'assumed_plus_10pct_mn':estimate*1.1,
        'range_type':'Assumed +/-10% planning scenarios; not a prediction interval'}])
    return pred,metrics,next_month

def serial_frame(df):
    result=df.copy()
    for col in result.select_dtypes(include=['datetime64[ns]']).columns:result[col]=result[col].dt.strftime('%Y-%m-%d')
    return result

def warehouse(m,merchants,banks,states,metrics):
    frames={
        'sources':pd.read_csv(ROOT/'data/sources.csv'),
        'dim_month':pd.DataFrame({'month':m.month,'year':m.month.dt.year,'month_number':m.month.dt.month,'days_in_month':m.days_in_month}),
        'dim_merchant':merchants[['mcc','merchant']].drop_duplicates(),
        'dim_bank':banks[['bank_id','bank']].drop_duplicates(),
        'fact_monthly':m.drop(columns=['days_in_month']),
        'fact_merchant':merchants.drop(columns=['merchant']),
        'fact_bank':banks.drop(columns=['bank']),
        'fact_state':states,
        'forecast_metrics':metrics,
    }
    db=ROOT/'data/upi_intelligence.sqlite'
    with sqlite3.connect(db) as con:
        con.execute('PRAGMA foreign_keys=ON')
        # Recreate the disposable analytical database; source CSVs are immutable here.
        for name in ['fact_merchant','fact_bank','fact_state','fact_monthly','forecast_metrics','dim_merchant','dim_bank','dim_month','sources']:
            con.execute(f'DROP TABLE IF EXISTS {name}')
        con.executescript((ROOT/'sql/schema_sqlite.sql').read_text(encoding='utf-8'))
        for name,frame in frames.items():serial_frame(frame).to_sql(name,con,index=False,if_exists='append')
        if con.execute('PRAGMA foreign_key_check').fetchall():raise ValueError('Foreign key validation failed.')
        result_dir=REPORTS/'sql_results';result_dir.mkdir(exist_ok=True)
        text=(ROOT/'sql/analysis_queries.sql').read_text(encoding='utf-8')
        for chunk in re.split(r'(?m)^-- QUERY: ',text)[1:]:
            title,sql=chunk.split('\n',1)
            pd.read_sql_query(sql,con).to_csv(result_dir/(title.strip()+'.csv'),index=False)
        sql_latest=pd.read_sql_query('SELECT 10.0*value_cr/volume_mn AS ticket FROM fact_monthly ORDER BY month DESC LIMIT 1',con).ticket.iloc[0]
        if not np.isclose(sql_latest,m.avg_ticket_inr.iloc[-1],rtol=1e-12):raise ValueError('SQL/Python ticket reconciliation failed.')
    return frames

def figures(m,merchants,banks,states,pred,next_month,summary):
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.titleweight':'bold'})
    navy,blue,orange='#142B45','#2A70B8','#D97736'
    fig=plt.figure(figsize=(16,10),facecolor='#F7F9FC')
    fig.text(.055,.94,'UPI PAYMENTS INTELLIGENCE',fontsize=23,weight='bold',color=navy)
    fig.text(.055,.902,'August 2026 snapshot  |  National growth, merchant mix and operational review',fontsize=12,color='#52647A')
    cards=[('Monthly transactions',f"{summary['latest_volume_bn']:.2f} billion"),('Volume growth YoY',f"{summary['latest_yoy']:.1%}"),('Average transfer value',f"INR {summary['latest_ticket_inr']:,.0f}"),('Unclassified state share',f"{summary['unclassified_share']:.1%}")]
    for i,(label,val) in enumerate(cards):
        x=.055+i*.235;fig.text(x,.837,val,fontsize=23,weight='bold',color=blue);fig.text(x,.802,label,fontsize=10,color='#52647A')
    gs=fig.add_gridspec(2,2,left=.095,right=.95,top=.73,bottom=.12,hspace=.52,wspace=.37)
    ax=fig.add_subplot(gs[0,0]);ax.plot(m.month,m.volume_mn/1000,color=blue,lw=2.5)
    ax.set_title('National volume (billion transactions)',loc='left',pad=12);ax.grid(axis='y',alpha=.15)
    ax.xaxis.set_major_locator(mdates.YearLocator());ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax=fig.add_subplot(gs[0,1]);top=merchants.nlargest(6,'volume_mn').iloc[::-1]
    names={'Groceries & supermarkets':'Groceries','Eating places & restaurants':'Restaurants','Fast food restaurants':'Fast food','Telecommunication services':'Telecom','Service stations':'Service stations','Bakeries':'Bakeries'}
    ax.barh([names.get(x,x) for x in top.merchant],top.volume_mn/1000,color=blue);ax.set_title('Largest observed merchant categories',loc='left',pad=12);ax.set_xlabel('Billion transactions; rounded source figures');ax.grid(axis='x',alpha=.15)
    ax=fig.add_subplot(gs[1,0]);sample=banks[banks.role.eq('Sending')].nlargest(6,'estimated_td_mn').iloc[::-1]
    labels=[x.replace(' Limited','').replace('Maharashtra Gramin Bank','Maharashtra G.').replace('Rajasthan Marudhara Gramin Bank','Rajasthan M.').replace('Central Bank of India','Central Bank').replace('Punjab and Sind Bank','Punjab & Sind').replace('NSDL Payments Bank','NSDL Payments').replace('Baroda U.P. Bank','Baroda U.P.') for x in sample.bank]
    ax.barh(labels,sample.estimated_td_mn,color=orange);ax.set_title('Estimated TD: six displayed sending banks',loc='left',pad=12);ax.set_xlabel('Million attempts; sample only, not national failures');ax.grid(axis='x',alpha=.15)
    ax=fig.add_subplot(gs[1,1]);bt=pred[(pred.model.eq(summary['selected_model']))&pred.split.eq('test')]
    ax.plot(bt.month,bt.actual_mn/1000,label='Actual',color=navy,lw=2)
    ax.plot(bt.month,bt.predicted_mn/1000,label='1-month ahead',color=orange,lw=2,linestyle='--')
    ax.set_title(f"Forecast holdout WAPE: {summary['test_wape']:.1%}",loc='left',pad=12);ax.set_ylabel('Billion transactions');ax.legend(frameon=False,fontsize=9);ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3));ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %y'));ax.grid(axis='y',alpha=.15)
    fig.text(.055,.04,'Sources: NPCI (latest 5 national months); India Dispatch Research citing NPCI (rounded history and ecosystem tables).\nPayment value is money transferred. Bank decline counts are estimates. Forecast and improvement scenarios are unverified planning outputs.',fontsize=9,color='#52647A')
    fig.savefig(REPORTS/'dashboard.png',dpi=150);plt.close(fig)

def main():
    CLEAN.mkdir(parents=True,exist_ok=True);REPORTS.mkdir(exist_ok=True)
    m,merchants,banks,states=clean_data()
    pred,metrics,next_month=forecasting(m)
    for name,frame in {'monthly':m,'merchants':merchants,'banks':banks,'states':states,'forecast_backtest':pred,'forecast_metrics':metrics,'forecast_next_month':next_month}.items():
        serial_frame(frame).to_csv(CLEAN/f'{name}.csv',index=False,float_format='%.10g')
    frames=warehouse(m,merchants,banks,states,metrics)
    # BI import files retain fact/dimension grain and all numeric precision labels.
    for name,frame in frames.items():serial_frame(frame).to_csv(CLEAN/f'{name}.csv',index=False,float_format='%.10g')
    model=next_month.model.iloc[0]
    summary={
        'as_of':CONFIG['as_of'],'latest_month':str(m.month.iloc[-1].date()),'history_months':len(m),
        'latest_volume_bn':float(m.volume_mn.iloc[-1]/1000),'latest_value_lakh_cr':float(m.value_cr.iloc[-1]/100000),
        'latest_mom':float(m.mom_volume.iloc[-1]),'latest_yoy':float(m.yoy_volume.iloc[-1]),
        'latest_ticket_inr':float(m.avg_ticket_inr.iloc[-1]),'daily_volume_mn':float(m.daily_volume_mn.iloc[-1]),
        'unclassified_share':float(states.loc[states.state.eq('Unclassified'),'national_volume_share'].iloc[0]),
        'selected_model':model,'test_wape':float(metrics[(metrics.model.eq(model))&metrics.split.eq('test')].wape.iloc[0]),
        'forecast_next_month':str(next_month.month.iloc[0].date()),'forecast_bn':float(next_month.forecast_mn.iloc[0]/1000),
        'observed_merchant_count':len(merchants),'bank_rows':len(banks),'state_rows':len(states),
        'sending_scenario_avoided_mn':float(banks[banks.role.eq('Sending')].scenario_avoided_mn.sum()),
        'top_sending_bank_estimated_declines':banks[banks.role.eq('Sending')].sort_values('estimated_td_mn',ascending=False).iloc[0]['bank'],
    }
    (REPORTS/'summary.json').write_text(json.dumps(summary,indent=2), encoding='utf-8')
    figures(m,merchants,banks,states,pred,next_month,summary)
    checks={
        'status':'passed','checks':['unique fact keys','contiguous monthly history','positive volumes','rate bounds','official-versus-rounded reconciliation','foreign keys','SQL-versus-Python average ticket'],
        'observations':{k:len(v) for k,v in [('monthly',m),('merchants',merchants),('banks',banks),('states',states)]},
        'known_limits':['43 historical monthly rows are rounded secondary data','bank sample: six displayed banks per role; not all banks','29 merchant categories do not cover all P2M','forecast holdout has 12 observations'],
        'raw_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(RAW.glob('*.csv'))},
        'runtime':{'python':platform.python_version(),'pandas':pd.__version__,'numpy':np.__version__,'matplotlib':matplotlib.__version__},
    }
    (REPORTS/'validation.json').write_text(json.dumps(checks,indent=2), encoding='utf-8')
    payload={'summary':summary,'config':CONFIG,'tables':{name:json.loads(serial_frame(df).to_json(orient='records')) for name,df in [('monthly',m),('merchants',merchants),('banks',banks),('states',states)]}}
    (REPORTS/'workbook_data.json').write_text(json.dumps(payload,indent=2), encoding='utf-8')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
