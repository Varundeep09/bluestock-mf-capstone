# Data Dictionary — Bluestock Mutual Fund Analytics Star Schema

This data dictionary documents all tables and fields within the SQLite analytical database (`db/bluestock_mf.db`) and processed data files (`data/processed/`).

---

## Table Summary

| Table Name | Type | Primary Key | Description | Source Dataset |
| :--- | :--- | :--- | :--- | :--- |
| **`dim_fund`** | Dimension | `amfi_code` | Master repository of mutual fund schemes, fund houses, plans, and manager details | `01_fund_master.csv` |
| **`dim_date`** | Dimension | `date_id` | Calendar dimension covering daily date grains, quarters, weekdays, and year attributes | Generated Dimension |
| **`fact_nav`** | Fact | `(amfi_code, date)` | Daily Net Asset Value (NAV) records and calculated daily percentage returns | `02_nav_history.csv` |
| **`fact_transactions`** | Fact | `tx_id` | Granular investor transaction logs across SIP, Lumpsum, and Redemptions | `08_investor_transactions.csv` |
| **`fact_performance`** | Fact | `amfi_code` | Fund risk and return metrics (CAGR, Alpha, Beta, Sharpe, Sortino, Max Drawdown) | `07_scheme_performance.csv` |
| **`fact_portfolio`** | Fact | `(amfi_code, stock_symbol)` | Underlying equity holdings, sector classifications, weights, and market values | `09_portfolio_holdings.csv` |
| **`fact_aum`** | Fact | `(fund_house, date)` | Quarterly Assets Under Management (AUM) history by Asset Management Company (AMC) | `03_aum_by_fund_house.csv` |
| **`fact_sip_industry`** | Fact | `month` | Industry-wide monthly SIP contribution totals, active account counts, and YoY growth | `04_monthly_sip_inflows.csv` |
| **`fact_benchmark`** | Fact | `(index_name, date)` | Historical daily closing values for market benchmark indices (NIFTY50, etc.) | `10_benchmark_indices.csv` |
| **`fact_category_inflows`** | Fact | `(category, month)` | Monthly net capital inflows across SEBI mutual fund categories | `05_category_inflows.csv` |
| **`fact_folio_count`** | Fact | `month` | Quarterly mutual fund folio counts segmented across asset classes | `06_industry_folio_count.csv` |

---

## Detailed Table Schemas

### 1. `dim_fund` (Fund Master Dimension)
*Source File*: `data/raw/01_fund_master.csv` -> `data/processed/clean_fund_master.csv`

| Column Name | SQL Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `amfi_code` | `TEXT` | `PRIMARY KEY` | Unique 6-digit Association of Mutual Funds in India (AMFI) scheme identifier |
| `fund_house` | `TEXT` | `NOT NULL` | Name of the Asset Management Company (AMC) / Fund House |
| `scheme_name` | `TEXT` | `NOT NULL` | Full official name of the mutual fund scheme |
| `category` | `TEXT` | `NOT NULL` | Broad asset class (e.g., Equity, Debt, Hybrid) |
| `sub_category` | `TEXT` | | Specific SEBI classification (e.g., Large Cap, Flexi Cap, Small Cap, Gilt) |
| `plan` | `TEXT` | | Investment plan type (`Regular` vs `Direct`) |
| `launch_date` | `DATE` | | Inception/allotment date of the scheme (`YYYY-MM-DD`) |
| `benchmark` | `TEXT` | | Official benchmark index used to gauge relative performance |
| `expense_ratio_pct` | `REAL` | | Total Expense Ratio (TER) expressed as an annual percentage |
| `exit_load_pct` | `REAL` | | Exit load penalty percentage for early redemptions |
| `min_sip_amount` | `INTEGER` | | Minimum required monthly SIP investment amount (INR) |
| `min_lumpsum_amount` | `INTEGER` | | Minimum required one-time initial lumpsum investment amount (INR) |
| `fund_manager` | `TEXT` | | Lead portfolio manager managing the fund |
| `risk_category` | `TEXT` | | Risk-o-meter rating (`Low`, `Moderate`, `High`, `Very High`) |
| `sebi_category_code` | `TEXT` | | Regulatory category identification code |

---

### 2. `dim_date` (Date Dimension)
*Source*: Generated dynamically across all temporal fact records.

| Column Name | SQL Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `date_id` | `INTEGER` | `PRIMARY KEY` | Surrogate integer key for calendar date |
| `date` | `DATE` | `UNIQUE NOT NULL` | Standard calendar date (`YYYY-MM-DD`) |
| `year` | `INTEGER` | `NOT NULL` | Calendar year (e.g., `2024`) |
| `month` | `INTEGER` | `NOT NULL` | Calendar month integer (`1` to `12`) |
| `quarter` | `INTEGER` | `NOT NULL` | Calendar quarter (`1` to `4`) |
| `day` | `INTEGER` | `NOT NULL` | Day of the month (`1` to `31`) |
| `day_name` | `TEXT` | `NOT NULL` | Name of the day (`Monday`, `Tuesday`, etc.) |
| `month_name` | `TEXT` | `NOT NULL` | Name of the month (`January`, `February`, etc.) |
| `is_weekday` | `INTEGER` | `NOT NULL` | Boolean flag (`1` for Monday–Friday, `0` for Weekend) |

---

### 3. `fact_nav` (Historical Daily NAV Fact)
*Source File*: `data/raw/02_nav_history.csv` -> `data/processed/clean_nav.csv`

| Column Name | SQL Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `amfi_code` | `TEXT` | `PK / FK` | Scheme identifier referencing `dim_fund(amfi_code)` |
| `date` | `DATE` | `PK` | NAV evaluation date (`YYYY-MM-DD`) |
| `nav` | `REAL` | `NOT NULL` | Per-unit Net Asset Value in INR |
| `daily_return_pct` | `REAL` | | Daily percentage return calculated as `(NAV_t / NAV_t-1 - 1) * 100` |

---

### 4. `fact_transactions` (Investor Transactions Fact)
*Source File*: `data/raw/08_investor_transactions.csv` -> `data/processed/clean_transactions.csv`

| Column Name | SQL Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `tx_id` | `TEXT` | `PRIMARY KEY` | Unique transaction reference ID (e.g., `TX000001`) |
| `investor_id` | `TEXT` | `NOT NULL` | Anonymized investor profile identifier |
| `amfi_code` | `TEXT` | `FK` | Scheme identifier referencing `dim_fund(amfi_code)` |
| `transaction_date` | `DATE` | `NOT NULL` | Date when the transaction was executed (`YYYY-MM-DD`) |
| `transaction_type` | `TEXT` | `NOT NULL` | Standardized transaction mode (`SIP`, `Lumpsum`, `Redemption`) |
| `amount_inr` | `INTEGER` | `NOT NULL` | Gross transaction value in Indian Rupees (INR > 0) |
| `state` | `TEXT` | | Indian state of investor residence |
| `city` | `TEXT` | | City of investor residence |
| `city_tier` | `TEXT` | | Geographic classification (`T30` top 30 cities vs `B30` beyond top 30) |
| `age_group` | `TEXT` | | Investor demographic bracket (`18-25`, `26-35`, `36-45`, `46-55`, `56+`) |
| `gender` | `TEXT` | | Investor gender (`Male`, `Female`, `Other`) |
| `annual_income_lakh` | `REAL` | | Self-reported annual income in INR Lakhs |
| `payment_mode` | `TEXT` | | Payment channel (`UPI`, `Net Banking`, `Mandate`, `Cheque`) |
| `kyc_status` | `TEXT` | | Compliance validation status (`Verified`, `Pending`) |

---

### 5. `fact_performance` (Fund Risk & Return Fact)
*Source File*: `data/raw/07_scheme_performance.csv` -> `data/processed/clean_performance.csv`

| Column Name | SQL Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `amfi_code` | `TEXT` | `PK / FK` | Scheme identifier referencing `dim_fund(amfi_code)` |
| `scheme_name` | `TEXT` | `NOT NULL` | Official scheme name |
| `fund_house` | `TEXT` | `NOT NULL` | Asset Management Company name |
| `category` | `TEXT` | `NOT NULL` | Fund asset category |
| `plan` | `TEXT` | | Plan structure (`Regular`, `Direct`) |
| `return_1yr_pct` | `REAL` | | 1-year trailing annualized compound return (%) |
| `return_3yr_pct` | `REAL` | | 3-year trailing annualized compound return (%) |
| `return_5yr_pct` | `REAL` | | 5-year trailing annualized compound return (%) |
| `benchmark_3yr_pct` | `REAL` | | 3-year trailing annualized return of designated benchmark index (%) |
| `alpha` | `REAL` | | Jensen's Alpha measuring excess risk-adjusted return over benchmark |
| `beta` | `REAL` | | Systematic volatility sensitivity relative to benchmark |
| `sharpe_ratio` | `REAL` | | Annualized Sharpe Ratio using Rf = 6.5% |
| `sortino_ratio` | `REAL` | | Sortino Ratio penalizing only downside volatility using Rf = 6.5% |
| `std_dev_ann_pct` | `REAL` | | Annualized standard deviation of daily returns (%) |
| `max_drawdown_pct` | `REAL` | | Peak-to-trough historical maximum portfolio loss (%) |
| `aum_crore` | `REAL` | | Current assets under management (INR Crores) |
| `expense_ratio_pct` | `REAL` | | Current total expense ratio (%) |
| `morningstar_rating` | `INTEGER` | | Independent star rating from 1 to 5 |
| `risk_grade` | `TEXT` | | Qualitative risk grading |

---

### 6. `fact_portfolio` (Portfolio Holdings Fact)
*Source File*: `data/raw/09_portfolio_holdings.csv` -> `data/processed/clean_portfolio.csv`

| Column Name | SQL Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `amfi_code` | `TEXT` | `PK / FK` | Scheme identifier referencing `dim_fund(amfi_code)` |
| `stock_symbol` | `TEXT` | `PK` | Stock ticker symbol traded on NSE/BSE |
| `stock_name` | `TEXT` | | Registered company name |
| `sector` | `TEXT` | | Industry sector (e.g., Banking, IT, Pharma, Auto) |
| `weight_pct` | `REAL` | | Percentage allocation of fund NAV |
| `market_value_cr` | `REAL` | | Absolute position holding value in INR Crores |
| `current_price_inr` | `REAL` | | Latest closing stock price in INR |
| `portfolio_date` | `DATE` | | Portfolio disclosure reporting date |

---

### 7. `fact_aum` (Fund House AUM Fact)
*Source File*: `data/raw/03_aum_by_fund_house.csv` -> `data/processed/clean_aum.csv`

| Column Name | SQL Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `date` | `DATE` | `PK` | Quarter-end disclosure date (`YYYY-MM-DD`) |
| `fund_house` | `TEXT` | `PK` | Asset Management Company name |
| `aum_lakh_crore` | `REAL` | | Total AUM expressed in Lakh Crores INR |
| `aum_crore` | `REAL` | | Total AUM expressed in Crores INR |
| `num_schemes` | `INTEGER` | | Active count of funds managed by AMC |

---

### 8. `fact_sip_industry` (Industry SIP Inflows Fact)
*Source File*: `data/raw/04_monthly_sip_inflows.csv` -> `data/processed/clean_sip_inflows.csv`

| Column Name | SQL Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `month` | `TEXT` | `PRIMARY KEY` | Reporting calendar month (`YYYY-MM`) |
| `sip_inflow_crore` | `REAL` | | Gross monthly SIP contributions in INR Crores |
| `active_sip_accounts_crore`| `REAL` | | Total active SIP accounts in Crores |
| `new_sip_accounts_lakh` | `REAL` | | Newly registered SIP accounts in Lakhs |
| `sip_aum_lakh_crore` | `REAL` | | Total cumulative SIP AUM in Lakh Crores |
| `yoy_growth_pct` | `REAL` | | Year-over-Year percentage change in SIP inflows |

---

### 9. `fact_benchmark` (Benchmark Indices Fact)
*Source File*: `data/raw/10_benchmark_indices.csv` -> `data/processed/clean_benchmark.csv`

| Column Name | SQL Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `date` | `DATE` | `PK` | Trading session date (`YYYY-MM-DD`) |
| `index_name` | `TEXT` | `PK` | Benchmark ticker (e.g., `NIFTY50`, `NIFTYMIDCAP150`) |
| `close_value` | `REAL` | | Daily index closing valuation level |

---

### 10. `fact_category_inflows` (Category Flows Fact)
*Source File*: `data/raw/05_category_inflows.csv` -> `data/processed/clean_category_inflows.csv`

| Column Name | SQL Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `month` | `TEXT` | `PK` | Reporting calendar month (`YYYY-MM`) |
| `category` | `TEXT` | `PK` | Mutual fund category classification |
| `net_inflow_crore` | `REAL` | | Net monthly capital flow (inflow minus outflow) in INR Crores |

---

### 11. `fact_folio_count` (Industry Folio Aggregates Fact)
*Source File*: `data/raw/06_industry_folio_count.csv` -> `data/processed/clean_folio_count.csv`

| Column Name | SQL Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `month` | `TEXT` | `PRIMARY KEY` | Reporting calendar month (`YYYY-MM`) |
| `total_folios_crore` | `REAL` | | Total investor folios in Crores |
| `equity_folios_crore` | `REAL` | | Folios in Equity schemes in Crores |
| `debt_folios_crore` | `REAL` | | Folios in Debt schemes in Crores |
| `hybrid_folios_crore` | `REAL` | | Folios in Hybrid schemes in Crores |
| `others_folios_crore` | `REAL` | | Folios in Index/ETFs/Solution schemes in Crores |
