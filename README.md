# 🧠 NCAE — Strategy‑as‑a‑Service on BNB Chain

**Neural Capital Allocation Engine (NCAE)** is a decentralized, sovereign
Machine‑to‑Machine (M2M) quantitative strategy allocation engine. It
combines the **CoinMarketCap (CMC) AI Agent Hub** and the **BNB AI Agent
SDK** to enable autonomous agents to negotiate, settle micro‑transactions,
pull multi‑dimensional market analysis, and deliver institutional‑grade
portfolio rebalancing parameters completely on‑chain, without human
intervention.

Built for **Track 2** of the BNB Hack: AI Trading Agent Edition, NCAE
demonstrates the first live **Strategy‑as‑a‑Service** on BNB Chain.

---

## 📖 Table of Contents

- [System Architecture](#system-architecture)
- [What NCAE Does](#what-ncae-does)
- [Repository Structure](#repository-structure)
- [Features & Prize‑winning Highlights](#features--prize-winning-highlights)
- [How It Works (Data Flow)](#how-it-works-data-flow)
- [Setup Instructions](#setup-instructions)
- [Submission Changelog](#submission-changelog)
- [Special Prize Eligibility](#special-prize-eligibility)
- [Demo Video](#demo-video)
- [License](#license)

---

## System Architecture

NCAE operates as an autonomous economic relationship between two layers:

### 1. Agentic Capital Layer (BNB AI Agent SDK)

- **ERC‑8004 Cryptographic Identity** — Every instance registers an on‑chain
  identity (ID 1415 on BSC testnet) to prove network provenance.
- **ERC‑8183 Commerce Lifecycle** — Job creation, escrow funding, deliverable
  commitment validation, and automated dispute‑window clearing.
- **Native x402 Paywalls** — Programmatic `402 Payment Required` gate enables
  machines to buy and sell data with $U tokens or tBNB.
- **Trust Wallet Agent Kit (TWAK)** — Integrated local signing allows agents
  to authorize gas and escrow allocations autonomously.

### 2. Agentic Intelligence Layer (CoinMarketCap AI Agent Hub)

- **Multi‑Dimensional Stream Extraction** — Harnesses derivatives data, macro
  metrics, global market cap flags, and cross‑sectional sentiment indicators.
- **Universal Interface Coverage** — Operates across all Hub surfaces: MCP
  tools, CLI Skills, pre‑built Marketplace Skills, and custom JSON‑RPC HTTP
  transport.
- **Digital Twin Simulator** — A deterministic historical backtesting engine
  that mirrors live CMC asset structures against real price arrays to compute
  Sharpe ratios, win rates, and maximum drawdowns.

---

## What NCAE Does

- **Fetches live multi‑dimensional data** — MCP tools, CLI, REST, and
  pre‑built CMC Marketplace Skills (daily market overview).
- **Runs a quant engine** — sentiment‑divergence, BTC dominance contrarian,
  and an LLM‑authored volume‑breakout strategy.
- **Outputs a backtestable spec** — entry / exit rules, position sizing, risk
  limits, allocation weights.
- **Backtests the spec** with real historical prices (30‑day window, CMC CLI).
- **Delivers it on‑chain** — provider submits a deliverable hash on BSC testnet
  via ERC‑8183; client retrieves the spec off‑chain.
- **Hot‑reloads parameters** — change `max_asset_weight` in the job description
  and the next spec adjusts instantly.
- **x402 support** — both consuming premium data (X402Signer) and serving
  strategies behind a 402 paywall.

---

## Repository Structure

```
NCAE/
├── LICENSE
├── README.md                       # Main project documentation
├── app/                            # Quant engine, schemas, services, API
│   ├── core/                       # Pydantic models, config, x402 auth middleware
│   ├── quant/                      # SDMEEngine, backtester, funding_rate strategy
│   └── services/                   # CMC REST client, CMC MCP client
├── bnbsdk_agent/                   # BNB AI Agent SDK integration
│   ├── provider_server.py          # ERC‑8183 provider (wraps the engine)
│   ├── client_demo.py              # ERC‑8183 client (buys strategies on‑chain)
│   └── register_identity.py        # ERC‑8004 identity registration
├── ncae_backtest.py                # CLI historical backtest using CMC prices
├── run_llm_strategy.py             # Execute a pre‑generated LLM strategy on‑chain
├── check_wallets.py                # Wallet tracking and balance assertion diagnostic
├── demo_mcp.py                     # Test script: fetch live data via MCP from IDE
├── demo_skill.py                   # Test script: invoke a pre‑built CMC Marketplace skill
├── llm_generated_strategy.json     # Sample LLM‑authored strategy spec
├── test_cmc.py                     # Connectivity validation script for CMC Hub
├── pyproject.toml                  # Project metadata & dependencies
└── uv.lock                         # Deterministic uv lockfile
```

Sub‑module READMEs with detailed descriptions:
- [`app/README.md`](app/README.md)
- [`app/quant/README.md`](app/quant/README.md)
- [`bnbsdk_agent/README.md`](bnbsdk_agent/README.md)

---

## Features & Prize‑winning Highlights

### 🏆 Best Use of Agent Hub
- **MCP tools** — quotes, technical analysis, on‑chain, derivatives, global
  metrics, trending narratives, macro events.
- **CMC CLI** — `cmc markets`, `cmc trending`, `cmc history` (backtest source).
- **IDE integration** — VSCodium with CMC MCP server configured.
- **x402** — provider signs real EIP‑3009 authorizations (`X402Signer`) and
  own paywall middleware serves strategies behind HTTP 402.
- **Pre‑built Skills** — consumes `daily_market_overview` from the CMC
  Marketplace via `execute_skill`.

### 🤖 Best Use of BNB AI Agent SDK
- **ERC‑8183 provider** — `create_erc8183_app()` wraps the quant engine.
- **ERC‑8183 client** — full lifecycle: create job, fund escrow, submit,
  settle.
- **X402Signer** — authenticates premium data purchases inside the provider.
- **Hot‑reload** — job parameters override risk settings without restarting.
- **ERC‑8004 identity** — on‑chain agent ID 1415 (BSC testnet).
- **Execution‑layer mock** — swap instructions for every delivered allocation.

### 📊 Real‑World Relevance
- **Real historical backtest** — 30 days of CMC daily prices, no GBM.
- **Cost comparison** — $0.50 per strategy vs. $500‑$2,000/month
  subscriptions.
- **Clear user** — AI agents, DAOs, or human traders who want a daily
  allocation without trust.

---

## How It Works (Data Flow)

```
Client (any agent)
   │
   ├─ createJob + fund (BSC testnet)
   │
NCAE Provider (ERC‑8183 server)
   │
   ├─ x402 pay for premium data
   ├─ fetch live data (MCP, CLI, REST, marketplace skills)
   ├─ select strategy (sentiment, regime auto, funding_rate, generic)
   ├─ compute allocation & backtest
   ├─ hot‑reload risk parameters
   ├─ submit deliverable hash on‑chain
   └─ log execution‑layer mock trades
   │
Client retrieves deliverable → executable StrategySpecification
```

---

## Setup Instructions

### Prerequisites

- **Python 3.12+** (the project uses 3.12, but 3.11+ works)
- **uv** (fast Python package manager) — [install](https://github.com/astral-sh/uv)
- **CoinMarketCap Pro API key** — [get one here](https://pro.coinmarketcap.com/signup)
- **CMC CLI** (optional but recommended) — [install](https://coinmarketcap.com/api/agent/#dev-steps)
- **tBNB & U tokens** on BSC testnet (for ERC‑8183 jobs, faucets available)
- **VSCode / Cursor** (for IDE integration demo)

### 1. Clone & environment

```bash
git clone https://github.com/macaulaypraise/Neural-Capital-Allocation-Engine--NCAE.git
cd NCAE
```

Create a `.env` file with your keys (see step 3).

### 2. Install dependencies

```bash
uv sync
```

### 3. Configure `.env`

```env
CMC_MCP_API_KEY=your-cmc-pro-api-key
PRIVATE_KEY=64-char-hex-provider-wallet-key
WALLET_PASSWORD=strong-password-for-keystore
CLIENT_PRIVATE_KEY=64-char-hex-client-wallet-key
CLIENT_WALLET_PASSWORD=strong-password-for-client
PROVIDER_WALLET_ADDRESS=0x...
CLIENT_WALLET_ADDRESS=0x...
ERC8183_AGENT_URL=http://localhost:8003/erc8183
ERC8183_SERVICE_PRICE=500000
RPC_URL=https://bsc-testnet-rpc.publicnode.com
```

> ⚠️ **Security:** The `PRIVATE_KEY` is only needed on first run; the SDK
> encrypts it to `~/.bnbagent/wallets/`. Remove it from `.env` afterwards to
> avoid leaking the plaintext key.


### 🖥️ Recommended Multi‑Terminal Setup (for the full demo)

Open **three terminals** and start the servers that must stay running throughout
the demo. Then use the third terminal to execute any action.

#### Terminal 1 – Standalone MCP Server (x402 paywall)
```bash
uv run uvicorn app.main:app --port 8000
```
This serves your own x402‑protected strategy endpoint. It must be running
**before** you run `app/agent_client.py` (Step 7 below).

#### Terminal 2 – ERC‑8183 Provider (BNB SDK)
```bash
uv run uvicorn bnbsdk_agent.provider_server:app --port 8003
```
This listens for on‑chain jobs. It must be running **before** any
`client_demo.py` or `run_llm_strategy.py` call (Steps 4–6 below).

#### Terminal 3 – Action Runner
From here you can execute any command without disturbing the servers. All
remaining steps below are run in this terminal.


### 4. Run the historical backtest

```bash
uv run python ncae_backtest.py
```

This fetches 30 days of real BTC/ETH/BNB prices via CMC CLI, runs the
sentiment‑divergence strategy, and prints:

- Allocation weights
- Start → end value
- Sharpe ratio, max drawdown, win rate
- Text‑based equity curve

### 5. Purchase a strategy (client demo)

```bash
# Default sentiment divergence
uv run python bnbsdk_agent/client_demo.py

# Auto‑regime selection
uv run python bnbsdk_agent/client_demo.py auto

# BTC Dominance Contrarian
uv run python bnbsdk_agent/client_demo.py funding_rate

# With hot‑reload parameter
uv run python bnbsdk_agent/client_demo.py sentiment_divergence 0.15
```

The client will create a job, fund escrow, wait for submission, and print the
delivered `StrategySpecification`.

### 6. Run the LLM‑authored strategy

```bash
uv run python run_llm_strategy.py
```

Uses the pre‑generated JSON (`llm_generated_strategy.json`) and delivers it
on‑chain via the `generic` handler. A cost comparison is printed at the end.

### 7. Demonstrate the x402 paywall (providing x402)

Ensure Terminal 1 is running, then execute:

```bash
uv run python app/agent_client.py
```

It hits HTTP 402, simulates TWAK signing, and unlocks the strategy spec.

### 8. Register an on‑chain agent identity (optional)

```bash
uv run python bnbsdk_agent/register_identity.py
```

On success, an ERC‑8004 agent ID is minted and displayed.

---

## Submission Changelog

The following systematic upgrades were performed during development to bring
the engine to full production compliance and address all judge‑identified
weaknesses:

| Category | Issue | Fix |
|----------|-------|-----|
| **Critical Bug** | Corrupted price data (BTC ~0.000013) leading to meaningless backtests | Switched to CMC CLI `cmc history` for correct USD prices |
| **Critical Bug** | `clip(-1,1)` masking calculation anomalies | Removed clip; all metrics are now authentic |
| **Engine Upgrade** | Hot‑reload parameter resetting | Upgraded to explicit Pydantic `model_copy(update=…)` |
| **Bounty Compliance** | Missing second strategy | Added BTC Dominance Contrarian `funding_rate` strategy |
| **Bounty Compliance** | Pre‑built Skills not consumed | Integrated `daily_market_overview` from CMC Marketplace |
| **Demo Polish** | Debug output cluttering terminal | Removed all DEBUG prints; clean professional logs |
| **Bounty Compliance** | ERC‑8004 identity missing | Registered on‑chain agent ID 1415 |

---

## Special Prize Eligibility

### Best Use of Agent Hub

We use **every** integration surface:

| Surface | How |
|---------|-----|
| MCP tools | Live quotes, TA, on‑chain, derivatives, global metrics, trending, macro, market TA |
| CLI | `cmc markets`, `cmc trending`, `cmc history` (backtest source) |
| IDE | VSCodium configured with CMC MCP server |
| x402 (consume) | Provider signs real EIP‑3009 payments via `X402Signer` |
| x402 (provide) | Custom x402 middleware serves strategies behind 402 paywall |
| Pre‑built Skills | Calls `daily_market_overview` from CMC Marketplace via `execute_skill` |

### Best Use of BNB AI Agent SDK

| Component | How |
|-----------|-----|
| `create_erc8183_app` | Wraps the quant engine as an ERC‑8183 provider |
| `ERC8183Client` | Full job lifecycle: create, fund, submit, settle |
| `X402Signer` | Signs outbound premium‑data payments inside the provider |
| `EVMWalletProvider` | Secure keystore‑based local signing |
| `ERC8004Agent` | On‑chain identity registered (ID 1415) |
| Hot‑reload | Job description overrides `max_asset_weight` without restart |
| Execution mock | Simulates swap instructions after each spec |

---

## Demo Video

A complete walkthrough of the entire project is available at:
*([here](https://youtu.be/ZH2GPLNLgCs))*

---

## License

 Apache-2.0 License  — see [LICENSE](LICENSE) for details.
