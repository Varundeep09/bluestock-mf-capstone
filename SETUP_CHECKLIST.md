# Setup Checklist

## Right now
- [x] Download the 10 CSVs from Bluestock Workspace → Capstone Project →
      Project Documents → Datasets Files → BF Capstone
- [x] Place them, unrenamed, into `data/raw/`
- [x] Create virtual environment and `pip install -r requirements.txt`
- [x] Run `python scripts/data_ingestion.py` — paste/share the output
- [x] Run `python scripts/live_nav_fetch.py`
- [x] Run `python scripts/validate_fund_codes.py`
- [x] `git init`, `git add .`, `git commit -m "Day 1: Data ingestion complete"`
- [x] Create the GitHub repo and push

## Once data_ingestion.py output is reviewed
- [x] Confirm real column names against `sql/schema.sql` — adjust if needed
- [x] Build `02_data_cleaning.ipynb` / cleaning logic into `data/processed/`
- [x] Load cleaned data into `db/bluestock_mf.db` via schema.sql
- [x] Run and extend `sql/queries.sql` to 10 queries
- [x] Write `data_dictionary.md`

## Then, per the workspace due dates
- [x] Sep 5 — Data cleaning + SQL DB design complete
- [x] Sep 6 — Day 1 ETL fully committed
- [x] Sep 8 — Fund performance analytics (CAGR, Sharpe, Sortino, Alpha, Beta, Max DD)
- [x] Sep 10 — EDA (15+ charts) and Power BI dashboard (4 pages)
- [x] Sep 13 — Advanced analytics (VaR/CVaR, rolling Sharpe, cohorts, recommender, HHI)
- [x] Sep 15 — Rubric self-check against all 7 deliverables
- [ ] Sep 16 — Final PDF report (15–20 pages) + 12-slide PPT + clean GitHub push
