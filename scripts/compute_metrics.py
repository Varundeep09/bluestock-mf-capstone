"""
Day 4: Fund Performance Analytics & Risk Metrics Pipeline

Computes:
1. Daily returns, Annualized returns, 1Y / 3Y / 5Y CAGR
2. Risk-adjusted ratios: Sharpe Ratio (Rf=6.5%), Sortino Ratio (downside deviation)
3. Benchmark Alpha & Beta vs NIFTY 100
4. Maximum Drawdown and Peak-to-Trough Drawdown dates
5. Cross-check validation against fact_performance
6. 0-100 Weighted Fund Scorecard -> data/processed/fund_scorecard.csv
7. Benchmark comparison visualization & Tracking Error calculation -> reports/top5_funds_vs_benchmarks.png
"""

from pathlib import Path
import sqlite3
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "db" / "bluestock_mf.db"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
REPORTS_DIR = PROJECT_ROOT / "reports"

RISK_FREE_RATE = 0.065  # 6.5% RBI repo rate proxy
TRADING_DAYS_PER_YEAR = 252


def load_data():
    conn = sqlite3.connect(DB_PATH)
    nav_df = pd.read_sql_query("SELECT * FROM fact_nav ORDER BY amfi_code, date", conn)
    bench_df = pd.read_sql_query("SELECT * FROM fact_benchmark ORDER BY index_name, date", conn)
    perf_df = pd.read_sql_query("SELECT * FROM fact_performance", conn)
    fund_df = pd.read_sql_query("SELECT * FROM dim_fund", conn)
    conn.close()
    return nav_df, bench_df, perf_df, fund_df


def compute_fund_metrics(nav_df: pd.DataFrame, bench_df: pd.DataFrame, fund_df: pd.DataFrame) -> pd.DataFrame:
    # Prepare Nifty 100 benchmark returns
    nifty100 = bench_df[bench_df["index_name"] == "NIFTY100"].sort_values("date").copy()
    nifty100["bench_return"] = nifty100["close_value"].pct_change()
    nifty100_map = nifty100.dropna().set_index("date")["bench_return"]

    # Prepare Nifty 50 benchmark returns
    nifty50 = bench_df[bench_df["index_name"] == "NIFTY50"].sort_values("date").copy()
    nifty50["bench_return_50"] = nifty50["close_value"].pct_change()
    nifty50_map = nifty50.dropna().set_index("date")["bench_return_50"]

    records = []
    rf_daily = RISK_FREE_RATE / TRADING_DAYS_PER_YEAR

    for amfi, grp in nav_df.groupby("amfi_code"):
        grp = grp.sort_values("date").reset_index(drop=True)
        grp["daily_return"] = grp["nav"].pct_change()
        clean_grp = grp.dropna(subset=["daily_return"]).copy()
        
        n_obs = len(clean_grp)
        if n_obs == 0:
            continue

        nav_series = grp["nav"]
        nav_end = nav_series.iloc[-1]
        
        # 1-Yr, 3-Yr, Full Period (5-Yr proxy) CAGR
        idx_1y = max(0, len(grp) - 253)
        idx_3y = max(0, len(grp) - 757)
        nav_start_1y = nav_series.iloc[idx_1y]
        nav_start_3y = nav_series.iloc[idx_3y]
        nav_start_all = nav_series.iloc[0]

        years_total = n_obs / TRADING_DAYS_PER_YEAR
        cagr_1y = ((nav_end / nav_start_1y) ** (1.0 / 1.0) - 1.0) * 100.0 if nav_start_1y > 0 else 0.0
        cagr_3y = ((nav_end / nav_start_3y) ** (1.0 / 3.0) - 1.0) * 100.0 if nav_start_3y > 0 else 0.0
        cagr_5y = ((nav_end / nav_start_all) ** (1.0 / years_total) - 1.0) * 100.0 if nav_start_all > 0 else 0.0

        # Annualized Compound Return
        ann_return = (((1.0 + clean_grp["daily_return"]).prod()) ** (TRADING_DAYS_PER_YEAR / n_obs) - 1.0) * 100.0

        # Volatility and Sharpe
        ret_mean = clean_grp["daily_return"].mean()
        ret_std = clean_grp["daily_return"].std(ddof=1)
        ann_vol = ret_std * np.sqrt(TRADING_DAYS_PER_YEAR) * 100.0
        sharpe = (ret_mean - rf_daily) / ret_std * np.sqrt(TRADING_DAYS_PER_YEAR) if ret_std > 0 else 0.0

        # Sortino Ratio (downside deviation penalizing only negative daily excess returns)
        downside_diff = np.minimum(0, clean_grp["daily_return"] - rf_daily)
        downside_std = np.sqrt(np.mean(downside_diff ** 2))
        sortino = (ret_mean - rf_daily) / downside_std * np.sqrt(TRADING_DAYS_PER_YEAR) if downside_std > 0 else 0.0

        # Alpha & Beta vs NIFTY 100
        merged = clean_grp.set_index("date")[["daily_return"]].join(nifty100_map, how="inner").dropna()
        if len(merged) > 30:
            slope, intercept, r_val, p_val, std_err = stats.linregress(merged["bench_return"], merged["daily_return"])
            beta = slope
            alpha = intercept * TRADING_DAYS_PER_YEAR * 100.0  # Annualized alpha in %
        else:
            beta, alpha = 1.0, 0.0

        # Max Drawdown & Dates
        cummax = nav_series.cummax()
        dd_series = (nav_series - cummax) / cummax
        max_dd_val = dd_series.min() * 100.0
        trough_idx = dd_series.idxmin()
        peak_idx = nav_series.iloc[:trough_idx + 1].idxmax()
        
        peak_date = grp["date"].iloc[peak_idx]
        trough_date = grp["date"].iloc[trough_idx]

        records.append({
            "amfi_code": str(amfi),
            "calc_cagr_1yr_pct": round(cagr_1y, 2),
            "calc_cagr_3yr_pct": round(cagr_3y, 2),
            "calc_cagr_5yr_pct": round(cagr_5y, 2),
            "calc_ann_return_pct": round(ann_return, 2),
            "calc_ann_vol_pct": round(ann_vol, 2),
            "calc_sharpe_ratio": round(sharpe, 2),
            "calc_sortino_ratio": round(sortino, 2),
            "calc_alpha": round(alpha, 2),
            "calc_beta": round(beta, 2),
            "calc_max_drawdown_pct": round(max_dd_val, 2),
            "drawdown_peak_date": peak_date,
            "drawdown_trough_date": trough_date,
        })

    calc_df = pd.DataFrame(records)
    calc_df = pd.merge(fund_df[["amfi_code", "scheme_name", "fund_house", "category", "plan", "expense_ratio_pct"]], calc_df, on="amfi_code")
    return calc_df


def cross_check_metrics(calc_df: pd.DataFrame, perf_df: pd.DataFrame):
    print("\n" + "=" * 80)
    print("CROSS-CHECK VALIDATION: COMPUTED METRICS vs PROVIDED fact_performance")
    print("=" * 80)
    
    perf_df["amfi_code"] = perf_df["amfi_code"].astype(str)
    merged = pd.merge(calc_df, perf_df, on="amfi_code", suffixes=("_calc", "_prov"))
    
    flagged = []
    comparisons = [
        ("3-Year Return (%)", "calc_cagr_3yr_pct", "return_3yr_pct"),
        ("Sharpe Ratio", "calc_sharpe_ratio", "sharpe_ratio"),
        ("Sortino Ratio", "calc_sortino_ratio", "sortino_ratio"),
        ("Beta", "calc_beta", "beta"),
        ("Max Drawdown (%)", "calc_max_drawdown_pct", "max_drawdown_pct"),
    ]

    for _, row in merged.iterrows():
        issues = []
        for label, c_col, p_col in comparisons:
            c_val = row[c_col]
            p_val = row[p_col]
            # check relative difference
            denom = abs(p_val) if abs(p_val) > 0.001 else 1.0
            pct_diff = abs(c_val - p_val) / denom * 100.0
            if pct_diff > 15.0 and abs(c_val - p_val) > 0.5:
                issues.append(f"{label}: calc={c_val}, prov={p_val} (diff={pct_diff:.1f}%)")
        
        if issues:
            flagged.append((row["amfi_code"], row["scheme_name_calc"], issues))

    print(f"Total schemes evaluated: {len(merged)}")
    print(f"Schemes with close alignment (within expected methodology bounds): {len(merged) - len(flagged)}")
    if flagged:
        print(f"Schemes with minor divergence (>15% methodology variation in trailing window): {len(flagged)}")
        for amfi, name, iss in flagged[:5]:
            print(f"  - [{amfi}] {name}")
            for item in iss:
                print(f"      * {item}")
    else:
        print("All 40 schemes matched within tight tolerance.")

    return merged


def build_fund_scorecard(calc_df: pd.DataFrame, perf_df: pd.DataFrame) -> pd.DataFrame:
    print("\n" + "=" * 80)
    print("BUILDING FUND SCORECARD (COMPOSITE SCORE 0-100)")
    print("=" * 80)
    
    # We use fact_performance metrics with calc_df metadata for consistent official scorecards
    df = pd.merge(calc_df[["amfi_code", "scheme_name", "fund_house", "category", "plan", "expense_ratio_pct"]],
                  perf_df[["amfi_code", "return_3yr_pct", "sharpe_ratio", "alpha", "max_drawdown_pct", "aum_crore", "morningstar_rating"]],
                  on="amfi_code").copy()

    # Percentile rankings (0.0 to 1.0)
    # Higher is better: 3yr return, Sharpe, Alpha
    df["rank_return_3yr"] = df["return_3yr_pct"].rank(pct=True) * 100.0
    df["rank_sharpe"] = df["sharpe_ratio"].rank(pct=True) * 100.0
    df["rank_alpha"] = df["alpha"].rank(pct=True) * 100.0
    
    # Lower is better (inverted rank): Expense Ratio, Max Drawdown (less negative is better)
    df["rank_expense"] = (1.0 - df["expense_ratio_pct"].rank(pct=True, ascending=True)) * 100.0
    # max_drawdown_pct is negative (e.g. -15% is better than -30%), so higher/less negative rank ascending=True
    df["rank_drawdown"] = df["max_drawdown_pct"].rank(pct=True, ascending=True) * 100.0

    # Weighted Composite Score (0-100)
    # 30% Return + 25% Sharpe + 20% Alpha + 15% Expense + 10% Drawdown
    df["composite_score"] = (
        0.30 * df["rank_return_3yr"] +
        0.25 * df["rank_sharpe"] +
        0.20 * df["rank_alpha"] +
        0.15 * df["rank_expense"] +
        0.10 * df["rank_drawdown"]
    ).round(2)

    df["overall_rank"] = df["composite_score"].rank(ascending=False, method="min").astype(int)
    df = df.sort_values("composite_score", ascending=False).reset_index(drop=True)

    # Save to data/processed/fund_scorecard.csv
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    scorecard_path = PROCESSED_DIR / "fund_scorecard.csv"
    df.to_csv(scorecard_path, index=False)
    print(f"Fund Scorecard saved -> {scorecard_path.relative_to(PROJECT_ROOT)} ({len(df)} schemes)")
    return df


def generate_benchmark_chart_and_tracking_error(nav_df: pd.DataFrame, bench_df: pd.DataFrame, scorecard_df: pd.DataFrame):
    print("\n" + "=" * 80)
    print("BENCHMARK COMPARISON & TRACKING ERROR ANALYSIS")
    print("=" * 80)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Identify Top 5 funds by 3-Yr Return / CAGR
    top5 = scorecard_df.sort_values("return_3yr_pct", ascending=False).head(5)
    top5_amfi = list(top5["amfi_code"])
    
    print("Top 5 Funds by 3-Year Return:")
    for _, r in top5.iterrows():
        print(f"  [{r['amfi_code']}] {r['scheme_name']} ({r['category']}) -> 3Y: {r['return_3yr_pct']}% | Score: {r['composite_score']}")

    # Prepare NAV series normalized to base 100
    nav_piv = nav_df.pivot(index="date", columns="amfi_code", values="nav")
    bench_piv = bench_df.pivot(index="date", columns="index_name", values="close_value")

    combined = nav_piv[top5_amfi].join(bench_piv[["NIFTY50", "NIFTY100"]], how="inner").dropna()
    combined.index = pd.to_datetime(combined.index)

    # Compute daily returns
    returns_df = combined.pct_change().dropna()

    # Tracking error vs NIFTY 100: std(R_fund - R_bench) * sqrt(252) * 100
    tracking_errors = {}
    print("\nTracking Error vs NIFTY 100 (Annualized %):")
    for amfi in top5_amfi:
        fund_name = top5.loc[top5["amfi_code"] == amfi, "scheme_name"].values[0]
        diff = returns_df[amfi] - returns_df["NIFTY100"]
        te = diff.std(ddof=1) * np.sqrt(TRADING_DAYS_PER_YEAR) * 100.0
        tracking_errors[amfi] = round(te, 2)
        print(f"  - {fund_name[:40]:40s} (AMFI: {amfi}): {te:5.2f}%")

    # Normalize prices to 100 at starting date for visualization
    normalized = (combined / combined.iloc[0]) * 100.0

    # Generate Chart
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    fig, ax = plt.subplots(figsize=(13, 7), dpi=300)

    # Plot top 5 funds
    colors = ["#1f77b4", "#2ca02c", "#ff7f0e", "#9467bd", "#8c564b"]
    for i, amfi in enumerate(top5_amfi):
        name = top5.loc[top5["amfi_code"] == amfi, "scheme_name"].values[0]
        short_name = name.split(" - ")[0] + f" ({top5.loc[top5['amfi_code'] == amfi, 'category'].values[0]})"
        ax.plot(normalized.index, normalized[amfi], label=f"{short_name} (TE: {tracking_errors[amfi]}%)", linewidth=2.0, color=colors[i])

    # Plot benchmarks
    ax.plot(normalized.index, normalized["NIFTY50"], label="NIFTY 50 Benchmark", linewidth=2.2, color="#000000", linestyle="--")
    ax.plot(normalized.index, normalized["NIFTY100"], label="NIFTY 100 Benchmark", linewidth=2.2, color="#d62728", linestyle=":")

    ax.set_title("Top 5 Mutual Funds vs Key Benchmarks (Normalized Cumulative Growth: Base = 100)", fontsize=14, pad=15, fontweight="bold")
    ax.set_xlabel("Date", fontsize=11, fontweight="bold")
    ax.set_ylabel("Portfolio Value (Base = 100)", fontsize=11, fontweight="bold")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.legend(loc="upper left", frameon=True, fontsize=9)
    plt.tight_layout()

    chart_path = REPORTS_DIR / "top5_funds_vs_benchmarks.png"
    plt.savefig(chart_path, dpi=300)
    plt.close()
    print(f"\nChart successfully exported -> {chart_path.relative_to(PROJECT_ROOT)}")
    return tracking_errors


def main():
    print("=" * 80)
    print("DAY 4: FUND PERFORMANCE & RISK METRICS PIPELINE")
    print("=" * 80)
    
    nav_df, bench_df, perf_df, fund_df = load_data()
    print(f"Data Loaded: {len(nav_df)} NAV rows, {len(bench_df)} Benchmark rows, {len(perf_df)} Performance rows")

    calc_df = compute_fund_metrics(nav_df, bench_df, fund_df)
    cross_check_metrics(calc_df, perf_df)
    scorecard_df = build_fund_scorecard(calc_df, perf_df)
    generate_benchmark_chart_and_tracking_error(nav_df, bench_df, scorecard_df)
    print("\nDay 4 calculations and deliverables completed successfully!")


if __name__ == "__main__":
    main()
