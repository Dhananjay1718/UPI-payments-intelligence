"""Extract published TABLE DATA only. No synthetic transaction records.

Offline project runs use the committed CSV snapshots. An optional refresh reads
the two public pages and fails if their structure or observation date changes.
Review refreshed data and official overrides before accepting a new release.
"""
from html.parser import HTMLParser
from pathlib import Path
import argparse
import csv
import datetime
import hashlib
import json
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
URLS = {
    'ecosystem': 'https://data.indiadispatch.com/payments',
    'monthly': 'https://data.indiadispatch.com/payments/upi-transactions',
}

class TableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tables, self.table, self.row, self.cell = [], None, None, None

    def handle_starttag(self, tag, attrs):
        if tag == 'table': self.table = []
        elif tag == 'tr' and self.table is not None: self.row = []
        elif tag in ('td', 'th') and self.row is not None: self.cell = ''

    def handle_data(self, text):
        if self.cell is not None: self.cell += text

    def handle_endtag(self, tag):
        if tag in ('td', 'th') and self.cell is not None:
            self.row.append(self.cell.strip()); self.cell = None
        elif tag == 'tr' and self.row is not None:
            self.table.append(self.row); self.row = None
        elif tag == 'table' and self.table is not None:
            self.tables.append(self.table); self.table = None

def extract(monthly_html, ecosystem_html, observation_month, retrieved_on):
    observation_date = datetime.date.fromisoformat(observation_month)
    if observation_date.day != 1:
        raise ValueError('Observation month must be the first day of its month.')
    retrieval_date = datetime.date.fromisoformat(retrieved_on)
    label = observation_date.strftime('%B %Y')
    if f'in {label}' not in ecosystem_html:
        raise ValueError('Observation month is not supported by page text; review source.')
    a, b = TableParser(), TableParser()
    a.feed(monthly_html); b.feed(ecosystem_html)
    history = next(t for t in a.tables if t[0] == ['Month', 'Transactions', 'Value moved'])
    merchants = next(t for t in b.tables if t[0][:3] == ['Rank', 'Merchant category', 'Transactions'])
    states = next(t for t in b.tables if t[0][:3] == ['Rank', 'State / UT', 'Transactions'])
    banks = [t for t in b.tables if t[0] == ['Bank', 'Technical decline', 'Volume']]
    if len(banks) != 2: raise ValueError('Expected sending and receiving bank tables.')
    if len(merchants) < 10 or len(history) < 37: raise ValueError('Source tables incomplete.')
    out = {
        'monthly_reported': (['month_label','volume_reported','value_reported','source_id'],
            [[*r,'S2'] for r in history[1:]]),
        'merchants_reported': (['month','rank_reported','merchant_reported','volume_reported','mom_reported','six_month_reported','yoy_reported','value_reported','ticket_reported','source_id'],
            [[observation_month,*r,'S3'] for r in merchants[1:]]),
        'states_reported': (['month','rank_reported','state','volume_reported','volume_share_reported','value_reported','value_share_reported','source_id'],
            [[observation_month,*r,'S3'] for r in states[1:]]),
        'banks_reported': (['month','role','bank','td_reported','volume_reported','source_id'],
            [[observation_month,role,*r,'S3'] for role,t in zip(['Sending','Receiving'],banks) for r in t[1:]]),
    }
    for name,(header,rows) in out.items():
        path = ROOT/'data'/'raw'/f'{name}.csv'
        with path.open('w',encoding='utf-8',newline='') as f:
            w=csv.writer(f);w.writerow(header);w.writerows(rows)
    manifest={
        'observation_month':observation_month,
        'retrieved_on':retrieval_date.isoformat(),
        'extracted_on':datetime.date.today().isoformat(),
        'extraction':'HTML table facts; presentation prose and entire pages are not redistributed',
        'source_page_sha256':{k:hashlib.sha256(s.encode()).hexdigest() for k,s in [('monthly',monthly_html),('ecosystem',ecosystem_html)]},
        'row_counts':{k:len(v[1]) for k,v in out.items()},
        'urls':URLS,
    }
    (ROOT/'data'/'raw'/'extraction_manifest.json').write_text(json.dumps(manifest,indent=2), encoding='utf-8')
    return manifest

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--monthly-html',type=Path)
    p.add_argument('--ecosystem-html',type=Path)
    p.add_argument('--observation-month',required=True,help='Verified first day of reporting month, YYYY-MM-01')
    p.add_argument('--retrieved-on',help='Date the supplied local HTML was obtained, YYYY-MM-DD; required for local HTML')
    p.add_argument('--refresh',action='store_true',help='Downloads both published pages using curl; review output before use')
    args=p.parse_args()
    if args.refresh:
        with tempfile.TemporaryDirectory() as d:
            texts={}
            for key,url in URLS.items():
                dest=Path(d)/f'{key}.html'
                subprocess.run(['curl','--fail','--location','--max-time','45','--output',str(dest),url],check=True)
                texts[key]=dest.read_text(encoding='utf-8')
            result=extract(texts['monthly'],texts['ecosystem'],args.observation_month,datetime.date.today().isoformat())
    elif args.monthly_html and args.ecosystem_html:
        if not args.retrieved_on:
            p.error('--retrieved-on is required for local HTML; use the actual source retrieval date.')
        result=extract(args.monthly_html.read_text(encoding='utf-8'),args.ecosystem_html.read_text(encoding='utf-8'),args.observation_month,args.retrieved_on)
    else: p.error('Supply two local HTML files or --refresh.')
    print(json.dumps(result['row_counts'],indent=2))

if __name__=='__main__': main()
