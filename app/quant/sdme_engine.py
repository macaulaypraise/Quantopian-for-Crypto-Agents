import pandas as pd
import numpy as np
from typing import Dict, Any, List
from datetime import datetime, timezone
import uuid
import re

from app.core.schemas import AgentIntent, StrategySpecification, ExecutionRules, RiskManagement, SimulationMetrics
from app.quant.backtester import run_digital_twin_simulation

# --- Helper for Execution Rules ---
def generate_execution_rules() -> Dict[str, Dict[str, str]]:
    return {
        "entry_logic": {"condition_1": "S_zscore > 1.0", "condition_2": "M_zscore < 0.5", "action": "allocate_capital"},
        "exit_logic": {"condition_1": "S_zscore < -1.0", "condition_2": "M_zscore > 1.5", "action": "liquidate_to_base"}
    }

class SDMEEngine:
    def compute_allocations(self, market_data: List[Dict], max_assets: int = 4, social_sentiment_base: float = 0.0, macro_risk_penalty: float = 0.0) -> Dict[str, float]:
        """
        Unified Math Engine. Computes allocations for both the new MCP pipeline and the legacy fallback routes.
        Safely defaults missing advanced dimensions (on-chain/derivatives) to 0 if fed legacy REST data.
        """
        df = pd.DataFrame(market_data)
        df = df[df['volume_24h'] >= 5_000_000].copy()

        if df.empty:
            return {"USDT": 1.0}

        df['M_zscore'] = (df['price_momentum'] - df['price_momentum'].mean()) / df['price_momentum'].std()
        df['S_zscore'] = (df['social_heat'] - df['social_heat'].mean()) / df['social_heat'].std()

        # Handle legacy inputs gracefully by checking if the advanced columns exist
        if 'onchain_flow' in df.columns:
            df['onchain_flow_z'] = (df['onchain_flow'] - df['onchain_flow'].mean()) / df['onchain_flow'].std()
        else:
            df['onchain_flow_z'] = 0.0

        if 'oi_growth' in df.columns:
            df['oi_growth_z'] = (df['oi_growth'] - df['oi_growth'].mean()) / df['oi_growth'].std()
        else:
            df['oi_growth_z'] = 0.0

        df.fillna(0.0, inplace=True)
        w1, w2, w3, w4 = 0.4, 0.2, 0.2, 0.2

        df['alpha'] = (
            w1 * ((df['S_zscore'] + social_sentiment_base) - df['M_zscore']) +
            w2 * df['onchain_flow_z'] +
            w3 * df['oi_growth_z'] +
            w4 * macro_risk_penalty
        )

        top_assets = df.sort_values(by='alpha', ascending=False).head(max_assets).copy()
        exp_alpha = np.exp(top_assets['alpha'])
        top_assets['weight'] = exp_alpha / exp_alpha.sum()
        allocations = top_assets.set_index('ticker')['weight'].to_dict()

        clean_allocations = {k: round(v, 4) for k, v in allocations.items()}
        difference = 1.0 - sum(clean_allocations.values())

        if difference != 0 and clean_allocations:
            first_key = list(clean_allocations.keys())[0]
            clean_allocations[first_key] = round(clean_allocations[first_key] + difference, 4)

        return clean_allocations

    def generate_spec(self, intent: AgentIntent, live_data: Dict[str, Any], max_assets: int = 4) -> StrategySpecification:
        """
        Agent Hub Pipeline: Parses unstructured MCP data, runs the unified math engine, and outputs the Pydantic spec.
        """
        whitelist = getattr(intent, 'whitelist', ["BTC", "ETH", "BNB"])

        fear_greed_score = self._extract_numerical_value(live_data.get("global", ""), default=50.0)
        macro_risk_penalty = self._extract_numerical_value(live_data.get("macro", ""), default=0.0)
        social_sentiment_base = (fear_greed_score - 50.0) / 50.0

        matrix_data = []
        for ticker in whitelist:
            matrix_data.append({
                "ticker": ticker,
                "price_momentum": self._extract_numerical_value(live_data.get("quotes", ""), default=np.random.uniform(-5, 15)),
                "social_heat": self._extract_numerical_value(live_data.get("trending", ""), default=np.random.uniform(10, 90)),
                "volume_24h": self._extract_numerical_value(live_data.get("quotes", ""), default=np.random.uniform(1_000_000, 500_000_000)),
                "onchain_flow": self._extract_numerical_value(live_data.get("onchain", ""), default=np.random.uniform(-100, 500)),
                "oi_growth": self._extract_numerical_value(live_data.get("derivatives", ""), default=np.random.uniform(-2, 8))
            })

        # Execute the unified math method instead of redundant code
        clean_allocations = self.compute_allocations(matrix_data, max_assets, social_sentiment_base, macro_risk_penalty)

        simulation_results = run_digital_twin_simulation(clean_allocations, window_days=30)

        return StrategySpecification(
            strategy_spec_id=f"NCAE-SDME-{uuid.uuid4().hex[:8].upper()}",
            generated_at=datetime.now(timezone.utc),
            name="Composite Sentiment-Divergence",
            target_universe="CMC_BEP20_WHITELIST",
            rebalance_frequency="12H",
            execution_rules=ExecutionRules(**generate_execution_rules()),
            risk_management=RiskManagement(
                max_asset_weight=0.50,
                portfolio_drawdown_limit=getattr(intent, 'max_drawdown', 15.0) / 100.0,
                base_currency="USDT"
            ),
            current_target_allocation=clean_allocations,
            simulation_metrics=SimulationMetrics(**simulation_results)
        )

    def _extract_numerical_value(self, mcp_text: Any, default: float) -> float:
        if isinstance(mcp_text, (int, float)):
            return float(mcp_text)
        if isinstance(mcp_text, str):
            match = re.search(r"[-+]?\d*\.\d+|\d+", mcp_text)
            if match:
                return float(match.group())
        return default
