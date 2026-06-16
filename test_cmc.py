import os
import asyncio
import httpx
import json
from dotenv import load_dotenv

load_dotenv()

async def run_test():
    api_key = os.getenv("CMC_MCP_API_KEY", "")
    masked_key = f"{api_key[:5]}...{api_key[-4:]}" if len(api_key) > 10 else api_key
    print(f"🔑 Loaded API Key: {masked_key}")

    if api_key == "1089d8e329d0425192141e0e812d12d9":
        print("❌ ERROR: You still have the placeholder API key in your .env file!")
        print("Please use your REAL key from the CoinMarketCap Developer Portal.")
        return

    url = "https://mcp.coinmarketcap.com/skill-hub/stream"
    headers = {
        "X-CMC-MCP-API-KEY": api_key,
        "Content-Type": "application/json"
    }

    # Standard MCP JSON-RPC Payload for Tool Execution
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "find_skill",
            "arguments": {
                "query": "btc price"
            }
        }
    }

    print(f"📡 Sending Streamable HTTP POST to {url}...")

    # Using a longer timeout as requested by the CMC docs (300 seconds)
    async with httpx.AsyncClient(timeout=300.0) as client:
        try:
            # Send the Streamable POST request
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()

            print("\n" + "="*50)
            print("🟢 SMOKE TEST SUCCESS! HUB RESPONSE:")

            # The server might return SSE-framed text (event: message \n data: {...})
            # We will print the raw text so we can see exactly how they formatted it
            print(response.text)
            print("="*50 + "\n")

        except httpx.HTTPStatusError as e:
            print(f"\n❌ HTTP Error {e.response.status_code}: {e.response.text}")
        except Exception as e:
            print(f"\n❌ Connection Failed: {e}")

if __name__ == "__main__":
    asyncio.run(run_test())
