"""
Day 6: Advanced Analytics & Risk Analytics Pipeline

Computes:
1. Historical VaR (95%) & CVaR (Expected Shortfall) per scheme -> data/processed/var_cvar_report.csv
2. Rolling 90-day Sharpe ratio across multi-asset funds -> reports/rolling_sharpe_chart.png
3. Investor Cohort Analysis by initial investment year -> data/processed/cohort_analysis.csv
4. SIP Continuity & At-Risk Investor Churn Analysis -> data/processed/sip_continuity.csv
5. Sector Concentration Analysis (Herfindahl-Hirschman Index - HHI) -> data/processed/sector_hhi.csv & reports/sector_hhi_chart.png
"""

from pathlib import Path
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "db" / "bluestock_mf.db"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
REPORTS_DIR = PROJECT_ROOT / "reports"

RISK_FREE_RATE = 0.065
TRADING_DAYS_PER_YEAR = 252

# Set aesthetic charts styling
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.sans-serif"] = "DejaVu Sans"
plt.rcParams["axes.edgecolor"] = "#cccccc"
plt.rcParams["axes.linewidth"] = 0.8


def load_datasets():
    conn = sqlite3.connect(DB_PATH)
    nav_df = pd.read_sql_query("SELECT * FROM fact_nav ORDER BY amfi_code, date", conn)
    fund_df = pd.read_sql_query("SELECT * FROM dim_fund", conn)
    tx_df = pd.read_sql_query("SELECT * FROM fact_transactions", conn)
    port_df = pd.read_sql_query("SELECT * FROM fact_portfolio", conn)
    perf_df = pd.read_sql_query("SELECT * FROM fact_performance", conn)
    conn.close()
    return nav_df, fund_df, tx_df, port_df, perf_df


# =========================================================================
# 1. Historical VaR (95%) and CVaR per Fund
# =========================================================================
def compute_var_cvar(nav_df: pd.DataFrame, fund_df: pd.DataFrame) -> pd.DataFrame:
    print("\n" + "=" * 80)
    print("1. HISTORICAL VaR (95%) AND CVaR (EXPECTED SHORTFALL) CALCULATION")
    print("=" * 80)

    results = []
    for amfi, grp in nav_df.groupby("amfi_code"):
        grp = grp.sort_values("date").copy()
        daily_returns = grp["nav"].pct_change().dropna() * 100.0  # In %
        
        if len(daily_returns) < 50:
            continue

        # 95% Historical VaR (5th percentile of daily return distribution)
        var_95 = float(np.percentile(daily_returns, 5))
        
        # CVaR (Expected Shortfall): Mean of returns at or below VaR threshold
        tail_returns = daily_returns[daily_returns <= var_95]
        cvar_95 = float(tail_returns.mean()) if len(tail_returns) > 0 else var_95

        results.append({
            "amfi_code": str(amfi),
            "var_95_pct": round(var_95, 3),
            "cvar_95_pct": round(cvar_95, 3),
            "std_daily_pct": round(float(daily_returns.std()), 3),
            "worst_day_return_pct": round(float(daily_returns.min()), 3),
        })

    var_df = pd.DataFrame(results)
    var_df = pd.merge(fund_df[["amfi_code", "scheme_name", "fund_house", "category", "plan"]], var_df, on="amfi_code")
    var_df = var_df.sort_values("var_95_pct", ascending=True).reset_index(drop=True)  # Most negative / highest risk first

    out_path = PROCESSED_DIR / "var_cvar_report.csv"
    var_df.to_csv(out_path, index=False)
    print(f"VaR/CVaR report saved -> {out_path.relative_to(PROJECT_ROOT)} ({len(var_df)} schemes)")

    print("\nTop 5 Highest-VaR Funds (Greatest Tail Risk / Largest Potential 1-Day Loss at 95% Confidence):")
    top5_var = var_df.head(5)
    for idx, r in top5_var.iterrows():
        print(f"  {idx+1}. [{r['amfi_code']}] {r['scheme_name'][:45]:45s} | Cat: {r['category']:10s} | VaR (95%): {r['var_95_pct']:6.2f}% | CVaR: {r['cvar_95_pct']:6.2f}%")

    return var_df


# =========================================================================
# 2. Rolling 90-Day Sharpe Ratio for 5 Representative Schemes
# =========================================================================
def generate_rolling_sharpe(nav_df: pd.DataFrame, fund_df: pd.DataFrame):
    print("\n" + "=" * 80)
    print("2. ROLLING 90-DAY SHARPE RATIO ANALYSIS")
    print("=" * 80)

    # 5 Representative schemes across Large Cap, Small Cap, Flexi Cap, Debt, and Liquid
    target_funds = [
        ("119551", "SBI Bluechip (Large Cap)"),
        ("119598", "SBI Small Cap (Small Cap)"),
        ("120843", "Kotak Flexicap (Flexi Cap)"),
        ("100025", "HDFC Short Term Debt (Debt)"),
        ("120507", "ICICI Pru Liquid (Liquid)")
    ]

    piv = nav_df.pivot(index="date", columns="amfi_code", values="nav")
    piv.index = pd.to_datetime(piv.index)
    rf_daily = RISK_FREE_RATE / TRADING_DAYS_PER_YEAR

    fig, ax = plt.subplots(figsize=(14, 7), dpi=300)
    colors = ["#1f77b4", "#e63946", "#2a9d8f", "#e76f51", "#7209b7"]

    for i, (amfi, label) in enumerate(target_funds):
        if amfi not in piv.columns:
            continue
        series = piv[amfi].pct_change().dropna()
        # Rolling 90-day metrics
        roll_mean = series.rolling(90).mean()
        roll_std = series.rolling(90).std()
        roll_sharpe = ((roll_mean - rf_daily) / roll_std) * np.sqrt(TRADING_DAYS_PER_YEAR)
        
        ax.plot(roll_sharpe.index, roll_sharpe, label=label, color=colors[i], linewidth=2.0)

    ax.axhline(0.0, color="#888888", linestyle="--", alpha=0.7, label="Zero Excess Return")
    ax.axhline(1.0, color="#2ca02c", linestyle=":", alpha=0.7, label="Strong Sharpe Benchmark (1.0)")
    ax.set_title("Rolling 90-Day Annualized Sharpe Ratio (2022–2026, Multi-Asset Comparison)", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Date", fontweight="bold")
    ax.set_ylabel("90-Day Rolling Sharpe Ratio", fontweight="bold")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.legend(loc="upper left", frameon=True, fontsize=9.5)
    plt.tight_layout()

    chart_path = REPORTS_DIR / "rolling_sharpe_chart.png"
    plt.savefig(chart_path, dpi=300)
    plt.close()
    print(f"Rolling Sharpe chart exported -> {chart_path.relative_to(PROJECT_ROOT)}")


# =========================================================================
# 3. Investor Cohort Analysis
# =========================================================================
def compute_cohort_analysis(tx_df: pd.DataFrame, fund_df: pd.DataFrame) -> pd.DataFrame:
    print("\n" + "=" * 80)
    print("3. INVESTOR COHORT ANALYSIS")
    print("=" * 80)

    tx_with_fund = pd.merge(tx_df, fund_df[["amfi_code", "category"]], on="amfi_code", how="left")
    tx_with_fund["tx_date"] = pd.to_datetime(tx_with_fund["transaction_date"])

    # First transaction date per investor
    first_tx = tx_with_fund.groupby("investor_id")["tx_date"].min().reset_index()
    first_tx["cohort_year"] = first_tx["tx_date"].dt.year

    # Merge cohort year back into all transactions
    tx_cohort = pd.merge(tx_with_fund, first_tx[["investor_id", "cohort_year"]], on="investor_id")

    cohort_records = []
    for cohort_yr, grp in tx_cohort.groupby("cohort_year"):
        inv_count = grp["investor_id"].nunique()
        total_tx = len(grp)
        sip_tx = grp[grp["transaction_type"] == "SIP"]
        avg_sip = sip_tx["amount_inr"].mean() if len(sip_tx) > 0 else 0.0
        total_invested = grp["amount_inr"].sum()
        total_invested_cr = total_invested / 1e7
        top_cat = grp["category"].mode()[0] if not grp["category"].empty else "Equity"
        avg_income = grp["annual_income_lakh"].mean()

        cohort_records.append({
            "cohort_year": int(cohort_yr),
            "investor_count": inv_count,
            "total_transactions": total_tx,
            "avg_sip_amount_inr": round(float(avg_sip), 2),
            "total_invested_crore": round(float(total_invested_cr), 2),
            "avg_annual_income_lakh": round(float(avg_income), 2),
            "preferred_category": top_cat,
        })

    cohort_df = pd.DataFrame(cohort_records).sort_values("cohort_year").reset_index(drop=True)
    out_path = PROCESSED_DIR / "cohort_analysis.csv"
    cohort_df.to_csv(out_path, index=False)
    print(f"Cohort analysis saved -> {out_path.relative_to(PROJECT_ROOT)}")
    print("\nCohort Breakdown Summary:")
    print(cohort_df.to_string(index=False))
    return cohort_df


# =========================================================================
# 4. SIP Continuity / At-Risk Investor Analysis
# =========================================================================
def compute_sip_continuity(tx_df: pd.DataFrame) -> tuple[pd.DataFrame, float]:
    print("\n" + "=" * 80)
    print("4. SIP CONTINUITY & AT-RISK INVESTOR ANALYSIS")
    print("=" * 80)

    sip_df = tx_df[tx_df["transaction_type"] == "SIP"].copy()
    sip_df["tx_date"] = pd.to_datetime(sip_df["transaction_date"])

    continuity_records = []
    for inv_id, grp in sip_df.groupby("investor_id"):
        grp = grp.sort_values("tx_date")
        sip_count = len(grp)
        
        if sip_count >= 6:
            date_diffs = grp["tx_date"].diff().dt.days.dropna()
            avg_gap = float(date_diffs.mean())
            max_gap = float(date_diffs.max())
            is_at_risk = bool(avg_gap > 35.0)

            continuity_records.append({
                "investor_id": str(inv_id),
                "sip_count": sip_count,
                "avg_gap_days": round(avg_gap, 1),
                "max_gap_days": round(max_gap, 1),
                "is_at_risk": is_at_risk,
            })

    cont_df = pd.DataFrame(continuity_records)
    out_path = PROCESSED_DIR / "sip_continuity.csv"
    cont_df.to_csv(out_path, index=False)

    total_eligible = len(cont_df)
    at_risk_count = int(cont_df["is_at_risk"].sum())
    at_risk_pct = (at_risk_count / total_eligible * 100.0) if total_eligible > 0 else 0.0

    print(f"SIP continuity report saved -> {out_path.relative_to(PROJECT_ROOT)}")
    print(f"Total Eligible SIP Investors (6+ transactions): {total_eligible}")
    print(f"Flagged At-Risk Investors (Avg Gap > 35 Days):    {at_risk_count} ({at_risk_pct:.2f}%)")

    return cont_df, at_risk_pct


# =========================================================================
# 5. Sector Concentration Analysis (HHI)
# =========================================================================
def compute_sector_hhi(port_df: pd.DataFrame, fund_df: pd.DataFrame) -> pd.DataFrame:
    print("\n" + "=" * 80)
    print("5. SECTOR CONCENTRATION ANALYSIS (HERFINDAHL-HIRSCHMAN INDEX - HHI)")
    print("=" * 80)

    hhi_records = []
    for amfi, grp in port_df.groupby("amfi_code"):
        # Sum weights by sector
        sector_weights = grp.groupby("sector")["weight_pct"].sum()
        hhi = float((sector_weights ** 2).sum())
        
        top_sector = sector_weights.idxmax() if not sector_weights.empty else "N/A"
        top_weight = float(sector_weights.max()) if not sector_weights.empty else 0.0
        is_conc = bool(hhi > 2500.0)

        hhi_records.append({
            "amfi_code": str(amfi),
            "top_sector": top_sector,
            "top_sector_weight_pct": round(top_weight, 2),
            "hhi_score": round(hhi, 2),
            "is_concentrated": is_conc,
        })

    hhi_df = pd.DataFrame(hhi_records)
    hhi_df = pd.merge(fund_df[["amfi_code", "scheme_name", "fund_house", "category", "plan"]], hhi_df, on="amfi_code")
    hhi_df = hhi_df.sort_values("hhi_score", ascending=False).reset_index(drop=True)

    out_path = PROCESSED_DIR / "sector_hhi.csv"
    hhi_df.to_csv(out_path, index=False)
    print(f"Sector HHI report saved -> {out_path.relative_to(PROJECT_ROOT)} ({len(hhi_df)} schemes)")

    # Plot HHI Bar Chart
    fig, ax = plt.subplots(figsize=(12, 7), dpi=300)
    top_plot = hhi_df.head(15).copy()
    
    colors = ["#e63946" if x else "#457b9d" for x in top_plot["is_concentrated"]]
    bars = ax.barh(top_plot["scheme_name"].apply(lambda x: x.split(" - ")[0][:28]), top_plot["hhi_score"], color=colors)
    ax.axvline(2500, color="#d62828", linestyle="--", linewidth=1.8, label="Concentration Threshold (HHI = 2500)")
    
    ax.set_title("Top 15 Mutual Funds by Sector Concentration (Herfindahl-Hirschman Index)", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("HHI Score (Sum of Squared Sector Weights)", fontweight="bold")
    ax.legend(loc="lower right", frameon=True)
    plt.gca().invert_yaxis()
    plt.tight_layout()

    chart_path = REPORTS_DIR / "sector_hhi_chart.png"
    plt.savefig(chart_path, dpi=300)
    plt.close()
    print(f"Sector HHI chart exported -> {chart_path.relative_to(PROJECT_ROOT)}")

    conc_funds = hhi_df[hhi_df["is_concentrated"]]
    print(f"\nConcentrated Funds (HHI > 2500): {len(conc_funds)}")
    for _, r in conc_funds.iterrows():
        print(f"  - [{r['amfi_code']}] {r['scheme_name']} -> HHI: {r['hhi_score']} (Top Sector: {r['top_sector']} @ {r['top_sector_weight_pct']}%)")

    return hhi_df


def main():
    print("=" * 80)
    print("DAY 6: ADVANCED ANALYTICS & RISK METRICS ENGINE")
    print("=" * 80)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    nav_df, fund_df, tx_df, port_df, perf_df = load_datasets()

    # 1. VaR & CVaR
    compute_var_cvar(nav_df, fund_df)

    # 2. Rolling Sharpe
    generate_rolling_sharpe(nav_df, fund_df)

    # 3. Cohort Analysis
    compute_cohort_analysis(tx_df, fund_df)

    # 4. SIP Continuity
    compute_sip_continuity(tx_df)

    # 5. Sector HHI
    compute_sector_hhi(port_df, fund_df)

    print("\nDay 6 Advanced Analytics pipeline executed successfully!")


if __name__ == "__main__":
    main()
