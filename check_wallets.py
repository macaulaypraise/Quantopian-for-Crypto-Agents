import os
from dotenv import load_dotenv
from eth_account import Account

load_dotenv()

def print_wallet_info():
    print("🏦 NCAE Agent Wallet Addresses 🏦\n" + "="*40)

    provider_pk = os.getenv("PRIVATE_KEY")
    if provider_pk and len(provider_pk) == 64:
        provider_acct = Account.from_key(provider_pk)
        print(f"🔹 PROVIDER WALLET (Server)")
        print(f"   Public Address: {provider_acct.address}")
        print("   Needs: tBNB (for gas to submit deliverable)\n")
    else:
        print("❌ Invalid PROVIDER PRIVATE_KEY in .env\n")

    client_pk = os.getenv("CLIENT_PRIVATE_KEY")
    if client_pk and len(client_pk) == 64:
        client_acct = Account.from_key(client_pk)
        print(f"🔸 CLIENT WALLET (Buyer)")
        print(f"   Public Address: {client_acct.address}")
        print("   Needs: tBNB (for gas) AND U Tokens (for escrow budget)\n")
    else:
        print("❌ Invalid CLIENT CLIENT_PRIVATE_KEY in .env\n")

    print("="*40)

if __name__ == "__main__":
    print_wallet_info()
