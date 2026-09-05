"""
Day 2 - Data Cleaning Pipeline for Bluestock Mutual Fund Capstone

This script:
1. Loads all 10 raw CSV datasets from data/raw/
2. Cleans, normalizes, validates, and enhances each dataset
3. Generates the dimension date table (dim_date)
4. Saves all cleaned datasets into data/processed/
5. Prints comprehensive before/after row count, null count, and data quality summaries
"""

from pathlib import Path
import re
import pandas as pd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


def find_csv(raw_dir: Path, filename: str) -> Path | None:
    exact = raw_dir / filename
    if exact.exists():
        return exact
    matches = list(raw_dir.glob(f"*{filename}"))
    if matches:
        return matches[0]
    return None


def clean_fund_master(raw_dir: Path) -> pd.DataFrame:
    path = find_csv(raw_dir, "01_fund_master.csv")
    df = pd.read_csv(path)
    initial_rows = len(df)
    initial_nulls = df.isnull().sum().sum()

    # Deduplicate and trim strings
    df = df.drop_duplicates(subset=["amfi_code"]).copy()
    str_cols = df.select_dtypes(include=["object", "string", "str"]).columns
    for col in str_cols:
        df[col] = df[col].astype(str).str.strip()

    # Convert numeric fields
    df["amfi_code"] = df["amfi_code"].astype(str)
    df["expense_ratio_pct"] = pd.to_numeric(df["expense_ratio_pct"], errors="coerce")
    df["exit_load_pct"] = pd.to_numeric(df["exit_load_pct"], errors="coerce").fillna(0.0)
    df["min_sip_amount"] = pd.to_numeric(df["min_sip_amount"], errors="coerce").fillna(500).astype(int)
    df["min_lumpsum_amount"] = pd.to_numeric(df["min_lumpsum_amount"], errors="coerce").fillna(1000).astype(int)
    df["launch_date"] = pd.to_datetime(df["launch_date"], errors="coerce").dt.strftime("%Y-%m-%d")

    print(f"01_fund_master: {initial_rows} -> {len(df)} rows | Nulls: {initial_nulls} -> {df.isnull().sum().sum()}")
    return df


def clean_nav_history(raw_dir: Path) -> pd.DataFrame:
    path = find_csv(raw_dir, "02_nav_history.csv")
    df = pd.read_csv(path)
    initial_rows = len(df)
    initial_nulls = df.isnull().sum().sum()

    df["amfi_code"] = df["amfi_code"].astype(str)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["nav"] = pd.to_numeric(df["nav"], errors="coerce")

    # Drop invalid dates and NAV <= 0
    df = df.dropna(subset=["date", "nav"])
    df = df[df["nav"] > 0]

    # Deduplicate on (amfi_code, date)
    df = df.drop_duplicates(subset=["amfi_code", "date"]).sort_values(["amfi_code", "date"]).reset_index(drop=True)

    # Compute daily return % per amfi_code
    df["daily_return_pct"] = df.groupby("amfi_code")["nav"].pct_change() * 100
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")

    print(f"02_nav_history: {initial_rows} -> {len(df)} rows | Nulls: {initial_nulls} -> {df['nav'].isnull().sum()} (NAV)")
    return df


def clean_aum(raw_dir: Path) -> pd.DataFrame:
    path = find_csv(raw_dir, "03_aum_by_fund_house.csv")
    df = pd.read_csv(path)
    initial_rows = len(df)
    initial_nulls = df.isnull().sum().sum()

    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    df["fund_house"] = df["fund_house"].astype(str).str.strip()
    df["aum_lakh_crore"] = pd.to_numeric(df["aum_lakh_crore"], errors="coerce")
    df["aum_crore"] = pd.to_numeric(df["aum_crore"], errors="coerce")
    df["num_schemes"] = pd.to_numeric(df["num_schemes"], errors="coerce").fillna(0).astype(int)

    df = df.drop_duplicates(subset=["fund_house", "date"]).sort_values(["fund_house", "date"]).reset_index(drop=True)
    print(f"03_aum_by_fund_house: {initial_rows} -> {len(df)} rows | Nulls: {initial_nulls} -> {df.isnull().sum().sum()}")
    return df


def clean_sip_inflows(raw_dir: Path) -> pd.DataFrame:
    path = find_csv(raw_dir, "04_monthly_sip_inflows.csv")
    df = pd.read_csv(path)
    initial_rows = len(df)
    initial_nulls = df.isnull().sum().sum()

    df["month"] = df["month"].astype(str).str.strip()
    df = df.sort_values("month").reset_index(drop=True)
    df["sip_inflow_crore"] = pd.to_numeric(df["sip_inflow_crore"], errors="coerce")
    df["active_sip_accounts_crore"] = pd.to_numeric(df["active_sip_accounts_crore"], errors="coerce")
    df["new_sip_accounts_lakh"] = pd.to_numeric(df["new_sip_accounts_lakh"], errors="coerce")
    df["sip_aum_lakh_crore"] = pd.to_numeric(df["sip_aum_lakh_crore"], errors="coerce")

    # If yoy_growth_pct is missing, calculate it via 12-month lag where possible
    computed_yoy = df["sip_inflow_crore"].pct_change(12) * 100
    df["yoy_growth_pct"] = pd.to_numeric(df["yoy_growth_pct"], errors="coerce").combine_first(computed_yoy)

    df = df.drop_duplicates(subset=["month"]).reset_index(drop=True)
    print(f"04_monthly_sip_inflows: {initial_rows} -> {len(df)} rows | Nulls: {initial_nulls} -> {df.isnull().sum().sum()}")
    return df


def clean_category_inflows(raw_dir: Path) -> pd.DataFrame:
    path = find_csv(raw_dir, "05_category_inflows.csv")
    df = pd.read_csv(path)
    initial_rows = len(df)
    initial_nulls = df.isnull().sum().sum()

    df["month"] = df["month"].astype(str).str.strip()
    df["category"] = df["category"].astype(str).str.strip()
    df["net_inflow_crore"] = pd.to_numeric(df["net_inflow_crore"], errors="coerce").fillna(0.0)

    df = df.drop_duplicates(subset=["category", "month"]).sort_values(["category", "month"]).reset_index(drop=True)
    print(f"05_category_inflows: {initial_rows} -> {len(df)} rows | Nulls: {initial_nulls} -> {df.isnull().sum().sum()}")
    return df


def clean_folio_count(raw_dir: Path) -> pd.DataFrame:
    path = find_csv(raw_dir, "06_industry_folio_count.csv")
    df = pd.read_csv(path)
    initial_rows = len(df)
    initial_nulls = df.isnull().sum().sum()

    df["month"] = df["month"].astype(str).str.strip()
    for col in ["total_folios_crore", "equity_folios_crore", "debt_folios_crore", "hybrid_folios_crore", "others_folios_crore"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.drop_duplicates(subset=["month"]).sort_values("month").reset_index(drop=True)
    print(f"06_industry_folio_count: {initial_rows} -> {len(df)} rows | Nulls: {initial_nulls} -> {df.isnull().sum().sum()}")
    return df


def clean_scheme_performance(raw_dir: Path) -> pd.DataFrame:
    path = find_csv(raw_dir, "07_scheme_performance.csv")
    df = pd.read_csv(path)
    initial_rows = len(df)
    initial_nulls = df.isnull().sum().sum()

    df["amfi_code"] = df["amfi_code"].astype(str)
    str_cols = ["scheme_name", "fund_house", "category", "plan", "risk_grade"]
    for col in str_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    numeric_cols = [
        "return_1yr_pct", "return_3yr_pct", "return_5yr_pct", "benchmark_3yr_pct",
        "alpha", "beta", "sharpe_ratio", "sortino_ratio", "std_dev_ann_pct",
        "max_drawdown_pct", "aum_crore", "expense_ratio_pct"
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["morningstar_rating"] = pd.to_numeric(df["morningstar_rating"], errors="coerce").fillna(3).astype(int)

    # Validation checks
    neg_sharpe_count = (df["sharpe_ratio"] < 0).sum()
    expense_out_of_bounds = ((df["expense_ratio_pct"] < 0.1) | (df["expense_ratio_pct"] > 2.5)).sum()

    print(f"   [Validation] Negative Sharpe count: {neg_sharpe_count}, Expense ratio out of [0.1%, 2.5%]: {expense_out_of_bounds}")

    df = df.drop_duplicates(subset=["amfi_code"]).reset_index(drop=True)
    print(f"07_scheme_performance: {initial_rows} -> {len(df)} rows | Nulls: {initial_nulls} -> {df.isnull().sum().sum()}")
    return df


def clean_transactions(raw_dir: Path) -> pd.DataFrame:
    path = find_csv(raw_dir, "08_investor_transactions.csv")
    df = pd.read_csv(path)
    initial_rows = len(df)
    initial_nulls = df.isnull().sum().sum()

    # Standardize transaction types
    df["transaction_type"] = df["transaction_type"].astype(str).str.strip()
    type_map = {
        "sip": "SIP", "SIP": "SIP",
        "lumpsum": "Lumpsum", "Lumpsum": "Lumpsum", "LUMP": "Lumpsum",
        "redemption": "Redemption", "Redemption": "Redemption", "RED": "Redemption"
    }
    df["transaction_type"] = df["transaction_type"].map(lambda x: type_map.get(x, x.title()))

    # Clean other columns
    df["investor_id"] = df["investor_id"].astype(str).str.strip()
    df["amfi_code"] = df["amfi_code"].astype(str)
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce").dt.strftime("%Y-%m-%d")
    df["amount_inr"] = pd.to_numeric(df["amount_inr"], errors="coerce").fillna(0).astype(int)
    df = df[df["amount_inr"] > 0]  # amount must be > 0

    str_cols = ["state", "city", "city_tier", "age_group", "gender", "payment_mode", "kyc_status"]
    for col in str_cols:
        df[col] = df[col].astype(str).str.strip()

    df["annual_income_lakh"] = pd.to_numeric(df["annual_income_lakh"], errors="coerce").fillna(0.0)

    # Ensure tx_id surrogate key
    df["tx_id"] = [f"TX{i+1:06d}" for i in range(len(df))]
    cols_order = ["tx_id"] + [c for c in df.columns if c != "tx_id"]
    df = df[cols_order].reset_index(drop=True)

    print(f"08_investor_transactions: {initial_rows} -> {len(df)} rows | Nulls: {initial_nulls} -> {df.isnull().sum().sum()}")
    return df


def clean_portfolio(raw_dir: Path) -> pd.DataFrame:
    path = find_csv(raw_dir, "09_portfolio_holdings.csv")
    df = pd.read_csv(path)
    initial_rows = len(df)
    initial_nulls = df.isnull().sum().sum()

    df["amfi_code"] = df["amfi_code"].astype(str)
    df["stock_symbol"] = df["stock_symbol"].astype(str).str.strip()
    df["stock_name"] = df["stock_name"].astype(str).str.strip()
    df["sector"] = df["sector"].astype(str).str.strip()
    df["weight_pct"] = pd.to_numeric(df["weight_pct"], errors="coerce").fillna(0.0)
    df["market_value_cr"] = pd.to_numeric(df["market_value_cr"], errors="coerce").fillna(0.0)
    df["current_price_inr"] = pd.to_numeric(df["current_price_inr"], errors="coerce").fillna(0.0)
    df["portfolio_date"] = pd.to_datetime(df["portfolio_date"], errors="coerce").dt.strftime("%Y-%m-%d")

    df = df.drop_duplicates(subset=["amfi_code", "stock_symbol"]).reset_index(drop=True)
    print(f"09_portfolio_holdings: {initial_rows} -> {len(df)} rows | Nulls: {initial_nulls} -> {df.isnull().sum().sum()}")
    return df


def clean_benchmark(raw_dir: Path) -> pd.DataFrame:
    path = find_csv(raw_dir, "10_benchmark_indices.csv")
    df = pd.read_csv(path)
    initial_rows = len(df)
    initial_nulls = df.isnull().sum().sum()

    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    df["index_name"] = df["index_name"].astype(str).str.strip()
    df["close_value"] = pd.to_numeric(df["close_value"], errors="coerce")

    df = df.dropna(subset=["date", "index_name", "close_value"])
    df = df.drop_duplicates(subset=["index_name", "date"]).sort_values(["index_name", "date"]).reset_index(drop=True)
    print(f"10_benchmark_indices: {initial_rows} -> {len(df)} rows | Nulls: {initial_nulls} -> {df.isnull().sum().sum()}")
    return df


def build_dim_date(all_dates: set) -> pd.DataFrame:
    """Builds a comprehensive date dimension table."""
    sorted_dates = sorted(pd.to_datetime(list(all_dates)))
    if not sorted_dates:
        start_date = "2020-01-01"
        end_date = "2026-12-31"
        dt_range = pd.date_range(start_date, end_date)
    else:
        min_dt = sorted_dates[0]
        max_dt = sorted_dates[-1]
        dt_range = pd.date_range(min_dt, max_dt)

    df_date = pd.DataFrame({"date_dt": dt_range})
    df_date["date"] = df_date["date_dt"].dt.strftime("%Y-%m-%d")
    df_date["date_id"] = range(1, len(df_date) + 1)
    df_date["year"] = df_date["date_dt"].dt.year
    df_date["month"] = df_date["date_dt"].dt.month
    df_date["quarter"] = df_date["date_dt"].dt.quarter
    df_date["day"] = df_date["date_dt"].dt.day
    df_date["day_name"] = df_date["date_dt"].dt.day_name()
    df_date["month_name"] = df_date["date_dt"].dt.month_name()
    df_date["is_weekday"] = df_date["date_dt"].dt.dayofweek.apply(lambda x: 1 if x < 5 else 0)

    cols = ["date_id", "date", "year", "month", "quarter", "day", "day_name", "month_name", "is_weekday"]
    df_date = df_date[cols]
    print(f"dim_date: Generated {len(df_date)} date records from {df_date['date'].min()} to {df_date['date'].max()}")
    return df_date


def main():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    print("=" * 70)
    print("DAY 2: DATA CLEANING PIPELINE")
    print(f"Raw Input:       {RAW_DIR}")
    print(f"Processed Out:   {PROCESSED_DIR}")
    print("=" * 70)

    # 1. Clean all datasets
    fund_master = clean_fund_master(RAW_DIR)
    nav_history = clean_nav_history(RAW_DIR)
    aum = clean_aum(RAW_DIR)
    sip_inflows = clean_sip_inflows(RAW_DIR)
    cat_inflows = clean_category_inflows(RAW_DIR)
    folio_count = clean_folio_count(RAW_DIR)
    performance = clean_scheme_performance(RAW_DIR)
    transactions = clean_transactions(RAW_DIR)
    portfolio = clean_portfolio(RAW_DIR)
    benchmark = clean_benchmark(RAW_DIR)

    # 2. Collect all dates for dim_date
    all_dates = set(nav_history["date"]).union(
        set(benchmark["date"]),
        set(transactions["transaction_date"]),
        set(aum["date"]),
        set(portfolio["portfolio_date"])
    )
    dim_date = build_dim_date(all_dates)

    # 3. Save to data/processed/
    files = {
        "clean_fund_master.csv": fund_master,
        "clean_nav.csv": nav_history,
        "clean_aum.csv": aum,
        "clean_sip_inflows.csv": sip_inflows,
        "clean_category_inflows.csv": cat_inflows,
        "clean_folio_count.csv": folio_count,
        "clean_performance.csv": performance,
        "clean_transactions.csv": transactions,
        "clean_portfolio.csv": portfolio,
        "clean_benchmark.csv": benchmark,
        "clean_dim_date.csv": dim_date,
    }

    print("\n" + "=" * 70)
    print("SAVING CLEANED DATASETS TO data/processed/")
    print("=" * 70)
    for filename, df in files.items():
        out_path = PROCESSED_DIR / filename
        df.to_csv(out_path, index=False)
        print(f"  -> Saved {out_path.name:30s} | {len(df):6d} rows | {len(df.columns):2d} cols")

    print("\nData cleaning complete! All clean datasets are ready in data/processed/.")


if __name__ == "__main__":
    main()
