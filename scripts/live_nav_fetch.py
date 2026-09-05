"""
Day 1 - Task 4 & 5: Fetch live NAV history from mfapi.in (no auth required)
for HDFC Top 100 plus 5 additional schemes, and save each as a raw CSV.

Run:
    python scripts/live_nav_fetch.py

Output:
    data/raw/api_<amfi_code>_<scheme_slug>.csv  (one file per scheme)
"""

from pathlib import Path
import re
import time
import requests
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"

# Task 4 (required) + Task 5 (required) = 6 schemes total.
SCHEMES = {
    "125497": "HDFC Top 100",
    "119551": "SBI Bluechip",
    "120503": "ICICI Bluechip",
    "118632": "Nippon Large Cap",
    "119092": "Axis Bluechip",
    "120841": "Kotak Bluechip",
}

API_URL = "https://api.mfapi.in/mf/{code}"


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def fetch_scheme(code: str, name: str) -> pd.DataFrame | None:
    url = API_URL.format(code=code)
    try:
        resp = requests.get(url, timeout=20)
        resp.raise_for_status()
        payload = resp.json()
    except Exception as exc:
        print(f"  [FAILED] {code} ({name}): {exc}")
        return None

    data = payload.get("data", [])
    if not data:
        print(f"  [EMPTY] {code} ({name}) returned no NAV records")
        return None

    df = pd.DataFrame(data)  # columns: date, nav
    df["amfi_code"] = code
    df["scheme_name"] = payload.get("meta", {}).get("scheme_name", name)
    return df


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Fetching {len(SCHEMES)} schemes from mfapi.in ...")

    for code, name in SCHEMES.items():
        print(f"\n-> {code}: {name}")
        df = fetch_scheme(code, name)
        if df is None:
            continue

        out_path = RAW_DIR / f"api_{code}_{slugify(name)}.csv"
        df.to_csv(out_path, index=False)
        print(f"   saved {len(df)} rows -> {out_path.relative_to(PROJECT_ROOT)}")

        time.sleep(0.5)  # be polite to the free public API

    print("\nDone. These 6 files are in ADDITION to the 10 provided datasets.")


if __name__ == "__main__":
    main()
