-- Bluestock MF Capstone -- Star Schema (SQLite)
-- Schema fully adapted to real dataset column names and types.

PRAGMA foreign_keys = ON;

-- ============ DIMENSION TABLES ============

CREATE TABLE IF NOT EXISTS dim_fund (
    amfi_code           TEXT PRIMARY KEY,
    fund_house          TEXT NOT NULL,
    scheme_name         TEXT NOT NULL,
    category            TEXT NOT NULL,
    sub_category        TEXT,
    plan                TEXT,
    launch_date         DATE,
    benchmark           TEXT,
    expense_ratio_pct   REAL,
    exit_load_pct       REAL,
    min_sip_amount      INTEGER,
    min_lumpsum_amount  INTEGER,
    fund_manager        TEXT,
    risk_category       TEXT,
    sebi_category_code  TEXT
);

CREATE TABLE IF NOT EXISTS dim_date (
    date_id     INTEGER PRIMARY KEY,
    date        DATE UNIQUE NOT NULL,
    year        INTEGER NOT NULL,
    month       INTEGER NOT NULL,
    quarter     INTEGER NOT NULL,
    day         INTEGER NOT NULL,
    day_name    TEXT NOT NULL,
    month_name  TEXT NOT NULL,
    is_weekday  INTEGER NOT NULL
);

-- ============ FACT TABLES ============

CREATE TABLE IF NOT EXISTS fact_nav (
    amfi_code           TEXT NOT NULL,
    date                DATE NOT NULL,
    nav                 REAL NOT NULL,
    daily_return_pct    REAL,
    PRIMARY KEY (amfi_code, date),
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

CREATE TABLE IF NOT EXISTS fact_transactions (
    tx_id               TEXT PRIMARY KEY,
    investor_id         TEXT NOT NULL,
    amfi_code           TEXT NOT NULL,
    transaction_date    DATE NOT NULL,
    transaction_type    TEXT NOT NULL,
    amount_inr          INTEGER NOT NULL,
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
    amfi_code           TEXT PRIMARY KEY,
    scheme_name         TEXT NOT NULL,
    fund_house          TEXT NOT NULL,
    category            TEXT NOT NULL,
    plan                TEXT,
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
    aum_crore           REAL,
    expense_ratio_pct   REAL,
    morningstar_rating  INTEGER,
    risk_grade          TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

CREATE TABLE IF NOT EXISTS fact_portfolio (
    amfi_code           TEXT NOT NULL,
    stock_symbol        TEXT NOT NULL,
    stock_name          TEXT,
    sector              TEXT,
    weight_pct          REAL,
    market_value_cr     REAL,
    current_price_inr   REAL,
    portfolio_date      DATE,
    PRIMARY KEY (amfi_code, stock_symbol),
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

CREATE TABLE IF NOT EXISTS fact_aum (
    date                DATE NOT NULL,
    fund_house          TEXT NOT NULL,
    aum_lakh_crore      REAL,
    aum_crore           REAL,
    num_schemes         INTEGER,
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
    date                DATE NOT NULL,
    index_name          TEXT NOT NULL,
    close_value         REAL NOT NULL,
    PRIMARY KEY (index_name, date)
);

CREATE TABLE IF NOT EXISTS fact_category_inflows (
    month               TEXT NOT NULL,
    category            TEXT NOT NULL,
    net_inflow_crore    REAL,
    PRIMARY KEY (category, month)
);

CREATE TABLE IF NOT EXISTS fact_folio_count (
    month               TEXT PRIMARY KEY,
    total_folios_crore  REAL,
    equity_folios_crore REAL,
    debt_folios_crore   REAL,
    hybrid_folios_crore REAL,
    others_folios_crore REAL
);

-- ============ INDEXES ============
CREATE INDEX IF NOT EXISTS idx_fact_nav_date ON fact_nav(date);
CREATE INDEX IF NOT EXISTS idx_fact_nav_amfi ON fact_nav(amfi_code);
CREATE INDEX IF NOT EXISTS idx_fact_tx_date ON fact_transactions(transaction_date);
CREATE INDEX IF NOT EXISTS idx_fact_tx_state ON fact_transactions(state);
CREATE INDEX IF NOT EXISTS idx_fact_tx_amfi ON fact_transactions(amfi_code);
CREATE INDEX IF NOT EXISTS idx_fact_portfolio_amfi ON fact_portfolio(amfi_code);
CREATE INDEX IF NOT EXISTS idx_fact_benchmark_name ON fact_benchmark(index_name);
