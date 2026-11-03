# Course data sources and their role in this assignment

The assignment specifies product announcements in SEC Form 8-K filings. Sources from the broader course catalogue are not interchangeable with the required document type. 100 fiscal, economic or tax records cannot satisfy the 100-product target.

| Course source | Treatment in the pipeline |
|---|---|
| SEC EDGAR API / developer resources | Primary input. Ticker JSON maps symbols to CIKs; the instructor's Atom endpoint is parsed with BeautifulSoup; submissions JSON provides historical filings and acceptance timestamps. Only exact 2025 Form 8-Ks are selected. |
| SEC EDGAR corporate reports and PDFs | Primary documents. Read the primary 8-K and readable numbered Exhibit 99 attachments, including text-based PDFs. Image-only files remain logged coverage errors. |
| SEC 10-K and 10-Q reports | May supply background context, but are not added as 8-K product rows. The assignment requires instructor discussion before replacing the document type. |
| XBRL US API | Structured financial-reporting facts, not the unstructured release-announcement source needed here. Not queried or counted toward the target. |
| Treasury Fiscal Data API | Federal fiscal statistics; not used as corporate product-announcement evidence. |
| Data.gov | A general dataset catalogue. No listed catalogue record is assumed to be an 8-K launch announcement. Not used to pad the product output. |
| GAO reports | Government accountability reports; outside the required filing corpus. |
| FRED | Economic time-series data; outside the required product-release corpus. |
| IRS Exempt Organizations Search | Nonprofit status and tax filings; outside the public-company 8-K corpus. |

## SEC endpoints actually used

```python
url = 'https://www.sec.gov/files/company_tickers.json'
search_url = f'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type=8-K&count={count}&output=atom'
submissions_url = f'https://data.sec.gov/submissions/CIK{cik}.json'
```

JSON is decoded with Python's JSON tools; BeautifulSoup parses Atom XML and filing HTML. SEC filing-index links identify actual company documents. Identifying contact headers, paced requests, caching and bounded transient retries remain in place. No access-block bypass or API-key signup is introduced.

## Continuation and provenance

The original run attempted 881 filings, completed 874 processing records (including 563 retrieval skips), and retained 28 provisional product rows. Seven sources were unreadable. These are actual saved-run counts, not a complete 100-product result.

`expand_sec_sources.py` appends newly discovered SEC 8-K accessions while preserving the original manifest, extraction settings, completed checkpoints and model responses. `universe_extensions.json` records the extra ticker universe separately from the unchanged extraction fingerprint. Repeated accessions are excluded. If discovery is interrupted, the old manifest and its CSV are restored.

The extra-company list has 124 additional valid ticker candidates in the SEC map saved with the uploaded run. Actual eligibility is checked during discovery; some issuers may have no qualifying 2025 8-Ks. This is not a promise of 124 additional domestic filers or enough launches to reach 100.

Release detection, model consistency checks, deduplication and product-count stopping remain unchanged. The new pool is not a random sample. The 28 existing rows still need quality checking; a repeated product name, non-English corruption or unfinished description must not be treated as a verified product just because it passed earlier automatic checks.

## Links

- SEC developer resources: https://www.sec.gov/developer
- SEC API documentation: https://www.sec.gov/edgar/sec-api-documentation
- SEC filings search: https://www.sec.gov/edgar/search/
- Course XBRL link: https://xbrl.us/home/use/xbrl-api/
- Treasury Fiscal Data: https://fiscaldata.treasury.gov/api-documentation/
- Data.gov: https://catalog.data.gov/
- GAO: https://www.gao.gov/
- FRED API: https://fred.stlouisfed.org/docs/api/fred/
- IRS Exempt Organizations Search: https://www.irs.gov/charities-non-profits/tax-exempt-organization-search

The course's XBRL URL did not resolve during this check; Treasury and GAO requests were unavailable from this workspace. These services are not required by the SEC-only extraction workflow, and no successful integration with them is claimed.
