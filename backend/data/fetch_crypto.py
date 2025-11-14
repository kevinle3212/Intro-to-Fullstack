"""
Module: fetch_crypto.py
Path: backend/data/fetch_crypto.py
Author: Oregon Software Consulting; Junior Software Engineer, Kevin Le
Purpose: Fetch and analyze historical cryptocurrency price data from CryptoCompare API.

Overview:
---------
This module retrieves historical daily cryptocurrency price data (OHLCV: Open, High, Low, 
Close, Volume) from the CryptoCompare API and computes statistical summaries to help evaluate
crypto performance and market conditions.

Similar to the stock data module (fetch_stocks.py), this module transforms raw time-series
crypto data into structured statistical insights, including mean, standard deviation, median,
minimum, and maximum values for each price metric. It also classifies cryptocurrencies into
one of four health categories based on volatility, price range, and price trend (skewness).

Key Functions:
--------------
1. calculate_stats(values: list) -> dict
   - Helper function to calculate five statistical measures for any list of numbers.
   - Returns dictionary with mean, std, median, min, and max.

2. parse_data(raw_data: list) -> dict
   - Extracts OHLCV fields and timestamps from API response.
   - Creates list of data points with timestamps for each daily record.
   - Calculates statistics for open, high, low, close, and volume.
   - Adds count and standing classification.
   - Returns structured dictionary ready for export.

3. get_standing(data: dict) -> str
   - Analyzes crypto health using three key metrics:
     * Price range: Difference between average high and low (market volatility).
     * Volatility: Standard deviation of closing prices (price stability).
     * Skew: Difference between median and mean close (trend direction).
   - Returns classification: 'risky', 'improving', 'declining', or 'stable'.

4. fetch_crypto_data(symbol: str, days: int) -> dict | None
   - Main export function that orchestrates the entire data pipeline.
   - Sends GET request to CryptoCompare API with specified parameters.
   - Handles HTTP errors (404, 403, 500, 200) with appropriate error messages.
   - Parses response to extract timestamped price data.
   - Returns structured statistics with individual data points.
   - Returns None if any errors occur during fetching or processing.

Usage:
------
Run this module directly from the command line:
    python3 -m backend.data.fetch_crypto

Or import into another module:
    from backend.data.fetch_crypto import fetch_crypto_data
    
    data = fetch_crypto_data("BTC", days=30)
    print(data['BTC']['close']['mean'])
    print(data['BTC']['data_points'][0])
    print(data['standing'])

Output Format:
--------------
{
    'BTC': {
        'data_points': [
            {
                'timestamp': '11-14-2025 00:00',
                'open': 78561.62,
                'high': 83608.26,
                'low': 76581.52,
                'close': 82919.47,
                'volume': 3744822903.84
            },
            ...
        ],
        'open': {'mean': 78561.62, 'std': 2401.50, 'median': 78200.00, 'min': 75000.00, 'max': 82000.00},
        'high': {'mean': 83608.26, 'std': 2380.00, 'median': 83500.00, 'min': 76000.00, 'max': 88000.00},
        'low': {'mean': 76581.52, 'std': 2440.00, 'median': 76400.00, 'min': 72000.00, 'max': 81000.00},
        'close': {'mean': 82919.47, 'std': 2400.00, 'median': 82800.00, 'min': 75500.00, 'max': 87000.00},
        'volume': {'mean': 3744822903.84, 'std': 450000000, 'median': 3700000000, 'min': 2000000000, 'max': 5000000000},
        'count': 30
    },
    'standing': 'stable'
}

Dependencies:
-------------
- requests: HTTP library for making API calls.
- statistics: Built-in Python module for statistical calculations.
- datetime: Built-in Python module for timestamp conversions.
- python-dotenv: Load environment variables from .env file (via support.py).

Environment Variables:
----------------------
COINDESK_API_KEY: Your API key from CryptoCompare (stored in .env file).

API Documentation:
------------------
CryptoCompare API: https://min-api.cryptocompare.com/documentation
Example Request: https://min-api.cryptocompare.com/data/v2/histoday?fsym=BTC&tsym=USD&limit=30

Notes:
------
- API returns nested structure: data -> Data -> Data (array of daily records).
- Each record contains OHLCV data, Unix timestamp, and conversion metadata.
- Timestamps are converted from Unix format to MM-DD-YYYY HH:MM format.
- We extract: open, high, low, close, volumeto, and time (ignore volumefrom, conversionSymbol, etc.).
- Standard deviation calculated using statistics.stdev (sample std).
- Standing thresholds (10, 5, 2, -2) can be adjusted based on crypto volatility.

Error Handling:
---------------
- Returns None if HTTP request fails (404, 403, 500, timeout, connection issues).
- Handles empty or malformed API responses.
- Validates data structure before processing.
- All errors are caught and logged to console for debugging.

Differences from fetch_stocks.py:
----------------------------------
- Uses statistics module instead of pandas (simpler, no DataFrame needed).
- API returns daily data instead of intraday (5min intervals).
- Different API structure (nested Data.Data vs Time Series).
- Volume uses 'volumeto' (USD volume) instead of 'volume' (shares traded).
- Includes timestamped data points for each day in addition to statistics.

Author: Kevin Le
Last Modified: November 14, 2025
"""

import datetime
import statistics
import requests

from backend.utils.support import get_secret


def calculate_stats(values):
    """
    Calculate statistical measures for a list of numbers.
    
    This helper function computes five key statistics that help us understand
    the distribution and behavior of price data.
    
    Args:
        values: List of numbers (prices or volumes) to analyze.
    
    Returns:
        Dictionary with five statistical measures:
        {
            'mean': Average value,
            'std': Standard deviation (measure of volatility),
            'median': Middle value (50th percentile),
            'min': Lowest value,
            'max': Highest value
        }
    
    Raises:
        ValueError: If values list is empty.
        statistics.StatisticsError: If std cannot be calculated (need at least 2 values).
    
    Example:
        >>> prices = [100, 105, 98, 102, 110]
        >>> stats = calculate_stats(prices)
        >>> print(stats['mean'])
        103.0
    """
    if not values:
        raise ValueError("Cannot calculate stats on empty list.")

    return {
        "mean": float(statistics.mean(values)),
        "std": float(statistics.stdev(values)),
        "median": float(statistics.median(values)),
        "min": float(min(values)),
        "max": float(max(values)),
    }


def get_standing(data):
    """
    Determine if a crypto is risky, improving, declining, or stable.
    
    This function evaluates crypto health based on three calculated metrics:
    price range, volatility, and skewness. It assigns one of four status 
    categories: 'risky', 'improving', 'declining', or 'stable'.
    
    Args:
        data: Dictionary with 'high', 'low', and 'close' statistics.
              Each must contain 'mean', 'median', and 'std' keys.
    
    Returns:
        str: One of four status values:
            - 'risky': Price range > 10 AND volatility > 5.
            - 'improving': Price skew (median - mean) > 2.
            - 'declining': Price skew (median - mean) < -2.
            - 'stable': None of the above conditions met.
    
    Raises:
        KeyError: If expected statistical keys are missing from the input
    
    Example:
        >>> data = fetch_crypto_data("BTC")
        >>> print(data['standing'])
        'stable'
    
    Notes:
        - Price range = average high - average low (measures price movement span).
        - Volatility = standard deviation of closing prices (measures price variation).
        - Skew = median closing price - mean closing price (indicates trend direction).
        - Thresholds (10, 5, 2, -2) can be tuned for crypto's higher volatility.
        - Positive skew suggests upward trend, negative suggests downward.
    """

    try:
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

    except KeyError as e:
        raise ValueError(f"Missing required data for standing calculation: {e}") from e

def parse_data(raw_data):
    """
    Parse raw crypto API data into organized statistics with timestamped data points.
    
    This function performs the critical task of data cleaning and transformation:
    1. Converts Unix timestamps to human-readable MM-DD-YYYY HH:MM format.
    2. Extracts OHLCV fields for each daily record with its timestamp.
    3. Creates a list of complete data points (timestamp + all prices).
    4. Converts all string/numeric values to floats for consistency.
    5. Calculates five statistics for each price field.
    6. Counts the total number of data points.
    7. Determines the crypto's standing classification.
    
    Args:
        raw_data (list): List of daily crypto records from CryptoCompare API.
                        Each record is a dictionary containing:
                        - 'time': Unix timestamp (seconds since epoch).
                        - 'open': Opening price of the day.
                        - 'high': Highest price of the day.
                        - 'low': Lowest price of the day.
                        - 'close': Closing price of the day.
                        - 'volumeto': Volume traded in USD (we use this, not volumefrom).
                        - Other fields like 'conversionSymbol' (ignored).
    
    Returns:
        dict: Dictionary with this structure:
            {
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
                'count': int,
                'standing': str
            }
    
    Raises:
        ValueError: If data is empty or missing required fields, or if values 
                   cannot be converted to float.
        KeyError: If expected OHLCV or time fields are not in the data.
        TypeError: If timestamp conversion fails or values have wrong type.
    
    Example:
        >>> raw = [
        ...     {'time': 1760572800, 'open': 100, 'high': 105, 'low': 98, 
        ...      'close': 102, 'volumeto': 1000000},
        ...     ...
        ... ]
        >>> parsed = parse_data(raw)
        >>> print(parsed['close']['mean'])
        102.0
        >>> print(parsed['data_points'][0]['timestamp'])
        '11-14-2025 00:00'
        >>> print(parsed['data_points'][0]['close'])
        102.0
    
    Notes:
        - This is the "parsing" step - cleaning and structuring messy data.
        - Unix timestamps are converted using datetime.fromtimestamp().
        - Time format is MM-DD-YYYY HH:MM (e.g., "11-14-2025 00:00").
        - Since this is daily data, time is usually 00:00 (midnight UTC).
        - We ignore fields like 'conversionSymbol', 'conversionType', 'volumefrom'.
        - Volume uses 'volumeto' (USD value) which is more meaningful than 'volumefrom'.
        - All prices are converted to float for consistent statistical calculations.
        - Data points are ordered chronologically as returned by the API.
    """
    if not raw_data:
        raise ValueError("No data to parse - received empty list!")

    try:
        data_points = []
        for entry in raw_data:
            timestamp = datetime.datetime.fromtimestamp(entry["time"]).strftime("%m-%d-%Y %H:%M")
            data_points.append({
                "timestamp": timestamp,
                "open": float(entry["open"]),
                "high": float(entry["high"]),
                "low": float(entry["low"]),
                "close": float(entry["close"]),
                "volume": float(entry["volumeto"])
            })

        opens = [point["open"] for point in data_points]
        highs = [point["high"] for point in data_points]
        lows = [point["low"] for point in data_points]
        closes = [point["close"] for point in data_points]
        volumetos = [point["volume"] for point in data_points]

    except KeyError as e:
        raise KeyError(f"Missing expected field in crypto data: {e}") from e
    except (ValueError, TypeError) as e:
        raise ValueError(f"Could not convert price data to float: {e}") from e

    result = {
        "data_points": data_points,
        "open": calculate_stats(opens),
        "high": calculate_stats(highs),
        "low": calculate_stats(lows),
        "close": calculate_stats(closes),
        "volume": calculate_stats(volumetos),
        "count": len(raw_data),
    }

    # Determine the crypto's standing based on the statistics.
    result["standing"] = get_standing(result)

    return result


def fetch_crypto_data(symbol, days=30):
    """
    Fetch cryptocurrency data from CryptoCompare API and return timestamped statistics.
    
    This is the main export function that orchestrates the entire data pipeline:
    1. Builds the API request with proper authentication.
    2. Makes HTTP GET request to CryptoCompare API.
    3. Handles all possible HTTP errors (404, 403, 500, etc.) with detailed messages.
    4. Validates the API response structure.
    5. Parses the nested response to extract price records with timestamps.
    6. Calculates statistics using parse_data().
    7. Returns data in a structured format with both individual data points and summaries.
    
    Args:
        symbol (str): Crypto symbol (e.g., 'BTC', 'ETH', 'SOL', 'ADA').
                     Case insensitive - will be converted to uppercase.
        days (int, optional): Number of days of historical data to fetch.
                             Default: 30 days.
                             Valid range: 1-2000 days.
    
    Returns:
        dict | None: Dictionary in this format if successful:
            {
                'BTC': {  # The symbol in uppercase
                    'data_points': [
                        {
                            'timestamp': '11-14-2025 00:00',
                            'open': 78561.62,
                            'high': 83608.26,
                            'low': 76581.52,
                            'close': 82919.47,
                            'volume': 3744822903.84
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
        >>> data = fetch_crypto_data("BTC", days=30)
        >>> if data:
        ...     print(f"BTC average close: ${data['BTC']['close']['mean']:.2f}")
        ...     print(f"Market status: {data['standing']}")
        ...     print(f"Latest price on {data['BTC']['data_points'][-1]['timestamp']}: "
        ...           f"${data['BTC']['data_points'][-1]['close']:.2f}")
        Fetching 30 days of data for BTC...
        Yay! The connection works!
        
        BTC average close: $82919.47
        Market status: stable
        Latest price on 11-14-2025 00:00: $82919.47
        
        >>> # Access individual data points
        >>> for point in data['BTC']['data_points'][:3]:
        ...     print(f"{point['timestamp']}: ${point['close']:.2f}")
        11-14-2025 00:00: $82919.47
        11-13-2025 00:00: $80000.00
        11-12-2025 00:00: $78500.00
    
    API Details:
        Request URL: https://min-api.cryptocompare.com/data/v2/histoday
        Parameters:
            - fsym: From symbol (the crypto, e.g., BTC).
            - tsym: To symbol (the fiat currency, e.g., USD).
            - limit: Number of days to fetch (1-2000).
        Headers:
            - authorization: "Apikey {your_api_key}"
        Response Structure:
            {
                "Response": "Success",
                "Data": {
                    "Data": [
                        {
                            "time": 1741651200,
                            "open": 78561.62,
                            "high": 83608.26,
                            "low": 76581.52,
                            "close": 82919.47,
                            "volumefrom": 46456.32,
                            "volumeto": 3744822903.84,
                            "conversionType": "direct",
                            "conversionSymbol": ""
                        },
                        ...
                    ]
                }
            }
    
    Error Handling:
        - Network errors: Timeout (10s limit), ConnectionError.
        - HTTP errors: 
            * 404 (Not Found): API endpoint doesn't exist.
            * 403 (Forbidden): Invalid API key or insufficient permissions.
            * 500 (Server Error): CryptoCompare server issues.
        - API errors: Invalid symbol, rate limiting, malformed requests.
        - Data errors: Empty response, missing fields, invalid structure.
        All errors are caught, logged to console, and return None.
    
    Notes:
        - CryptoCompare API has rate limits (check their documentation).
        - API key is required and loaded from .env file via get_secret().
        - Response is nested: data["Data"]["Data"] contains the actual records.
        - This function matches fetch_stock_data() output format for consistency.
        - Request timeout is set to 10 seconds to prevent hanging.
        - Timestamps are converted from Unix format to MM-DD-YYYY HH:MM.
        - Data points are returned in chronological order.
    """

    try:
        base_url = "https://min-api.cryptocompare.com"
        endpoint = "data/v2/histoday"
        api_key = get_secret("COINDESK_API_KEY")

        if not api_key:
            raise ValueError("API key not found - check your .env file for 'COINDESK_API_KEY'!")

        params = {
            "fsym": symbol.upper(),
            "tsym": "USD",
            "limit": days
        }

        headers = {"authorization": f"Apikey {api_key}"}

        request_uri = f"{base_url}/{endpoint}"

        print(f"Fetching {days} days of data for {symbol.upper()}...")
        response = requests.get(request_uri, params=params, headers=headers, timeout=10)

        if response.status_code == 404:  # 404 Not Found
            raise requests.HTTPError(
                "404 Not Found - The API endpoint was not found. Check the URL."
            )

        if response.status_code == 403:  # 403 Forbidden
            raise requests.HTTPError(
                "403 Forbidden - Access denied. Check your API key spelling and permissions."
            )

        if response.status_code == 500:  # 500 Internal Server Error
            raise requests.HTTPError(
                "500 Internal Server Error - The API server encountered an error. Try again later."
            )

        if response.status_code == 200:  # 200 OK - Success!
            print("Yay! The connection works!\n")

            # Parse the JSON response.
            data = response.json()

            if not data:
                raise ValueError("API returned empty response!")

            # Check if the API returned an error message.
            if data.get("Response") == "Error":
                error_message = data.get("Message", "Unknown API error")
                raise ValueError(f"API Error: {error_message}")

            # Extract the actual price records (parsing the nested structure).
            # The response structure is: data -> Data -> Data.
            try:
                raw_data = data["Data"]["Data"]
            except KeyError as e:
                raise KeyError(
                    f"Unexpected API response structure - missing expected field: {e}. "
                    f"Received keys: {list(data.keys())}."
                ) from e

            if not raw_data:
                raise ValueError(f"No historical data available for {symbol.upper()}.")

            # Parse the data and calculate all statistics.
            details = parse_data(raw_data)

            # Extract standing from details (it's inside the parsed data).
            standing = details["standing"]

            # Build result matching fetch_stock_data structure.
            # Standing should be at root level, same as fetch_stock_data.
            result = {symbol.upper(): details, "standing": standing}

            return result

        else:
            raise requests.HTTPError(
                f"Request failed with status code {response.status_code}. Reason: {response.reason}"
            )

    except requests.exceptions.Timeout:
        print("Error: Request timed out after 10 seconds. Check your internet connection.")
        return None

    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to API. Check your internet connection.")
        return None

    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        return None

    except requests.exceptions.RequestException as e:
        print(f"There was an issue with fetching the data. Error:\n{e}")
        return None

    except (ValueError, KeyError) as e:
        print(f"Data processing error: {e}")
        return None

    # Catch the most likely unexpected runtime errors explicitly.
    except (TypeError, AttributeError, RuntimeError) as e:
        print(f"Unexpected processing error occurred: {type(e).__name__} - {e}")
        return None
