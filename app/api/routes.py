import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException

from app.core.schemas import (
    AgentIntent,
    StrategySpecification,
    ExecutionRules,
    RiskManagement,
    SimulationMetrics
)
from app.core.x402_auth import verify_x402_payment
from app.services.cmc_client import fetch_market_data
from app.quant.sdme_engine import compute_sdme_allocations, generate_execution_rules
from app.quant.backtester import run_digital_twin_simulation

router = APIRouter()

@router.post("/skill/generate_strategy", response_model=StrategySpecification)
async def generate_strategy(
    intent: AgentIntent,
    payment_receipt: str = Depends(verify_x402_payment)
):
    """
    Core MCP Endpoint for Track 2.
    Requires a valid x402 payment receipt header to execute the quant engine.
    """
    try:
        # 1. Data Hydration: Fetch live (or fallback synthetic) CMC data
        market_data = await fetch_market_data()

        # 2. Alpha Generation: Run the math engine to get proportional allocations
        allocations = compute_sdme_allocations(market_data, max_assets=4)

        # 3. Digital Twin: Simulate the portfolio against historical paths
        simulation_results = run_digital_twin_simulation(allocations, window_days=30)

        # 4. JSON Contract: Construct the strictly validated Pydantic response
        strategy_spec = StrategySpecification(
            strategy_spec_id=f"NCAE-SDME-{uuid.uuid4().hex[:8].upper()}",
            generated_at=datetime.now(timezone.utc),
            name="Sentiment-Divergence Momentum",
            target_universe="CMC_BEP20_WHITELIST",
            rebalance_frequency="12H",
            execution_rules=ExecutionRules(**generate_execution_rules()),
            risk_management=RiskManagement(
                max_asset_weight=0.50,
                # Converts the user's integer intent (e.g., 15) to a float percentage (0.15)
                portfolio_drawdown_limit=intent.max_drawdown / 100.0,
                base_currency="USDT"
            ),
            current_target_allocation=allocations,
            simulation_metrics=SimulationMetrics(**simulation_results)
        )

        return strategy_spec

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Quant Engine Execution Failed: {str(e)}"
        )
