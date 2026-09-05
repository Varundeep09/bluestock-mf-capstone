"""
Day 1 - Task 3: Load all 10 provided CSV datasets and profile them.

Run:
    python scripts/data_ingestion.py

This script does NOT modify any file. It only reads data/raw/*.csv and
prints shape, dtypes, null counts and a preview for each dataset, so we
can see the real column names before writing any cleaning/schema code.
"""

from pathlib import Path
import pandas as pd

# Always resolve paths relative to the project root, never hard-code them.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"

DATASETS = [
    "01_fund_master.csv",
    "02_nav_history.csv",
    "03_aum_by_fund_house.csv",
    "04_monthly_sip_inflows.csv",
    "05_category_inflows.csv",
    "06_industry_folio_count.csv",
    "07_scheme_performance.csv",
    "08_investor_transactions.csv",
    "09_portfolio_holdings.csv",
    "10_benchmark_indices.csv",
]


def find_csv(raw_dir: Path, filename: str) -> Path | None:
    exact = raw_dir / filename
    if exact.exists():
        return exact
    # Match files downloaded with LMS prefix, e.g. <timestamp>-<hash>-01_fund_master.csv
    matches = list(raw_dir.glob(f"*{filename}"))
    if matches:
        return matches[0]
    return None


def profile_csv(raw_dir: Path, filename: str) -> pd.DataFrame | None:
    path = find_csv(raw_dir, filename)
    if path is None:
        print(f"  [MISSING] {filename} not found in {raw_dir}")
        return None

    df = pd.read_csv(path)
    print(f"\n{'=' * 70}")
    print(f"FILE: {path.name}")
    print(f"{'=' * 70}")
    print(f"shape        : {df.shape}")
    print(f"columns      : {list(df.columns)}")
    print("\ndtypes:")
    print(df.dtypes)
    print("\nnull counts:")
    print(df.isnull().sum())
    print("\nhead(5):")
    print(df.head(5).to_string())
    return df


def main():
    print(f"Reading raw datasets from: {RAW_DIR}")
    if not RAW_DIR.exists():
        print(f"[ERROR] {RAW_DIR} does not exist. Create it and drop the 10 CSVs in.")
        return

    frames = {}
    for filename in DATASETS:
        df = profile_csv(RAW_DIR, filename)
        if df is not None:
            frames[filename] = df

    print(f"\n\nLoaded {len(frames)} / {len(DATASETS)} datasets successfully.")
    missing = set(DATASETS) - set(frames.keys())
    if missing:
        print(f"Still missing: {sorted(missing)}")
    else:
        print("All 10 provided datasets loaded. Ready for Task 4/5 (API fetch) and validation.")


if __name__ == "__main__":
    main()
