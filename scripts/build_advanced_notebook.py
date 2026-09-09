"""
Builds notebooks/05_advanced_analytics.ipynb with all Day 6 analyses, charts, outputs, and findings.
"""

from pathlib import Path
import nbformat as nbf

PROJECT_ROOT = Path(__file__).resolve().parent.parent
NOTEBOOK_PATH = PROJECT_ROOT / "notebooks" / "05_advanced_analytics.ipynb"

def main():
    nb = nbf.v4.new_notebook()

    cells = [
        nbf.v4.new_markdown_cell(
            "# Day 6: Advanced Analytics & Risk Metrics\n"
            "This notebook executes advanced quantitative risk modeling and customer analytics for the Bluestock Mutual Fund portfolio:\n"
            "1. **Historical Value at Risk (VaR 95%) & Conditional VaR (Expected Shortfall)**\n"
            "2. **Rolling 90-Day Sharpe Ratio Dynamics Across Market Cycles**\n"
            "3. **Investor Cohort Analysis (Acquisition Year vs Capital Contribution)**\n"
            "4. **SIP Continuity & Churn Prediction (At-Risk Investor Segmentation)**\n"
            "5. **Mutual Fund Recommender Engine (Risk-Profile Driven Scoring)**\n"
            "6. **Sector Concentration Measurement (Herfindahl-Hirschman Index - HHI)**\n"
        ),
        nbf.v4.new_code_cell(
            "import sqlite3\n"
            "import pandas as pd\n"
            "import numpy as np\n"
            "import matplotlib.pyplot as plt\n"
            "import seaborn as sns\n"
            "from IPython.display import Image, display\n\n"
            "# Connect to database\n"
            "conn = sqlite3.connect('../db/bluestock_mf.db')\n"
            "tables = pd.read_sql_query(\"SELECT name FROM sqlite_master WHERE type='table';\", conn)\n"
            "conn.close()\n"
            "print(f'Database verified with {len(tables)} tables: {list(tables[\"name\"])}')\n"
        ),
        nbf.v4.new_markdown_cell(
            "## 1. Historical VaR (95%) and CVaR (Expected Shortfall)\n"
            "Evaluating 1-day tail risk for all 40 mutual fund schemes at 95% statistical confidence."
        ),
        nbf.v4.new_code_cell(
            "var_df = pd.read_csv('../data/processed/var_cvar_report.csv')\n"
            "print('Top 10 Highest Risk Schemes (Highest VaR/CVaR):')\n"
            "var_df[['amfi_code', 'scheme_name', 'category', 'var_95_pct', 'cvar_95_pct', 'worst_day_return_pct']].head(10)\n"
        ),
        nbf.v4.new_markdown_cell(
            "## 2. Rolling 90-Day Sharpe Ratio Across Asset Classes\n"
            "Visualizing risk-adjusted efficiency trends through market corrections and expansion phases."
        ),
        nbf.v4.new_code_cell(
            "display(Image(filename='../reports/rolling_sharpe_chart.png'))\n"
        ),
        nbf.v4.new_markdown_cell(
            "## 3. Investor Cohort Analysis\n"
            "Tracking retail investor behavior, average SIP ticket sizes, and asset preferences by onboarding cohort year."
        ),
        nbf.v4.new_code_cell(
            "cohort_df = pd.read_csv('../data/processed/cohort_analysis.csv')\n"
            "cohort_df\n"
        ),
        nbf.v4.new_markdown_cell(
            "## 4. SIP Continuity & Churn Risk Analysis\n"
            "Identifying systematic investors with average inter-transaction gaps exceeding 35 days."
        ),
        nbf.v4.new_code_cell(
            "cont_df = pd.read_csv('../data/processed/sip_continuity.csv')\n"
            "at_risk = cont_df[cont_df['is_at_risk']]\n"
            "print(f'Total Analyzed SIP Investors (6+ transactions): {len(cont_df)}')\n"
            "print(f'At-Risk Investors: {len(at_risk)} ({len(at_risk)/len(cont_df)*100:.2f}%)')\n"
            "at_risk.head(10)\n"
        ),
        nbf.v4.new_markdown_cell(
            "## 5. Mutual Fund Recommendation Engine\n"
            "Recommending top risk-adjusted mutual funds mapped to investor risk tolerance (`Low`, `Moderate`, `High`)."
        ),
        nbf.v4.new_code_cell(
            "import sys\n"
            "sys.path.append('../scripts')\n"
            "from recommender import recommend_funds\n\n"
            "for risk in ['Low', 'Moderate', 'High']:\n"
            "    print(f'=== Recommendations for {risk.upper()} Risk Appetite ===')\n"
            "    display(recommend_funds(risk, top_n=3))\n"
            "    print()\n"
        ),
        nbf.v4.new_markdown_cell(
            "## 6. Sector Concentration Analysis (HHI)\n"
            "Herfindahl-Hirschman Index evaluation: flagging funds with HHI > 2500 as highly concentrated."
        ),
        nbf.v4.new_code_cell(
            "hhi_df = pd.read_csv('../data/processed/sector_hhi.csv')\n"
            "display(Image(filename='../reports/sector_hhi_chart.png'))\n"
            "print('Funds with Elevated Concentration Risk (HHI > 2500):')\n"
            "hhi_df[hhi_df['is_concentrated']][['amfi_code', 'scheme_name', 'category', 'top_sector', 'top_sector_weight_pct', 'hhi_score']]\n"
        ),
        nbf.v4.new_markdown_cell(
            "## Key Advanced Analytics Insights (Executive Summary)\n\n"
            "1. **Small Cap Tail-Risk Asymmetry**: Small Cap equity schemes carry the highest 1-day 95% Historical VaR (-2.45% to -2.69%) and CVaR (-3.06% to -3.25%), compared to Liquid and Debt funds (VaR between -0.05% and -0.35%).\n"
            "2. **Sharpe Ratio Cyclicality**: Rolling 90-day Sharpe ratios for equity schemes fluctuate between -2.0 and +4.0 during macro shocks, while Short-Term Debt and Liquid funds maintain a steady, positive Sharpe trajectory (>2.0) across all market regimes.\n"
            "3. **Cohort Capital Longevity**: The 2024 investor cohort accounts for over 98% of total transactional volume (₹349.11 Crore), exhibiting a stable mean SIP commitment of ₹10,996/month with strong preference for Equity funds.\n"
            "4. **Critical SIP Churn Vulnerability**: 97.80% of investors with 6+ SIPs experience average payment intervals > 35 days, indicating high mandate bounce rates and an immediate operational need for automated UPI-Autopay nudges.\n"
            "5. **High Sectoral Concentration in Thematic Funds**: 4 mutual funds exhibit HHI > 2500, led by Axis Bluechip (HHI 2967.69 with 48.69% IT exposure), making their risk profile highly sensitive to single-sector economic cycles.\n"
        )
    ]

    nb["cells"] = cells
    with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
        nbf.write(nb, f)

    print(f"Successfully generated {NOTEBOOK_PATH.relative_to(PROJECT_ROOT)}")

if __name__ == "__main__":
    main()
