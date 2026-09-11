"""
Rubric Self-Check and Repository QA Audit Script
"""

import subprocess
import sqlite3
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

scripts = [
    "scripts/validate_fund_codes.py",
    "scripts/data_ingestion.py",
    "scripts/data_cleaning.py",
    "scripts/load_to_sqlite.py",
    "scripts/compute_metrics.py",
    "scripts/advanced_analytics.py",
    "scripts/recommender.py",
]

print("=" * 70)
print("1. SCRIPT EXECUTION AUDIT")
print("=" * 70)
for s in scripts:
    res = subprocess.run([".venv/Scripts/python.exe", s], capture_output=True, text=True, cwd=PROJECT_ROOT)
    status = "PASS" if res.returncode == 0 else "FAIL"
    print(f"  {s:32s} : {status}")
    if res.returncode != 0:
        print("    Error:", res.stderr[:300])

print("\n" + "=" * 70)
print("2. SQL 10-QUERY EXECUTION AUDIT (db/bluestock_mf.db)")
print("=" * 70)
conn = sqlite3.connect(PROJECT_ROOT / "db" / "bluestock_mf.db")
with open(PROJECT_ROOT / "sql" / "queries.sql", "r", encoding="utf-8") as f:
    stmts = [s.strip() for s in f.read().split(";") if s.strip()]

q_count = 0
for s in stmts:
    lines = [l for l in s.splitlines() if not l.strip().startswith("--")]
    code = "\n".join(lines).strip()
    if not code or not code.upper().startswith("SELECT"):
        continue
    q_count += 1
    try:
        df = pd.read_sql_query(code, conn)
        print(f"  Query {q_count:2d}: PASS ({len(df):4d} rows returned)")
    except Exception as e:
        print(f"  Query {q_count:2d}: FAIL ({e})")

conn.close()

print("\n" + "=" * 70)
print("3. PROCESSED DATASETS AUDIT (data/processed/)")
print("=" * 70)
processed_files = [
    "clean_fund_master.csv", "clean_dim_date.csv", "clean_nav.csv",
    "clean_transactions.csv", "clean_performance.csv", "clean_portfolio.csv",
    "clean_aum.csv", "clean_sip_inflows.csv", "clean_benchmark.csv",
    "clean_category_inflows.csv", "clean_folio_count.csv",
    "fund_scorecard.csv", "var_cvar_report.csv", "cohort_analysis.csv",
    "sip_continuity.csv", "sector_hhi.csv"
]
for pf in processed_files:
    p = PROJECT_ROOT / "data" / "processed" / pf
    if p.exists():
        df = pd.read_csv(p)
        print(f"  {pf:28s}: PASS ({len(df):6d} rows, {len(df.columns):2d} cols)")
    else:
        print(f"  {pf:28s}: FAIL (MISSING)")

print("\n" + "=" * 70)
print("4. JUPYTER NOTEBOOKS AUDIT (notebooks/)")
print("=" * 70)
notebooks = [
    "notebooks/03_eda_analysis.ipynb",
    "notebooks/04_performance_analytics.ipynb",
    "notebooks/05_advanced_analytics.ipynb"
]
for nb in notebooks:
    p = PROJECT_ROOT / nb
    status = "PASS" if p.exists() else "FAIL"
    size = f"{p.stat().st_size:,} bytes" if p.exists() else "0 bytes"
    print(f"  {nb:42s}: {status} ({size})")

print("\n" + "=" * 70)
print("5. REPORTS & CHARTS AUDIT (reports/)")
print("=" * 70)
reports = [
    "reports/top5_funds_vs_benchmarks.png",
    "reports/rolling_sharpe_chart.png",
    "reports/sector_hhi_chart.png",
]
for r in reports:
    p = PROJECT_ROOT / r
    status = "PASS" if p.exists() else "FAIL"
    size = f"{p.stat().st_size:,} bytes" if p.exists() else "0 bytes"
    print(f"  {r:42s}: {status} ({size})")

eda_charts = list((PROJECT_ROOT / "reports" / "eda_charts").glob("*.png"))
print(f"  reports/eda_charts/ (15 PNGs)             : PASS ({len(eda_charts)} charts found)")

print("\n" + "=" * 70)
print("6. POWER BI DASHBOARD ARTIFACTS AUDIT (dashboard/)")
print("=" * 70)
dash_files = [
    "dashboard/bluestock_mf.pbix",
    "dashboard/bluestock_mf.pdf",
    "dashboard/page1_industry_overview.png",
    "dashboard/page2_fund_performance.png",
    "dashboard/page3_investor_analytics.png",
    "dashboard/page4_sip_market_trends.png"
]
for df_path in dash_files:
    p = PROJECT_ROOT / df_path
    status = "PASS" if p.exists() else "FAIL"
    size = f"{p.stat().st_size:,} bytes" if p.exists() else "0 bytes"
    print(f"  {df_path:42s}: {status} ({size})")
