import yfinance as yf
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv
from fredapi import Fred
from typing import Dict, Any, Optional, List

load_dotenv()

def get_market_snapshot(tickers: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Retrieves a market snapshot including price level, volatility, and calculated Z-scores.
    Also fetches foundational interest rate data from FRED.

    Args:
        tickers (list, optional): List of ticker symbols to fetch. 
                                  Defaults to a standard basket if not provided.

    Returns:
        Dict[str, Any]: A dictionary containing structured market data.
                        Example:
                        {
                            "SPY": { ... },
                            "rates": {
                                "10Y_Treasury": 4.2,
                                "2Y_Treasury": 4.5,
                                "Fed_Funds": 5.33
                            }
                        }
    """
    if tickers is None:
        tickers = ["SPY", "QQQ", "IWM", "TLT", "GLD", "BTC-USD"]

    snapshot = {}

    # --- 1. Fetch Market Data (YFinance) ---
    try:
        # Batch download for efficiency
        data = yf.download(tickers, period="3mo", progress=False)['Close']
        
        # Ensure data is a DataFrame even if one ticker
        if isinstance(data, pd.Series):
            data = data.to_frame()

        # Calculate metrics for each ticker
        for ticker in tickers:
            if ticker not in data.columns:
                snapshot[ticker] = {"error": "Data not found"}
                continue
                
            series = data[ticker].dropna()
            if series.empty:
                snapshot[ticker] = {"error": "No data available"}
                continue

            current_price = series.iloc[-1]
            prev_price = series.iloc[-2] if len(series) > 1 else current_price
            
            # Daily Change
            daily_change = (current_price - prev_price) / prev_price * 100

            # 30-Day Stats
            window_30 = series.tail(30)
            mean_30 = window_30.mean()
            std_30 = window_30.std()
            
            # Z-Score (Current vs 30d Mean)
            z_score = (current_price - mean_30) / std_30 if std_30 != 0 else 0.0
            
            # Volatility (Annualized std dev of daily returns)
            returns = series.pct_change().dropna()
            volatility = returns.std() * np.sqrt(252)

            snapshot[ticker] = {
                "price": round(float(current_price), 2),
                "daily_change_pct": round(float(daily_change), 2),
                "z_score_30d": round(float(z_score), 2),
                "volatility_annualized": round(float(volatility), 2)
            }

    except Exception as e:
        snapshot["market_data_error"] = f"Failed to fetch market data: {str(e)}"

    # --- 2. Fetch Macro Rates (FRED) ---
    try:
        fred_key = os.getenv("FRED_API_KEY")
        if fred_key:
            fred = Fred(api_key=fred_key)
            
            # DGS10: 10-Year Treasury Constant Maturity Rate
            # DGS2: 2-Year Treasury Constant Maturity Rate
            # FEDFUNDS: Effective Federal Funds Rate
            rates_series = ["DGS10", "DGS2", "FEDFUNDS"]
            
            rates_data = {}
            for series_id in rates_series:
                try:
                    # Get the most recent observation
                    series = fred.get_series(series_id, limit=5).dropna()
                    if not series.empty:
                        # Map readable names
                        name_map = {
                            "DGS10": "10Y_Treasury",
                            "DGS2": "2Y_Treasury",
                            "FEDFUNDS": "Fed_Funds_Rate"
                        }
                        name = name_map.get(series_id, series_id)
                        rates_data[name] = round(float(series.iloc[-1]), 2)
                except Exception:
                    continue # Skip individual series failure
            
            if rates_data:
                snapshot["rates"] = rates_data
        else:
             snapshot["rates"] = {"info": "FRED_API_KEY not found in env"}

    except Exception as e:
        snapshot["rates_error"] = f"Failed to fetch rates: {str(e)}"

    return snapshot
