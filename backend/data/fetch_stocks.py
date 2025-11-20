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
   - Creates list of data points with timestamps for each interval.
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
    print(data['AAPL']['data_points'][0])
    print(data['standing'])

Output Format:
--------------
{
    'IBM': {
        'data_points': [
            {
                'timestamp': '11-14-2025 09:30',
                'open': 215.34,
                'high': 216.12,
                'low': 214.56,
                'close': 215.78,
                'volume': 1250000.0
            },
            ...
        ],
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
- datetime: Built-in Python module for timestamp formatting.
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
- Timestamps are formatted as MM-DD-YYYY HH:MM for consistency with crypto module.
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
Last Modified: November 14, 2025
"""

from pprint import pprint
import datetime
import requests
import pandas as pd

from backend.utils.support import get_secret

# Loads variables from .env into the environment.
ALPHA_VANTAGE_API_KEY = get_secret("ALPHA_VANTAGE_API_KEY")


def get_data_details(data: dict) -> dict:
    """
    Convert Alpha Vantage API response to statistics format with timestamped data points.
    
    This function takes raw stock data from the Alpha Vantage API and transforms 
    it into a structured format containing both individual timestamped data points
    and statistical analysis (mean, std, median, min, max) for each price type 
    (open, high, low, close, volume).
    
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
                    'data_points': [
                        {
                            'timestamp': str (MM-DD-YYYY HH:MM),
                            'open': float,
                            'high': float,
                            'low': float,
                            'close': float,
                            'volume': float
                        },
                        ...
                    ],
                    'open': {'mean': float, 'std': float, 'median': float, 'min': float, 'max': float},
                    'high': {'mean': float, 'std': float, 'median': float, 'min': float, 'max': float},
                    'low': {'mean': float, 'std': float, 'median': float, 'min': float, 'max': float},
                    'close': {'mean': float, 'std': float, 'median': float, 'min': float, 'max': float},
                    'volume': {'mean': float, 'std': float, 'median': float, 'min': float, 'max': float},
                    'count': int  # Total number of data points.
                }
            }
    
    Raises:
        KeyError: If expected keys are missing from the input data dictionary.
        ValueError: If price/volume strings cannot be converted to floats or 
                   timestamp parsing fails.
    
    Example:
        >>> data = {...}  # API response
        >>> stats = get_data_details(data)
        >>> print(stats['IBM']['close']['mean'])
        279.45
        >>> print(stats['IBM']['data_points'][0]['timestamp'])
        '11-14-2025 09:30'
        >>> print(stats['IBM']['data_points'][0]['close'])
        279.45
    
    Notes:
        - All price strings from the API are converted to float values.
        - Timestamps are converted from 'YYYY-MM-DD HH:MM:SS' to 'MM-DD-YYYY HH:MM'.
        - Statistics are calculated using pandas built-in methods.
        - Standard deviation uses pandas default (sample std with ddof=1).
        - Data points are ordered as returned by the API (typically newest first).
    """

    # Extract ticker and time series data.
    ticker = data["Meta Data"]["2. Symbol"]
    time_series = data["Time Series (5min)"]

    # Convert time series to list of data points with formatted timestamps.
    data_points = []
    for timestamp, info in time_series.items():
        # Convert timestamp from 'YYYY-MM-DD HH:MM:SS' to 'MM-DD-YYYY HH:MM'
        dt = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        formatted_timestamp = dt.strftime("%m-%d-%Y %H:%M")

        data_points.append({
            "timestamp": formatted_timestamp,
            "open": float(info["1. open"]),
            "high": float(info["2. high"]),
            "low": float(info["3. low"]),
            "close": float(info["4. close"]),
            "volume": float(info["5. volume"]),
        })

    # Create DataFrame for statistical calculations
    df = pd.DataFrame(data_points)

    # Calculate statistics for each price type.
    result: dict[str, dict] = {ticker: {}}

    # Add data points list first
    result[ticker]["data_points"] = data_points

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
    categories that help traders and analysts quickly assess market conditions.
    
    The classification logic prioritizes risk detection first, then looks for
    trend signals (improving/declining), and defaults to stable if no strong
    signals are detected.
    
    Args:
        data (dict): A dictionary of statistics for a single stock, typically 
            from the ticker key in get_data_details() output. Must contain:
            - 'high': dict with 'mean' key.
            - 'low': dict with 'mean' key.
            - 'close': dict with 'mean', 'median', and 'std' keys.
    
    Returns:
        str: One of four status values:
            - 'risky': High volatility AND wide price range detected.
                      Price range > 10 AND volatility > 5.
            - 'improving': Positive price trend detected (prices trending up).
                          Price skew (median - mean) > 2.
            - 'declining': Negative price trend detected (prices trending down).
                          Price skew (median - mean) < -2.
            - 'stable': None of the above conditions met (normal market conditions).
    
    Raises:
        KeyError: If expected statistical keys are missing from the input.
        TypeError: If statistical values are not numeric.
    
    Example:
        >>> stats = get_data_details(api_data)
        >>> status = get_standing(stats['IBM'])
        >>> print(status)
        'stable'
        
        >>> # For a volatile stock
        >>> volatile_stats = get_data_details(volatile_api_data)
        >>> print(get_standing(volatile_stats['TSLA']))
        'risky'
    
    Notes:
        - Price range = average high - average low (measures price movement span).
          Higher range indicates larger intraday price swings.
        - Volatility = standard deviation of closing prices (measures price stability).
          Higher std indicates more unpredictable price movements.
        - Skew = median closing price - mean closing price (indicates trend direction).
          Positive skew: median > mean (recent prices higher than average).
          Negative skew: median < mean (recent prices lower than average).
        - Thresholds (10, 5, 2, -2) can be tuned based on your risk tolerance.
        - The function checks conditions in order: risky → improving → declining → stable.
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
    Fetch stock data from Alpha Vantage API and return timestamped statistics.
    
    This is the main export function that orchestrates the entire data pipeline:
    1. Builds the API request URL with proper parameters.
    2. Makes HTTP GET request to Alpha Vantage API.
    3. Handles all possible HTTP errors (404, 403, 200) with detailed messages.
    4. Validates the API response structure.
    5. Parses the response to extract timestamped price records.
    6. Calculates statistics using get_data_details().
    7. Determines market standing using get_standing().
    8. Returns data in a structured format with both individual data points and summaries.
    
    Args:
        params (str): URL query parameters for the API request.
                     Example: "function=TIME_SERIES_INTRADAY&interval=5min&apikey=YOUR_KEY"
                     Should include: function, interval, outputsize, and apikey.
        ticker (str): Stock ticker symbol (e.g., 'IBM', 'AAPL', 'TSLA').
                     Case sensitive - use uppercase for consistency.
        base_url (str, optional): Base URL for Alpha Vantage API.
                                 Default: "https://www.alphavantage.co"
        endpoint (str, optional): API endpoint path.
                                 Default: "query"
    
    Returns:
        dict | None: Dictionary in this format if successful:
            {
                'IBM': {  # The ticker symbol
                    'data_points': [
                        {
                            'timestamp': '11-14-2025 09:30',
                            'open': 215.34,
                            'high': 216.12,
                            'low': 214.56,
                            'close': 215.78,
                            'volume': 1250000.0
                        },
                        ...
                    ],
                    'open': {'mean': float, 'std': float, 'median': float, 'min': float, 'max': float},
                    'high': {'mean': float, 'std': float, 'median': float, 'min': float, 'max': float},
                    'low': {'mean': float, 'std': float, 'median': float, 'min': float, 'max': float},
                    'close': {'mean': float, 'std': float, 'median': float, 'min': float, 'max': float},
                    'volume': {'mean': float, 'std': float, 'median': float, 'min': float, 'max': float},
                    'count': int
                },
                'standing': str  # 'risky', 'improving', 'declining', or 'stable'
            }
        
        Returns None if any error occurs (network, API, or data processing errors).
    
    Raises:
        Does not raise exceptions - catches all errors and returns None.
        Prints detailed error messages to console for debugging.
    
    Example:
        >>> data = fetch_stock_data(
        ...     "function=TIME_SERIES_INTRADAY&interval=5min&outputsize=compact&apikey=demo",
        ...     "IBM"
        ... )
        >>> if data:
        ...     print(f"IBM average close: ${data['IBM']['close']['mean']:.2f}")
        ...     print(f"Market status: {data['standing']}")
        ...     print(f"Latest price at {data['IBM']['data_points'][0]['timestamp']}: "
        ...           f"${data['IBM']['data_points'][0]['close']:.2f}")
        Yay! The connection works!
        
        IBM average close: $215.78
        Market status: stable
        Latest price at 11-14-2025 16:00: $215.78
        
        >>> # Access individual data points
        >>> for point in data['IBM']['data_points'][:3]:
        ...     print(f"{point['timestamp']}: ${point['close']:.2f}")
        11-14-2025 16:00: $215.78
        11-14-2025 15:55: $215.45
        11-14-2025 15:50: $215.20
    
    API Details:
        Request URL Format: 
        https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=IBM&interval=5min&apikey=demo
        
        Parameters:
            - function: API function (e.g., TIME_SERIES_INTRADAY)
            - symbol: Stock ticker symbol
            - interval: Time interval (1min, 5min, 15min, 30min, 60min)
            - outputsize: 'compact' (100 points) or 'full' (full day)
            - apikey: Your Alpha Vantage API key
        
        Response Structure:
            {
                "Meta Data": {
                    "1. Information": "Intraday (5min) open, high, low, close prices and volume",
                    "2. Symbol": "IBM",
                    "3. Last Refreshed": "2025-11-14 16:00:00",
                    "4. Interval": "5min",
                    "5. Output Size": "Compact",
                    "6. Time Zone": "US/Eastern"
                },
                "Time Series (5min)": {
                    "2025-11-14 16:00:00": {
                        "1. open": "215.3400",
                        "2. high": "216.1200",
                        "3. low": "214.5600",
                        "4. close": "215.7800",
                        "5. volume": "1250000"
                    },
                    ...
                }
            }
    
    Error Handling:
        - Network errors: Timeout (10s limit), ConnectionError.
        - HTTP errors:
            * 404 (Not Found): API endpoint doesn't exist or invalid URL.
            * 403 (Forbidden): Invalid API key or insufficient permissions.
        - API errors: Invalid symbol, rate limiting (5 calls/min free tier).
        - Data errors: Missing fields, invalid structure, conversion failures.
        All errors are caught, logged to console, and return None.
    
    Notes:
        - Alpha Vantage has rate limits: 5 calls/minute (free), 75 calls/minute (premium).
        - Request timeout is set to 10 seconds to prevent hanging.
        - Timestamps are converted from 'YYYY-MM-DD HH:MM:SS' to 'MM-DD-YYYY HH:MM'.
        - Data points are returned in the order provided by the API (newest first).
        - This function matches fetch_crypto_data() output format for consistency.
    
    URL Sample:
        https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&outputsize=full&apikey=demo&symbol=IBM

    Full Documentation: 
        https://www.alphavantage.co/documentation/
    """

    result = {}
    request_uri = f"{base_url}/{endpoint}?{params}&symbol={ticker}"

    try:
        response = requests.get(request_uri, timeout=10)

        if response.status_code == 404:  # 404 Not Found.
            raise requests.HTTPError(
                "404 Not Found - The request was not found. Check the URL and try again."
            )

        if response.status_code == 403:  # 403 Forbidden.
            raise requests.HTTPError(
                "403 Forbidden - Access was denied. Ensure exact API key spelling and try again."
            )

        if response.status_code == 200:  # 200 OK.
            pprint("Yay! The connection works!\n")

            data: dict = response.json()

            # Get the details and standings.
            details = get_data_details(data)
            standing = get_standing(details[data["Meta Data"]["2. Symbol"]])

            # Add standing to the result.
            result = {**details, "standing": standing}

        return result

    except requests.exceptions.Timeout:
        print("Error: Request timed out after 10 seconds. Check your internet connection.")
        return None

    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to API. Check your internet connection.")
        return None

    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        return None

    except requests.RequestException as error:
        print(f"There was an issue with fetching the data. Error:\n{error}")
        return None

    except (KeyError, ValueError) as e:
        print(f"Data processing error: {e}")
        return None

def print_result():
    """
    Helper function to print the fetched stock data for a given ticker symbol.

    Args:
        name (str): The stock ticker symbol to fetch data for.

    Returns:
        dict | None: The fetched stock data dictionary or None if an error occurred.
    """

    return fetch_stock_data(
          f"function=TIME_SERIES_INTRADAY&interval=5min&outputsize=full&apikey={ALPHA_VANTAGE_API_KEY}", "IBM"
      )

pprint(print_result())
