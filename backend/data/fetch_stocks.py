"""
Module: fetch_stocks.py
Path: backend/data/fetch_stocks.py
Author: Oregon Software Consulting; Junior Software Engineer, Kevin Le
Purpose: Fetch and analyze real-time stock market data from Alpha Vantage API.

Overview:
---------
This module retrieves intraday stock price data (OHLCV: Open, High, Low, Close, Volume)
from the Alpha Vantage API, processes it using pandas DataFrames, and computes statistical
summaries to help evaluate stock performance and market conditions.

The module transforms raw time-series stock data into structured statistical insights,
including mean, standard deviation, median, minimum, and maximum values for each price
metric. It also classifies stocks into one of four health categories based on volatility,
price range, and price trend (skewness).

Key Functions:
--------------
1. get_data_details(data: dict) -> dict
   - Parses Alpha Vantage API response containing timestamped OHLCV data.
   - Converts string prices to floats and loads into pandas DataFrame.
   - Calculates five statistical measures (mean, std, median, min, max) for each metric.
   - Returns structured dictionary with ticker symbol as key.

2. get_standing(data: dict) -> str
   - Analyzes stock health using three key metrics:
     * Price range: Difference between average high and low (market volatility).
     * Volatility: Standard deviation of closing prices (price stability).
     * Skew: Difference between median and mean close (trend direction).
   - Returns classification: 'risky', 'improving', 'declining', or 'stable'.

3. fetch_stock_data(params: str, base_url: str, endpoint: str) -> dict | None
   - Main export function that orchestrates the entire data pipeline.
   - Sends GET request to Alpha Vantage API with specified parameters.
   - Handles HTTP errors (404, 403, 200) with appropriate error messages.
   - Combines statistical details with standing classification.
   - Returns None if any errors occur during fetching or processing.

Usage:
------
Run this module directly from the command line:
    python3 -m backend.data.fetch_stocks

Or import into another module:
    from backend.data.fetch_stocks import fetch_stock_data
    
    data = fetch_stock_data(
        "function=TIME_SERIES_INTRADAY&symbol=AAPL&interval=5min&apikey=YOUR_KEY"
    )
    print(data['AAPL']['close']['mean'])
    print(data['standing'])

Output Format:
--------------
{
    'IBM': {
        'open': {'mean': 215.34, 'std': 2.41, 'median': 215.20, 'min': 210.50, 'max': 220.10},
        'high': {'mean': 216.12, 'std': 2.38, 'median': 216.00, 'min': 211.80, 'max': 221.50},
        'low': {'mean': 214.56, 'std': 2.44, 'median': 214.40, 'min': 209.20, 'max': 219.30},
        'close': {'mean': 215.78, 'std': 2.40, 'median': 215.65, 'min': 210.90, 'max': 220.80},
        'volume': {'mean': 1250000, 'std': 450000, 'median': 1200000, 'min': 800000, 'max': 2500000},
        'count': 100
    },
    'standing': 'stable'
}

Dependencies:
-------------
- requests: HTTP library for making API calls.
- pandas: Data analysis and manipulation library.
- pprint: Pretty-print for debugging output.
- python-dotenv: Load environment variables from .env file (via support.py).

Environment Variables:
----------------------
ALPHA_VANTAGE_API_KEY: Your API key from Alpha Vantage (stored in .env file).

API Documentation:
------------------
Alpha Vantage API: https://www.alphavantage.co/documentation/
Free API Key: https://www.alphavantage.co/support/#api-key

Notes:
------
- API requests are rate-limited by Alpha Vantage (5 calls/minute for free tier).
- Intraday data is available in 1min, 5min, 15min, 30min, and 60min intervals.
- 'outputsize=full' returns full trading day data; 'compact' returns latest 100 points.
- Standard deviation calculated using pandas default (sample std with ddof=1).
- Standing thresholds (10, 5, 2, -2) can be adjusted based on your risk tolerance.

Error Handling:
---------------
- Returns None if HTTP request fails (404, 403, timeout, connection issues).
- Raises KeyError if API response structure is unexpected.
- Raises ValueError if price/volume data cannot be converted to float.
- All errors are caught and logged to console for debugging.

Example Trading Strategies:
---------------------------
- 'risky' stocks: High volatility and large price swings (day trading potential).
- 'improving' stocks: Upward trend indicated by positive skew (buy signal).
- 'declining' stocks: Downward trend indicated by negative skew (sell signal).
- 'stable' stocks: Low volatility and balanced prices (long-term holding).

Author: Kevin Le
Last Modified: November 9, 2025
"""

from pprint import pprint
import requests
import pandas as pd

from backend.utils.support import get_secret

# Loads variables from .env into the environment.
ALPHA_VANTAGE_API_KEY = get_secret("ALPHA_VANTAGE_API_KEY")


def get_data_details(data: dict) -> dict:
    """
    Convert Alpha Vantage API response to statistics format using pandas.
    
    This function takes raw stock data from the Alpha Vantage API and transforms 
    it into a structured format containing statistical analysis (mean, std, median, 
    min, max) for each price type (open, high, low, close, volume).
    
    Args:
        data (dict): A dictionary containing the API response with two main keys:
            - 'Meta Data': Contains metadata like symbol, interval, and timezone.
            - 'Time Series (5min)': Contains timestamped candle data with keys:
                - '1. open': Opening price as string.
                - '2. high': High price as string.
                - '3. low': Low price as string.
                - '4. close': Closing price as string.
                - '5. volume': Trading volume as string.
    
    Returns:
        dict: A dictionary with the following structure:
            {
                'TICKER_SYMBOL': {
                    'open': {'mean': float, 'std': float, 'median': float, 'min': float, 'max': float},
                    'high': {'mean': float, 'std': float, 'median': float, 'min': float, 'max': float},
                    'low': {'mean': float, 'std': float, 'median': float, 'min': float, 'max': float},
                    'close': {'mean': float, 'std': float, 'median': float, 'min': float, 'max': float},
                    'volume': {'mean': float, 'std': float, 'median': float, 'min': float, 'max': float}
                },
                'count': int  # Total number of data points.
            }
    
    Raises:
        KeyError: If expected keys are missing from the input data dictionary.
        ValueError: If price/volume strings cannot be converted to floats.
    
    Example:
        >>> data = {...}  # API response
        >>> stats = get_data_details(data)
        >>> print(stats['IBM']['close']['mean'])
        279.45
    
    Notes:
        - All price strings from the API are converted to float values.
        - Statistics are calculated using pandas built-in methods.
        - Standard deviation uses pandas default (sample std with ddof=1).
    """

    # Extract ticker and time series data.
    ticker = data["Meta Data"]["2. Symbol"]
    time_series = data["Time Series (5min)"]

    # Convert time series to DataFrame.
    df_data = []
    for timestamp, info in time_series.items():
        df_data.append(
            {
                "timestamp": timestamp,
                "open": float(info["1. open"]),
                "high": float(info["2. high"]),
                "low": float(info["3. low"]),
                "close": float(info["4. close"]),
                "volume": float(info["5. volume"]),
            }
        )

    df = pd.DataFrame(df_data)

    # Calculate statistics for each price type.
    result: dict[str, dict] = {ticker: {}}

    for col in ["open", "high", "low", "close", "volume"]:
        result[ticker][col] = {
            "mean": float(df[col].mean()),
            "std": float(df[col].std()),
            "median": float(df[col].median()),
            "min": float(df[col].min()),
            "max": float(df[col].max()),
        }

    result[ticker]["count"] = len(df)

    return result

def get_standing(data: dict) -> str:
    """
    Analyze stock statistics and return a status classification.
    
    This function evaluates stock health based on three calculated metrics:
    price range, volatility, and skewness. It assigns one of four status 
    categories: 'risky', 'improving', 'declining', or 'stable'.
    
    Args:
        data (dict): A dictionary of statistics for a single stock, typically 
            from the ticker key in get_data_details() output. Must contain:
            - 'open': dict with 'mean' key.
            - 'high': dict with 'mean' key.
            - 'low': dict with 'mean' key.
            - 'close': dict with 'mean', 'median', and 'std' keys.
    
    Returns:
        str: One of four status values:
            - 'risky': Price range > 10 AND volatility > 5.
            - 'improving': Price skew (median - mean) > 2.
            - 'declining': Price skew (median - mean) < -2.
            - 'stable': None of the above conditions met.
    
    Raises:
        KeyError: If expected statistical keys are missing from the input.
        TypeError: If statistical values are not numeric.
    
    Example:
        >>> stats = get_data_details(api_data)
        >>> status = get_standing(stats['IBM'])
        >>> print(status)
        'stable'
    
    Notes:
        - Price range = average high - average low (measures price movement span).
        - Volatility = standard deviation of closing prices (measures price variation).
        - Skew = median closing price - mean closing price (indicates trend direction).
        - Thresholds (10, 5, 2, -2) can be tuned based on your needs.
        - Positive skew suggests upward trend, negative suggests downward.
    """

    high_stats = data["high"]
    low_stats = data["low"]
    close_stats = data["close"]

    price_range = high_stats["mean"] - low_stats["mean"]
    volatility = close_stats["std"]
    skew = close_stats["median"] - close_stats["mean"]

    if price_range > 10 and volatility > 5:
        standing = "risky"
    elif skew > 2:
        standing = "improving"
    elif skew < -2:
        standing = "declining"
    else:
        standing = "stable"

    return standing


def fetch_stock_data(
    params: str, ticker: str, base_url: str = "https://www.alphavantage.co", endpoint: str = "query"
):
    """
    URL Sample:
    https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&outputsize=full&apikey=demo&symbol=IBM

    Full Documentation: https://www.alphavantage.co/documentation/
    """

    result = {}
    request_uri = f"{base_url}/{endpoint}?{params}&symbol={ticker}"

    try:
        response = requests.get(request_uri, timeout=10)

        if response.status_code == 404:  # 404 Not Found.
            raise requests.HTTPError(
                "The request was not found. Check and try again."
            )

        if response.status_code == 403:  # 403 Forbidden.
            raise requests.HTTPError(
                "Access was denied to you. Ensure exact API key spelling and try again."
            )

        if response.status_code == 200:  # 200 OK.
            pprint("Yay! The connection works!\n")

            data: dict = (
                response.json()
            )  # Get the content of the API. This should include the JSON files.

            # Get the details and standings.
            details = get_data_details(data)
            standing = get_standing(details[data["Meta Data"]["2. Symbol"]])

            # Add standing to the result.
            result = {**details, "standing": standing}

        return result

    except requests.RequestException as error:
        print(f"There was an issue with fetching the data. Error:\n{error}")
        return None
