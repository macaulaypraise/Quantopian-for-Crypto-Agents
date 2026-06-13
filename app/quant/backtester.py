import numpy as np
import pandas as pd
from typing import Dict, Any

def run_digital_twin_simulation(
    allocations: Dict[str, float],
    window_days: int = 30,
    simulations: int = 1000
) -> Dict[str, Any]:
    """
    Runs a vectorized Monte Carlo backtest using Geometric Brownian Motion.
    Evaluates the proposed asset allocations across 1,000 synthetic 30-day market paths.
    """

    # 1. Define Baseline Crypto Volatility Profiles
    # In a production environment, these are derived from real historical standard deviations.
    # For the stateless hackathon simulation, we mock realistic daily volatility (e.g., 5% daily std dev).
    daily_mu = 0.001  # Slight positive drift (0.1% per day)
    daily_sigma = 0.05  # 5% daily volatility

    num_assets = len(allocations)
    weights = np.array(list(allocations.values()))

    # 2. Simulate Asset Returns (GBM Matrix)
    # Shape: (Simulations, Window Days, Num Assets)
    # This generates 1,000 parallel realities of 30-day returns for our selected tokens instantly.
    random_shocks = np.random.normal(
        loc=daily_mu,
        scale=daily_sigma,
        size=(simulations, window_days, num_assets)
    )

    # 3. Calculate Portfolio Returns
    # Multiply the random daily returns by our portfolio weights
    # Shape: (Simulations, Window Days)
    portfolio_daily_returns = np.dot(random_shocks, weights)

    # 4. Calculate Cumulative Equity Curves
    # Start at 1.0 (100% capital). Calculate cumulative product of (1 + R_t)
    cumulative_returns = np.cumprod(1 + portfolio_daily_returns, axis=1)

    # 5. Extract Key Metrics across all 1,000 simulations
    final_returns = cumulative_returns[:, -1] - 1.0

    # Win Rate: Percentage of simulations that ended with a positive return
    win_rate = np.mean(final_returns > 0)

    # Max Drawdown Calculation
    # Find the rolling maximum peak for each simulation at every time step
    rolling_peaks = np.maximum.accumulate(cumulative_returns, axis=1)
    drawdowns = (rolling_peaks - cumulative_returns) / rolling_peaks
    max_drawdowns = np.max(drawdowns, axis=1)
    expected_max_drawdown = np.mean(max_drawdowns)

    # Sharpe Ratio Calculation
    # Annualized based on 365 trading days in crypto
    mean_daily_return = np.mean(portfolio_daily_returns)
    std_daily_return = np.std(portfolio_daily_returns)

    if std_daily_return == 0:
        simulated_sharpe = 0.0
    else:
        simulated_sharpe = (mean_daily_return / std_daily_return) * np.sqrt(365)

    # 6. Return strictly typed dictionary mapping to SimulationMetrics Pydantic schema
    return {
        "backtest_window_days": window_days,
        "simulated_sharpe_ratio": round(float(simulated_sharpe), 2),
        "max_drawdown_observed": round(float(expected_max_drawdown), 4),
        "win_rate": round(float(win_rate), 4)
    }

# --- Quick Test Execution ---
if __name__ == "__main__":
    test_allocation = {"FET": 0.40, "TAO": 0.35, "USDT": 0.25}
    results = run_digital_twin_simulation(test_allocation)
    print("Digital Twin Simulation Results:")
    print(results)
