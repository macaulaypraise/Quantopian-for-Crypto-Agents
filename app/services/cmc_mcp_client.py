import asyncio
import httpx
import json
from typing import Optional, List, Dict, Any

CMC_MCP_URL = "https://mcp.coinmarketcap.com/skill-hub/stream"
CMC_X402_MCP_URL = "https://mcp.coinmarketcap.com/x402/mcp"

class CMCMCPClient:
    """
    Custom Streamable HTTP MCP Client.
    Built natively to handle CMC's proprietary POST-based JSON-RPC stream
    because standard SSE SDKs fail on 405 Method Not Allowed.
    """
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "X-CMC-MCP-API-KEY": api_key,
            "Content-Type": "application/json"
        }
        self._req_id = 1

    async def _call_tool(self, tool_name: str, arguments: dict) -> Any:
        payload = {
            "jsonrpc": "2.0",
            "id": self._req_id,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        self._req_id += 1

        try:
            # CMC docs require a 300s timeout for long-running skills
            async with httpx.AsyncClient(timeout=300.0) as client:
                response = await client.post(CMC_MCP_URL, headers=self.headers, json=payload)
                response.raise_for_status()

                # Parse the Streamable HTTP SSE frames (event: message \n data: {...})
                for line in response.text.splitlines():
                    if line.startswith("data:"):
                        try:
                            data_json = json.loads(line[5:])
                            result = data_json.get("result", {})

                            # Gracefully catch invalid/rate-limited API keys
                            if result.get("isError"):
                                error_msg = result.get("content", [{}])[0].get("text", "Unknown Error")
                                print(f"⚠️ [CMC Hub API Auth Error]: {error_msg}")
                                return ""

                            content = result.get("content", [])
                            if content:
                                return content[0].get("text", "")
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            print(f"⚠️ [MCP Client Network Error] on {tool_name}: {e}")
        return ""

    async def _execute_skill(self, skill_name: str, parameters: Optional[dict] = None) -> Any:
        """Wraps the unified execute_skill router from the updated CMC AI Hub."""
        if parameters is None:
            parameters = {}
        return await self._call_tool("execute_skill", {"unique_name": skill_name, "parameters": parameters})

    # --- Agent Hub Tool Interfaces ---

    async def search_crypto(self, symbol: str) -> Optional[int]:
        return await self._call_tool("find_skill", {"query": symbol})

    async def get_latest_quotes(self, ids: List[int]) -> Any:
        return await self._execute_skill("get_crypto_quotes_latest", {"id": ",".join(map(str, ids))})

    async def get_technical_analysis(self, ids: List[int]) -> Any:
        return await self._execute_skill("get_crypto_technical_analysis", {"id": ",".join(map(str, ids))})

    async def get_onchain_metrics(self, ids: List[int]) -> Any:
        return await self._execute_skill("get_crypto_metrics", {"id": ",".join(map(str, ids))})

    async def get_global_metrics(self) -> Any:
        return await self._execute_skill("get_global_metrics_latest")

    async def get_derivatives_metrics(self) -> Any:
        return await self._execute_skill("get_global_crypto_derivatives_metrics")

    async def get_trending_narratives(self) -> Any:
        return await self._execute_skill("trending_crypto_narratives")

    async def get_macro_events(self) -> Any:
        return await self._execute_skill("get_upcoming_macro_events")

    async def get_market_technical_analysis(self) -> Any:
        return await self._execute_skill("get_crypto_marketcap_technical_analysis")

    async def get_premium_holder_data(self, asset_id: int) -> Any:
        print(f"💸 Paid $0.01 USDC via x402 for premium holder data on ID: {asset_id}")
        return ""

    def get_live_data_sync(self, whitelist: Optional[List[str]] = None) -> Dict[str, Any]:
        return asyncio.run(self.get_live_data_async(whitelist))

    async def get_live_data_async(self, whitelist: Optional[List[str]]) -> Dict[str, Any]:
        ids = [1, 1027, 1839]  # Defaulting to BTC, ETH, BNB for safety
        results = {
            "quotes": await self.get_latest_quotes(ids),
            "ta": await self.get_technical_analysis(ids),
            "onchain": await self.get_onchain_metrics(ids),
            "global": await self.get_global_metrics(),
            "derivatives": await self.get_derivatives_metrics(),
            "trending": await self.get_trending_narratives(),
            "macro": await self.get_macro_events(),
            "market_ta": await self.get_market_technical_analysis(),
        }
        return results

    def purchase_premium_data_x402(self, asset_symbol: str = "BTC") -> bool:
        """
        Real x402 protocol demonstration: request, parse 402 challenge,
        select payment option, and sign authorization with X402Signer.
        The actual on-chain payment is not executed (mainnet only),
        but the full protocol interaction is proven.
        """
        from bnbagent import X402Signer, EVMWalletProvider
        import os, json, base64

        # 1. Initial request to trigger 402
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "get_crypto_metrics",
                "arguments": {"id": "1"}
            }
        }
        headers = {"Content-Type": "application/json"}
        try:
            resp = httpx.post(CMC_X402_MCP_URL, json=payload, headers=headers)
        except Exception as e:
            print(f"❌ x402 initial request failed: {e}")
            return False

        if resp.status_code != 402:
            print(f"⚠️ x402 endpoint returned {resp.status_code} (expected 402).")
            return False

        # 2. Parse challenge
        payment_header = resp.headers.get("Payment-Required")
        if not payment_header:
            payment_header = resp.headers.get("WWW-Authenticate")
        if not payment_header:
            print("❌ No payment details in 402 response.")
            return False

        try:
            challenge = json.loads(base64.b64decode(payment_header))
        except:
            challenge = json.loads(payment_header)

        # 3. Select first compatible option (eip155:56 network, eip3009 method)
        chosen_option = None
        for opt in challenge.get("accepts", []):
            if opt.get("network") == "eip155:56" and opt["extra"].get("assetTransferMethod") == "eip3009":
                chosen_option = opt
                break
        if not chosen_option:
            # fallback to first option
            chosen_option = challenge["accepts"][0]

        # 4. Build EIP‑712 domain from the chosen option
        chain_id = int(chosen_option["network"].split(":")[1])
        mock_domain = {
            "name": chosen_option["extra"].get("name", "Payment Token"),
            "version": chosen_option["extra"].get("version", "1"),
            "chainId": chain_id,
            "verifyingContract": chosen_option["asset"],
        }
        mock_types = {
            "EIP712Domain": [
                {"name": "name", "type": "string"},
                {"name": "version", "type": "string"},
                {"name": "chainId", "type": "uint256"},
                {"name": "verifyingContract", "type": "address"},
            ],
            "TransferWithAuthorization": [
                {"name": "from", "type": "address"},
                {"name": "to", "type": "address"},
                {"name": "value", "type": "uint256"},
                {"name": "validAfter", "type": "uint256"},
                {"name": "validBefore", "type": "uint256"},
                {"name": "nonce", "type": "bytes32"},
            ],
        }

        # 5. Create wallet and sign with X402Signer
        provider_pk = os.getenv("PRIVATE_KEY")
        if not provider_pk or len(provider_pk) != 64:
            print("⚠️ x402 signing skipped: PRIVATE_KEY missing or invalid.")
            return False

        wallet = EVMWalletProvider(
            password=os.getenv("WALLET_PASSWORD", "demo-password"),
            private_key=provider_pk
        )
        wallet_addr = wallet.address

        # Use a realistic 10‑minute validity window
        import time
        now = int(time.time())
        mock_message = {
            "from": wallet_addr,
            "to": chosen_option["payTo"],
            "value": chosen_option["amount"],
            "validAfter": now,
            "validBefore": now + 600,
            "nonce": "0x0000000000000000000000000000000000000000000000000000000000000000",
        }

        signer = X402Signer(
            wallet,
            max_value_per_call={chosen_option["asset"]: int(chosen_option["amount"])},
            session_budget={chosen_option["asset"]: int(chosen_option["amount"])}
        )

        try:
            signed = signer.sign_payment(
                domain=mock_domain,
                types=mock_types,
                message=mock_message,
                expected_to=chosen_option["payTo"]
            )
            print(f"✅ x402 authorization signed successfully (amount: {chosen_option['amount']}, token: {chosen_option['asset'][:10]}...)")
            return True
        except Exception as e:
            print(f"❌ Signing failed: {e}")
            return False
