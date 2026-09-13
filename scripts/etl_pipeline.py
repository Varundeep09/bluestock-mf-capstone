"""
Master ETL Pipeline Orchestrator — Bluestock Mutual Fund Analytics

This script orchestrates the complete End-to-End data pipeline:
  Stage 1: Raw Dataset Profiling & Verification (data_ingestion.py)
  Stage 2: Comprehensive Data Cleaning & Processing (data_cleaning.py)
  Stage 3: SQLite Star Schema Loading & Index Creation (load_to_sqlite.py)

Usage:
    python scripts/etl_pipeline.py
"""

import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT / "scripts"))

import data_ingestion
import data_cleaning
import load_to_sqlite


def run_etl_pipeline():
    start_time = time.time()
    print("=" * 80)
    print("BLUESTOCK MUTUAL FUND ANALYTICS — MASTER ETL PIPELINE")
    print("=" * 80)
    print(f"Project Root: {PROJECT_ROOT}\n")

    # -------------------------------------------------------------
    # STAGE 1: Data Ingestion & Profiling
    # -------------------------------------------------------------
    print(">>> [STAGE 1/3] EXECUTING RAW DATA INGESTION & PROFILING...")
    print("-" * 80)
    data_ingestion.main()
    print("[STAGE 1 COMPLETE] All raw CSV datasets verified.\n")

    # -------------------------------------------------------------
    # STAGE 2: Data Cleaning & Processing
    # -------------------------------------------------------------
    print(">>> [STAGE 2/3] EXECUTING DATA CLEANING & ENHANCEMENT...")
    print("-" * 80)
    data_cleaning.main()
    print("[STAGE 2 COMPLETE] Cleaned files written to data/processed/.\n")

    # -------------------------------------------------------------
    # STAGE 3: Database Loading & Star Schema Creation
    # -------------------------------------------------------------
    print(">>> [STAGE 3/3] LOADING CLEAN DATA INTO SQLITE (data/db/bluestock_mf.db)...")
    print("-" * 80)
    load_to_sqlite.main()
    print("[STAGE 3 COMPLETE] SQLite star schema populated and indexed.\n")

    elapsed = time.time() - start_time
    print("=" * 80)
    print(f"ETL PIPELINE COMPLETED SUCCESSFULLY IN {elapsed:.2f} SECONDS!")
    print("=" * 80)


if __name__ == "__main__":
    run_etl_pipeline()
