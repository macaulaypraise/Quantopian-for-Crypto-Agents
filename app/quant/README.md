# app/quant/ — Strategy Engine & Backtester

## Modules

### `sdme_engine.py`
The **Sentiment‑Divergence Meta Engine** (SDME).
- Parses raw MCP/REST data and extracts price momentum, social heat,
  on‑chain flow, and derivatives signals.
- Computes z‑scores and a composite alpha.
- Uses softmax weighting to produce a target allocation.
- Generates a `StrategySpecification` with backtest metrics.

### `funding_rate_strategy.py`
The **BTC Dominance Contrarian** strategy (formerly funding‑rate mean
reversion).
- Fetches live BTC Dominance from CMC REST API.
- If dominance > 60% → go short (stablecoins). Else → go long (alt basket).
- Produces a full `StrategySpecification` with its own execution rules.

### `backtester.py`
The **historical walk‑forward backtester**.
- Replaces the original Monte Carlo GBM simulation.
- Fetches daily prices for BTC, ETH, BNB using the CMC CLI (`cmc history`).
- Aligns portfolio weights with the price columns and computes daily returns.
- Returns Sharpe ratio, max drawdown, win rate, cumulative equity curve,
  and start/end values.

All metrics are based on **real historical data**, not synthetic simulations.
