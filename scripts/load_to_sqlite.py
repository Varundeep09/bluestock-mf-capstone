"""
Day 2 - Task 3: Load cleaned datasets into SQLite database (db/bluestock_mf.db).

This script:
1. Creates the db/ directory if not present.
2. Executes sql/schema.sql to set up tables, constraints, and indexes.
3. Loads all cleaned CSV files from data/processed/ into their corresponding tables.
4. Verifies row counts between processed CSVs and database tables.
"""

from pathlib import Path
import sqlite3
import pandas as pd
from sqlalchemy import create_engine, text

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_DIR = PROJECT_ROOT / "db"
DB_PATH = DB_DIR / "bluestock_mf.db"
SCHEMA_PATH = PROJECT_ROOT / "sql" / "schema.sql"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

TABLE_FILE_MAP = [
    ("dim_fund", "clean_fund_master.csv"),
    ("dim_date", "clean_dim_date.csv"),
    ("fact_nav", "clean_nav.csv"),
    ("fact_transactions", "clean_transactions.csv"),
    ("fact_performance", "clean_performance.csv"),
    ("fact_portfolio", "clean_portfolio.csv"),
    ("fact_aum", "clean_aum.csv"),
    ("fact_sip_industry", "clean_sip_inflows.csv"),
    ("fact_benchmark", "clean_benchmark.csv"),
    ("fact_category_inflows", "clean_category_inflows.csv"),
    ("fact_folio_count", "clean_folio_count.csv"),
]


def init_database():
    DB_DIR.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()  # Clean rebuild

    print(f"Initializing database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    conn.executescript(schema_sql)
    conn.commit()
    conn.close()
    print("Schema created successfully.")


def load_tables():
    engine = create_engine(f"sqlite:///{DB_PATH}")
    
    print("\nLoading data into SQLite tables:")
    print("=" * 65)

    summary = []
    with engine.begin() as conn:
        for table_name, filename in TABLE_FILE_MAP:
            file_path = PROCESSED_DIR / filename
            if not file_path.exists():
                print(f"[MISSING] {filename} not found in {PROCESSED_DIR}")
                continue

            df = pd.read_csv(file_path)
            # Ensure amfi_code is string where relevant
            if "amfi_code" in df.columns:
                df["amfi_code"] = df["amfi_code"].astype(str)

            df.to_sql(table_name, con=conn, if_exists="append", index=False)
            
            # Verify count
            res = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
            print(f"  {table_name:22s} <- {filename:26s} | {res:6d} rows")
            summary.append((table_name, len(df), res))

    print("=" * 65)
    print("All tables successfully loaded and verified.")
    return summary


def main():
    init_database()
    load_tables()


if __name__ == "__main__":
    main()
