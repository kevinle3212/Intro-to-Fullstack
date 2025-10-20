"""
Module: 1 - fetch_stocks
Author: Oregon Software Consulting; Junior Software Engineer, Kevin Le
Purpose: Analyze real-time stock data using Alpha Vantage API and pandas.

This module fetches intraday stock data from the Alpha Vantage API, transforms it into a structured
pandas DataFrame, computes descriptive statistics (mean, std, median, min, max) for each price type,
and classifies the stock's standing based on volatility, price range, and skewness.

Key Functions:
- get_data_details(data: dict) -> dict:
    Converts raw API response into statistical summaries for open, high, low, close, and volume.

- get_standing(data: dict) -> str:
    Evaluates stock health and returns one of four status labels: 'risky', 'improving', 'declining', 'stable'.

- fetch_stock_data(params: str, base_url: str, endpoint: str) -> dict | None:
    Sends a GET request to Alpha Vantage, parses the response, and returns structured statistics and standing.

Usage:
Run this module (without the '.py' extension) with:
    python3 -m backend.data.fetch_stocks

Example:
    >>> output = fetch_stock_data("function=TIME_SERIES_INTRADAY&symbol=IBM&interval=5min&apikey=YOUR_API_KEY")
    >>> print(output['IBM']['close']['mean'])
    >>> print(output['standing'])

Dependencies:
- requests
- pandas
- pprint (For Debugging)
- os
- python-dotenv

Notes:
- API key is required and passed via query string.
- Standard deviation uses sample std (ddof=1).
- Designed for modular integration with fullstack backend pipelines.
"""

import os
from pprint import pprint
from dotenv import load_dotenv
import pandas as pd
import requests

load_dotenv()  # Loads variables from .env into the environment.
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")


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
    for timestamp, candle in time_series.items():
        df_data.append(
            {
                "timestamp": timestamp,
                "open": float(candle["1. open"]),
                "high": float(candle["2. high"]),
                "low": float(candle["3. low"]),
                "close": float(candle["4. close"]),
                "volume": float(candle["5. volume"]),
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
    params: str, base_url: str = "https://www.alphavantage.co", endpoint: str = "query"
):
    """
    URL Sample:
    https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=IBM&outputsize=full&apikey=demo

    Full Documentation: https://www.alphavantage.co/documentation/
    """

    result = {}
    request_uri = f"{base_url}/{endpoint}?{params}"

    try:
        response = requests.get(request_uri, timeout=10)

        if response.status_code == 404:  # 404 Not Found.
            raise requests.HTTPError(
                "The request was not found. Check and try again."
            )
        elif response.status_code == 403:  # 403 Forbidden.
            raise requests.HTTPError(
                "Access was denied to you. Ensure exact API key spelling and try again."
            )
        elif response.status_code == 200:  # 200 OK.
            print("Yay! The connection works!\n")

            data: dict = (
                response.json()
            )  # Get the content of the API. This should include the JSON files.
            pprint(data)

            # Get the details and standings.
            details = get_data_details(data)
            standing = get_standing(details[data["Meta Data"]["2. Symbol"]])

            # Add standing to the result.
            result = {**details, "standing": standing}

        return result

    except requests.RequestException as error:
        print(f"There was an issue with fetching the data. Error:\n{error}")
        return None


output = fetch_stock_data(
    "function=TIME_SERIES_INTRADAY&symbol=IBM&interval=5min&outputsize=full&apikey={ALPHA_VANTAGE_API_KEY}"
)
print(output)
