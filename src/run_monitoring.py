"""Run the optional SQL monitoring extension against the rebuilt SQLite snapshot."""
import csv
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main():
    with sqlite3.connect(ROOT / 'data/upi_intelligence.sqlite') as connection:
        source = (ROOT / 'sql/anomaly_monitoring.sql').read_text()
        for block in re.split(r'-- QUERY: ', source)[1:]:
            name = block.splitlines()[0].strip()
            cursor = connection.execute(block[block.index('WITH '):])
            rows = cursor.fetchall()
            output = ROOT / 'reports/sql_results' / f'{name}.csv'
            output.parent.mkdir(parents=True, exist_ok=True)
            with output.open('w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([column[0] for column in cursor.description])
                writer.writerows(rows)
            print(f'{name}: {len(rows)} months; {sum(row[-1] == "investigate" for row in rows)} investigation flags')

if __name__ == '__main__':
    main()
