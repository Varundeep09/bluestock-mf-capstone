# Bluestock MF Capstone — Mutual Fund Analytics Platform

Individual capstone project for Bluestock Fintech. Builds an end-to-end
ETL pipeline, SQLite star-schema database, EDA, performance/risk
analytics, and a 4-page Power BI dashboard on 10 provided mutual fund
datasets plus live NAV data from mfapi.in.

## Project status
This repo currently contains the **project scaffold** only (folders,
starter scripts, schema, requirements). The 10 provided CSVs and the
actual analysis/dashboard/report still need to be added — see
`SETUP_CHECKLIST.md`.

## Folder structure
```
data/raw/          Original CSVs exactly as provided (never edited)
data/processed/    Cleaned/derived CSVs produced by our scripts
db/                bluestock_mf.db (SQLite, git-ignored)
notebooks/         01_data_ingestion ... 05_advanced_analytics
scripts/           etl / fetch / validate / metrics Python scripts
sql/               schema.sql, queries.sql
dashboard/         Power BI .pbix file
reports/           Final_Report.pdf, Presentation.pptx
```

## Setup
```bash
cd bluestock_mf_capstone
python -m venv .venv

# Windows
.\.venv\Scripts\Activate.ps1
# macOS/Linux
source .venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Running the Day 1 scripts
1. Put the 10 provided CSVs into `data/raw/` (unchanged filenames).
2. `python scripts/data_ingestion.py` — profiles all 10 datasets (shape,
   dtypes, nulls, preview).
3. `python scripts/live_nav_fetch.py` — pulls live NAV history for
   HDFC Top 100 + 5 more schemes from mfapi.in, saves to `data/raw/`.
4. `python scripts/validate_fund_codes.py` — confirms every fund in
   `01_fund_master.csv` has matching NAV records in `02_nav_history.csv`.

## Data authenticity note
AMFI codes, fund names, expense ratios and AUM figures are real,
publicly published data. NAV values are anchored to real historical
values. Investor transaction data (`08_investor_transactions.csv`) is
synthetically generated using realistic demographic/geographic
distributions. This is disclosed in the final report's Limitations
section.

## License / purpose
Educational capstone project. Not financial advice.
