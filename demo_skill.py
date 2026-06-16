# demo_skill.py
import asyncio
from app.services.cmc_mcp_client import CMCMCPClient
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("CMC_MCP_API_KEY")
assert api_key is not None, "CMC_MCP_API_KEY not set in .env"
client = CMCMCPClient(api_key=api_key)

async def main():
    print("📊 Running CMC Market Report Skill (pre‑built)...")
    # The unique_name for the official Market Report Skill is "market-report"
    report = await client._execute_skill("market-report")
    print(report[:1500] if report else "No output (check API key / credits)")
    print("\n✅ Successfully consumed a pre‑built CMC Skill via MCP.")

asyncio.run(main())
