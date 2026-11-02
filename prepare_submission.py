"""Rebuild submitted CSV from the completed run and disclosed source decisions.
This exports real saved LLM candidates. It does not run a new model or invent rows.
Usage: python prepare_submission.py sec8k_colab_v2.zip --output .
"""
from pathlib import Path
import argparse,csv,hashlib,json,unicodedata,re,zipfile
FIELDS=['company_name','stock_name','filing_time','new_product','product_description']
EXPECTED_ZIP_SHA256='30b6caa74e2d11df0ff4a6e370c1be2a75ddf7babb1d93bb249e10bd7e93b990'  # Set during packaging to bind decisions to the reviewed source snapshot.
def normalized(value):
 value=unicodedata.normalize('NFKC',re.sub(r'[™®©]','',str(value)))
 return re.sub(r'\s+',' ',value.translate(str.maketrans({'’':"'",'–':'-','—':'-','‑':'-'}))).strip().casefold()
def write_csv(path,rows,fields,delimiter=','):
 path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('w',encoding='utf-8-sig',newline='') as handle:
  writer=csv.DictWriter(handle,fieldnames=fields,delimiter=delimiter);writer.writeheader();writer.writerows(rows)
def build(zip_path,output,decision_path=None):
 zip_path=Path(zip_path);output=Path(output);data=output/'data';data.mkdir(parents=True,exist_ok=True)
 digest=hashlib.sha256(zip_path.read_bytes()).hexdigest()
 if digest!=EXPECTED_ZIP_SHA256:raise ValueError('Source ZIP differs from the reviewed run. These decisions cannot be silently applied to another run.')
 decisions=json.loads(Path(decision_path or Path(__file__).with_name('source_decisions.json')).read_text(encoding='utf-8'))
 with zipfile.ZipFile(zip_path) as z:
  manifest=json.loads(z.read('exports/manifest.json'))
  summary=json.loads(z.read('exports/run_summary.json'))
  records=[json.loads(z.read(n)) for n in z.namelist() if n.startswith('checkpoints/') and n.endswith('.json')]
  for original,new in [('exports/products.csv','products_provisional.csv'),('exports/manifest.csv','manifest.csv'),('exports/filing_log.csv','filing_log.csv')]:
   (data/new).write_bytes(z.read(original))
 assert len(manifest)==100 and len({f['accession'] for f in manifest})==100
 assert len(records)==100 and all(r['status']=='complete' for r in records)
 groups={}
 for record in records:
  for item in record['events']:
   group=groups.setdefault(item['candidate_id'],{'filing':record['filing'],'versions':[]})
   group['versions'].append(item)
 assert set(groups)==set(decisions),'Every unique candidate needs a disclosed disposition'
 rows=[];audit=[];evidence=[]
 for cid,group in groups.items():
  decision=decisions[cid];item=group['versions'][0];f=group['filing'];event=item['event']
  audit.append({'candidate_id':cid,'accession':f['accession'],'stock_name':f['stock_name'],
                'original_product':event['product_name'],'disposition':decision['disposition'],
                'reason':decision['reason'],'source_url':item['evidence'][0]['url'] if item['evidence'] else ''})
  if decision['disposition']!='retain':continue
  name=decision.get('product_name',event['product_name']);desc=decision['product_description']
  assert 0<len(desc)<180 and normalized(name)
  # Correct product-name ordering or split a combined list only when grounded in cited source.
  supporting=next((v for v in group['versions'] if normalized(name) in normalized(' '.join(u['text'] for u in v['evidence']))),None)
  assert supporting,'Accepted name absent from cited source'
  quote=decision['evidence_quote']
  assert normalized(quote) in normalized(' '.join(u['text'] for u in supporting['evidence']))
  row={key:f[key] for key in FIELDS[:3]};row.update(new_product=name,product_description=desc);rows.append(row)
  evidence.append({'accession':f['accession'],'stock_name':f['stock_name'],'new_product':name,
                   'source_url':supporting['evidence'][0]['url'],'evidence_ids':json.dumps(event['evidence_ids']),
                   'evidence_quote':quote,'source_units_sha256':hashlib.sha256(json.dumps(supporting['evidence'],sort_keys=True).encode()).hexdigest(),
                   'review_provenance':'AI-assisted source check by ChatGPT; not independent human validation'})
 rows.sort(key=lambda r:(r['stock_name'],r['filing_time'],r['new_product']))
 write_csv(output/'products.csv',rows,FIELDS)
 write_csv(output/'products_pipe.txt',rows,FIELDS,'|')
 write_csv(data/'candidate_decisions.csv',audit,list(audit[0]))
 write_csv(data/'source_evidence.csv',evidence,list(evidence[0]))
 (data/'original_run_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
 final_summary={'selected':len(manifest),'completed':len(records),'companies':len({f['stock_name'] for f in manifest}),
                'model_calls':summary['model_calls'],'recorded_pipeline_minutes':summary['elapsed_minutes'],
                'input_zip_sha256':digest,'original_provisional_rows':summary['product_rows'],'original_candidate_flags':summary['review_items'],
                'final_csv_rows':len(rows),'filings_with_retained_rows':len({e['accession'] for e in evidence}),
                'unique_candidates_source_checked':len(groups),'not_retained_candidates':len(groups)-len(rows),
                'source_check_provenance':'AI-assisted source checking and conservative corrections; not independent human validation',
                'final_csv_semantics':'Named or identifiable technical product families; expected availability and sampling explicitly retained',
                'accuracy_metrics_measured':False}
 (data/'run_summary.json').write_text(json.dumps(final_summary,indent=2,ensure_ascii=False),encoding='utf-8')
 # Save canonical filing metadata for the separate one-row-per-filing export.
 metadata=[{k:next(r['filing'] for r in records if r['filing']['accession']==f['accession'])[k] for k in ['accession',*FIELDS[:3]]} for f in manifest]
 write_csv(data/'filing_metadata.csv',metadata,['accession',*FIELDS[:3]])
 return final_summary
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('zip_path');parser.add_argument('--output',default='.');args=parser.parse_args()
 print(json.dumps(build(args.zip_path,args.output),indent=2))
