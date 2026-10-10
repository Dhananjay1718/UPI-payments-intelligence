"""Protect provenance dates and reject invalid snapshot keys before file writes."""
import datetime
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import extract_snapshot as snapshot


class TestSnapshotProvenance(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'data/raw').mkdir(parents=True)
        self.root_patch = patch.object(snapshot, 'ROOT', self.root)
        self.root_patch.start()
        self.addCleanup(self.root_patch.stop)

    @staticmethod
    def table(header, rows):
        return '<table>' + ''.join(
            '<tr>' + ''.join(f'<td>{cell}</td>' for cell in row) + '</tr>'
            for row in [header] + rows
        ) + '</table>'

    def fixture_pages(self):
        # Synthetic parser fixtures stay inside this test and are never project data.
        monthly = self.table(['Month', 'Transactions', 'Value moved'],
                             [['August 2026', '1 million', '₹1 billion']] * 36)
        merchant = self.table(['Rank', 'Merchant category', 'Transactions'],
                              [['1', 'Test MCC 1234', '1 million']] * 9)
        state = self.table(['Rank', 'State / UT', 'Transactions'],
                           [['1', 'Test state', '1 million']])
        bank = self.table(['Bank', 'Technical decline', 'Volume'],
                          [['Test bank', '1%', '1 million']])
        return monthly, 'Reported in August 2026' + merchant + state + bank + bank

    def test_local_html_preserves_its_actual_retrieval_date(self):
        monthly, ecosystem = self.fixture_pages()
        result = snapshot.extract(monthly, ecosystem, '2026-08-01', '2026-09-25')
        self.assertEqual(result['retrieved_on'], '2026-09-25')
        self.assertEqual(result['extracted_on'], datetime.date.today().isoformat())
        saved = json.loads((self.root/'data/raw/extraction_manifest.json').read_text(encoding='utf-8'))
        self.assertEqual(saved, result)

    def test_non_month_start_cannot_overwrite_snapshot(self):
        with self.assertRaisesRegex(ValueError, 'first day'):
            snapshot.extract('', '', '2026-08-15', '2026-09-25')
        self.assertEqual(list((self.root/'data/raw').iterdir()), [])

    def test_invalid_retrieval_date_cannot_overwrite_snapshot(self):
        with self.assertRaises(ValueError):
            snapshot.extract('', '', '2026-08-01', 'unknown')
        self.assertEqual(list((self.root/'data/raw').iterdir()), [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
