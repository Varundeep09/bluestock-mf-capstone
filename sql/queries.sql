-- Bluestock MF Capstone -- 10 Business Analytical Queries (Day 2, Task 4)
-- Executable against db/bluestock_mf.db

-- ==============================================================================
-- Query 1: Top 5 Fund Houses by Peak AUM
-- Business Goal: Identify market leaders and their peak managed asset size.
-- ==============================================================================
SELECT fund_house,
       MAX(aum_crore) AS peak_aum_crore,
       MAX(aum_lakh_crore) AS peak_aum_lakh_crore
FROM fact_aum
GROUP BY fund_house
ORDER BY peak_aum_crore DESC
LIMIT 5;


-- ==============================================================================
-- Query 2: Monthly Average NAV for Key Benchmark Schemes
-- Business Goal: Track monthly average valuation trend per fund.
-- ==============================================================================
SELECT amfi_code,
       strftime('%Y-%m', date) AS month,
       ROUND(AVG(nav), 4) AS avg_nav,
       ROUND(MIN(nav), 4) AS min_nav,
       ROUND(MAX(nav), 4) AS max_nav
FROM fact_nav
GROUP BY amfi_code, month
ORDER BY amfi_code, month
LIMIT 10;


-- ==============================================================================
-- Query 3: Industry Monthly SIP Inflow & YoY Growth Trend
-- Business Goal: Analyze retail investor systematic participation and growth.
-- ==============================================================================
SELECT month,
       sip_inflow_crore,
       active_sip_accounts_crore,
       new_sip_accounts_lakh,
       ROUND(yoy_growth_pct, 2) AS yoy_growth_pct
FROM fact_sip_industry
ORDER BY month DESC
LIMIT 10;


-- ==============================================================================
-- Query 4: Geographic State-wise Transaction Volume & Capital Flow
-- Business Goal: Spot geographic clusters driving highest transaction volumes.
-- ==============================================================================
SELECT state,
       COUNT(*) AS total_transactions,
       ROUND(SUM(amount_inr) / 10000000.0, 2) AS total_volume_crore,
       ROUND(AVG(amount_inr), 2) AS avg_ticket_size_inr
FROM fact_transactions
GROUP BY state
ORDER BY total_volume_crore DESC
LIMIT 10;


-- ==============================================================================
-- Query 5: Low-Cost Funds (Expense Ratio < 1.0%)
-- Business Goal: Identify cost-efficient Direct/Passive schemes for investors.
-- ==============================================================================
SELECT amfi_code,
       scheme_name,
       fund_house,
       category,
       plan,
       expense_ratio_pct
FROM dim_fund
WHERE expense_ratio_pct < 1.0
ORDER BY expense_ratio_pct ASC
LIMIT 10;


-- ==============================================================================
-- Query 6: Top Funds by Risk-Adjusted Return (Sortino Ratio & Downside Protection)
-- Business Goal: Highlight schemes offering superior downside-adjusted performance.
-- ==============================================================================
SELECT f.scheme_name,
       f.category,
       f.fund_house,
       p.sortino_ratio,
       p.sharpe_ratio,
       p.alpha,
       p.max_drawdown_pct
FROM fact_performance p
JOIN dim_fund f ON f.amfi_code = p.amfi_code
ORDER BY p.sortino_ratio DESC
LIMIT 5;


-- ==============================================================================
-- Query 7: T30 vs B30 City Tier Transaction & Volume Distribution
-- Business Goal: Measure financial inclusion penetration between metro (T30) and beyond-metro (B30) markets.
-- ==============================================================================
SELECT city_tier,
       transaction_type,
       COUNT(*) AS transaction_count,
       ROUND(SUM(amount_inr) / 10000000.0, 2) AS total_volume_crore,
       ROUND(AVG(amount_inr), 2) AS avg_ticket_size_inr
FROM fact_transactions
GROUP BY city_tier, transaction_type
ORDER BY city_tier, total_volume_crore DESC;


-- ==============================================================================
-- Query 8: Category-wise Net Inflow Trends & Retail Investor Preference
-- Business Goal: Determine which asset classes (Large Cap, Mid Cap, Small Cap, etc.) attract highest net liquidity.
-- ==============================================================================
SELECT category,
       ROUND(SUM(net_inflow_crore), 2) AS total_net_inflow_crore,
       ROUND(AVG(net_inflow_crore), 2) AS avg_monthly_inflow_crore,
       COUNT(DISTINCT month) AS observed_months
FROM fact_category_inflows
GROUP BY category
ORDER BY total_net_inflow_crore DESC;


-- ==============================================================================
-- Query 9: Industry Folio Growth Rate & Equity vs Debt Folio Expansion
-- Business Goal: Track long-term retail folio migration towards equity vs debt instruments.
-- ==============================================================================
SELECT month,
       total_folios_crore,
       equity_folios_crore,
       debt_folios_crore,
       hybrid_folios_crore,
       ROUND((equity_folios_crore / total_folios_crore) * 100, 2) AS equity_folio_share_pct
FROM fact_folio_count
ORDER BY month DESC
LIMIT 10;


-- ==============================================================================
-- Query 10: Top Sectoral Holdings Allocation Across Portfolios
-- Business Goal: Assess systemic sectoral exposure and concentration risk across mutual fund schemes.
-- ==============================================================================
SELECT sector,
       COUNT(DISTINCT stock_symbol) AS unique_stocks,
       COUNT(DISTINCT amfi_code) AS fund_count,
       ROUND(SUM(market_value_cr), 2) AS total_allocated_cr,
       ROUND(AVG(weight_pct), 2) AS avg_holding_weight_pct
FROM fact_portfolio
GROUP BY sector
ORDER BY total_allocated_cr DESC
LIMIT 10;
