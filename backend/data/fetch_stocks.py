
# _____________________________________ Module 1 _____________________________________ #

import requests # run `pip install requests` if haven't already
from pprint import pprint
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# For code running (print testing, etc...), run the file as a `module` with the flag -m
# py -m backend.data.fetch_stocks <- no .py

# TODO 4
def get_data_details(data:dict)->dict:
    # Extract the time series data (the key varies based on the function used)
    # For TIME_SERIES_MONTHLY, the key is "Monthly Time Series"
    time_series_key = None
    symbol_key = "Meta Data"
    
    # Find the time series key
    for key in data.keys():
        if "Time Series" in key:
            time_series_key = key
            break
    
    if not time_series_key:
        raise Exception("Could not find time series data in response")
    
    # Get the ticker symbol from metadata
    ticker = data.get(symbol_key, {}).get("2. Symbol", "UNKNOWN")
    
    # Extract the time series records
    time_series = data[time_series_key]
    
    # Convert to list of dictionaries for easier pandas processing
    records = []
    for date, values in time_series.items():
        record = {
            'open': float(values['1. open']),
            'high': float(values['2. high']),
            'low': float(values['3. low']),
            'close': float(values['4. close']),
            'volume': float(values['5. volume'])
        }
        records.append(record)
    
    # Create pandas DataFrame
    stocks = pd.DataFrame(records)
    
    # Get count of records
    count = len(stocks)
    
    # Calculate statistics for each column in the correct order
    ticker_data = {}
    
    for column in ['open', 'high', 'low', 'close', 'volume']:
        ticker_data[column] = {
            'mean': float(stocks[column].mean()),
            'std': float(stocks[column].std()),
            'median': float(stocks[column].median()),
            'low': float(stocks[column].min()),
            'max': float(stocks[column].max())
        }
    
    # Build result in the correct order: ticker data first, then count
    result = {
        ticker: ticker_data,
        'count': count
    }
    
    return result


# TODO 5
def get_standing(details:dict)->str:
    # Extract the ticker name (first key that isn't 'count')
    ticker = None
    for key in details.keys():
        if key != 'count':
            ticker = key
            break
    
    if not ticker:
        return "unknown"
    
    # Get the statistics for the ticker
    data = details[ticker]
    
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

# we will export this function 
def fetch_stock_data(params:str, base_url:str=" https://www.alphavantage.co", endpoint:str="query"):
    '''
    URL Sample:
    https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=IBM&outputsize=full&apikey=demo
    
    API Key: 4YFVIJ6LXV2U1GZ9
    ---
    
    Full Documentation:
    
    https://www.alphavantage.co/documentation/ <---------- # TODO 1
    
    '''
    result = {}
    api_key = os.getenv('APIKEY')
    if not api_key:
        raise ValueError("API key not found in environment variables")
    request_uri = f'{base_url}/{endpoint}?{params}&apikey={api_key}' # TODO 2: build the request URI here!! use the parameters (base_url, endpoint, params) as building blocks
    try:
        
        response = requests.get(request_uri) # creates the request
        
        if response.status_code == 404: # 404 not found
            raise Exception("The error indicates that the request was not found. Check the request and try again.")
        elif response.status_code == 403: # 403 forbidden
            raise Exception("Access was denied to you. Ensure exact API key spelling and try again. If issue persists contact Daniel")
        elif response.status_code == 200: # 200 OK
            print('Yay! The connection works!\n')

            data:dict = response.json() # get the content of the API. This should include the JSON files
            #pprint(data)
            
            # TODO 4: Uncomment and implement
            details = get_data_details(data)
            #pprint(details)
            
            # TODO 5
            standing = get_standing(details)
            details["standing"] = standing
            result = details
            
            #pprint(result)
        
        return result 

    except Exception as some_error:
        print(f"There was an issue with the data fetching function. Error:\n{some_error}")
        return None

fetch_stock_data('function=TIME_SERIES_MONTHLY&symbol=IBM&outputsize=full') # TODO 3: Test the function!


