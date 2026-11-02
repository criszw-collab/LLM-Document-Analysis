from pathlib import Path
import csv,json,sys,tempfile,unittest
from datetime import datetime
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from prepare_submission import FIELDS,build
ROOT=Path(__file__).resolve().parents[1]
def rows(name):
 with (ROOT/name).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
class SubmissionTests(unittest.TestCase):
 def test_csv_contract(self):
  data=rows('products.csv');self.assertEqual(len(data),5)
  self.assertEqual(list(data[0]),FIELDS)
  for r in data:
   self.assertTrue(all(r.values()));self.assertLess(len(r['product_description']),180)
   self.assertIsNotNone(datetime.fromisoformat(r['filing_time']).tzinfo)
  self.assertNotIn('B Medical Systems business',[r['new_product'] for r in data])
  self.assertNotIn('MIPI D-PHY ReDrivers',[r['new_product'] for r in data])
 def test_complete_sample(self):
  manifest=rows('data/manifest.csv');log=rows('data/filing_log.csv')
  self.assertEqual(len(manifest),100);self.assertEqual(len({r['accession'] for r in manifest}),100)
  self.assertEqual(len(log),100);self.assertTrue(all(r['status']=='complete' for r in log))
  self.assertEqual({r['accession'] for r in log},{r['accession'] for r in manifest})
 def test_audit_and_status(self):
  evidence=rows('data/source_evidence.csv');data=rows('products.csv');decisions=rows('data/candidate_decisions.csv')
  self.assertEqual(len(evidence),5);self.assertEqual(len(decisions),22)
  self.assertEqual(sum(r['disposition']=='retain' for r in decisions),len(data))
  self.assertEqual({(r['stock_name'],r['new_product']) for r in evidence},{(r['stock_name'],r['new_product']) for r in data})
  summary=json.loads((ROOT/'data/run_summary.json').read_text())
  self.assertEqual(summary['completed'],100);self.assertEqual(summary['final_csv_rows'],5)
  self.assertFalse(summary['accuracy_metrics_measured'])
 def test_different_run_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'wrong.zip';p.write_bytes(b'wrong source')
   with self.assertRaises(ValueError):build(p,Path(d)/'out',ROOT/'source_decisions.json')
if __name__=='__main__':unittest.main()
