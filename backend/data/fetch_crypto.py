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

    # Turns the metadata into a dictionary where each time interval is a new row
    
    stocks = pd.DataFrame(data)
    cols = ["open", "high", "low", "close", "volumefrom", "volumeto"]
    stocks.columns = cols
    
    
    # Extract data for each column    
    foo = {}

    for col in cols:
        col_data = stocks[col].astype(float)
        foo[col] = {
            "mean": col_data.mean(),
            "std": col_data.std(),
            "median": col_data.median(),
            "low": col_data.min(),
            "max": col_data.max(),
        }

        
        
    
    # Metadata (mean, std, low, max)
    details[data["Meta Data"]["2. Symbol"]] = foo
    
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
        elif response.status_code == 200: # 200 OK
            print('Yay! The connection works!\n')
        
    except Exception as some_error:
        print(f"There was an issue with the data fetching function. Error:\n{some_error}")
        return None
 
    data = response.json()
    #pprint(data)
    parsed_data = parse_data(data)
    
    
    #details = get_data_details(parsed_data)
    #pprint(details)
    
    # standing = get_standing(details)
    # print(standing)   
    return 


def parse_data(data:dict) -> list[dict]:
    keys_wanted = ["close", "high", "low", "open", "volumefrom", "volumeto"]
    
    # Check if keys wanted are in data, if so filter fo them
    #if keys_wanted not in data["Data"]["Data"]:
    #    raise ValueError(f"One of the keys wanted is not in the data. Keys wanted: {keys_wanted}")
    #else:
    parsed_data = [{key: d[key] for key in keys_wanted if key in d} for d in data["Data"]["Data"]]
    
    return parsed_data

