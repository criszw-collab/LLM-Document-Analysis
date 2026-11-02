from pathlib import Path
import sys,unittest,csv,json
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from export_filing_results import export,read_csv,FIELDS,NO_PRODUCT
ROOT=Path(__file__).resolve().parents[1]
class FilingExportTests(unittest.TestCase):
 def test_row_contract_and_outcomes(self):
  rows=read_csv(ROOT/'filing_results_100.csv');index=read_csv(ROOT/'data/filing_results_index.csv')
  self.assertEqual(len(rows),100);self.assertEqual(list(rows[0]),FIELDS)
  self.assertEqual(len({x['accession'] for x in index}),100)
  self.assertEqual(sum(r['new_product']==NO_PRODUCT for r in rows),96)
  self.assertEqual(sum(int(x['retained_product_rows']) for x in index),5)
  self.assertTrue(all(0<len(r['product_description'])<180 for r in rows))
  self.assertEqual(sum(';' in r['new_product'] for r in rows),1)
  self.assertFalse(json.loads((ROOT/'data/filing_results_summary.json').read_text())['is_100_product_announcements'])
if __name__=='__main__':unittest.main()
