"""
Day 1 - Task 7: Validate that every fund in 01_fund_master.csv has
matching NAV records in 02_nav_history.csv.

Run:
    python scripts/validate_fund_codes.py
"""

from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"


def find_csv(raw_dir: Path, filename: str) -> Path | None:
    exact = raw_dir / filename
    if exact.exists():
        return exact
    matches = list(raw_dir.glob(f"*{filename}"))
    if matches:
        return matches[0]
    return None


def main():
    fund_master_path = find_csv(RAW_DIR, "01_fund_master.csv")
    nav_history_path = find_csv(RAW_DIR, "02_nav_history.csv")

    for p, name in [(fund_master_path, "01_fund_master.csv"), (nav_history_path, "02_nav_history.csv")]:
        if p is None or not p.exists():
            print(f"[ERROR] {name} not found in {RAW_DIR}. Run data_ingestion.py first / add the CSVs.")
            return

    fund_master = pd.read_csv(fund_master_path)
    nav_history = pd.read_csv(nav_history_path)

    # amfi_code is the expected join key per the dataset schema appendix.
    if "amfi_code" not in fund_master.columns or "amfi_code" not in nav_history.columns:
        print("[ERROR] Expected an 'amfi_code' column in both files. "
              f"fund_master columns: {list(fund_master.columns)}; "
              f"nav_history columns: {list(nav_history.columns)}")
        return

    master_codes = set(fund_master["amfi_code"].astype(str))
    nav_codes = set(nav_history["amfi_code"].astype(str))

    missing_in_nav = master_codes - nav_codes
    extra_in_nav = nav_codes - master_codes

    print(f"Fund master schemes : {len(master_codes)}")
    print(f"Schemes with NAV data: {len(nav_codes)}")

    if not missing_in_nav:
        print("PASS: every fund_master scheme has NAV history.")
    else:
        print(f"FAIL: {len(missing_in_nav)} scheme(s) in fund_master have NO NAV records:")
        for code in sorted(missing_in_nav):
            print(f"   - {code}")

    if extra_in_nav:
        print(f"\nNote: {len(extra_in_nav)} amfi_code(s) appear in nav_history "
              f"but not in fund_master (check for typos/extra schemes):")
        for code in sorted(extra_in_nav):
            print(f"   - {code}")


if __name__ == "__main__":
    main()
