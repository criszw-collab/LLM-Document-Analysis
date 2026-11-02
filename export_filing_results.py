"""Export one row for each processed filing, without claiming 100 product releases.
Run after prepare_submission.py: python export_filing_results.py --project-root .
"""
from pathlib import Path
import argparse,csv,json
from datetime import datetime
FIELDS=['company_name','stock_name','filing_time','new_product','product_description']
NO_PRODUCT='No qualifying product extracted'
def read_csv(path):
 with Path(path).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write_csv(path,rows,fields):
 with Path(path).open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def export(root):
 root=Path(root)
 filings=read_csv(root/'data/filing_metadata.csv');manifest=read_csv(root/'data/manifest.csv');logs=read_csv(root/'data/filing_log.csv')
 products=read_csv(root/'products.csv');evidence=read_csv(root/'data/source_evidence.csv')
 overrides=json.loads((root/'data/filing_description_overrides.json').read_text(encoding='utf-8'))
 ids={f['accession'] for f in filings}
 if len(filings)!=100 or len(ids)!=100:raise ValueError('Expected 100 unique completed filings')
 if ids!={r['accession'] for r in manifest}:raise ValueError('Filing metadata does not match manifest')
 if ids!={r['accession'] for r in logs} or not all(r['status']=='complete' for r in logs):raise ValueError('Incomplete filing processing')
 evidence_map={}
 for e in evidence:evidence_map.setdefault((e['stock_name'],e['new_product']),[]).append(e['accession'])
 by_id={a:[] for a in ids}
 for p in products:
  matching=evidence_map.get((p['stock_name'],p['new_product']),[])
  matching=[a for a in matching if any(f['accession']==a and f['filing_time']==p['filing_time'] for f in filings)]
  if len(matching)!=1:raise ValueError('Ambiguous or missing product-to-filing evidence')
  by_id[matching[0]].append(p)
 rows=[];index=[]
 for number,f in enumerate(filings,1):
  if datetime.fromisoformat(f['filing_time']).tzinfo is None:raise ValueError('Timestamp lacks timezone')
  items=by_id[f['accession']];row={k:f[k] for k in FIELDS[:3]}
  if not items:
   row.update(new_product=NO_PRODUCT,product_description='No qualifying product retained within the examined primary 8-K and first Exhibit 99.1 scope.')
  else:
   row['new_product']='; '.join(p['new_product'] for p in items)
   description='; '.join(p['product_description'] for p in items)
   if len(description)>=180:
    override=overrides.get(f['accession'])
    if not override or set(override['product_names'])!={p['new_product'] for p in items}:raise ValueError('Supply a source-supported concise multi-product description')
    description=override['description']
   row['product_description']=description
  if not 0<len(row['product_description'])<180:raise ValueError('Invalid description length')
  rows.append(row)
  index.append({'row_number':number,'accession':f['accession'],'stock_name':f['stock_name'],
                'retained_product_rows':len(items),'outcome':'product_retained' if items else 'no_product_retained',
                'meaning':'Pipeline extraction outcome, not proof that no release exists'})
 write_csv(root/'filing_results_100.csv',rows,FIELDS)
 write_csv(root/'data/filing_results_index.csv',index,list(index[0]))
 summary={'filing_rows':len(rows),'filings_with_retained_products':sum(bool(v) for v in by_id.values()),
          'filings_without_retained_products':sum(not v for v in by_id.values()),'retained_product_rows':len(products),
          'row_unit':'One processed filing; multiple products in one row are separated by semicolons',
          'no_product_marker':NO_PRODUCT,'is_100_product_announcements':False}
 (root/'data/filing_results_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
 return summary
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--project-root',default='.');a=p.parse_args();print(json.dumps(export(a.project_root),indent=2))
