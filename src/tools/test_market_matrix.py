import sys
import os
from dotenv import load_dotenv

# Add the parent directory of 'src' to the Python path
# This allows importing 'src.tools.market_matrix' correctly when running this script directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Load env vars
load_dotenv()

from src.tools.market_matrix import get_market_snapshot

def run_market_snapshot_test():
    """
    Tests the get_market_snapshot tool independently.
    """
    print("--- Testing get_market_snapshot tool ---")
    
    # Test with default tickers
    print("\nFetching snapshot for default tickers (SPY, QQQ, IWM, TLT, GLD, BTC-USD)...")
    default_snapshot = get_market_snapshot()
    
    if "market_data_error" in default_snapshot:
        print(f"Error fetching market data: {default_snapshot['market_data_error']}")
    
    if "rates_error" in default_snapshot:
        print(f"Error fetching rates: {default_snapshot['rates_error']}")

    # Print Rates if available
    if "rates" in default_snapshot:
        print("\n  [Rates Data]:")
        for rate, value in default_snapshot["rates"].items():
            print(f"    {rate}: {value}%")
    
    # Print Market Data
    print("\n  [Market Data]:")
    for ticker, data in default_snapshot.items():
        if ticker in ["rates", "market_data_error", "rates_error"]:
            continue
        print(f"  {ticker}:")
        for key, value in data.items():
            print(f"    {key}: {value}")
    
    # Test with custom tickers
    print("\nFetching snapshot for custom tickers (AAPL, MSFT)...")
    custom_snapshot = get_market_snapshot(tickers=["AAPL", "MSFT"])
    if "error" in custom_snapshot:
        print(f"Error fetching custom snapshot: {custom_snapshot['error']}")
    else:
        for ticker, data in custom_snapshot.items():
            print(f"  {ticker}:")
            for key, value in data.items():
                print(f"    {key}: {value}")

    print("\n--- Test complete ---")

if __name__ == "__main__":
    run_market_snapshot_test()
