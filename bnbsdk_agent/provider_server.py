import os
import json
import asyncio
import requests
from dotenv import load_dotenv
from bnbagent.erc8183.server import create_erc8183_app
from bnbagent.wallets import EVMWalletProvider
from bnbagent import X402Signer

# Import your upgraded OOP engine and MCP client
from app.quant.sdme_engine import SDMEEngine
from app.services.cmc_mcp_client import CMCMCPClient
from app.core.schemas import AgentIntent, StrategySpecification

load_dotenv()

# Instantiate the CMC MCP client (API key from env)
cmc_client = CMCMCPClient(api_key=os.getenv("CMC_MCP_API_KEY", "demo_mode"))

# Instantiate your quant engine
engine = SDMEEngine()

def _simulate_execution(allocation: dict, base_currency: str = "USDT"):
    """Print mock trade instructions for the given allocation."""
    print(f"🔧 [Execution Layer]: Simulating on‑chain rebalance to {allocation}...")
    for asset, weight in allocation.items():
        if asset == base_currency:
            continue
        # Assume total portfolio value of 1000 USDT for demo
        trade_value = round(1000 * weight, 2)
        print(f"   ➤ Swap {trade_value} {base_currency} → {asset}")
    print("🔧 [Execution Layer]: Trades would be submitted via BNB SDK SwapTool (gas sponsored).")

def _fetch_market_overview() -> str:
    """Call the official CMC Skill Hub 'daily_market_overview' via MCP."""
    try:
        # Use the existing async client synchronously
        import asyncio
        loop = asyncio.new_event_loop()
        result = loop.run_until_complete(cmc_client._execute_skill("daily_market_overview", {"preview": True}))
        loop.close()
        if result and "error" not in str(result).lower():
            return result[:2000]  # first 2000 chars for the log
        return "Skill returned no content"
    except Exception as e:
        return f"Skill call failed: {e}"

def _fetch_btc_dominance() -> float:
    """Return current BTC Dominance from CMC REST API. Fallback 50."""
    api_key = os.getenv("CMC_MCP_API_KEY")
    if not api_key:
        return 50.0
    url = "https://pro-api.coinmarketcap.com/v1/global-metrics/quotes/latest"
    headers = {"X-CMC_PRO_API_KEY": api_key}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()["data"]
        return float(data.get("btc_dominance", 50.0))
    except Exception as e:
        print(f"⚠️ [Regime] BTC Dominance fetch failed: {e}")
        return 50.0

def on_job(job: dict) -> str:
    """
    This callback is called automatically by the BNB SDK when a FUNDED job
    is assigned to this provider.
    It generates the strategy spec using live CMC data.
    """
    # Correctly extract the jobId
    job_id = job.get('jobId', job.get('id', 'Unknown'))
    print(f"💼 [Provider]: New FUNDED job detected! Job ID: {job.get('id')}")

    # Parse client parameters from the on-chain job description
    try:
        params = json.loads(job.get("description", "{}"))
    except json.JSONDecodeError:
        params = {"risk_profile": "moderate", "max_drawdown": 15.0, "whitelist": ["BTC", "ETH", "BNB"]}

    raw_profile = params.get("risk_profile", "moderate")
    safe_profile = str(raw_profile) if isinstance(raw_profile, (str, int, float)) else "moderate"

    raw_drawdown = params.get("max_drawdown", 15.0)
    safe_drawdown = float(raw_drawdown) if isinstance(raw_drawdown, (str, int, float)) else 15.0

    intent = AgentIntent(
        intent=safe_profile,
        max_drawdown=safe_drawdown
    )
    # Ensure whitelist is passed via intent & Pull whitelist into a strict local list of strings
    raw_whitelist = params.get("whitelist", ["BTC", "ETH", "BNB"])
    whitelist = list(raw_whitelist) if isinstance(raw_whitelist, list) else ["BTC", "ETH", "BNB"]

    # --- B4: x402 Payment Integration Placeholder ---
    # To fetch premium KOL metrics from the Hub, the provider agent
    # authorizes a $0.01 USDC micro-payment via the SDK's X402Signer.
    # wallet = EVMWalletProvider(password=os.getenv("WALLET_PASSWORD"), private_key=os.getenv("PRIVATE_KEY"))
    # signer = X402Signer(wallet, max_value_per_call={"U": 1000000}, session_budget={"U": 50000000})
    # await signer.sign_payment(...)
    # ------------------------------------------------

    # Executing B4 Upgrade without removing the structural placeholders above:
    # --- x402: Purchase premium on-chain data (real payment) ---
    try:
        print("💸 [Provider]: Attempting real x402 payment for premium KOL data...")
        success = cmc_client.purchase_premium_data_x402("BTC")
        if success:
            print("✅ [Provider]: x402 payment executed. Premium data available.")
        else:
            print("⚠️ [Provider]: x402 payment skipped (check network/keys).")
    except Exception as e:
        print(f"⚠️ [Provider]: x402 error: {e}")

    print("📡 [Provider]: Fetching live multi-dimensional data via CMC Hub MCP...")
    # Fetch live data from CMC Hub via MCP
    live_data = cmc_client.get_live_data_sync(whitelist)

    # ========== Strategy dispatch based on job description ==========
    strategy_name = params.get("strategy", "sentiment_divergence")
    print(f"🧠 [Provider]: Selected strategy -> {strategy_name}")

    if strategy_name == "sentiment_divergence":
        spec: StrategySpecification = engine.generate_spec(intent, live_data)
    elif strategy_name == "auto":
        # ---- Market-Regime Switching (Originality) ----
        btc_dom = _fetch_btc_dominance()
        print(f"🌦️ [Regime] Live BTC Dominance = {btc_dom:.2f}%")
        if btc_dom > 60:
            print("🌦️ [Regime] Fearful regime → selecting Funding Rate (Contrarian)")
            from app.quant.funding_rate_strategy import FundingRateStrategy
            strategy_engine = FundingRateStrategy()
            spec = strategy_engine.generate(live_data, intent)
        else:
            print("🌦️ [Regime] Greedy/Neutral regime → selecting Sentiment Divergence (Momentum)")
            spec = engine.generate_spec(intent, live_data)

    elif strategy_name == "funding_rate":
        # ---- Funding Rate / BTC Dominance Contrarian ----
        from app.quant.funding_rate_strategy import FundingRateStrategy
        strategy_engine = FundingRateStrategy()
        spec = strategy_engine.generate(live_data, intent)

    elif strategy_name == "generic":
        # ---- LLM-Authored Strategy (Originality) ----
        print("🧠 [Provider]: Executing LLM-authored strategy from job description...")
        spec_dict = params.get("spec", {})
        if not spec_dict:
            raise ValueError("Generic strategy requires a 'spec' dict in the job description")
        # Build the strategy specification directly from the LLM's JSON
        spec = StrategySpecification(**spec_dict)  # type: ignore[arg-type]
    else:
        print(f"⚠️ [Provider]: Unknown strategy '{strategy_name}', falling back to sentiment_divergence")
        spec = engine.generate_spec(intent, live_data)

    # --- Consume pre-built CMC Skill (Best Use of Agent Hub) ---
    print("📡 [Provider]: Invoking CMC Skill Hub 'daily_market_overview'...")
    market_overview = _fetch_market_overview()
    print(f"📡 [Provider]: Market overview (first 300 chars): {market_overview[:300]}")

    # ========== NEW: Hot‑reload – apply overrides from job params ==========
    # Allow clients to override risk parameters without touching engine code
    if "max_asset_weight" in params:
        raw_weight = params["max_asset_weight"]
        if isinstance(raw_weight, (int, float, str)):
            try:
                new_weight = float(raw_weight)
                updated_rm = spec.risk_management.model_copy(
                    update={"max_asset_weight": new_weight}
                )
                spec.risk_management = updated_rm
                print(f"🔄 [Provider]: Hot‑reload: max_asset_weight set to {updated_rm.max_asset_weight}")
            except (ValueError, TypeError):
                print(f"⚠️ [Provider]: Invalid max_asset_weight value: {raw_weight}")
        else:
            print(f"⚠️ [Provider]: max_asset_weight has unsupported type: {type(raw_weight)}")
    # Additional hot‑reload parameters can be added here in the future.

    _simulate_execution(spec.current_target_allocation)
    print("✅ [Provider]: Strategy generated. Submitting deliverable hash on-chain...")
    # Return deliverable as JSON string (SDK stores it)
    return spec.model_dump_json(indent=2)

# Create the ERC-8183 app (all routes auto-created)
app = create_erc8183_app(on_job=on_job)
