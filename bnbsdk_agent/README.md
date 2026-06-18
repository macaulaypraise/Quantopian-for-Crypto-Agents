# bnbsdk_agent/ — BNB AI Agent SDK Integration

## Files

### `provider_server.py`
ERC‑8183 provider that wraps the quant engine.
- Polls for `FUNDED` jobs on BSC testnet.
- Calls the CMC MCP client and runs the selected strategy.
- Supports `sentiment_divergence`, `auto`, `funding_rate`, and `generic`
  strategies.
- Logs x402 outbound payment, execution‑layer mock trades, and hot‑reload
  parameter overrides.
- Built with `create_erc8183_app()`.

### `client_demo.py`
Command‑line ERC‑8183 client.
- Creates a job with a strategy name and optional `max_asset_weight`.
- Funds escrow (0.5 U tokens) and waits for provider submission.
- Attempts settlement (dispute window is active for demo) and retrieves
  the off‑chain deliverable.

Usage:
```bash
uv run python bnbsdk_agent/client_demo.py [strategy] [max_asset_weight]
```

### `register_identity.py`
Registers an ERC‑8004 agent identity on BSC testnet.
- Uses your wallet’s private key (first run) and keystore.
- Prints the agent ID and transaction hash.

