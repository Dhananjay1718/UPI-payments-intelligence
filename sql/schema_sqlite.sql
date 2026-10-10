-- A fact row is an aggregate observation, never an individual payment.
CREATE TABLE dim_month(month TEXT PRIMARY KEY, year INTEGER, month_number INTEGER, days_in_month INTEGER);
CREATE TABLE dim_merchant(mcc TEXT PRIMARY KEY, merchant TEXT NOT NULL);
CREATE TABLE dim_bank(bank_id TEXT PRIMARY KEY, bank TEXT NOT NULL);
CREATE TABLE sources(source_id TEXT PRIMARY KEY,publisher TEXT,url TEXT,accessed_on TEXT,coverage TEXT,source_type TEXT,precision_note TEXT);
CREATE TABLE fact_monthly(month TEXT PRIMARY KEY REFERENCES dim_month(month),volume_mn REAL NOT NULL CHECK(volume_mn>0),value_cr REAL NOT NULL,banks_live REAL,source_id TEXT REFERENCES sources(source_id),precision TEXT,daily_volume_mn REAL,avg_ticket_inr REAL,mom_volume REAL,mom_daily_volume REAL,yoy_volume REAL,rolling_3m_volume_mn REAL);
CREATE TABLE fact_merchant(month TEXT REFERENCES dim_month(month),mcc TEXT REFERENCES dim_merchant(mcc),volume_mn REAL,value_cr REAL,mom_volume REAL,six_month_volume REAL,yoy_volume REAL,source_id TEXT REFERENCES sources(source_id),avg_ticket_inr REAL,observed_volume_share REAL,segment TEXT,PRIMARY KEY(month,mcc));
CREATE TABLE fact_bank(month TEXT REFERENCES dim_month(month),role TEXT,volume_mn REAL,td_rate REAL CHECK(td_rate BETWEEN 0 AND 1),source_id TEXT REFERENCES sources(source_id),bank_id TEXT REFERENCES dim_bank(bank_id),estimated_td_mn REAL,target_td_rate REAL,effectiveness REAL,scenario_avoided_mn REAL,PRIMARY KEY(month,role,bank_id));
CREATE TABLE fact_state(month TEXT REFERENCES dim_month(month),state TEXT,volume_mn REAL,value_cr REAL,reported_volume_share REAL,reported_volume_share_label TEXT,source_id TEXT REFERENCES sources(source_id),national_volume_mn REAL,national_volume_share REAL,PRIMARY KEY(month,state));
CREATE TABLE forecast_metrics(split TEXT,model TEXT,mae_mn REAL,absolute_error_total REAL,actual_total REAL,months INTEGER,wape REAL,PRIMARY KEY(split,model));
CREATE INDEX idx_bank_month_role ON fact_bank(month,role);
CREATE INDEX idx_merchant_month ON fact_merchant(month);
