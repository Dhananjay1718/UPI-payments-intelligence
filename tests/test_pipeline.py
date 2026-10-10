"""Business-risk checks: units, grain, missing values, leakage and SQL consistency."""
import sys
import unittest
from pathlib import Path
import sqlite3
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import pipeline as p

class TestPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.m,cls.merchants,cls.banks,cls.states=p.clean_data()

    def test_indian_units_and_secondary_currency(self):
        self.assertEqual(p.compact_number('₹29.82 trillion · $311 billion'),29.82e12)
        self.assertAlmostEqual(10*2982355.95/24508.96,1216.8431259425124)

    def test_duplicate_keys_are_rejected(self):
        with self.assertRaises(ValueError):p.validate_unique(pd.DataFrame({'id':[1,1]}),['id'])

    def test_impossible_rates_are_rejected(self):
        with self.assertRaises(ValueError):p.validate_rate(pd.Series([.02,2.44]),'TD')

    def test_missing_and_censored_are_not_zero(self):
        self.assertTrue(np.isnan(p.rate('Not comparable')))
        self.assertTrue(np.isnan(p.rate('<0.01%')))
        self.assertEqual(p.rate('0%'),0)
        self.assertEqual(p.rate('−2.4%'),-.024)

    def test_known_official_control(self):
        r=self.m.iloc[-1]
        self.assertEqual(r.month,pd.Timestamp('2026-08-01'))
        self.assertEqual(r.volume_mn,24508.96)
        self.assertEqual(self.m.precision.eq('primary_verified').sum(),5)

    def test_forecast_does_not_use_future(self):
        first=p.predict_one(self.m.iloc[:36],self.m.month.iloc[36],'log_trend_12m')
        altered=self.m.copy();altered.loc[36:,'daily_volume_mn']=1e9
        second=p.predict_one(altered.iloc[:36],altered.month.iloc[36],'log_trend_12m')
        self.assertEqual(first,second)
        with self.assertRaises(ValueError):p.predict_one(self.m,self.m.month.iloc[-1],'daily_naive')

    def test_selection_is_validation_only(self):
        pred,metrics,nxt=p.forecasting(self.m)
        best=metrics[metrics.split.eq('validation')].sort_values(['wape','model']).iloc[0].model
        self.assertEqual(nxt.model.iloc[0],best)
        self.assertTrue((pred.train_last_month<pred.month).all())
        self.assertEqual(len(pred[pred.split.eq('test') & pred.model.eq(best)]),12)

    def test_sql_weighted_rates_and_grain(self):
        with sqlite3.connect(ROOT/'data/upi_intelligence.sqlite') as con:
            got=pd.read_sql_query('SELECT role,SUM(volume_mn*td_rate)/SUM(volume_mn) AS rate FROM fact_bank GROUP BY role',con).set_index('role')['rate']
            for role,g in self.banks.groupby('role'):
                self.assertAlmostEqual(got[role],np.average(g.td_rate,weights=g.volume_mn))
            self.assertEqual(con.execute('PRAGMA foreign_key_check').fetchall(),[])

    def test_scenario_cannot_exceed_estimated_declines(self):
        self.assertTrue((self.banks.scenario_avoided_mn>=0).all())
        self.assertTrue((self.banks.scenario_avoided_mn<=self.banks.estimated_td_mn).all())

if __name__=='__main__':unittest.main(verbosity=2)
