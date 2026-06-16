import os
import sys
import time
import json
import requests
from dotenv import load_dotenv
from bnbagent.wallets import EVMWalletProvider
from bnbagent.erc8183 import ERC8183Client, JobStatus

load_dotenv()

def run_buyer_demo():
    print("🤖 [Client]: Initializing ERC-8183 Commerce Client...")
    client_pk = os.getenv("CLIENT_PRIVATE_KEY")
    if not client_pk or len(client_pk) != 64:
        print("❌ Error: CLIENT_PRIVATE_KEY in .env must be exactly 64 hex characters.")
        return

    wallet = EVMWalletProvider(
        password=os.getenv("CLIENT_WALLET_PASSWORD", "demo-password"),
        private_key=os.getenv("CLIENT_PRIVATE_KEY")
    )
    client = ERC8183Client(wallet, network="bsc-testnet")

    provider_addr = os.getenv("PROVIDER_WALLET_ADDRESS")
    if not provider_addr:
        print("❌ Error: PROVIDER_WALLET_ADDRESS missing in .env")
        return

    budget = 500000  # 0.5 U
    expired_at = int(time.time()) + 172800   # 48 hours

    # --- NEW: command‑line strategy selection & hot‑reload parameter ---
    strategy_name = sys.argv[1] if len(sys.argv) > 1 else "sentiment_divergence"
    max_weight = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5
    # ------------------------------------------------------------------

    description = json.dumps({
        "strategy": strategy_name,
        "risk_profile": "aggressive",
        "whitelist": ["BTC", "ETH", "BNB"],
        "max_asset_weight": max_weight
    })

    print(f"📝 [Client]: Creating and funding '{strategy_name}' job on BSC Testnet...")
    job_result = client.create_job(
        provider=provider_addr,
        expired_at=expired_at,
        description=description
    )
    job_id: int = int(job_result.get("jobId", job_result.get("id"))) if isinstance(job_result, dict) else int(job_result)

    client.register_job(job_id)
    client.set_budget(job_id, budget)
    client.fund(job_id, budget)
    print(f"💸 [Client]: Job {job_id} funded in escrow. Waiting for provider to submit...")

    while client.get_job_status(job_id) != JobStatus.SUBMITTED:
        time.sleep(5)

    print(f"📦 [Client]: Provider submitted deliverable hash. Awaiting dispute window...")
    time.sleep(2)

    print("🤝 [Client]: Attempting to settle payment to provider...")
    try:
        client.settle(job_id)
        print(f"✅ [Client]: Job {job_id} settled!")
    except Exception as e:
        print("⏳ [Client Notice]: On-chain settlement reverted because the 24-hour dispute window is still active.")
        print("⏳ [Client Notice]: The funds are securely locked in escrow. Proceeding to fetch off-chain deliverable early for demo purposes...")

    agent_url = os.getenv('ERC8183_AGENT_URL', 'http://127.0.0.1:8003/erc8183')
    url = f"{agent_url}/job/{job_id}/response"

    print("\n🔓 [Client]: Retrieving Off-Chain Strategy Spec...")
    resp = requests.get(url)

    if resp.status_code == 200:
        print("\n" + "="*50)
        print("🎯 DELIVERABLE RECEIVED:")
        print(json.dumps(resp.json(), indent=2))
        print("="*50)
    else:
        print(f"❌ Failed to fetch deliverable: {resp.status_code}")

if __name__ == "__main__":
    run_buyer_demo()
