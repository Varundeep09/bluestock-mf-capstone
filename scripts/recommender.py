"""
Day 6: Mutual Fund Recommender Engine

Provides fund recommendations based on investor risk appetite (Low / Moderate / High),
ranking by risk-adjusted efficiency (Sharpe ratio and Composite Fund Scorecard).
"""

from pathlib import Path
import sqlite3
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "db" / "bluestock_mf.db"
SCORECARD_PATH = PROJECT_ROOT / "data" / "processed" / "fund_scorecard.csv"

# Risk mapping from user appetite to database risk profiles and asset categories
RISK_MAP = {
    "low": {
        "label": "Low Risk (Capital Preservation & Stability)",
        "categories": ["Debt", "Liquid", "Gilt"],
        "risk_grades": ["Low", "Low to Moderate", "Moderate"],
    },
    "moderate": {
        "label": "Moderate Risk (Balanced Growth & Moderate Volatility)",
        "categories": ["Large Cap", "Flexi Cap", "Large & Mid Cap", "Hybrid"],
        "risk_grades": ["Moderate", "Moderately High"],
    },
    "high": {
        "label": "High Risk (Aggressive Capital Appreciation)",
        "categories": ["Small Cap", "Mid Cap", "Sectoral/Thematic", "Equity"],
        "risk_grades": ["High", "Very High"],
    }
}


def get_fund_data() -> pd.DataFrame:
    if SCORECARD_PATH.exists():
        return pd.read_csv(SCORECARD_PATH)
    
    conn = sqlite3.connect(DB_PATH)
    query = """
    SELECT f.amfi_code, f.scheme_name, f.fund_house, f.category, f.plan,
           f.risk_category, f.expense_ratio_pct,
           p.return_3yr_pct, p.sharpe_ratio, p.sortino_ratio, p.alpha, p.max_drawdown_pct
    FROM dim_fund f
    JOIN fact_performance p ON f.amfi_code = p.amfi_code
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def recommend_funds(risk_appetite: str = "Moderate", top_n: int = 3) -> pd.DataFrame:
    """
    Recommends top N mutual funds based on investor risk tolerance.
    
    Parameters:
        risk_appetite: 'Low', 'Moderate', or 'High'
        top_n: Number of recommendations to return (default 3)
        
    Returns:
        pd.DataFrame containing top recommended funds with key metrics
    """
    risk_key = risk_appetite.strip().lower()
    if risk_key not in RISK_MAP:
        raise ValueError(f"Invalid risk appetite '{risk_appetite}'. Choose from 'Low', 'Moderate', or 'High'.")

    profile = RISK_MAP[risk_key]
    df = get_fund_data()

    # Filter by category or risk category
    filtered = df[
        df["category"].str.lower().isin([c.lower() for c in profile["categories"]]) |
        df["scheme_name"].str.contains("|".join(profile["categories"]), case=False, na=False)
    ].copy()

    # Fallback to full dataset if category filter is too strict
    if len(filtered) < top_n:
        filtered = df.copy()

    # Rank primarily by Sharpe ratio, tie-break by 3yr return and composite score if present
    sort_cols = ["sharpe_ratio", "return_3yr_pct"]
    if "composite_score" in filtered.columns:
        sort_cols = ["composite_score", "sharpe_ratio"]
        
    recommended = filtered.sort_values(by=sort_cols, ascending=False).head(top_n).reset_index(drop=True)
    
    cols_to_display = [
        "amfi_code", "scheme_name", "category", "plan",
        "return_3yr_pct", "sharpe_ratio", "alpha", "expense_ratio_pct"
    ]
    if "composite_score" in recommended.columns:
        cols_to_display.append("composite_score")
        
    return recommended[[c for c in cols_to_display if c in recommended.columns]]


def demo():
    print("=" * 75)
    print("BLUESTOCK MUTUAL FUND RECOMMENDER ENGINE — DEMO")
    print("=" * 75)

    for appetite in ["Low", "Moderate", "High"]:
        profile = RISK_MAP[appetite.lower()]
        print(f"\n>>> Investor Risk Appetite: {appetite.upper()} [{profile['label']}]")
        print("-" * 75)
        recs = recommend_funds(appetite, top_n=3)
        print(recs.to_string(index=False))


if __name__ == "__main__":
    demo()
