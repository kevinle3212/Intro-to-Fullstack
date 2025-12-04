
# _____________________________________ Module 4 _____________________________________ #

# Pay close attention to the absolute import pathing.
# We don't do relative paths for projects like these.

import sys
from pathlib import Path

# Add project root to path for imports to work when running directly
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# ____________________ Loaders ____________________ #
from backend.data.fetch_stocks import fetch_stock_data
from backend.data.fetch_crypto import fetch_crypto_data

# connection to SQL class that we created in Module 3
from backend.database.Connection import Connection

# main commander class. Similar to a main function.
# we will use this export to manage all of the API endpoint we will create
class Commander(Connection):
    
    # def __init__(self) -> None:
    def __init__(self, stock_parameters=None, crypto_ticker='BTC', crypto_limit=30) -> None:
        '''
        Initialize the Commander class with stock and crypto parameters.
        
        Parameters:
        - stock_parameters: API parameters for stock data (e.g., 'function=TIME_SERIES_MONTHLY&symbol=IBM&outputsize=full')
        - crypto_ticker: Cryptocurrency symbol to fetch (default: 'BTC')
        - crypto_limit: Number of days of crypto data to fetch (default: 30)
        '''
        super().__init__()
        
# ____________________ Stocks ____________________#

        # Stock API parameters - can be passed during initialization
        self.stock_parameters = stock_parameters or 'function=TIME_SERIES_MONTHLY&symbol=IBM&outputsize=full'
        
        self.stock_data:dict = self.__load_stocks()

# _____________________ Crypto _____________________#

        # Crypto parameters - can be passed during initialization
        self.crypto_ticker = crypto_ticker
        self.crypto_limit = crypto_limit
        
        self.crypto_data:dict = self.__load_crypto()
        
# __________________________________________________ #

        self.tables:list = self.show_tables() 
        
    def __load_stocks(self):
        result = fetch_stock_data(self.stock_parameters)
        return result
    
    def __load_crypto(self):
        result = fetch_crypto_data(self.crypto_ticker, self.crypto_limit) if self.crypto_limit else  fetch_crypto_data(self.crypto_ticker)
        return result
    
# __________________________________________________ #

    def __init_stocks_table(self):
        '''
        Initializes and populates the stocks table from self.stock_data
        '''
        if not self.stock_data:
            print("No stock data available to populate table")
            return
        
        # Get the count and standing from the data
        count = self.stock_data.get('count', 0)
        standing = self.stock_data.get('standing', 'unknown')
        
        # Iterate through the data structure
        for ticker, metrics in self.stock_data.items():
            if ticker in ['count', 'standing']:
                continue

            # Iterate through each metric (open, high, low, close, volume)
            for metric, stats in metrics.items():
                # Insert a record for this ticker/metric combination
                status = self.query_submit(
                    table_name="stocks",
                    ticker=ticker,
                    metric=metric,
                    mean=stats.get('mean', 0.0),
                    median=stats.get('median', 0.0),
                    std=stats.get('std', 0.0),
                    low=stats.get('min_val', 0.0),
                    max=stats.get('max_val', 0.0),
                    count=count
                )
                
                if status != 201:
                    print(f"Failed to insert stock record for {ticker} - {metric}. Status: {status}")

    def __init_crypto_table(self):
        '''
        Initializes and populates the crypto table from self.crypto_data
        '''
        if not self.crypto_data:
            print("No crypto data available to populate table")
            return
        
        # Get the count and standing from the data
        count = self.crypto_data.get('count', 0)
        standing = self.crypto_data.get('standing', 'unknown')
        
        # Iterate through the data structure
        for ticker, metrics in self.crypto_data.items():
            if ticker in ['count', 'standing']:
                continue

            # Iterate through each metric (open, high, low, close, volumefrom, volumeto)
            for metric, stats in metrics.items():
                # Insert a record for this ticker/metric combination
                status = self.query_submit(
                    table_name="crypto",
                    ticker=ticker,
                    metric=metric,
                    mean=stats.get('mean', 0.0),
                    median=stats.get('median', 0.0),
                    std=stats.get('std', 0.0),
                    low=stats.get('min_val', 0.0),
                    max=stats.get('max_val', 0.0),
                    count=count
                )
                
                if status != 201:
                    print(f"Failed to insert crypto record for {ticker} - {metric}. Status: {status}")
    
    def __init_tables(self):
        '''
        *This function should only be run once*
        
        This function will populate the tables for both of our data sets within the same data base.
        Of course, one will be for the stock description and the other for the cyrpto.
        
        We must check if there are tables that already exist. At the start, there shouldn't.
        We will check by using the `show_tables` method from our child class.
        
        We then must create a table using the `query_create_table` function.
        
        We will iterate over the dictionaries within the `self.stock_data` and `self.crypto_data`, and populate 
        the entries one by one with the `query_submit` function. 
        '''
        try:
            self.query_create_table('stocks')
            self.query_create_table('crypto')
            
            self.__init_stocks_table()
            self.__init_crypto_table()
 
        except Exception as error:
            print("There was an error initializing the tables operation")
            return None
    
    # _________________ CRUD _________________ #
    
    def enter_record(self, table: str, **kwargs) -> int:
        '''
        Insert a single record manually into the specified table.
        
        Parameters:
        - table: The name of the table to insert into ('stocks' or 'crypto')
        - **kwargs: Column-value pairs for the record (e.g., ticker='AAPL', metric='open', mean=150.0)
        
        Returns:
        - Status code: 201 (Created) on success, 400 (Bad Request) on failure
        '''
        if not self.__is_valid_table(table):
            print(f"Error: Invalid table '{table}'. Valid tables are: {self.tables}")
            return 400
        
        if not kwargs:
            print("Error: No data provided to insert")
            return 400
        
        status = self.query_submit(table_name=table, **kwargs)
        
        if status == 201:
            print(f"Successfully inserted record into '{table}' table")
        else:
            print(f"Failed to insert record into '{table}' table")
        
        return status
    
    def extract_record(self, table: str, condition: str = None, values: tuple = None) -> list:
        '''
        Get specific record(s) from a table by condition or filter.
        
        Parameters:
        - table: The name of the table to query ('stocks' or 'crypto')
        - condition: SQL WHERE clause condition (e.g., "ticker = %s AND metric = %s")
        - values: Tuple of values to substitute in the condition (e.g., ('IBM', 'open'))
        
        Returns:
        - List of records matching the condition, or empty list if none found
        
        Example:
        - extract_record('stocks', 'ticker = %s', ('IBM',))
        - extract_record('stocks', 'ticker = %s AND metric = %s', ('IBM', 'open'))
        '''
        if not self.__is_valid_table(table):
            print(f"Error: Invalid table '{table}'. Valid tables are: {self.tables}")
            return []
        
        try:
            records = self.query_extract(table, condition or "", values)
            return records
        except Exception as error:
            print(f"Error extracting records from '{table}': {error}")
            return []
    
    def delete_record(self, table: str, condition: str, values: tuple = None) -> int:
        '''
        Delete record(s) from a table by a unique key or filter.
        
        Parameters:
        - table: The name of the table to delete from ('stocks' or 'crypto')
        - condition: SQL WHERE clause condition (e.g., "ticker = %s" or "id = %s")
        - values: Tuple of values to substitute in the condition
        
        Returns:
        - Status code: 200 (OK) on success, 400 (Bad Request) on failure
        
        Example:
        - delete_record('stocks', 'ticker = %s AND metric = %s', ('IBM', 'open'))
        - delete_record('stocks', 'id = %s', (5,))
        '''
        if not self.__is_valid_table(table):
            print(f"Error: Invalid table '{table}'. Valid tables are: {self.tables}")
            return 400
        
        if not condition:
            print("Error: No condition provided. Refusing to delete all records.")
            return 400
        
        try:
            status = self.query_delete_table(table, condition, values)
            if status == 200:
                print(f"Successfully deleted record(s) from '{table}' table")
            else:
                print(f"Failed to delete record(s) from '{table}' table")
            return status
        except Exception as error:
            print(f"Error deleting records from '{table}': {error}")
            return 400
    
    def extract_table(self, table: str) -> list:
        '''
        Return all records from a given table.
        
        Parameters:
        - table: The name of the table to query ('stocks' or 'crypto')
        
        Returns:
        - List of all records in the table, or empty list if none found
        
        Example:
        - extract_table('stocks')
        - extract_table('crypto')
        '''
        if not self.__is_valid_table(table):
            print(f"Error: Invalid table '{table}'. Valid tables are: {self.tables}")
            return []
        
        try:
            records = self.get_table_data(table)
            print(f"Retrieved {len(records)} record(s) from '{table}' table")
            return records
        except Exception as error:
            print(f"Error extracting table '{table}': {error}")
            return []
    
    # ________________ Support ________________ #

    def __is_valid_table(self, table):
        return table in self.tables
    

if __name__ == "__main__":
    print("=== Initializing Commander ===")
    cmd = Commander()
    
    print(f"\nDatabase Connection Status: {cmd.status}")
    print(f"Current Tables in Database: {cmd.tables}")
    
    print("\n=== Stock Data Summary ===")
    if cmd.stock_data:
        for key in cmd.stock_data.keys():
            print(f"  - {key}")
    else:
        print("  No stock data loaded")
    
    print("\n=== Crypto Data Summary ===")
    if cmd.crypto_data:
        for key in cmd.crypto_data.keys():
            print(f"  - {key}")
    else:
        print("  No crypto data loaded")
    
    # Initialize tables if they don't exist
    if 'stocks' not in cmd.tables or 'crypto' not in cmd.tables:
        print("\n=== Creating and Populating Tables ===")
        cmd._Commander__init_tables()  # Call private method
        
        # Refresh table list
        cmd.tables = cmd.show_tables()
        print(f"\nTables after initialization: {cmd.tables}")
    else:
        print("\nTables already exist. Skipping initialization.")
    
    # Show record counts
    if 'stocks' in cmd.tables:
        stock_records = cmd.extract_table('stocks')
        print(f"\nStock records in database: {len(stock_records)}")
    
    if 'crypto' in cmd.tables:
        crypto_records = cmd.extract_table('crypto')
        print(f"Crypto records in database: {len(crypto_records)}")
    
    cmd.close()