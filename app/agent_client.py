import time
import httpx

SERVER_URL = "http://127.0.0.1:8000/skill/generate_strategy"

def run_autonomous_agent_loop():
    """
    Simulates a fully machine-to-machine loop.
    The client agent automatically catches the HTTP 402 payment barrier,
    extracts the invoice metrics, signs a mock transaction, and unlocks the data.
    """
    # Define the core trading intent and safety guardrails
    payload = {
        "intent": "Aggressive Growth via high-sentiment momentum baskets",
        "max_drawdown": 15.0
    }

    print("🤖 [Client Agent]: Initializing strategy request loop...")
    print(f"🤖 [Client Agent]: Submitting intent -> '{payload['intent']}'")
    print(f"🤖 [Client Agent]: Enforcing Max Drawdown Limit -> {payload['max_drawdown']}%")
    print("-" * 70)

    with httpx.Client() as client:
        # STEP 1: Attempt to access the strategy endpoint without payment headers
        print("📡 [Client Agent]: Sending initial request (No Payment Receipt)...")
        response = client.post(SERVER_URL, json=payload)

        # STEP 2: Intercept the mandatory HTTP 402 Payment Required block
        if response.status_code == 402:
            invoice = response.json()["detail"]
            print("\n❌ [Server Response]: HTTP 402 Payment Required!")
            print(f"   | Required Token: {invoice['required_token']}")
            print(f"   | Target Chain:   {invoice['chain'].upper()}")
            print(f"   | Merchant Gate:  {invoice['payment_address']}")
            print("-" * 70)

            # STEP 3: Automated On-Chain Settling Simulation
            print("⚡ [Client Agent]: Executing automated payment primitive...")
            print("⚡ [Client Agent]: Invoking Trust Wallet Agent Kit (TWAK) local signer...")
            time.sleep(1.5)  # Simulate network latency for BSC block broadcast

            # High-fidelity mock of a completed 66-character BNB Chain transaction hash
            mock_tx_hash = "0x7d5a01345f6236ef89adcfbc1249571024bcdaef35160ef98cdba836aef192b0"
            print(f"✅ [Client Agent]: Payment broadcast successful! TX Hash: {mock_tx_hash}")
            print("-" * 70)

            # STEP 4: Re-submit the exact payload with the cryptographic invoice receipt
            print("📡 [Client Agent]: Re-submitting request with verified 'x-payment-receipt' header...")
            headers = {"x-payment-receipt": mock_tx_hash}
            success_response = client.post(SERVER_URL, json=payload, headers=headers, timeout=300.0)

            if success_response.status_code == 200:
                strategy_spec = success_response.json()

                # STEP 5: Parse and display the unlocked institutional asset specs
                print("\n🔓 [Server Response]: HTTP 200 Success! Strategy Specification Unlocked.")
                print("=" * 70)
                print(f"STRATEGY ID:        {strategy_spec['strategy_spec_id']}")
                print(f"GENERATED AT:       {strategy_spec['generated_at']}")
                print(f"TARGET UNIVERSE:    {strategy_spec['target_universe']}")
                print("-" * 70)
                print("CURRENT TARGET ALLOCATIONS:")
                for token, weight in strategy_spec['current_target_allocation'].items():
                    print(f"   • {token}: {round(weight * 100, 2)}%")
                print("-" * 70)
                print("DIGITAL TWIN SIMULATION METRICS (30-DAY HISTORICAL BACKTEST):")
                metrics = strategy_spec['simulation_metrics']
                print(f"   • Annualized Sharpe Ratio: {metrics['simulated_sharpe_ratio']}")
                print(f"   • Expected Max Drawdown:   {round(metrics['max_drawdown_observed'] * 100, 2)}%")
                print(f"   • Historical Win Rate:     {round(metrics['win_rate'] * 100, 2)}%")
                print("=" * 70)
                print("📋 [Client Agent]: Strategy JSON ingestion complete. Ready for execution layer routing.")
            else:
                print(f"💥 Error during re-submission: {success_response.status_code} - {success_response.text}")
        else:
            print(f"💥 Unexpected Server Response: {response.status_code} - {response.text}")

if __name__ == "__main__":
    try:
        run_autonomous_agent_loop()
    except httpx.ConnectError:
        print("\n❌ Error: Cannot connect to the FastAPI server. Ensure it is running via 'uv run uvicorn main:app' first.")
