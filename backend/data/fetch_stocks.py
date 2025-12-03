# _____________________________________ Module 1 _____________________________________ #

import os
import pandas as pd
import yfinance as yf
from dotenv import load_dotenv
from pprint import pprint


def get_data_details(data: dict) -> dict:
    '''
    This function takes in the data dictionary fetched from the API and extracts relevant details.

    Parameters:
    - data (dict): The JSON-like data fetched from the API (or yfinance),
      shaped like:
        {
            "Meta Data": { "2. Symbol": "IBM", ... },
            "Time Series (60min)": {
                "2024-01-01 10:00:00": {"open": "...", "high": "...", ...},
                ...
            }
        }

    Returns:
    - dict: A dictionary containing extracted stats and row count, e.g.:
        {
            "IBM": {
                "open":  {"mean": ..., "std": ..., "median": ..., "low": ..., "max": ...},
                "high":  {...},
                "low":   {...},
                "close": {...},
                "volume": {...}
            },
            "count": 1234
        }
    '''
    details = {}

    # Turns the time series into a DataFrame where each time interval is a row
    stocks = pd.DataFrame.from_dict(data["Time Series (60min)"], orient="index")
    cols = ["open", "high", "low", "close", "volume"]
    stocks.columns = cols

    # Extract stats for each column
    stats = {}
    for col in cols:
        col_data = stocks[col].astype(float)
        stats[col] = {
            "mean": col_data.mean(),
            "std": col_data.std(),
            "median": col_data.median(),
            "low": col_data.min(),
            "max": col_data.max(),
        }

    # Use the symbol as the top-level key
    symbol = data["Meta Data"]["Symbol"]
    details[symbol] = stats

    # Number of rows
    details["count"] = stocks.shape[0]

    return details


def get_standing(details: dict) -> str:
    '''
    Take the details dict from get_data_details and return a qualitative standing.
    '''

    # Find the symbol key (anything that's not "count")
    symbol_key = next(k for k in details.keys() if k != "count")
    data = details[symbol_key]

    open_stats = data["open"]
    high_stats = data["high"]
    low_stats = data["low"]
    close_stats = data["close"]

    price_range = high_stats["mean"] - low_stats["mean"]
    volatility = close_stats["std"]
    skew = close_stats["median"] - close_stats["mean"]

    # You can tune these thresholds however you like
    if price_range > 10 and volatility > 5:
        standing = "risky"
    elif skew > 2:
        standing = "improving"
    elif skew < -2:
        standing = "declining"
    else:
        standing = "stable"

    return standing


def fetch_stock_data(symbol: str = "IBM", interval: str = "60m", period: str = "1mo") -> dict | None:
    '''
    Fetch intraday stock data using yfinance and mirror the existing Alpha Vantage–style data shape.

    Returns a dict like:
        {
            "data": { "Meta Data": {...}, "Time Series (60min)": {...} },
            "details": {...},   # stats from get_data_details
            "standing": "stable" | "risky" | ...
        }
    Or None on error.
    '''

    load_dotenv()

    result: dict = {}
    print(f"Fetching {symbol} with interval={interval} and period={period}\n")

    try:
        ticker = yf.Ticker(symbol)
        data_frame = ticker.history(interval=interval, period=period)

        # Preserve the existing try/if error handling style
        if data_frame is None or data_frame.empty:  # not found or no data
            raise Exception("The error indicates that the request was not found. Check the request and try again.")
        elif "Open" not in data_frame.columns:  # missing expected fields
            raise Exception("Access was denied to you. Ensure exact parameters and try again.")
        else:  # data retrieved
            print("Yay! The connection works!\n")

            # Keep only the columns we need and rename to lower-case
            data_frame = data_frame[["Open", "High", "Low", "Close", "Volume"]].copy()
            data_frame.columns = ["open", "high", "low", "close", "volume"]

            # Format index as string timestamps
            data_frame.index = data_frame.index.strftime("%Y-%m-%d %H:%M:%S")

            # Mirror the Alpha Vantage-like shape
            time_series_key = "Time Series (60min)"
            meta = {
                "Information": "Intraday data from yfinance",
                "Symbol": symbol,
                "Interval": interval,
                "Period": period,
            }

            data = {
                "Meta Data": meta,
                time_series_key: data_frame.to_dict(orient="index"),
            }

            # Attach raw-like data
            result["data"] = data

            # Compute stats + standing
            details = get_data_details(data)
            standing = get_standing(details)

            result["details"] = details
            result["standing"] = standing

        return result

    except Exception as some_error:
        print(f"There was an issue with the data fetching function. Error:\n{some_error}")
        return None


if __name__ == "__main__":
    print("Running Stock")
    data = fetch_stock_data(symbol="AAPL", interval="60m", period="max")
   
    pprint(data["details"]["AAPL"])