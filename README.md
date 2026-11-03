# SEC 8-K Product Announcement Analysis

**Crispen Chachengwa · MS in Financial Technology · University of Central Florida**

A Python and Ollama workflow that extracts named product announcements from SEC Form 8-K filings and associated Exhibit 99 releases. The executed Google Colab notebook produces a five-column CSV and preserves progress between sessions.

[Open in Colab](https://colab.research.google.com/github/criszw-collab/LLM-Document-Analysis/blob/main/notebooks/SEC_8K_Product_Analysis.ipynb) · [Product CSV](data/products.csv) · [Two-page methodology report](reports/SEC_8K_Methodology_Report.pdf)

## Submitted results

| Item | Result |
|---|---|
| Filing date scope | January 1–December 31, 2025 |
| Saved product rows | 100 |
| Companies represented in CSV | 70 |
| Required columns / missing values | Five columns / no blank required values |
| Description length | 55–179 characters |
| Model | `qwen3:4b-instruct-2507-q4_K_M` through Ollama |
| Intended runtime | Google Colab GPU; T4 recommended |

These are saved model extractions, not 100 independently verified announcements. Formatting checks do not measure factual accuracy. The supplied CSV contains mixed-language text, incomplete descriptions and a possible SoloVPE alias duplicate. These limitations are documented in the report; the uploaded notebook and CSV are preserved without manual corrections.

## Repository contents

| Path | Purpose |
|---|---|
| `notebooks/SEC_8K_Product_Analysis.ipynb` | Main executed notebook, including continuation cells and saved outputs |
| `data/products.csv` | Uploaded final 100-row extraction output |
| `reports/SEC_8K_Methodology_Report.pdf` | Uploaded two-page report: methodology, results and limitations |
| `data/validation_summary.json` | Offline structural checks and original file checksums |
| `requirements.txt` | Python packages used by the main notebook |
| `archive/SEC_8K_Fresh_Simple_Package.zip` | Earlier alternative implementation, retained as supplied |

The archive is historical supporting material. Its tests, output and instructions do not establish validation of the main notebook's latest dataset.

## Run in Google Colab

1. Open the notebook using the Colab link above, or upload it through **File → Upload notebook**.
2. Select **Runtime → Change runtime type → GPU**. Use a T4 when available. The notebook checks GPU access; ordinary CPU-only execution is not its configured path.
3. Run the setup cells to install packages, start Ollama inside Colab and load the specified model. The Ollama installation on your personal computer is separate from the Colab environment. No paid model API key is required.
4. Mount your Google Drive and confirm the author/contact details used in SEC request headers.
5. Choose a run mode in the configuration cell. For a **new run**, use `RUN_MODE='fresh'` and an unused `RUN_NAME`. For **continuation**, use `RUN_MODE='resume'` and the same Drive folder containing the original `configuration.json`, checkpoints and manifest.
6. Run the numbered cells in order. Read the notes on continuation and extra-company discovery before running appended continuation cells. Saved outputs in this repository document a previous execution; they do not preload checkpoints into a new runtime.
7. Download the generated CSV and project ZIP from the final cells. Download the executed notebook separately through **File → Download → Download .ipynb**.

The repository does not include the full live Drive checkpoint folder. A CSV alone cannot resume extraction. Resume requires the saved project ZIP or original Drive folder and matching configuration/model digest. The notebook refuses incompatible checkpoints rather than silently mixing configurations.

## Pipeline

1. **Discover:** map tickers to SEC CIKs using `company_tickers.json`; parse the instructor's 8-K Atom feed and supplement historical discovery with SEC submissions JSON.
2. **Read:** download primary 8-K documents and readable numbered Exhibit 99 documents. BeautifulSoup removes HTML markup; pypdf extracts text from readable PDFs.
3. **Retrieve:** select release-related text units and neighboring context. Units are about 900 characters and batches about 9,000 characters. A keyword skip is not proof that a filing contains no announcement.
4. **Extract:** Python queries Ollama for structured JSON. The prompt identifies ORGANIZATION and PRODUCT entities and requests a name, concise description, event type and cited evidence.
5. **Check:** validate JSON, source names/quotes and the 1–179 character description limit. A second check uses the same model, so it is not an independent evaluator.
6. **Save:** checkpoint progress, preserve model responses, log errors and remove repeated normalized names per CIK. Filings without accepted products add no product rows.
7. **Continue:** skip completed filings and expand company discovery when necessary. Export the final product CSV when the pipeline's accepted-row count reaches 100.

## CSV schema

| Column | Meaning |
|---|---|
| `company_name` | SEC filing company name |
| `stock_name` | Company ticker symbol |
| `filing_time` | Filing acceptance timestamp; see notebook metadata for time basis |
| `new_product` | Extracted named product, family, feature or version |
| `product_description` | Model-generated description, fewer than 180 characters |

The target is product rows, not processing-status rows. Failed filings are not padded into this CSV. Explicit future introductions or sampling may be retained; the description should communicate their status. The filename `filing_results_100.csv` from older work is not the submitted product dataset. Use `data/products.csv`.

## Progress, timing and limitations

The notebook stores `checkpoints/`, `responses/`, `source_cache/` and `exports/` under its Drive project folder. Its progress bar counts accepted product entries. Interrupt execution or create `STOP.txt` in that folder to pause; resume with the same settings. Requests may take until their timeout to return.

Runtime depends on GPU availability, SEC responses and the number of batches. A session budget is not a guarantee that 100 entries will be found. Recorded issues include local CPU heating/slowness, SEC timeouts and 503 responses, image-only exhibits and truncated model JSON. One session's duration is not the total multi-session runtime.

Keyword retrieval, parsing errors and model decisions can miss announcements or accept incorrect ones. Normalized-name deduplication does not resolve all aliases. Precision and recall have not been measured against independent reference labels. Further source-based validation is needed before using this dataset as research-grade ground truth.

## Checks performed before this commit

- Parsed the uploaded CSV: 100 rows, 70 tickers and the exact five-column schema.
- Checked nonempty required fields, 1–179 character descriptions and exact ticker/name duplicates.
- Parsed the uploaded notebook and compiled ordinary Python cells; no saved exception outputs were present.
- Confirmed the supplied report has two pages and the supporting ZIP can be read.

These are offline checks. SEC retrieval and Ollama inference were not rerun during repository preparation. Python package versions are not a locked environment; use the notebook's model digest/configuration checks when resuming.

## Sources and submission

- [SEC ticker-to-CIK mapping](https://www.sec.gov/files/company_tickers.json)
- [Instructor's Atom endpoint example](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=855658&type=8-K&count=100&output=atom)
- [SEC developer resources](https://www.sec.gov/developer)
- [SEC submissions example](https://data.sec.gov/submissions/CIK0000855658.json)
- [Ollama](https://ollama.com/)

Submit the main notebook, `data/products.csv` and the methodology PDF. Repository URL: **https://github.com/criszw-collab/LLM-Document-Analysis**. Include this URL in the report and at the top of your CV, as required by the assignment. The uploaded report retains its historical note about an unavailable older CSV path; the current product CSV is linked above.

## License

Code and documentation are provided under the [MIT License](LICENSE). SEC source documents and third-party software remain subject to their own applicable terms. The dataset contains model-generated research output and carries no accuracy guarantee.
