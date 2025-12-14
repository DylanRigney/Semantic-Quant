import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional

def get_market_snapshot(tickers: Optional[list] = None) -> Dict[str, Any]:
    """
    Retrieves a market snapshot including price level, volatility, and calculated Z-scores.

    Args:
        tickers (list, optional): List of ticker symbols to fetch. 
                                  Defaults to a standard basket if not provided.

    Returns:
        Dict[str, Any]: A dictionary containing structured market data.
                        Example:
                        {
                            "SPY": {
                                "price": 450.0,
                                "daily_change_pct": 0.5,
                                "z_score_30d": 1.2,
                                "volatility_30d": 0.15
                            },
                            ...
                        }
    """
    if tickers is None:
        tickers = ["SPY", "QQQ", "IWM", "TLT", "GLD", "BTC-USD"]

    snapshot = {}

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
        return {"error": f"Failed to fetch market data: {str(e)}"}

    return snapshot
