"""Append additional SEC 8-K candidates without changing extraction policy or discarding progress.
Functions expect the original notebook's pipeline instance and module namespace.
"""
import json
from pathlib import Path
EXTRA_TICKERS=['FSLY','DDOG','DT','NTNX','PSTG','NTAP','INFA','INOD','EXLS','APPN','PATH','AI',
 'BBAI','VERI','AEYE','AVT','AVNW','MOV','UEIC','DLB','XPER','SONO','VUZI','OLED','LFUS',
 'ALGM','ALAB','MX','RDWR','ALLT','SERV','RR','KSCP','PDYN','RCAT','ONDS','UMAC','ACHR',
 'JOBY','BLDE','BTMD','CBLL','HYPR','NPCE','OPRX','RXST','NTRA','VCYT','CDNA','MYGN',
 'GH','EXAS','ADPT','AKYA','LQDA','YMAB','BCRX','BHVN','CRNX','DNLI','IOVA','VRNA',
 'ANIP','AMPH','SUPN','AVDL','AVNS','AVTR','BIO','TECH','QTRX','RGEN','CTKB','SDGR',
 'CERT','MMSI','LMAT','PEN','SWAV','SIBN','SIEN','INSP','AXSM','IRBT','AMOT','ROK',
 'EMR','FTV','ITT','DOV','GRC','MOG-A','MOG-B','HEI','FELE','WTS','AOS','ZWS','ESAB',
 'HAYW','ENOV','VNT','GMS','NVT','HUBB','ENS','ESE','KEYS','IR','IEX','GGG','WDFC',
 'HELE','YETI','FLYW','PAYO','PAY','FOUR','BILL','QTWO','NCNO','ALKT','BL','TOST',
 'AVDX','EVCM','WK','INTA','PCOR','DOCN','BOX','ASAN','FRSH','AMPL','BRZE','SPT',
 'ZI','DMRC','EGHT','FIVN','BAND']

def atomic_local(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(value,indent=2,ensure_ascii=False),encoding='utf-8');tmp.replace(path)

def extend_sec_manifest(pipe,namespace,requested_tickers=EXTRA_TICKERS):
    """Temporarily change discovery universe only; restore original policy/configuration globals."""
    output=pipe.project/'exports';path=output/'manifest.json'
    if not path.exists():raise ValueError('Restore the previous run manifest first; do not restart from scratch.')
    old=json.loads(path.read_text(encoding='utf-8'))
    old_ids={f['accession'] for f in old};old_tickers={f['stock_name'] for f in old}
    if len(old_ids)!=len(old):raise ValueError('Existing manifest has duplicate accessions')
    lookup={x['ticker']:x for x in pipe.sec_json('https://www.sec.gov/files/company_tickers.json').values()}
    candidates=[t for t in dict.fromkeys(requested_tickers) if t not in old_tickers and t in lookup]
    unavailable=[t for t in requested_tickers if t not in lookup]
    atomic_local(output/'extra_company_selection.json',{'source':'SEC company_tickers.json','requested':requested_tickers,
                 'new_valid_tickers':candidates,'unavailable':unavailable,'old_filings':len(old)})
    if not candidates:return old
    backup=output/'manifest_before_extension.json'
    if not backup.exists():atomic_local(backup,old)
    ledger_path=output/'universe_extensions.json'
    ledger=json.loads(ledger_path.read_text(encoding='utf-8')) if ledger_path.exists() else []
    original_tickers=namespace['TICKERS'];discovery_path=output/'discovery_log.json'
    old_log=json.loads(discovery_path.read_text(encoding='utf-8')) if discovery_path.exists() else []
    csv_path=output/'manifest.csv'
    old_csv=csv_path.read_bytes() if csv_path.exists() else None
    pipe.discovery=[]
    try:
        namespace['TICKERS']=candidates
        added=pipe.discover()  # Original instructor Atom + SEC submissions implementation, exact 8-Ks.
    finally:
        namespace['TICKERS']=original_tickers
        # Discovery may temporarily write a new-only manifest. Never leave old work detached.
        atomic_local(path,old)
        if old_csv is not None:csv_path.write_bytes(old_csv)
        pipe.discovery=old_log+pipe.discovery
        atomic_local(discovery_path,pipe.discovery)
    combined=list(old)
    for f in added:
        if f['accession'] not in old_ids:
            combined.append(f);old_ids.add(f['accession'])
    ledger.append({'source':'SEC EDGAR only','extra_tickers':candidates,'filings_before':len(old),
                   'filings_added':len(combined)-len(old),'filings_after':len(combined),
                   'extraction_policy_changed':False,'checkpoint_configuration_id':pipe.config_id})
    atomic_local(ledger_path,ledger);atomic_local(path,combined)
    # Import locally: this script can also be tested without installing the LLM stack.
    import pandas as pd
    pd.DataFrame(combined).to_csv(output/'manifest.csv',index=False)
    return combined
