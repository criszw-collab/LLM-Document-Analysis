from pathlib import Path
import tempfile,json,unittest
from expand_sec_sources import extend_sec_manifest,atomic_local
class Fake:
 def __init__(self,path,namespace,fail=False):
  self.project=Path(path);self.config_id='unchanged';self.discovery=[];self.namespace=namespace;self.fail=fail
 def sec_json(self,url):return {'0':{'ticker':'OLD'},'1':{'ticker':'NEW'}}
 def discover(self):
  assert self.namespace['TICKERS']==['NEW']
  self.discovery.append({'ticker':'NEW'})
  result=[{'accession':'a','stock_name':'OLD'},{'accession':'b','stock_name':'NEW'}]
  atomic_local(self.project/'exports/manifest.json',result)
  (self.project/'exports/manifest.csv').write_text('new-only temporary CSV')
  if self.fail:raise RuntimeError('Simulated interrupted discovery')
  return result
class ExpansionTests(unittest.TestCase):
 def setup_project(self,d):
  path=Path(d);(path/'exports').mkdir();(path/'checkpoints').mkdir()
  old=[{'accession':'a','stock_name':'OLD'}]
  atomic_local(path/'exports/manifest.json',old)
  (path/'exports/manifest.csv').write_bytes(b'accession,stock_name\na,OLD\n')
  (path/'checkpoints/a.json').write_bytes(b'prior checkpoint retained')
  return old
 def test_append_preserves_completed_work(self):
  with tempfile.TemporaryDirectory() as d:
   old=self.setup_project(d);namespace={'TICKERS':['OLD']};pipe=Fake(d,namespace)
   result=extend_sec_manifest(pipe,namespace,['OLD','NEW','BAD'])
   self.assertEqual([f['accession'] for f in result],['a','b'])
   self.assertEqual(namespace['TICKERS'],['OLD'])
   self.assertEqual((Path(d)/'checkpoints/a.json').read_bytes(),b'prior checkpoint retained')
   ledger=json.loads((Path(d)/'exports/universe_extensions.json').read_text())
   self.assertEqual(ledger[-1]['filings_added'],1);self.assertFalse(ledger[-1]['extraction_policy_changed'])
 def test_failure_restores_old_manifest(self):
  with tempfile.TemporaryDirectory() as d:
   old=self.setup_project(d);namespace={'TICKERS':['OLD']};pipe=Fake(d,namespace,True)
   with self.assertRaises(RuntimeError):extend_sec_manifest(pipe,namespace,['NEW'])
   self.assertEqual(json.loads((Path(d)/'exports/manifest.json').read_text()),old)
   self.assertEqual((Path(d)/'exports/manifest.csv').read_bytes(),b'accession,stock_name\na,OLD\n')
   self.assertEqual(namespace['TICKERS'],['OLD'])
if __name__=='__main__':unittest.main(verbosity=2)
