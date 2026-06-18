# app/ — Quant Engine & Services

This directory contains the core business logic of Neural Capital Allocation Engine (NCAE).

## Subdirectories

- **`core/`**
  Pydantic schemas (`AgentIntent`, `StrategySpecification`, `ExecutionRules`,
  `RiskManagement`, `SimulationMetrics`), environment configuration, and the
  x402 authentication middleware that serves strategies behind a paywall.

- **`quant/`**
  The quant engine itself. See [`app/quant/README.md`](quant/README.md) for
  details on the strategies and backtester.

- **`services/`**
  CMC data clients:
  - `cmc_client.py` — synchronous REST client (fallback / legacy).
  - `cmc_mcp_client.py` — asynchronous MCP client that calls the CMC Agent Hub
    via JSON‑RPC over HTTP, including `execute_skill` for marketplace skills.

- **`api/`**
  FastAPI route definitions for the standalone MCP server (if run separately).

- **`agent_client.py`**
  Autonomous M2M client that demonstrates the x402 paywall flow: sends a
  request, receives HTTP 402, simulates TWAK payment, and retrieves the
  strategy spec.

- **`main.py`**
  FastAPI Gateway application entrypoint
