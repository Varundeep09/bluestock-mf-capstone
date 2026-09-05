"""
Day 4 stub: Fund performance & risk metrics (CAGR, Sharpe, Sortino, Alpha, Beta,
Max Drawdown). Left as a stub until we've inspected the real column names from
data_ingestion.py's output -- filling this in blind from the PDF risks getting
column names wrong.

Formulas we will implement here (per the project spec):
    daily_return   = nav_t / nav_t-1 - 1
    annual_return  = (1 + daily_return).prod() ** (252 / n) - 1
    CAGR           = (NAV_end / NAV_start) ** (1 / years) - 1
    Sharpe         = (Rp - Rf) / std(Rp) * sqrt(252),  Rf = 6.5%
    Sortino        = (Rp - Rf) / downside_std(Rp) * sqrt(252)
    Alpha, Beta    = scipy.stats.linregress(benchmark_returns, fund_returns)
                     Alpha = intercept * 252, Beta = slope
    Max Drawdown   = min(NAV / NAV.cummax() - 1)

TODO (after Day 1 output is reviewed):
    1. Load data/processed/clean_nav.csv and data/processed/clean_benchmark.csv
    2. Compute the metrics above per amfi_code
    3. Write results to data/processed/fund_scorecard.csv
"""

RISK_FREE_RATE = 0.065  # RBI repo-rate proxy, per project spec
TRADING_DAYS_PER_YEAR = 252

if __name__ == "__main__":
    print("compute_metrics.py is a stub. Implement after Day 1 data profiling is reviewed.")
