from bnbagent import ERC8004Agent, AgentEndpoint
from bnbagent.wallets import EVMWalletProvider
from dotenv import load_dotenv
import os

load_dotenv()

wallet = EVMWalletProvider(
    password=os.getenv("WALLET_PASSWORD", ""),
    private_key=os.getenv("PRIVATE_KEY", "")
)
# ERC8004Agent only needs network + wallet_provider
sdk = ERC8004Agent(
    network="bsc-testnet",
    wallet_provider=wallet
)
uri = sdk.generate_agent_uri(
    name="NCAE Quant Strategy Provider",
    description="Institutional-grade portfolio allocations powered by CMC data",
    endpoints=[
        AgentEndpoint(
            name="ERC-8183",
            endpoint=f"{os.getenv('ERC8183_AGENT_URL')}/status",
            version="1.0.0"
        )
    ]
)
result = sdk.register_agent(agent_uri=uri)
print(f"Agent registered! ID: {result['agentId']}, TX: {result['transactionHash']}")
