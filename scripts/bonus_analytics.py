"""
Bonus Challenges:
  B3: Monte Carlo 5-Year NAV Projections with Geometric Brownian Motion (GBM)
  B4: Markowitz Modern Portfolio Theory & Efficient Frontier Optimization
"""

from pathlib import Path
import sqlite3
import pandas as pd
import numpy as np
import scipy.optimize as sco
import matplotlib.pyplot as plt
import seaborn as sns

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "db" / "bluestock_mf.db"
if not DB_PATH.exists() and (PROJECT_ROOT / "db" / "bluestock_mf.db").exists():
    DB_PATH = PROJECT_ROOT / "db" / "bluestock_mf.db"

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
REPORTS_DIR = PROJECT_ROOT / "reports"

RISK_FREE_RATE = 0.065
TRADING_DAYS_PER_YEAR = 252

plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")


# =============================================================================
# BONUS B3: MONTE CARLO 5-YEAR NAV PROJECTION
# =============================================================================
def run_monte_carlo():
    print("=" * 75)
    print("BONUS B3: MONTE CARLO 5-YEAR NAV SIMULATION (1,000 PATHS)")
    print("=" * 75)

    conn = sqlite3.connect(DB_PATH)
    nav_df = pd.read_sql_query("SELECT amfi_code, date, nav FROM fact_nav ORDER BY amfi_code, date", conn)
    fund_df = pd.read_sql_query("SELECT amfi_code, scheme_name, category FROM dim_fund", conn)
    conn.close()

    # 3 Representative funds: Equity, Debt, Gilt/Liquid
    target_funds = [
        ("120843", "Equity (Flexi Cap)", "Kotak Flexicap Fund"),
        ("100025", "Debt (Short Term)", "HDFC Short Term Debt Fund"),
        ("119120", "Debt/Gilt", "SBI Magnum Gilt Fund")
    ]

    n_sims = 1000
    n_days = 5 * TRADING_DAYS_PER_YEAR  # 1260 trading days = 5 years
    dt = 1.0 / TRADING_DAYS_PER_YEAR

    fig, axes = plt.subplots(1, 3, figsize=(16, 5), dpi=300, sharey=False)
    summary_records = []

    np.random.seed(42)

    for i, (amfi, cat_label, name) in enumerate(target_funds):
        fund_nav = nav_df[nav_df["amfi_code"] == amfi].sort_values("date")
        s0 = float(fund_nav["nav"].iloc[-1])
        
        # Calculate daily log returns
        log_ret = np.log(fund_nav["nav"] / fund_nav["nav"].shift(1)).dropna()
        mu = float(log_ret.mean() * TRADING_DAYS_PER_YEAR)
        sigma = float(log_ret.std() * np.sqrt(TRADING_DAYS_PER_YEAR))

        # GBM Simulation: S_t = S_0 * exp(cumsum((mu - 0.5*sigma^2)*dt + sigma*sqrt(dt)*Z))
        drift = (mu - 0.5 * sigma ** 2) * dt
        vol = sigma * np.sqrt(dt)
        
        random_shocks = np.random.normal(0, 1, (n_days, n_sims))
        daily_increments = drift + vol * random_shocks
        price_paths = np.vstack([np.ones((1, n_sims)) * s0, s0 * np.exp(np.cumsum(daily_increments, axis=0))])

        # Percentile paths
        p5 = np.percentile(price_paths, 5, axis=1)
        p50 = np.percentile(price_paths, 50, axis=1)
        p95 = np.percentile(price_paths, 95, axis=1)
        years = np.linspace(0, 5, n_days + 1)

        # Plot
        ax = axes[i]
        # Plot 50 random sample paths
        ax.plot(years, price_paths[:, :40], color="#90e0ef", alpha=0.15, linewidth=0.8)
        ax.fill_between(years, p5, p95, color="#0077b6", alpha=0.25, label="5th–95th Percentile Cone")
        ax.plot(years, p50, color="#d62828", linewidth=2.2, label=f"Median Path (₹{p50[-1]:.1f})")

        ax.set_title(f"{name}\n[{cat_label}] | Ann. Vol: {sigma*100:.1f}%", fontsize=11, fontweight="bold")
        ax.set_xlabel("Projection Horizon (Years)", fontweight="bold")
        ax.set_ylabel("Projected NAV (₹)", fontweight="bold")
        ax.legend(loc="upper left", fontsize=8.5)

        summary_records.append({
            "amfi_code": amfi,
            "scheme_name": name,
            "category": cat_label,
            "initial_nav": round(s0, 2),
            "expected_ann_return_pct": round(mu * 100, 2),
            "ann_volatility_pct": round(sigma * 100, 2),
            "projected_5yr_5th_pct_nav": round(p5[-1], 2),
            "projected_5yr_median_nav": round(p50[-1], 2),
            "projected_5yr_95th_pct_nav": round(p95[-1], 2),
            "5yr_median_gain_pct": round(((p50[-1] - s0) / s0) * 100, 2),
        })

    plt.suptitle("5-Year Monte Carlo NAV Projections (1,000 Geometric Brownian Motion Simulations)", fontsize=13, fontweight="bold", y=1.03)
    plt.tight_layout()

    chart_path = REPORTS_DIR / "monte_carlo_projections.png"
    plt.savefig(chart_path, dpi=300)
    plt.close()
    print(f"Chart saved -> {chart_path.relative_to(PROJECT_ROOT)}")

    summary_df = pd.DataFrame(summary_records)
    out_csv = PROCESSED_DIR / "monte_carlo_summary.csv"
    summary_df.to_csv(out_csv, index=False)
    print(f"Summary table saved -> {out_csv.relative_to(PROJECT_ROOT)}")
    print("\nMonte Carlo 5-Year Projection Summary:")
    print(summary_df[["scheme_name", "category", "initial_nav", "projected_5yr_5th_pct_nav", "projected_5yr_median_nav", "projected_5yr_95th_pct_nav", "5yr_median_gain_pct"]].to_string(index=False))
    return summary_df


# =============================================================================
# BONUS B4: MARKOWITZ EFFICIENT FRONTIER OPTIMIZATION
# =============================================================================
def run_markowitz_optimization():
    print("\n" + "=" * 75)
    print("BONUS B4: MARKOWITZ EFFICIENT FRONTIER (5-ASSET OPTIMIZATION)")
    print("=" * 75)

    conn = sqlite3.connect(DB_PATH)
    nav_df = pd.read_sql_query("SELECT amfi_code, date, nav FROM fact_nav ORDER BY amfi_code, date", conn)
    fund_df = pd.read_sql_query("SELECT amfi_code, scheme_name FROM dim_fund", conn)
    conn.close()

    # 5 Diverse funds
    selected_funds = [
        ("119551", "SBI Bluechip (Large Cap)"),
        ("119598", "SBI Small Cap (Small Cap)"),
        ("120843", "Kotak Flexicap (Flexi Cap)"),
        ("100025", "HDFC Short Term (Debt)"),
        ("120507", "ICICI Liquid (Liquid)")
    ]
    amfi_list = [f[0] for f in selected_funds]
    name_map = {f[0]: f[1] for f in selected_funds}

    piv = nav_df[nav_df["amfi_code"].isin(amfi_list)].pivot(index="date", columns="amfi_code", values="nav")
    returns = piv.pct_change().dropna()

    mean_returns = returns.mean() * TRADING_DAYS_PER_YEAR
    cov_matrix = returns.cov() * TRADING_DAYS_PER_YEAR
    num_assets = len(amfi_list)

    def portfolio_performance(weights):
        ret = np.sum(mean_returns * weights)
        vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        return ret, vol

    def neg_sharpe(weights):
        r, v = portfolio_performance(weights)
        return -(r - RISK_FREE_RATE) / v

    def portfolio_vol(weights):
        return portfolio_performance(weights)[1]

    # Constraints: sum(w) = 1, 0 <= w <= 1
    bounds = tuple((0.0, 1.0) for _ in range(num_assets))
    cons_sum = {"type": "eq", "fun": lambda w: np.sum(w) - 1.0}
    init_w = num_assets * [1.0 / num_assets]

    # 1. Maximum Sharpe Ratio Portfolio
    opt_sharpe = sco.minimize(neg_sharpe, init_w, method="SLSQP", bounds=bounds, constraints=cons_sum)
    max_sharpe_weights = opt_sharpe.x
    ret_max_sharpe, vol_max_sharpe = portfolio_performance(max_sharpe_weights)
    max_sharpe_val = (ret_max_sharpe - RISK_FREE_RATE) / vol_max_sharpe

    # 2. Minimum Volatility Portfolio
    opt_min_vol = sco.minimize(portfolio_vol, init_w, method="SLSQP", bounds=bounds, constraints=cons_sum)
    min_vol_weights = opt_min_vol.x
    ret_min_vol, vol_min_vol = portfolio_performance(min_vol_weights)
    min_vol_sharpe = (ret_min_vol - RISK_FREE_RATE) / vol_min_vol

    # 3. Efficient Frontier curve
    target_returns = np.linspace(ret_min_vol * 0.95, mean_returns.max() * 0.98, 50)
    frontier_vols = []
    for target in target_returns:
        cons = (
            {"type": "eq", "fun": lambda w: np.sum(w) - 1.0},
            {"type": "eq", "fun": lambda w: portfolio_performance(w)[0] - target}
        )
        res = sco.minimize(portfolio_vol, init_w, method="SLSQP", bounds=bounds, constraints=cons)
        if res.success:
            frontier_vols.append(res.fun)
        else:
            frontier_vols.append(np.nan)

    # 4. Generate Random Portfolios for visual context
    n_portfolios = 3000
    rand_w = np.random.dirichlet(np.ones(num_assets), size=n_portfolios)
    rand_ret = np.dot(rand_w, mean_returns)
    rand_vol = np.sqrt(np.einsum("ij,jk,ik->i", rand_w, cov_matrix.values, rand_w))
    rand_sharpe = (rand_ret - RISK_FREE_RATE) / rand_vol

    # Plotting
    fig, ax = plt.subplots(figsize=(12, 7), dpi=300)
    scatter = ax.scatter(rand_vol * 100, rand_ret * 100, c=rand_sharpe, cmap="viridis", alpha=0.3, s=10, label="Simulated Portfolios")
    plt.colorbar(scatter, label="Sharpe Ratio (Rf = 6.5%)")

    # Plot Efficient Frontier
    valid_mask = ~np.isnan(frontier_vols)
    ax.plot(np.array(frontier_vols)[valid_mask] * 100, target_returns[valid_mask] * 100, "b-", linewidth=2.8, label="Markowitz Efficient Frontier")

    # Plot Capital Allocation Line (CAL)
    cal_x = np.linspace(0, vol_max_sharpe * 1.4, 50) * 100
    cal_y = (RISK_FREE_RATE + max_sharpe_val * (cal_x / 100)) * 100
    ax.plot(cal_x, cal_y, "r--", linewidth=1.8, label=f"Capital Allocation Line (Max Sharpe = {max_sharpe_val:.2f})")

    # Mark Special Portfolios
    ax.scatter(vol_max_sharpe * 100, ret_max_sharpe * 100, color="#d62828", s=140, marker="*", edgecolors="black", zorder=5, label=f"Max Sharpe ({ret_max_sharpe*100:.1f}%, {vol_max_sharpe*100:.1f}%)")
    ax.scatter(vol_min_vol * 100, ret_min_vol * 100, color="#2ca02c", s=120, marker="D", edgecolors="black", zorder=5, label=f"Min Volatility ({ret_min_vol*100:.1f}%, {vol_min_vol*100:.1f}%)")

    # Mark Individual Assets
    for amfi in amfi_list:
        asset_r = mean_returns[amfi] * 100
        asset_v = np.sqrt(cov_matrix.loc[amfi, amfi]) * 100
        ax.scatter(asset_v, asset_r, color="#1d3557", s=80, marker="o")
        ax.annotate(name_map[amfi], (asset_v, asset_r), xytext=(5, 5), textcoords="offset points", fontsize=8.5, fontweight="bold")

    ax.set_title("Markowitz Modern Portfolio Theory: 5-Asset Efficient Frontier & Capital Allocation Line", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Annualized Volatility (%)", fontweight="bold")
    ax.set_ylabel("Annualized Expected Return (%)", fontweight="bold")
    ax.legend(loc="upper left", frameon=True, fontsize=9)
    plt.tight_layout()

    chart_path = REPORTS_DIR / "efficient_frontier.png"
    plt.savefig(chart_path, dpi=300)
    plt.close()
    print(f"Chart saved -> {chart_path.relative_to(PROJECT_ROOT)}")

    # Prepare optimization results CSV
    weights_df = pd.DataFrame({
        "amfi_code": amfi_list,
        "scheme_name": [name_map[c] for c in amfi_list],
        "max_sharpe_weight_pct": np.round(max_sharpe_weights * 100, 2),
        "min_vol_weight_pct": np.round(min_vol_weights * 100, 2),
    })

    summary_df = pd.DataFrame([
        {
            "portfolio_type": "Maximum Sharpe Ratio",
            "expected_annual_return_pct": round(ret_max_sharpe * 100, 2),
            "annual_volatility_pct": round(vol_max_sharpe * 100, 2),
            "sharpe_ratio": round(max_sharpe_val, 2),
        },
        {
            "portfolio_type": "Minimum Volatility",
            "expected_annual_return_pct": round(ret_min_vol * 100, 2),
            "annual_volatility_pct": round(vol_min_vol * 100, 2),
            "sharpe_ratio": round(min_vol_sharpe, 2),
        }
    ])

    out_csv = PROCESSED_DIR / "portfolio_optimization.csv"
    weights_df.to_csv(out_csv, index=False)
    print(f"Optimization weights saved -> {out_csv.relative_to(PROJECT_ROOT)}")

    print("\nOptimal Portfolio Allocations:")
    print(weights_df.to_string(index=False))
    print("\nPortfolio Performance Metrics:")
    print(summary_df.to_string(index=False))

    return weights_df, summary_df


def main():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    run_monte_carlo()
    run_markowitz_optimization()


if __name__ == "__main__":
    main()
