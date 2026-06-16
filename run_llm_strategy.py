# run_llm_strategy.py
import json, time, os, requests
from dotenv import load_dotenv
from bnbagent.wallets import EVMWalletProvider
from bnbagent.erc8183 import ERC8183Client

load_dotenv()

provider_addr = os.getenv("PROVIDER_WALLET_ADDRESS")
if not provider_addr:
    raise EnvironmentError("PROVIDER_WALLET_ADDRESS not set in .env")
assert provider_addr is not None   # narrow type for type checker

# Load the LLM-generated strategy JSON
with open("llm_generated_strategy.json") as f:
    spec = json.load(f)

# Build the job description with the generic strategy and embedded spec
description = json.dumps({
    "strategy": "generic",
    "spec": spec,
    "max_asset_weight": 0.4
})

# Use the same client wallet as always
wallet = EVMWalletProvider(
    password=os.getenv("CLIENT_WALLET_PASSWORD", "demo-password"),
    private_key=os.getenv("CLIENT_PRIVATE_KEY")
)
client = ERC8183Client(wallet, network="bsc-testnet")


budget = 500000
expired_at = int(time.time()) + 172800

job_result = client.create_job(provider=provider_addr, expired_at=expired_at, description=description)
job_id = int(job_result.get("jobId", job_result.get("id"))) if isinstance(job_result, dict) else int(job_result)

client.register_job(job_id)
client.set_budget(job_id, budget)
client.fund(job_id, budget)
print(f"💸 Job {job_id} funded. Waiting for LLM strategy execution...")

# Wait for submission (short demo)
for _ in range(30):
    if client.get_job_status(job_id).value == "SUBMITTED":
        break
    time.sleep(2)

# Fetch deliverable
agent_url = os.getenv('ERC8183_AGENT_URL', 'http://127.0.0.1:8003/erc8183')
resp = requests.get(f"{agent_url}/job/{job_id}/response")
if resp.status_code == 200:
    print("🎯 LLM Strategy Deliverable:")
    print(json.dumps(resp.json(), indent=2))
else:
    print(f"❌ Error: {resp.status_code}")


print("\n💡 Cost Comparison:")
print("   • NCAE on‑chain strategy (ERC‑8183 escrow): ~$0.50 per request (gas + fees)")
print("   • Traditional quant subscription: $500 – $2,000/month")
print("   → Trustless, per‑use, 1000x cheaper, no human middleman.")
