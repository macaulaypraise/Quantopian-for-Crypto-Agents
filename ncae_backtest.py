# ncae_backtest.py
import sys
import os
from dotenv import load_dotenv

load_dotenv()

from app.quant.sdme_engine import SDMEEngine
from app.services.cmc_mcp_client import CMCMCPClient
from app.core.schemas import AgentIntent

def main():
    print("📊 [NCAE CLI]: Initiating historical backtest sequence...")

    # 1. Fetch live data via MCP (or REST)
    api_key = os.getenv("CMC_MCP_API_KEY")
    if not api_key:
        print("❌ CMC_MCP_API_KEY not set in .env")
        return
    cmc_client = CMCMCPClient(api_key=api_key)
    # Use a default whitelist
    whitelist = ["BTC", "ETH", "BNB"]
    print("⚙️ [NCAE CLI]: Fetching live market data from CMC...")
    live_data = cmc_client.get_live_data_sync(whitelist)

    # 2. Generate strategy allocation using the engine
    engine = SDMEEngine()
    intent = AgentIntent(intent="moderate", max_drawdown=15.0)
    spec = engine.generate_spec(intent, live_data)


    alloc = spec.current_target_allocation
    metrics = spec.simulation_metrics  # still from the spec, but now we'll also get the series from the engine

    # Re‑run backtest separately to get the series (or better, modify generate_spec to include series)
    # For simplicity, we'll call the backtester directly with the allocation
    from app.quant.backtester import run_historical_backtest
    bt_result = run_historical_backtest(alloc, 30)

    print("\n" + "="*50)
    print(f"📈 HISTORICAL BACKTEST RESULTS ({bt_result['backtest_window_days']}-DAY WINDOW):")
    print(f"   • Allocation: {alloc}")
    print(f"   • Start Value: ${bt_result['start_value']:.2f}  →  End Value: ${bt_result['end_value']:.2f}")
    print(f"   • Sharpe Ratio:           {bt_result['simulated_sharpe_ratio']}")
    print(f"   • Max Drawdown:           {bt_result['max_drawdown_observed']*100:.2f}%")
    print(f"   • Win Rate:               {bt_result['win_rate']*100:.1f}%")
    print(f"   • Equity Curve (daily):")
    # Simple text chart: each * represents ~1% return
    cum = bt_result['cumulative_returns']
    # Scale so that the max height is 20 stars
    max_cum = max(cum)
    min_cum = min(cum)
    for val in cum:
        # Normalize to 0-20 stars
        stars = int(20 * (val - min_cum) / (max_cum - min_cum)) if max_cum > min_cum else 0
        print(f"     {stars * '▐'}")
    print("="*50)
    print("✅ [NCAE CLI]: Backtest complete. Real data, real metrics.")

if __name__ == "__main__":
    main()
