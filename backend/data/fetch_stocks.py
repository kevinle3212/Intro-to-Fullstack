
# _____________________________________ Module 1 _____________________________________ #

import requests # run `pip install requests` if haven't already
import pandas as pd
from pprint import pprint

# For code running (print testing, etc...), run the file as a `module` with the flag -m
# py -m backend.data.fetch_stocks <- no .py

# we will export this function 
def fetch_stock_data(params:str, base_url:str=" https://www.alphavantage.co", endpoint:str="query"):
    '''
    URL Sample:
    https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=IBM&outputsize=full&apikey=demo
    
    API Key:
    ---
    
    Full Documentation:
    
    https://www.alphavantage.co/documentation/ <---------- # TODO 1
    
    '''
    result = {}
    base_url = 'https://www.alphavantage.co'
    endpoint = 'query'
    params = 'function=TIME_SERIES_MONTHLY&symbol=IBM&apikey=QTX7LZ15VYHS2FWB'
    request_uri = f'{base_url}/{endpoint}?{params}' 
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
            get_data_details(data)
            
            # TODO 4: Uncomment and implement
            details = get_data_details(data)
            pprint(details)
            
            # TODO 5
            standing = get_standing(details)
            result = details["standing"] = standing
        
        return result # Done

    except Exception as some_error:
        print(f"There was an issue with the data fetching function. Error:\n{some_error}")
        return None



# TODO 4
def get_data_details(data:dict)->dict:
    """
    Parse Alpha Vantage time-series JSON and return:
    {
        "<SYMBOL>": {
            "open": {mean, std, median, low, max},
            "high": {mean, std, median, low, max},
            "low": {mean, std, median, low, max},
            "close": {mean, std, median, low, max},
            "volume": {mean, std, median, low, max},
        },
        "count": <int>
    }
    """
    # Extract ticker and time series data.
    ticker = data["Meta Data"]["2. Symbol"]

    time_series_key = next((k for k in data.keys() if "Time Series" in k), None)


    time_series = data[time_series_key]

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

    result["count"] = len(df)

    return result


            
   

    



# TODO 5
def get_standing(data:dict)->str:
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



fetch_stock_data('params', 'https://www.alphavantage.co', 'query') 