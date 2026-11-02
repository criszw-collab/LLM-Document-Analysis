# SEC 8-K Product Extraction: Methodology Report

**Crispen Chachengwa** | November 2, 2026

GitHub: https://github.com/criszw-collab/LLM-Document-Analysis

## Objective and sample

This project uses a large language model to extract named new-product announcements from 100 unique SEC Form 8-K filings dated January 1 to December 31, 2025. The sample covers 20 less prominent publicly traded companies. A fixed round-robin selection distributes filings across companies, with a maximum of ten per company. Selection takes place before product extraction. Multiple products may produce several rows from one filing; a product-free filing produces no artificial product row.

## Data collection and preprocessing

The company_tickers.json endpoint maps stock tickers to company CIKs. The instructor's browse-edgar Atom endpoint is queried for 8-K filings and parsed with BeautifulSoup as XML. SEC submissions JSON supplements historical coverage and exact form matching [1]. JSON responses are decoded as JSON, while BeautifulSoup parses XML and HTML [2]. The code records company metadata and SEC acceptance timestamps, converted to UTC. Requests use an identifying contact header, pacing, caching and bounded retries for temporary failures.

## Document scope and text preparation

The pipeline reads each primary 8-K and its first Exhibit 99.1, where available. Other supplementary exhibits are logged as excluded. HTML formatting is removed while narrative and table text are retained; pypdf handles text-based PDFs. Text is divided into approximately 900-character source-linked units. Announcement-related units and neighboring context are selected. When no keyword matches, full text is used. Selected units are grouped into batches of about 9,000 characters, with overlap and a twelve-batch ceiling. Unreadable or excessive material is flagged instead of silently discarded.

## LLM extraction and NER

Ollama runs qwen3:4b-instruct-2507-q4_K_M inside a Google Colab GPU runtime, independently of any laptop installation. Python sends one structured extraction request per batch. The prompt performs ORGANIZATION and PRODUCT named entity recognition together with event extraction. It requests explicit source names, short descriptions and supporting passage IDs. JSON schema constraints guide the response format [3]. The model uses temperature 0, a fixed seed, an 8,192-token context and a 1,500-token output limit. No separate model-training, teacher-model or LLM-judge stage is used.

## Decision rules and submitted output

The extraction prompt targets explicit named launches, new versions and availability milestones. Future availability and initial sampling remain labelled as such. Financial results, personnel changes, business transactions alone and existing-product adoption do not qualify. Python checks schema, source IDs, product-name occurrence, organization grounding and descriptions of 1-179 characters. For the submitted CSV, ChatGPT checked all 22 unique saved candidates against their cited passages. Five named or distinguishing voltage/version-specified technical product-family rows were retained. This AI-assisted correction is disclosed separately from the original inference and is not independent human validation.

## Execution and results

The completed Colab run selected and processed 100 unique filings from 20 companies, making 135 extraction calls in a recorded pipeline-session time of 7.37 minutes [5]. The original export contained seven provisional rows and 15 candidate flags. Source corrections removed a business sale and existing-product adoption, narrowed a combined Diodes list to PCI Express 6.0 ReDrivers, and recovered an explicitly newly released diode family whose organization check had failed. The submitted five rows come from four filings and preserve future rollout or sampling status. The original export, source decisions, short evidence extracts, manifest and logs accompany the corrected CSV.

| Measure | Recorded value |
|---|---|
| Selected / completed filings | 100 / 100 |
| Companies / extraction model calls | 20 / 135 |
| Original rows / submitted product-family rows | 7 / 5 |
| Recorded pipeline-session time | 7.37 minutes |

## Limitations

Product-family rows are not individual catalogue SKUs or a claim of first-ever public disclosure. Ambiguous or truncated candidates without a clear identity were not guessed. Restricting exhibits and selecting passages can miss releases, and no retained row does not prove that a filing contains no release. No independent precision, recall or human-validation result is claimed. Manual approval is an optional implementation feature. All 100 completed statuses refer to processing within the documented scope, not perfect semantic accuracy.

## Reproducibility and deliverables

The notebook saves source caches, raw model responses, a frozen manifest and batch/filing checkpoints to Drive. The correction script checks the source ZIP SHA-256. A separate filing_results_100.csv contains exactly 100 filing records, including 96 marked No qualifying product extracted. Products from the same filing share one row. This is not a dataset of 100 product announcements; the rubric interpretation remains subject to instructor confirmation. The CSV has exactly company_name, stock_name, filing_time, new_product and product_description; a parallel output separates values with vertical bars. The recorded time excludes model installation/setup and is not a future-runtime guarantee; Colab resources vary [4]. Both CSVs and this report are published at the GitHub URL above. The same URL must be added at the top of the CV; the CV has not been edited here.

## References

[1] SEC. EDGAR Application Programming Interfaces. https://www.sec.gov/edgar/sec-api-documentation

[2] Beautiful Soup. Documentation. https://www.crummy.com/software/BeautifulSoup/bs4/doc/

[3] Ollama. Structured Outputs. https://docs.ollama.com/capabilities/structured-outputs

[4] Google. Colab Frequently Asked Questions. https://research.google.com/colaboratory/faq.html

[5] Chachengwa, C. Completed Colab run and correction audit. Repository data/run_summary.json, data/filing_log.csv, data/manifest.csv, data/products_provisional.csv and data/source_evidence.csv; source archive sec8k_colab_v2.zip.

Web sources accessed November 2, 2026. Results refer to the completed 100-filing Colab run and disclosed AI-assisted source corrections.
