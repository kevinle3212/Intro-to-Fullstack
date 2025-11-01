
# _____________________________________ Module 1 _____________________________________ #

import requests # run `pip install requests` if haven't already
from pprint import pprint
from dotenv import load_dotenv
import os

# For code running (print testing, etc...), run the file as a `module` with the flag -m
# py -m backend.data.fetch_stocks <- no .py

# we will export this function 


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
    stocks = pd.DataFrame.from_dict(data["Time Series (60min)"], orient='index')
    cols = ["open", "high", "low", "close", "volume"]
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

def fetch_stock_data(params:str, base_url:str=" https://www.alphavantage.co", endpoint:str="query"):
    '''
    URL Sample:
    https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=IBM&outputsize=full&apikey=demo
    
    API Key:
    ---
    
    Full Documentation:
    
    https://www.alphavantage.co/documentation/ <---------- # TODO 1
    
    '''

    load_dotenv()
    api_key = os.getenv("API_KEY")

    result = {}
    request_uri = f'{base_url}' + '/' + f'{endpoint}' + f'{params}' + '&apikey=' + f"{api_key}"  # TODO 2: build the request URI here!! use the parameters (base_url, endpoint, params) as building blocks
    print(f"Request URI: {request_uri}\n")
    try:
        
        response = requests.get(request_uri) # creates the request
        
        if response.status_code == 404: # 404 not found
            raise Exception("The error indicates that the request was not found. Check the request and try again.")
        elif response.status_code == 403: # 403 forbidden
            raise Exception("Access was denied to you. Ensure exact API key spelling and try again. If issue persists contact Daniel")
        elif response.status_code == 200: # 200 OK
            print('Yay! The connection works!\n')

            data:dict = response.json() # get the content of the API. This should include the JSON files
            pprint(data)
            
            details = get_data_details(data)
            

            standing = get_standing(details)
            result = details["standing"] = standing
        
        return result # Done

    except Exception as some_error:
        print(f"There was an issue with the data fetching function. Error:\n{some_error}")
        return None

#fetch_stock_data(params="/?function=TIME_SERIES_INTRADAY&symbol=IBM&interval=60min&outputsize=full")
