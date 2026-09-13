"""
Script to build notebooks/01_data_ingestion.ipynb and notebooks/02_data_cleaning.ipynb
"""

from pathlib import Path
import nbformat as nbf

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# 1. Build 01_data_ingestion.ipynb
nb1 = nbf.v4.new_notebook()
nb1_cells = [
    nbf.v4.new_markdown_cell(
        "# Day 1: Data Ingestion & Dataset Profiling\n"
        "This notebook loads and profiles all 10 raw CSV datasets from `data/raw/`, inspecting dataset dimensions, data types, null values, and sample records."
    ),
    nbf.v4.new_code_cell(
        "import sys\n"
        "from pathlib import Path\n"
        "import pandas as pd\n\n"
        "# Always resolve relative to project root\n"
        "PROJECT_ROOT = Path('.').resolve().parent\n"
        "RAW_DIR = PROJECT_ROOT / 'data' / 'raw'\n"
        "print(f'Ingesting raw datasets from: {RAW_DIR}')\n"
    ),
    nbf.v4.new_markdown_cell("## Run Automated Data Profiling"),
    nbf.v4.new_code_cell(
        "sys.path.append(str(PROJECT_ROOT / 'scripts'))\n"
        "import data_ingestion\n\n"
        "data_ingestion.main()\n"
    )
]
nb1["cells"] = nb1_cells
with open(PROJECT_ROOT / "notebooks" / "01_data_ingestion.ipynb", "w", encoding="utf-8") as f:
    nbf.write(nb1, f)
print("Created notebooks/01_data_ingestion.ipynb")

# 2. Build 02_data_cleaning.ipynb
nb2 = nbf.v4.new_notebook()
nb2_cells = [
    nbf.v4.new_markdown_cell(
        "# Day 2: Data Cleaning & Processing Pipeline\n"
        "This notebook executes comprehensive data cleaning, type standardization, return calculations, and calendar dimension generation, saving processed outputs to `data/processed/`."
    ),
    nbf.v4.new_code_cell(
        "import sys\n"
        "from pathlib import Path\n"
        "import pandas as pd\n\n"
        "PROJECT_ROOT = Path('.').resolve().parent\n"
        "sys.path.append(str(PROJECT_ROOT / 'scripts'))\n"
        "import data_cleaning\n\n"
        "data_cleaning.main()\n"
    ),
    nbf.v4.new_markdown_cell("## Inspect Clean Processed Datasets"),
    nbf.v4.new_code_cell(
        "processed_dir = PROJECT_ROOT / 'data' / 'processed'\n"
        "for f in sorted(processed_dir.glob('clean_*.csv')):\n"
        "    df = pd.read_csv(f)\n"
        "    print(f'{f.name:30s} | Rows: {len(df):6d} | Cols: {len(df.columns):2d}')\n"
    )
]
nb2["cells"] = nb2_cells
with open(PROJECT_ROOT / "notebooks" / "02_data_cleaning.ipynb", "w", encoding="utf-8") as f:
    nbf.write(nb2, f)
print("Created notebooks/02_data_cleaning.ipynb")
