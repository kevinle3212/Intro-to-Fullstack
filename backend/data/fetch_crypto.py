# _____________________________________ Module 2 _____________________________________ #
import requests
from pprint import pprint
import pandas as pd 


def get_data_details(data : dict)->dict:
    '''
    This function takes in the data dictionary fetched from the API and extracts relevant details.
    
    Parameters:
    - data (dict): The JSON data fetched from the API.
    
    Returns:
    - dict: A dictionary containing extracted details such as metadata and time series data.
    '''
    details = {}

    # Validate data is not empty
    if not data:
        raise ValueError("Data is empty or None")

    # Create DataFrame from parsed data
    stocks = pd.DataFrame(data)
    
    # Select only the OHLCV columns we need for analysis
    cols = ["open", "high", "low", "close", "volumefrom", "volumeto"]
    
    # Validate all required columns exist
    missing_cols = [col for col in cols if col not in stocks.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    # Select only the columns we need
    stocks = stocks[cols]
    
    # Extract data for each column    
    foo = {}

    for col in cols:
        col_data = stocks[col].astype(float)
        foo[col] = {
            "mean": float(col_data.mean()),
            "std": float(col_data.std()),
            "median": float(col_data.median()),
            "low": float(col_data.min()),
            "max": float(col_data.max()),
        }

        
        
    
    # Metadata (mean, std, low, max)
    #details[data["Meta Data"]["2. Symbol"]] = foo
    details["BTC"] = foo
    
    # Numb of rows
    count = stocks.shape[0]
    details["count"] = count
        
    return details

def get_standing(details:dict)->str:
    
    data = details[tuple(details.keys())[0]]
    
    open_stats = data['open']
    high_stats = data['high']
    low_stats = data['low']
    close_stats = data['close']

    price_range = high_stats['mean'] - low_stats['mean']
    volatility = close_stats['std']
    skew = close_stats['median'] - close_stats['mean']

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

def fetch_crypto_data(symbol, days=30):
    '''
    Sample:
    https://min-api.cryptocompare.com/data/v2/histoday?fsym=BTC&tsym=USD&limit=30

    Full Documentation:
    
    https://developers.coindesk.com/documentation/legacy/Price/SingleSymbolPriceEndpoint
    
    Key:
    
    ---
    
    
    ADD ENOUGH ERROR HANDLING (try-except, if None checks, etc...)!
    
    '''
    url = 'https://min-api.cryptocompare.com/data/v2/histoday'
    
    key = ''
    
    params = {
        'fsym': symbol,
        'tsym': 'usd',
        'limit': days  # number of days
    }
    headers = {
        'authorization': f'Apikey {key}'
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        
        if response.status_code == 404: # 404 not found
            raise Exception("The error indicates that the request was not found. Check the request and try again.")
        elif response.status_code == 403: # 403 forbidden
            raise Exception("Access was denied to you. Ensure exact API key spelling and try again. If issue persists contact Daniel")
        elif response.status_code == 401: # 401 unauthorized
            raise Exception("Unauthorized access. API key is invalid or missing.")
        elif response.status_code == 429: # 429 too many requests
            raise Exception("Rate limit exceeded. Too many requests made to the API. Please wait before trying again.")
        elif response.status_code == 500: # 500 internal server error
            raise Exception("Internal server error. The API server encountered an issue. Try again later.")
        elif response.status_code == 503: # 503 service unavailable
            raise Exception("Service unavailable. The API is temporarily down. Try again later.")
        elif response.status_code != 200: # Any other non-200 status
            raise Exception(f"Unexpected error occurred. Status code: {response.status_code}")
        else: # 200 OK
            print('Yay! The connection works!\n')
        
    except Exception as some_error:
        print(f"There was an issue with the data fetching function. Error:\n{some_error}")
        return None
 
    data = response.json()
    
    # Validate response data
    if not data:
        raise ValueError("API returned empty response")
    
    # Parse the data to extract OHLCV records
    parsed_data = parse_data(data)
    
    # Get statistical details
    details = get_data_details(parsed_data)
    
    # Get the standing classification
    standing = get_standing(details)
    details["standing"] = standing
    
    # Return the complete result
    result = details
    pprint(result)
    
    return result 


def parse_data(data:dict) -> list[dict]:
    '''
    Parses the API response to extract only the relevant OHLCV data.
    
    Parameters:
    - data (dict): The full JSON response from the API
    
    Returns:
    - list[dict]: A list of dictionaries containing only the keys we care about
    '''
    # Validate that data structure exists
    if not data:
        raise ValueError("Data is None or empty")
    
    if "Data" not in data:
        raise ValueError("Expected 'Data' key not found in response")
    
    if "Data" not in data["Data"]:
        raise ValueError("Expected nested 'Data' key not found in response")
    
    # Keys we want to extract (OHLCV data)
    keys_wanted = ["open", "high", "low", "close", "volumefrom", "volumeto", "time", "conversionType", "conversionSymbol"]
    
    # Extract and filter the data
    try:
        parsed_data = [
            {key: record[key] for key in keys_wanted if key in record} 
            for record in data["Data"]["Data"]
        ]
    except (KeyError, TypeError) as e:
        raise ValueError(f"Error parsing data structure: {e}")
    
    # Validate we got data
    if not parsed_data:
        raise ValueError("No records were extracted from the API response")
    
    return parsed_data

fetch_crypto_data('BTC', 30)