"""
Day 3 - Exploratory Data Analysis (EDA) Visualization Script

Generates 15 publication-grade financial charts and exports them to reports/eda_charts/.
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
EDA_DIR = PROJECT_ROOT / "reports" / "eda_charts"
SCORECARD_PATH = PROJECT_ROOT / "data" / "processed" / "fund_scorecard.csv"

# Set global aesthetic styling
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.sans-serif"] = "DejaVu Sans"
plt.rcParams["axes.edgecolor"] = "#cccccc"
plt.rcParams["axes.linewidth"] = 0.8


def load_db():
    conn = sqlite3.connect(DB_PATH)
    nav_df = pd.read_sql_query("SELECT * FROM fact_nav", conn)
    fund_df = pd.read_sql_query("SELECT * FROM dim_fund", conn)
    aum_df = pd.read_sql_query("SELECT * FROM fact_aum", conn)
    sip_df = pd.read_sql_query("SELECT * FROM fact_sip_industry", conn)
    cat_df = pd.read_sql_query("SELECT * FROM fact_category_inflows", conn)
    tx_df = pd.read_sql_query("SELECT * FROM fact_transactions", conn)
    folio_df = pd.read_sql_query("SELECT * FROM fact_folio_count", conn)
    port_df = pd.read_sql_query("SELECT * FROM fact_portfolio", conn)
    perf_df = pd.read_sql_query("SELECT * FROM fact_performance", conn)
    conn.close()
    
    scorecard_df = pd.read_csv(SCORECARD_PATH) if SCORECARD_PATH.exists() else None
    return nav_df, fund_df, aum_df, sip_df, cat_df, tx_df, folio_df, port_df, perf_df, scorecard_df


def generate_charts():
    EDA_DIR.mkdir(parents=True, exist_ok=True)
    nav_df, fund_df, aum_df, sip_df, cat_df, tx_df, folio_df, port_df, perf_df, scorecard_df = load_db()

    print("Generating EDA charts...")

    # =========================================================================
    # Chart 1: NAV Trends for All 40 Schemes (2022-2026) with Corrections
    # =========================================================================
    fig, ax = plt.subplots(figsize=(14, 7), dpi=300)
    nav_piv = nav_df.pivot(index="date", columns="amfi_code", values="nav")
    nav_piv.index = pd.to_datetime(nav_piv.index)
    
    # Normalize to base 100 for visual comparison
    norm_nav = (nav_piv / nav_piv.iloc[0]) * 100.0
    for col in norm_nav.columns:
        ax.plot(norm_nav.index, norm_nav[col], color="#2b5c8f", alpha=0.25, linewidth=1.0)

    # Highlight median equity trend
    median_trend = norm_nav.median(axis=1)
    ax.plot(norm_nav.index, median_trend, color="#e63946", linewidth=2.5, label="Industry Median NAV Trajectory")

    # Annotations of corrections
    ax.axvspan(pd.to_datetime("2022-01-01"), pd.to_datetime("2022-06-30"), color="#ffb703", alpha=0.2, label="2022 Global Rate-Hike Correction")
    ax.axvspan(pd.to_datetime("2024-05-15"), pd.to_datetime("2024-06-15"), color="#fb8500", alpha=0.2, label="Mid-2024 General Election Volatility")

    ax.set_title("1. NAV Trajectory Across All 40 Schemes (2022–2026, Rebased to 100)", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Year", fontweight="bold")
    ax.set_ylabel("Normalized NAV (Base = 100)", fontweight="bold")
    ax.legend(loc="upper left", frameon=True, fontsize=9)
    plt.tight_layout()
    plt.savefig(EDA_DIR / "chart_01_nav_trends_all_funds.png", dpi=300)
    plt.close()

    # =========================================================================
    # Chart 2: AUM Growth by Fund House (2022-2025)
    # =========================================================================
    fig, ax = plt.subplots(figsize=(13, 6), dpi=300)
    aum_df["year"] = pd.to_datetime(aum_df["date"]).dt.year
    latest_aum_annual = aum_df.groupby(["year", "fund_house"])["aum_lakh_crore"].max().unstack()
    
    colors = ["#264653", "#2a9d8f", "#e76f51", "#f4a261", "#e9c46a", "#457b9d", "#1d3557", "#8d99ae"]
    latest_aum_annual.plot(kind="bar", ax=ax, width=0.8, colormap="tab10")
    ax.set_title("2. Annual AUM Growth by Top Asset Management Companies (2022–2025)", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Year", fontweight="bold")
    ax.set_ylabel("Peak AUM (₹ Lakh Crore)", fontweight="bold")
    ax.legend(title="Fund House", bbox_to_anchor=(1.02, 1), loc="upper left", frameon=True, fontsize=8.5)
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(EDA_DIR / "chart_02_aum_growth_fund_houses.png", dpi=300)
    plt.close()

    # =========================================================================
    # Chart 3: Monthly SIP Inflow Time Series (Jan 2022 - Dec 2025)
    # =========================================================================
    fig, ax = plt.subplots(figsize=(13, 6), dpi=300)
    sip_sorted = sip_df.sort_values("month").copy()
    sip_sorted["date_dt"] = pd.to_datetime(sip_sorted["month"] + "-01")
    
    ax.plot(sip_sorted["date_dt"], sip_sorted["sip_inflow_crore"], marker="o", color="#1d3557", linewidth=2.2, label="Monthly SIP Inflow (₹ Cr)")
    
    # Peak Month annotation
    peak_idx = sip_sorted["sip_inflow_crore"].idxmax()
    peak_val = sip_sorted.loc[peak_idx, "sip_inflow_crore"]
    peak_date = sip_sorted.loc[peak_idx, "date_dt"]
    ax.annotate(f"All-Time Peak: ₹{peak_val:,.0f} Cr\n({peak_date.strftime('%b %Y')})",
                xy=(peak_date, peak_val), xytext=(peak_date - pd.Timedelta(days=250), peak_val - 3000),
                arrowprops=dict(arrowstyle="->", color="#e63946", lw=1.8),
                fontweight="bold", color="#e63946", bbox=dict(boxstyle="round,pad=0.3", fc="#f8f9fa", ec="#e63946"))

    ax.set_title("3. Mutual Fund Industry Monthly SIP Inflows (Jan 2022 – Dec 2025)", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Month", fontweight="bold")
    ax.set_ylabel("SIP Inflows (₹ Crore)", fontweight="bold")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig(EDA_DIR / "chart_03_monthly_sip_inflows.png", dpi=300)
    plt.close()

    # =========================================================================
    # Chart 4: Category-Wise Net Inflow Heatmap
    # =========================================================================
    fig, ax = plt.subplots(figsize=(13, 7), dpi=300)
    cat_pivot = cat_df.pivot(index="category", columns="month", values="net_inflow_crore")
    sns.heatmap(cat_pivot, cmap="YlGnBu", annot=True, fmt=",.0f", cbar_kws={"label": "Net Inflow (₹ Crore)"}, ax=ax)
    ax.set_title("4. Category-Wise Monthly Net Inflow Heatmap (₹ Crore)", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Reporting Month", fontweight="bold")
    ax.set_ylabel("Mutual Fund Category", fontweight="bold")
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig(EDA_DIR / "chart_04_category_inflows_heatmap.png", dpi=300)
    plt.close()

    # =========================================================================
    # Chart 5: Investor Demographics & SIP Ticket Size Distribution
    # =========================================================================
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=300)
    
    # Pie chart of age group
    age_counts = tx_df["age_group"].value_counts()
    colors_pie = ["#2a9d8f", "#e76f51", "#f4a261", "#264653", "#e9c46a"]
    ax1.pie(age_counts, labels=age_counts.index, autopct="%1.1f%%", startangle=140, colors=colors_pie, wedgeprops=dict(width=0.6, edgecolor="w"))
    ax1.set_title("Investor Distribution by Age Group", fontsize=12, fontweight="bold")

    # Boxplot of SIP amount by age group
    sip_tx = tx_df[tx_df["transaction_type"] == "SIP"].copy()
    sns.boxplot(data=sip_tx, x="age_group", y="amount_inr", ax=ax2, palette="Set2", showmeans=True)
    ax2.set_title("Monthly SIP Ticket Size by Age Bracket", fontsize=12, fontweight="bold")
    ax2.set_xlabel("Age Group", fontweight="bold")
    ax2.set_ylabel("SIP Amount (INR)", fontweight="bold")

    plt.suptitle("5. Investor Demographics & Systematic Investment Ticket Size Profile", fontsize=13, fontweight="bold", y=1.02)
    plt.tight_layout()
    plt.savefig(EDA_DIR / "chart_05_investor_demographics_sip.png", dpi=300)
    plt.close()

    # =========================================================================
    # Chart 6: Geographic Distribution & City Tier Split (T30 vs B30)
    # =========================================================================
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=300, gridspec_kw={"width_ratios": [1.6, 1]})
    
    state_vol = tx_df.groupby("state")["amount_inr"].sum().sort_values(ascending=True) / 1e7  # In Crore
    ax1.barh(state_vol.index, state_vol.values, color="#457b9d", edgecolor="none")
    ax1.set_title("Capital Inflow by Indian State (₹ Crore)", fontsize=12, fontweight="bold")
    ax1.set_xlabel("Gross Transaction Value (₹ Crore)", fontweight="bold")

    tier_vol = tx_df.groupby("city_tier")["amount_inr"].sum()
    ax2.pie(tier_vol, labels=tier_vol.index, autopct="%1.1f%%", colors=["#2a9d8f", "#e76f51"], startangle=90, wedgeprops=dict(width=0.6, edgecolor="w"))
    ax2.set_title("Geographic Split: T30 vs B30 Cities", fontsize=12, fontweight="bold")

    plt.suptitle("6. Geographic Penetration & Urban vs Semi-Urban Flow Dynamics", fontsize=13, fontweight="bold", y=1.02)
    plt.tight_layout()
    plt.savefig(EDA_DIR / "chart_06_geographic_distribution_t30_b30.png", dpi=300)
    plt.close()

    # =========================================================================
    # Chart 7: Folio Count Growth by Asset Class (2022-2025)
    # =========================================================================
    fig, ax = plt.subplots(figsize=(13, 6), dpi=300)
    folio_sorted = folio_df.sort_values("month").copy()
    folio_sorted["date_dt"] = pd.to_datetime(folio_sorted["month"] + "-01")

    ax.plot(folio_sorted["date_dt"], folio_sorted["total_folios_crore"], label="Total Folios (Cr)", color="#1d3557", linewidth=2.8, marker="o")
    ax.plot(folio_sorted["date_dt"], folio_sorted["equity_folios_crore"], label="Equity Folios (Cr)", color="#2a9d8f", linewidth=2.2, linestyle="--")
    ax.plot(folio_sorted["date_dt"], folio_sorted["debt_folios_crore"], label="Debt Folios (Cr)", color="#e76f51", linewidth=2.0, linestyle=":")
    ax.plot(folio_sorted["date_dt"], folio_sorted["hybrid_folios_crore"], label="Hybrid Folios (Cr)", color="#f4a261", linewidth=2.0, linestyle="-.")

    ax.set_title("7. Industry Folio Expansion by Asset Class (2022–2025)", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Month", fontweight="bold")
    ax.set_ylabel("Investor Folios (Crore)", fontweight="bold")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.legend(loc="upper left", frameon=True)
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig(EDA_DIR / "chart_07_folio_count_growth.png", dpi=300)
    plt.close()

    # =========================================================================
    # Chart 8: Correlation Matrix Heatmap of Representative Schemes
    # =========================================================================
    fig, ax = plt.subplots(figsize=(11, 9), dpi=300)
    # Pick 10 representative schemes across Large Cap, Small Cap, Flexi Cap, Debt, Gilt, Liquid
    sample_amfis = [
        "119551", "125497", "119092", "119598", "118634",
        "120843", "102887", "119120", "120507", "100025"
    ]
    sample_nav = nav_df[nav_df["amfi_code"].isin(sample_amfis)].pivot(index="date", columns="amfi_code", values="nav")
    # Rename columns to scheme short names
    name_map = fund_df.set_index("amfi_code")["scheme_name"].to_dict()
    sample_nav.columns = [name_map.get(c, c).split(" - ")[0] for c in sample_nav.columns]
    
    returns_corr = sample_nav.pct_change().dropna().corr()
    sns.heatmap(returns_corr, cmap="coolwarm", annot=True, fmt=".2f", vmin=-0.2, vmax=1.0, ax=ax, cbar_kws={"label": "Pearson Correlation"})
    ax.set_title("8. Daily Return Correlation Matrix Across Representative Asset Classes", fontsize=13, fontweight="bold", pad=12)
    plt.xticks(rotation=45, ha="right", fontsize=9)
    plt.yticks(rotation=0, fontsize=9)
    plt.tight_layout()
    plt.savefig(EDA_DIR / "chart_08_correlation_matrix_returns.png", dpi=300)
    plt.close()

    # =========================================================================
    # Chart 9: Sector Allocation Donut Chart Across Portfolios
    # =========================================================================
    fig, ax = plt.subplots(figsize=(9, 7), dpi=300)
    sector_alloc = port_df.groupby("sector")["market_value_cr"].sum().sort_values(ascending=False)
    top_sectors = sector_alloc.head(6)
    other_sectors = pd.Series({"Others": sector_alloc.iloc[6:].sum()})
    final_sectors = pd.concat([top_sectors, other_sectors])

    ax.pie(final_sectors, labels=final_sectors.index, autopct="%1.1f%%", startangle=140,
           colors=sns.color_palette("mako", len(final_sectors)), wedgeprops=dict(width=0.55, edgecolor="w"))
    ax.set_title("9. Sector Allocation & Exposure Across All Mutual Fund Portfolios", fontsize=13, fontweight="bold", pad=12)
    plt.tight_layout()
    plt.savefig(EDA_DIR / "chart_09_sector_allocation_donut.png", dpi=300)
    plt.close()

    # =========================================================================
    # Chart 10: Transaction Type Breakdown (Count & Volume)
    # =========================================================================
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 6), dpi=300)
    tx_summary = tx_df.groupby("transaction_type").agg(
        tx_count=("amount_inr", "count"),
        total_vol=("amount_inr", "sum")
    )
    tx_summary["total_vol_cr"] = tx_summary["total_vol"] / 1e7

    # Count Donut
    ax1.pie(tx_summary["tx_count"], labels=tx_summary.index, autopct="%1.1f%%", startangle=90,
            colors=["#2a9d8f", "#e76f51", "#f4a261"], wedgeprops=dict(width=0.55, edgecolor="w"))
    ax1.set_title("Transaction Count Share (%)", fontsize=12, fontweight="bold")

    # Volume Bar
    sns.barplot(x=tx_summary.index, y=tx_summary["total_vol_cr"], ax=ax2, palette=["#2a9d8f", "#e76f51", "#f4a261"])
    ax2.set_title("Gross Capital Flow Volume (₹ Crore)", fontsize=12, fontweight="bold")
    ax2.set_ylabel("Volume (₹ Crore)", fontweight="bold")
    ax2.set_xlabel("Transaction Mode", fontweight="bold")

    plt.suptitle("10. Retail Investor Transaction Type Segmentation (Activity vs Volume)", fontsize=13, fontweight="bold", y=1.02)
    plt.tight_layout()
    plt.savefig(EDA_DIR / "chart_10_transaction_type_split.png", dpi=300)
    plt.close()

    # =========================================================================
    # Chart 11: Expense Ratio Distribution by Category
    # =========================================================================
    fig, ax = plt.subplots(figsize=(11, 6), dpi=300)
    sns.boxplot(data=fund_df, x="category", y="expense_ratio_pct", hue="plan", palette="Set1", ax=ax)
    ax.set_title("11. Total Expense Ratio (TER %) Distribution by Asset Class and Plan", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Category", fontweight="bold")
    ax.set_ylabel("Expense Ratio (%)", fontweight="bold")
    ax.legend(title="Plan Type", frameon=True)
    plt.tight_layout()
    plt.savefig(EDA_DIR / "chart_11_expense_ratio_by_category.png", dpi=300)
    plt.close()

    # =========================================================================
    # Chart 12: KYC Status Distribution Across Investors
    # =========================================================================
    fig, ax = plt.subplots(figsize=(8, 6), dpi=300)
    kyc_counts = tx_df["kyc_status"].value_counts()
    bars = ax.bar(kyc_counts.index, kyc_counts.values, color=["#2a9d8f", "#e76f51"], width=0.5)
    ax.set_title("12. Investor KYC Compliance Status Breakdown", fontsize=13, fontweight="bold", pad=12)
    ax.set_ylabel("Number of Transactions", fontweight="bold")
    for b in bars:
        height = b.get_height()
        ax.text(b.get_x() + b.get_width()/2., height + 400, f"{height:,} ({height/len(tx_df)*100:.1f}%)", ha="center", va="bottom", fontweight="bold")
    plt.tight_layout()
    plt.savefig(EDA_DIR / "chart_12_kyc_status_distribution.png", dpi=300)
    plt.close()

    # =========================================================================
    # Chart 13: Payment Mode Distribution
    # =========================================================================
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    pay_counts = tx_df["payment_mode"].value_counts()
    sns.barplot(x=pay_counts.index, y=pay_counts.values, palette="viridis", ax=ax)
    ax.set_title("13. Investor Payment Method Adoption & Digital Channel Share", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Payment Channel", fontweight="bold")
    ax.set_ylabel("Transaction Count", fontweight="bold")
    for i, v in enumerate(pay_counts.values):
        ax.text(i, v + 300, f"{v:,} ({v/len(tx_df)*100:.1f}%)", ha="center", fontweight="bold")
    plt.tight_layout()
    plt.savefig(EDA_DIR / "chart_13_payment_mode_distribution.png", dpi=300)
    plt.close()

    # =========================================================================
    # Chart 14: Scatter Plot: 3Y Return vs Sharpe Ratio by Category & AUM
    # =========================================================================
    fig, ax = plt.subplots(figsize=(12, 7), dpi=300)
    if scorecard_df is not None:
        plot_df = scorecard_df.copy()
    else:
        plot_df = perf_df.copy()

    sns.scatterplot(
        data=plot_df, x="return_3yr_pct", y="sharpe_ratio", hue="category",
        size="aum_crore", sizes=(50, 450), palette="tab10", alpha=0.85, ax=ax
    )
    ax.axhline(1.0, color="#888888", linestyle="--", alpha=0.6, label="Benchmark Sharpe = 1.0")
    ax.set_title("14. Risk-Adjusted Performance Matrix: 3-Year Return vs Sharpe Ratio", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("3-Year Trailing Return (%)", fontweight="bold")
    ax.set_ylabel("Sharpe Ratio (Risk-Adjusted Efficiency)", fontweight="bold")
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", frameon=True)
    plt.tight_layout()
    plt.savefig(EDA_DIR / "chart_14_return_vs_sharpe_scatter.png", dpi=300)
    plt.close()

    # =========================================================================
    # Chart 15: Top 10 Stock Holdings Across Mutual Fund Portfolios
    # =========================================================================
    fig, ax = plt.subplots(figsize=(12, 6), dpi=300)
    top_stocks = port_df.groupby(["stock_symbol", "stock_name"])["market_value_cr"].sum().reset_index()
    top_stocks = top_stocks.sort_values("market_value_cr", ascending=False).head(10)
    
    sns.barplot(data=top_stocks, x="market_value_cr", y="stock_symbol", palette="rocket", ax=ax)
    ax.set_title("15. Top 10 Concentrated Equity Holdings Across All Schemes (₹ Crore)", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Total Allocated Market Value (₹ Crore)", fontweight="bold")
    ax.set_ylabel("Stock Symbol", fontweight="bold")
    
    for i, row in enumerate(top_stocks.itertuples()):
        ax.text(row.market_value_cr + 500, i, f" ₹{row.market_value_cr:,.0f} Cr ({row.stock_name})", va="center", fontsize=8.5)
    
    plt.tight_layout()
    plt.savefig(EDA_DIR / "chart_15_top10_stock_holdings.png", dpi=300)
    plt.close()

    print("All 15 charts generated successfully in reports/eda_charts/!")


if __name__ == "__main__":
    generate_charts()
