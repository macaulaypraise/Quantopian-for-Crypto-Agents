# demo_mcp.py
import asyncio
from app.services.cmc_mcp_client import CMCMCPClient
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("CMC_MCP_API_KEY")
assert api_key is not None, "CMC_MCP_API_KEY not set in .env"
client = CMCMCPClient(api_key=api_key)

async def main():
    data = await client.get_live_data_async(["BTC", "ETH"])
    print("✅ Live data fetched via CMC MCP from inside VSCodium")
    print("Keys:", list(data.keys()))

asyncio.run(main())
