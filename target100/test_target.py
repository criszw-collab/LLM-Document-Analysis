import tempfile,time,json,unittest
from pathlib import Path
from unittest.mock import patch
import pipeline_100_products as m

def record(i,name=None,status='complete',supported=True):
 name=name or f'Sensor {i}'
 filing={'accession':f'fixture-{i}','company_name':'Example Co','stock_name':'EX','filing_time':'2025-02-01T12:00:00+00:00','filing_date':'2025-02-01','cik':'123'}
 event={'product_name':name,'organization':'Example Co','product_description':'A new sensor.',
        'evidence_ids':[1],'needs_review':False,'release_quote':f'Example Co launched {name}.','launch_type':'new_release',
        'verification':{'supported':supported,'reason':'Fixture-only source check'}}
 item={'event':event,'grounded':True,'reason':'Fixture','evidence':[{'id':1,'text':event['release_quote'],'url':'synthetic'}]}
 return {'filing':filing,'status':status,'events':[item],'model_calls':0,'seconds':0,'coverage':[{'selected_units':1}]}
class TargetTests(unittest.TestCase):
 def test_partial_and_dedup(self):
  with tempfile.TemporaryDirectory() as folder:
   p=m.ProductTargetPipeline(folder,time.monotonic()+60,model_digest='fixture')
   p.records=[record(1,'Sensor X'),record(2,'Sensor X™'),record(3,status='error'),record(4,supported=False)]
   frame,summary=p.export([r['filing'] for r in p.records])
   self.assertEqual(len(frame),1);self.assertFalse(summary['target_reached'])
   self.assertFalse((Path(folder)/'exports/products.csv').exists())
   self.assertTrue((Path(folder)/'exports/products_partial.csv').exists())
 def test_100_product_entry_contract(self):
  with tempfile.TemporaryDirectory() as folder:
   p=m.ProductTargetPipeline(folder,time.monotonic()+60,model_digest='fixture')
   p.records=[record(i) for i in range(102)]
   frame,s=p.export([r['filing'] for r in p.records])
   self.assertEqual(len(frame),100);self.assertTrue(s['target_reached'])
   self.assertEqual(list(frame.columns),m.FIELDS)
   self.assertTrue(frame.product_description.str.len().between(1,179).all())
   self.assertTrue((Path(folder)/'exports/products.csv').exists())
 def test_quote_and_schema(self):
  p=object.__new__(m.ProductTargetPipeline);r=record(1);e=dict(r['events'][0]['event']);e.pop('verification')
  batch=[{'id':1,'text':e['release_quote'],'url':'synthetic'}]
  m.validate({'events':[e]},m.schema([1]))
  self.assertTrue(p.check_event(e,batch,r['filing'])[0])
  self.assertFalse(p.check_event(dict(e,release_quote='Example Co launched Invented.'),batch,r['filing'])[0])
  with self.assertRaises(Exception):m.validate({'events':[dict(e,product_description='x'*180)]},m.schema([1]))
 def test_retrieval_skip_is_explicit(self):
  p=object.__new__(m.ProductTargetPipeline)
  batches,coverage=p.passages([{'url':'synthetic','text':'Example Co reported quarterly financial results.','text_sha256':'fixture'}])
  self.assertFalse(batches);self.assertIn('not selected',coverage[0]['mode'])
 def test_all_numbered_exhibits(self):
  with tempfile.TemporaryDirectory() as folder:
   p=m.ProductTargetPipeline(folder,time.monotonic()+60,model_digest='fixture');f=record(1)['filing']
   f.update(index_url='https://www.sec.gov/index.html',primary_url='https://www.sec.gov/primary.htm')
   html=b'<table class="tableFile"><tr><td>2</td><td>x</td><td><a href="/a.htm">a</a></td><td>EX-99.1</td></tr><tr><td>3</td><td>x</td><td><a href="/b.htm">b</a></td><td>EX-99.2</td></tr></table>'
   p.fetch=lambda url:html if url.endswith('index.html') else b'<p>'+b'Example Co source text. '*8+b'</p>'
   docs,excluded=p.documents(f)
   self.assertEqual(len(docs),3);self.assertEqual(len(excluded),0)
 def test_run_stops_on_products_and_resumes(self):
  class Fake(m.ProductTargetPipeline):
   def process(self,f):
    r=record(int(f['accession'].split('-')[-1]));self.save_record(r);return r
  with tempfile.TemporaryDirectory() as folder,patch.object(m,'TARGET',2):
   p=Fake(folder,time.monotonic()+60,model_digest='fixture')
   manifest=[record(i)['filing'] for i in range(5)]
   frame,s=p.run(manifest)
   self.assertEqual(len(p.records),2);self.assertEqual(len(frame),2)
   resumed=Fake(folder,time.monotonic()+60,model_digest='fixture')
   frame,s=resumed.run(manifest);self.assertEqual(len(resumed.records),2)
if __name__=='__main__':unittest.main(verbosity=2)
