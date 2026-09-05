-- Bluestock MF Capstone -- 10 required analytical queries (Day 2, Task 6)
-- Run against db/bluestock_mf.db once loaded.

-- 1. Top 5 funds by AUM
SELECT fund_house, MAX(aum_crore) AS latest_aum_crore
FROM fact_aum
GROUP BY fund_house
ORDER BY latest_aum_crore DESC
LIMIT 5;

-- 2. Average NAV per month, per fund
SELECT amfi_code,
       strftime('%Y-%m', date) AS month,
       AVG(nav) AS avg_nav
FROM fact_nav
GROUP BY amfi_code, month
ORDER BY amfi_code, month;

-- 3. SIP inflow YoY growth
SELECT month, sip_inflow_crore, yoy_growth_pct
FROM fact_sip_industry
ORDER BY month;

-- 4. Transactions by state
SELECT state,
       COUNT(*) AS num_transactions,
       SUM(amount_inr) AS total_amount_inr
FROM fact_transactions
GROUP BY state
ORDER BY total_amount_inr DESC;

-- 5. Funds with expense ratio < 1%
SELECT amfi_code, scheme_name, fund_house, expense_ratio_pct
FROM dim_fund
WHERE expense_ratio_pct < 1.0
ORDER BY expense_ratio_pct ASC;

-- 6. Top 10 funds by 3yr Sharpe ratio
SELECT f.scheme_name, f.fund_house, p.sharpe_ratio, p.return_3yr_pct
FROM fact_performance p
JOIN dim_fund f ON f.amfi_code = p.amfi_code
ORDER BY p.sharpe_ratio DESC
LIMIT 10;

-- 7. SIP vs Lumpsum vs Redemption split (overall)
SELECT transaction_type,
       COUNT(*) AS num_tx,
       SUM(amount_inr) AS total_amount_inr
FROM fact_transactions
GROUP BY transaction_type;

-- 8. Investor age-group vs average SIP amount
SELECT age_group, AVG(amount_inr) AS avg_amount_inr
FROM fact_transactions
WHERE transaction_type = 'SIP'
GROUP BY age_group
ORDER BY avg_amount_inr DESC;

-- 9. Funds underperforming their benchmark (negative alpha)
SELECT f.scheme_name, f.benchmark, p.alpha, p.return_3yr_pct, p.benchmark_3yr_pct
FROM fact_performance p
JOIN dim_fund f ON f.amfi_code = p.amfi_code
WHERE p.alpha < 0
ORDER BY p.alpha ASC;

-- 10. Category-wise net inflow trend (latest month per category)
-- NOTE: adapt table/column names once category_inflows is loaded into a fact table.
-- SELECT category, month, net_inflow_crore FROM fact_category_inflows ORDER BY month, category;
