# SEC 8-K Document Analysis — 100 Product Announcements

**Crispen Chachengwa**  
Project: https://github.com/criszw-collab/LLM-Document-Analysis

## Required target and current status

The required output is **100 actual product-announcement entries**, with a product name and a description shorter than 180 characters for each. Processing 100 filings does not satisfy that count. A filing-status CSV containing no-product markers does not satisfy it either.

**The target has not yet been achieved.** An earlier completed run analyzed 100 filings but retained only five product-family rows; the newer 881-filing run below retained 28 provisional entries. Those results, reports, scripts and the 100-filing status CSV are preserved under [`prior_run/`](prior_run/). They are preliminary/history, not a completed 100-product submission. No fake, repeated or placeholder products have been added.

## Continue the completed 881-filing run

Your latest saved run attempted 881 filings, completed 874 processing records and retained **28 provisional product entries** in 54.66 recorded minutes. It exhausted the candidate pool. These are not 100 verified product announcements; seven non-mutating quality flags are recorded in the progress snapshot.

[Open the continuation notebook in Colab](https://colab.research.google.com/github/criszw-collab/LLM-Document-Analysis/blob/main/SEC_8K_Continue_Expanded_SEC_Sources.ipynb)

Use the same Drive project, model and extraction settings. Run the continuation cells in order; it restores the saved ZIP only if Drive is missing the project, appends additional SEC 8-K candidates, and reuses completed checkpoints. The SEC ticker-map snapshot contains 124 valid additional ticker candidates; actual 2025 8-K eligibility is checked during discovery. It does not replace the original extraction fingerprint or repeat completed old filings.

- [Course-source selection and scope](DATA_SOURCES.md)
- [Expansion helper](continuation/expand_sec_sources.py)
- [Expansion tests](continuation/test_expansion.py)
- [Latest provisional 28-row CSV](progress_28/products_partial.csv)
- [Quality flags](progress_28/quality_flags.csv)

The new source discovery has not been live-run here; continue it in Colab. The helper passed interruption/preservation tests, and a no-inference compatibility check loaded all 881 actual checkpoints and retained the same 28 entries.

## Start a separate fresh run only if needed

[Open the 100-product notebook in Colab](https://colab.research.google.com/github/criszw-collab/LLM-Document-Analysis/blob/main/SEC_8K_100_Product_Announcements_Colab.ipynb)

[Download/view notebook](SEC_8K_100_Product_Announcements_Colab.ipynb)

1. Select **Runtime → Change runtime type → GPU**.
2. Run Cells 1–9 to install dependencies/Ollama inside Colab, verify GPU use, mount Drive and discover additional 2025 filings.
3. Run Cell 10 for a small pilot. Inspect actual responses and source evidence.
4. Run **Cell 11** to continue until 100 distinct product entries, the candidate pool ends, or the session budget is reached. It counts products, not documents.
5. If the session stops below 100, rerun setup with the same Drive project and Cell 11 to resume compatible saved work. Cell 12 can retry errors. More sources may be needed if the pool is exhausted; a changed policy/pool configuration requires a new project folder.
6. Cell 13 generates a short cited methodology report using the actual current counts. Cell 14 downloads the saved project. Also save the executed `.ipynb` through Colab's File menu.

Ollama runs inside Colab; the Ollama installed on your laptop is not used. No paid inference API key is required. No GPU or local Ollama server was available in the authoring workspace, so this revision has not been run through a live dataset here. You must execute it on the Colab GPU to obtain new product results.

## What changed

- The goal is 100 distinct company/product entries rather than 100 filings.
- Discovery uses a larger pool of less common companies. At packaging time, 96 candidate tickers were found in the official SEC ticker map; discovery validates availability again. The pool is capped at 5,000 2025 8-Ks and 80 filings per company.
- The primary 8-K and all readable numbered Exhibit 99 documents are considered, rather than just the first Exhibit 99.1.
- Release-cue retrieval selects relevant passages and context. Skipped passages/filings are disclosed as retrieval skips, not verified no-product findings.
- One extraction pass performs ORGANIZATION/PRODUCT NER and produces exact product names, release quotes, event types, descriptions and source IDs.
- Positive candidates also receive a same-model source-consistency check. Financial results, divestitures, appointments, generic categories and existing-product adoption do not count. Same-model agreement is not independent human validation.
- Exact source quotations and names are checked in Python; repeated normalized names for the same CIK count once across filings.
- Successful batches, responses and filings save automatically to Drive. The progress bar counts product entries. Errors remain visible while other filings continue.

## Output contract

Final `exports/products.csv` is written **only when 100 qualifying distinct entries have been collected**. It has exactly:

```text
company_name,stock_name,filing_time,new_product,product_description
```

Every description is 1–179 characters. Multiple unrelated products are separate rows. Product-free filings add zero rows. Expected upcoming introductions and sampling status stay explicit. Named product families can be entries; these are not necessarily individual catalogue SKUs.

Before the target is reached, `exports/products_partial.csv` records the actual count. It must not be presented as a complete 100-product submission. The final pipe-delimited file is also written only when the goal is reached. `product_evidence.json`, `filing_log.csv`, `excluded_candidates.csv` and `run_summary.json` retain evidence and actual execution status.

## Accuracy and runtime limits

Mechanical checks and a small model can still misclassify release meaning, ownership or descriptions. Alias variants can complicate deduplication. Retrieval can miss announcements, and unreadable sources remain errors. Check the linked source evidence; no independent accuracy statistic or human review is claimed. The model-check stage is an accuracy measure added to the code, not a separate manual-approval requirement from the assignment.

A processing session lasts up to 4.5 hours and can resume. Reaching 100 products within five hours is not guaranteed. The previous run's 7.37-minute processing time belongs to its much smaller output, not this revised target.

## Implementation and tests

- [Pipeline source](target100/pipeline_100_products.py)
- [Tests](target100/test_target.py)
- [SEC ticker validation](target100/ticker_validation.json)

```bash
pip install -r requirements.txt
python target100/test_target.py
```

Six offline tests cover the 100-entry output contract, no final CSV below target, cross-filing deduplication, explicit retrieval skips, all-numbered-exhibit parsing, quote/schema checks, and stopping/resuming by product count. Synthetic test outputs live only in temporary folders and are never submitted as results. A separate mocked HTTP check exercised verifier-response caching. These tests do not establish live model accuracy.

## Assignment references and remaining deliverables

The instructor's ticker JSON and BeautifulSoup-parsed Atom URLs remain in code. SEC submissions JSON adds historical metadata and exact form matching. JSON is decoded as JSON; HTML/XML use BeautifulSoup. See [SEC EDGAR APIs](https://www.sec.gov/edgar/sec-api-documentation), [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/), [Ollama structured outputs](https://docs.ollama.com/capabilities/structured-outputs), and [Colab FAQ](https://research.google.com/colaboratory/faq.html).

After the real run reaches the target, publish its executed notebook, 100-product CSV and actual-results 1–2 page report here. Put this repository URL in the report and at the top of your CV. The previous reports under `prior_run/` describe prior work; they do not claim completion of the new target.
