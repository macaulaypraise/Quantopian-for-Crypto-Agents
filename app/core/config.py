import os
from pathlib import Path

def load_env_file():
    """
    Locates and injects root-level .env key-value pairs into os.environ
    without adding extra external library dependencies.
    """
    root_dir = Path(__file__).resolve().parent.parent.parent
    env_path = root_dir / ".env"

    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, val = line.split("=", 1)
                # Set default if not already present in the shell environment
                os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))

# Execute loading sequence on initialization
load_env_file()

class AppSettings:
    """ Centralized, production-grade application configuration schema. """
    CMC_API_KEY: str = os.getenv("CMC_API_KEY", "demo_mode")
    MERCHANT_WALLET_ADDRESS: str = os.getenv(
        "MERCHANT_WALLET_ADDRESS",
        "0xYourBNBChainMerchantWalletAddressHere"
    )
    REQUIRED_PAYMENT_AMOUNT: str = "0.50 USDC"

settings = AppSettings()
