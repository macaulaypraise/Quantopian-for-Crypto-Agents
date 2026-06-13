from datetime import datetime, timezone
from typing import Dict, Literal
from pydantic import BaseModel, Field, field_validator

class AgentIntent(BaseModel):
    """
    Input schema representing the calling agent's raw investment parameters.
    Parsed out of natural language by the orchestrator or received directly via POST.
    """
    intent: str = Field(
        ...,
        description="Natural language trading or narrative investment objective."
    )
    max_drawdown: float = Field(
        default=15.0,
        ge=1.0,
        le=30.0,
        description="Maximum acceptable drawdown percentage before risk engine triggers."
    )


class ExecutionRules(BaseModel):
    """
    Deterministic parameters governing automated strategy adjustments.
    """
    entry_logic: Dict[str, str] = Field(
        ...,
        description="Mathematical conditions required to allocate capital into assets."
    )
    exit_logic: Dict[str, str] = Field(
        ...,
        description="Conditions forcing immediate liquidation back to base currency."
    )


class RiskManagement(BaseModel):
    """
    Guardrails enforcing safety constraints across the generated portfolio asset array.
    """
    max_asset_weight: float = Field(
        ...,
        ge=0.01,
        le=1.0,
        description="Maximum allocation weight limit allowed for any single token."
    )
    portfolio_drawdown_limit: float = Field(
        ...,
        ge=0.01,
        le=0.30,
        description="Hard stop drawdown threshold relative to initial capital simulation."
    )
    base_currency: Literal["USDT", "USDC", "FDUSD"] = Field(
        ...,
        description="The low-volatility settlement stablecoin token used as a safe haven."
    )


class SimulationMetrics(BaseModel):
    """
    Backtesting outputs computed deterministically via the Digital Twin engine.
    """
    backtest_window_days: int = Field(
        ...,
        ge=7,
        le=365,
        description="The window of historical data evaluated during vector simulation."
    )
    simulated_sharpe_ratio: float = Field(
        ...,
        description="Risk-adjusted return profile metric of the narrative basket."
    )
    max_drawdown_observed: float = Field(
        ...,
        description="Maximum peak-to-trough capital reduction witnessed during backtest."
    )
    win_rate: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="The percentage of profitable historical periods within the backtest window."
    )


class StrategySpecification(BaseModel):
    """
    The immutable API contract delivered back to the consumer agent upon successful x402 payment.
    Ensures absolute data integrity without database overhead.
    """
    strategy_spec_id: str = Field(
        ...,
        description="Unique alphanumeric string identifying this strategy snapshot."
    )
    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="ISO timestamp marking when the strategy math was executed."
    )
    name: str = Field(
        ...,
        description="Descriptive structural name of the tailored narrative strategy."
    )
    target_universe: Literal["CMC_BEP20_WHITELIST"] = Field(
        ...,
        description="The strict regulatory boundary limiting asset options to the 149 whitelisted tokens."
    )
    rebalance_frequency: str = Field(
        default="12H",
        description="The frequency required for target allocation recalculation."
    )
    execution_rules: ExecutionRules
    risk_management: RiskManagement
    current_target_allocation: Dict[str, float] = Field(
        ...,
        description="Token symbols mapped to exact mathematical percentage weights."
    )
    simulation_metrics: SimulationMetrics

    @field_validator("current_target_allocation")
    @classmethod
    def validate_allocation_sum(cls, weights: Dict[str, float]) -> Dict[str, float]:
        """
        Enforces floating point safety. Total allocation weights must sum to
        exactly 1.0 (100%) within a narrow rounding tolerance.
        """
        if not weights:
            raise ValueError("Target allocation dictionary cannot be empty.")

        total_weight = sum(weights.values())
        if not (0.99 <= total_weight <= 1.01):
            raise ValueError(f"Target allocations must sum to 1.0 (100%), got {total_weight}")

        return weights
