# app/quant/backtester.py
import numpy as np
import pandas as pd
import requests
import os
from typing import Dict, Any, List
from datetime import datetime, timedelta, timezone

CMC_BASE_URL = "https://pro-api.coinmarketcap.com"

def _fetch_historical_prices(tickers: List[str], days: int = 30) -> pd.DataFrame:
    """
    Fetch daily historical prices from CMC for the given tickers.
    Always returns a DataFrame with columns = tickers, index = date, values = USD price.
    """
    import subprocess, json

    series_dict = {}
    # CMC IDs for BTC, ETH, BNB
    cmc_ids = {"BTC": 1, "ETH": 1027, "BNB": 1839}

    for ticker in tickers:
        cid = cmc_ids.get(ticker.upper())
        if cid is None:
            continue
        try:
            result = subprocess.run(
                ["cmc", "history", "--id", str(cid), "--days", str(days), "-o", "json"],
                capture_output=True, text=True, check=True
            )
            raw = json.loads(result.stdout)
            # The CLI returns a list of quote objects with 'timestamp' and 'price'
            quotes = raw if isinstance(raw, list) else raw.get("data", raw.get("quotes", []))
            date_price = {}
            for q in quotes:
                # CLI returns "timestamp" and "price" (USD)
                ts = q.get("timestamp", "")
                price = q.get("price", q.get("quote", {}).get("USD", {}).get("price"))
                if ts and price is not None:
                    date = ts.split("T")[0]
                    date_price[date] = float(price)
            series = pd.Series(date_price, name=ticker)
            series.index = pd.to_datetime(series.index)
            series_dict[ticker] = series
        except Exception as e:
            print(f"⚠️ CLI history failed for {ticker}: {e}")

    df = pd.DataFrame(series_dict).sort_index().dropna()
    return df

def run_historical_backtest(allocations: Dict[str, float], window_days: int = 30) -> Dict[str, Any]:
    """
    Real historical walk‑forward backtest using CMC daily prices.
    Uses only the actual days where all assets have data (no artificial fill).
    """
    tickers = list(allocations.keys())

    # Fetch raw prices (only overlapping days)
    try:
        price_df = _fetch_historical_prices(tickers, window_days)
    except Exception as e:
        print(f"Historical backtest API error: {e}. Using placeholder.")
        return _placeholder(window_days)

    if price_df.empty or len(price_df) < 3:
        print("Too few overlapping data points – using placeholder.")
        return _placeholder(window_days)

    # Daily returns (percentage change from one valid day to the next)
    returns = price_df.pct_change().dropna()

    # Align weights with the column order
    weights_series = pd.Series(allocations).reindex(returns.columns, fill_value=0.0)
    if weights_series.sum() > 0:
        weights_series /= weights_series.sum()
    else:
        weights_series = pd.Series(0.0, index=returns.columns)

    portfolio_daily_returns = returns.dot(weights_series)


    # print("DEBUG price_df head:\n", price_df.head(10))
    # print("DEBUG returns head:\n", returns.head(10))
    # print("DEBUG portfolio_daily_returns:\n", portfolio_daily_returns.head(10))
    # print("DEBUG max portfolio_daily_return:", portfolio_daily_returns.max())
    # print("DEBUG min portfolio_daily_return:", portfolio_daily_returns.min())

    # Equity curve starting at 1.0
    equity = (1 + portfolio_daily_returns).cumprod()
    equity = pd.Series([1.0] + equity.tolist(), name="equity")
    cum_list = equity.tolist()

    # Metrics (annualised)
    mean_ret = portfolio_daily_returns.mean()
    std_ret = portfolio_daily_returns.std()
    sharpe = (mean_ret / std_ret) * np.sqrt(365) if std_ret != 0 else 0.0

    rolling_max = equity.cummax()
    drawdowns = (rolling_max - equity) / rolling_max
    max_drawdown = drawdowns.max()

    win_rate = (portfolio_daily_returns > 0).mean()

    return {
        "backtest_window_days": len(returns),
        "simulated_sharpe_ratio": round(float(sharpe), 2),
        "max_drawdown_observed": round(float(max_drawdown), 4),
        "win_rate": round(float(win_rate), 4),
        "cumulative_returns": cum_list,
        "start_value": 100.0,
        "end_value": round(100 * cum_list[-1], 2),
    }

def _placeholder(window_days: int) -> Dict[str, Any]:
    return {
        "backtest_window_days": window_days,
        "simulated_sharpe_ratio": 0.0,
        "max_drawdown_observed": 0.0,
        "win_rate": 0.0,
        "cumulative_returns": [1.0],
        "start_value": 100.0,
        "end_value": 100.0,
    }


def run_digital_twin_simulation(allocations: Dict[str, float], window_days: int = 30, simulations: int = 1000) -> Dict[str, Any]:
    """
    Alias for the historical backtest to maintain compatibility with existing imports.
    """
    return run_historical_backtest(allocations, window_days)
