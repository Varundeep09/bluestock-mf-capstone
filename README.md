# Bluestock MF Capstone — Mutual Fund Analytics Platform

Individual capstone project for **Bluestock Fintech**. Builds an end-to-end automated ETL pipeline, SQLite star-schema data warehouse, exploratory data analysis, multi-factor performance/risk scorecard, quantitative risk models (VaR, CVaR, Monte Carlo, Markowitz Frontier), and an interactive 4-page Power BI executive dashboard.

---

## 🏗️ Repository Architecture & Folder Structure

```
bluestock_mf_capstone/
├── data/
│   ├── raw/                      # 10 raw CSVs + 6 live API CSVs (never edited)
│   ├── processed/                # 11 cleaned CSVs + scorecards & quantitative outputs
│   └── db/                       # bluestock_mf.db (SQLite star schema, git-ignored)
├── notebooks/
│   ├── 01_data_ingestion.ipynb          # Raw dataset profiling & verification
│   ├── 02_data_cleaning.ipynb           # Data cleaning & schema alignment
│   ├── 03_eda_analysis.ipynb            # 15+ EDA charts & executive findings
│   ├── 04_performance_analytics.ipynb   # CAGR, Sharpe, Sortino, Alpha, Scorecard
│   └── 05_advanced_analytics.ipynb      # VaR/CVaR, Cohorts, Churn, Recommender, HHI
├── scripts/
│   ├── etl_pipeline.py           # Single master orchestrator (Ingest -> Clean -> DB)
│   ├── live_nav_fetch.py         # Real-time NAV fetcher via mfapi.in
│   ├── compute_metrics.py        # Fund performance, tracking error & scorecard engine
│   ├── advanced_analytics.py     # Quantitative risk, cohorts, churn, and HHI pipeline
│   ├── recommender.py            # Investor risk-profile fund recommendation engine
│   ├── bonus_analytics.py        # Monte Carlo 5Y simulation & Markowitz Efficient Frontier
│   ├── audit_rubric.py           # Automated regression test & rubric self-check suite
│   ├── test_fresh_clone.py       # End-to-end fresh-clone sandbox verification suite
│   ├── validate_fund_codes.py    # AMFI scheme code verification suite
│   ├── data_ingestion.py         # Modular raw ingestion script
│   ├── data_cleaning.py          # Modular data cleaning script
│   ├── load_to_sqlite.py         # Modular SQLite loader script
│   └── generate_eda_charts.py    # 15 publication-grade chart generator
├── sql/
│   ├── schema.sql                # Star schema DDL with PK/FK constraints & indexes
│   └── queries.sql               # 10 business analytical SQL queries
├── dashboard/
│   ├── bluestock_mf.pbix         # Interactive 4-page Power BI dashboard
│   ├── Dashboard.pdf             # Exported multi-page dashboard report
│   └── *.png                     # High-resolution page screenshot exports
├── reports/
│   ├── eda_charts/               # 15 high-res PNG visualization exports
│   ├── top5_funds_vs_benchmarks.png
│   ├── rolling_sharpe_chart.png
│   ├── sector_hhi_chart.png
│   ├── monte_carlo_projections.png
│   ├── efficient_frontier.png
│   ├── Final_Report.pdf          # Final 15–20 page executive research report (Day 7)
│   └── Presentation.pptx         # 12-slide executive presentation (Day 7)
├── data_dictionary.md            # Complete data dictionary for all tables and fields
└── README.md
```

---

## 🚀 Quickstart & Setup

### 1. Environment Setup
```bash
cd bluestock_mf_capstone
python -m venv .venv

# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Run End-to-End Master ETL Pipeline
Execute the single master command to profile raw data, clean all datasets, and populate the SQLite database (`data/db/bluestock_mf.db`):
```bash
python scripts/etl_pipeline.py
```

### 3. Run Analytics & Quantitative Pipelines
```bash
# Compute performance metrics, CAGR, risk ratios & scorecard
python scripts/compute_metrics.py

# Run advanced analytics (VaR, CVaR, cohorts, churn, HHI)
python scripts/advanced_analytics.py

# Run bonus challenges (Monte Carlo 5Y simulation & Markowitz Frontier)
python scripts/bonus_analytics.py

# Test fund recommendation engine
python scripts/recommender.py

# Run QA regression audit suite
python scripts/audit_rubric.py

# Run end-to-end fresh-clone verification test
python scripts/test_fresh_clone.py
```

---

## 🌟 Bonus Challenges Implemented (+10 Marks Each)

* **B3: Monte Carlo 5-Year NAV Projections**: 1,000 geometric Brownian motion simulation paths across Equity, Debt, and Gilt funds with 5th, 50th, and 95th percentile cones ([`reports/monte_carlo_projections.png`](reports/monte_carlo_projections.png)).
* **B4: Markowitz Modern Portfolio Theory & Efficient Frontier**: Mean-variance portfolio optimization using `scipy.optimize` (`SLSQP`) with Maximum Sharpe Ratio and Minimum Volatility portfolio weights along the Capital Allocation Line ([`reports/efficient_frontier.png`](reports/efficient_frontier.png)).

---

## 📌 Disclaimer
Educational capstone project conducted for the Bluestock Mutual Fund Analytics Capstone. Not financial advice.
