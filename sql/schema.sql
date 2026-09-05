-- Bluestock MF Capstone -- Star Schema (SQLite)
-- Mirrors project spec section 4.1 (8 tables: 2 dimension + 6 fact)
-- Column names here are a starting point; confirm/adjust once
-- data_ingestion.py shows the real raw column names.

PRAGMA foreign_keys = ON;

-- ============ DIMENSION TABLES ============

CREATE TABLE IF NOT EXISTS dim_fund (
    amfi_code           TEXT PRIMARY KEY,
    fund_house          TEXT,
    scheme_name         TEXT,
    category            TEXT,
    sub_category        TEXT,
    plan                TEXT,
    launch_date         DATE,
    benchmark           TEXT,
    expense_ratio_pct   REAL,
    exit_load_pct       REAL,
    fund_manager        TEXT,
    risk_category       TEXT,
    sebi_category_code  TEXT
);

CREATE TABLE IF NOT EXISTS dim_date (
    date_id     INTEGER PRIMARY KEY,
    date        DATE UNIQUE,
    year        INTEGER,
    month       INTEGER,
    quarter     INTEGER,
    is_weekday  INTEGER
);

-- ============ FACT TABLES ============

CREATE TABLE IF NOT EXISTS fact_nav (
    amfi_code       TEXT,
    date            DATE,
    nav             REAL,
    daily_return_pct REAL,
    PRIMARY KEY (amfi_code, date),
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

CREATE TABLE IF NOT EXISTS fact_transactions (
    tx_id               TEXT PRIMARY KEY,
    investor_id         TEXT,
    amfi_code           TEXT,
    transaction_date    DATE,
    transaction_type    TEXT,
    amount_inr          INTEGER,
    state               TEXT,
    city                TEXT,
    city_tier           TEXT,
    age_group           TEXT,
    gender              TEXT,
    annual_income_lakh  REAL,
    payment_mode        TEXT,
    kyc_status          TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

CREATE TABLE IF NOT EXISTS fact_performance (
    amfi_code           TEXT,
    as_of_date          DATE,
    return_1yr_pct      REAL,
    return_3yr_pct      REAL,
    return_5yr_pct      REAL,
    benchmark_3yr_pct   REAL,
    alpha               REAL,
    beta                REAL,
    sharpe_ratio        REAL,
    sortino_ratio       REAL,
    std_dev_ann_pct     REAL,
    max_drawdown_pct    REAL,
    morningstar_rating  INTEGER,
    PRIMARY KEY (amfi_code, as_of_date),
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

CREATE TABLE IF NOT EXISTS fact_portfolio (
    amfi_code     TEXT,
    stock_symbol  TEXT,
    weight_pct    REAL,
    sector        TEXT,
    date          DATE,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

CREATE TABLE IF NOT EXISTS fact_aum (
    fund_house    TEXT,
    date          DATE,
    aum_crore     REAL,
    num_schemes   INTEGER,
    PRIMARY KEY (fund_house, date)
);

CREATE TABLE IF NOT EXISTS fact_sip_industry (
    month                       TEXT PRIMARY KEY,
    sip_inflow_crore            REAL,
    active_sip_accounts_crore   REAL,
    new_sip_accounts_lakh       REAL,
    sip_aum_lakh_crore          REAL,
    yoy_growth_pct              REAL
);

CREATE TABLE IF NOT EXISTS fact_benchmark (
    index_name  TEXT,
    date        DATE,
    close_value REAL,
    PRIMARY KEY (index_name, date)
);

-- Indexes for common join/filter patterns
CREATE INDEX IF NOT EXISTS idx_fact_nav_date ON fact_nav(date);
CREATE INDEX IF NOT EXISTS idx_fact_tx_date ON fact_transactions(transaction_date);
CREATE INDEX IF NOT EXISTS idx_fact_tx_state ON fact_transactions(state);
