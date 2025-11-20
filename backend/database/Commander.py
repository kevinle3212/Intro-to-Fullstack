"""
Database commander module for managing stock and cryptocurrency data operations.

This module provides the Commander class, which serves as a high-level interface
for loading, storing, and managing financial data in a MySQL database. It handles
both stock market data (via Alpha Vantage API) and cryptocurrency data with full
CRUD operations.

Classes:
    Commander: Main database management class with CRUD operations for stocks and crypto.

Dependencies:
    - mysql.connector: Database connection and error handling
    - backend.data: Stock and crypto data fetching utilities
    - backend.database.connection: Base database connection class
    - backend.utils: Custom filters and secret management utilities

Environment Variables:
    ALPHA_VANTAGE_API_KEY: API key for Alpha Vantage stock data service
    SC_DATABASE_NAME: Name of the stock/crypto database

Example:
    >>> commander = Commander()
    >>> commander.enter_record("stocks", ticker="AAPL", price=150.25)
    >>> data = commander.extract_table("stocks")
"""

from typing import Any
from mysql.connector import Error

from backend.data.fetch_stocks import fetch_stock_data
from backend.data.fetch_crypto import fetch_crypto_data
from backend.database.connection import Connection
from backend.utils.filter import StockAndCryptoDatabaseFilter
from backend.utils.support import get_secret

ALPHA_VANTAGE_API_KEY = get_secret("ALPHA_VANTAGE_API_KEY")
STOCK_CRYPTO_DATABASE = get_secret("SC_DATABASE_NAME")

class Commander(Connection):
    """
    High-level database commander for managing stock and cryptocurrency data.
    
    Provides an interface for loading, storing, and managing financial data
    in a database. Handles both stock market data (via Alpha Vantage API) and
    cryptocurrency data with CRUD operations for database tables.
    
    Attributes:
        stock_parameters (str): API parameters for fetching stock data.
        stock_ticker (str): Stock ticker symbol to track (default: "IBM").
        stock_data (dict): Loaded stock market data.
        crypto_ticker (str): Cryptocurrency ticker symbol to track (default: "BTC").
        crypto_limit (int | None): Limit on crypto data retrieval.
        crypto_data (dict): Loaded cryptocurrency data.
        tables (list): Available database tables in the stock/crypto database.
    
    Inherits:
        Connection: Base database connection and query functionality.
    
    Example:
        >>> commander = Commander()
        >>> commander.enter_record("stocks", ticker="AAPL", price=150.25)
        >>> data = commander.extract_table("stocks")
    """
    def __init__(self):
        super().__init__()

        # Stock & Crypto Hard-coded Values.
        self.stock_parameters = f"""
            function=TIME_SERIES_INTRADAY&interval=5min&outputsize=full&apikey={ALPHA_VANTAGE_API_KEY}
            """
        self.stock_ticker = "IBM"

        self.stock_data = self.__load_stocks()

        self.crypto_ticker = "BTC"
        self.crypto_limit = None

        self.crypto_data = self.__load_crypto()

        self.tables = self.show_tables(STOCK_CRYPTO_DATABASE)

    def __load_stocks(self) -> dict | None:
        """
        Load stock data by fetching information for configured stock tickers.
        
        Uses:
            self.stock_parameters: Parameters for stock data retrieval.
            self.stock_ticker: Stock ticker symbol(s) to fetch data for.
        
        Returns:
            dict: Stock data returned by fetch_stock_data().
        """

        result = fetch_stock_data(self.stock_parameters, self.stock_ticker)
        return result

    def __load_crypto(self) -> dict | None:
        """
        Load cryptocurrency data by fetching information for configured crypto tickers.
        
        Uses:
            self.crypto_ticker: Cryptocurrency ticker symbol(s) to fetch data for.
            self.crypto_limit: Limit on the amount of crypto data to retrieve.
        
        Returns:
            dict: Cryptocurrency data returned by fetch_crypto_data().
        """

        result = fetch_crypto_data(self.crypto_ticker, self.crypto_limit)
        return result

    def __init_stocks_table(self) -> int:
        """
        Initialize the stocks database table by submitting metrics for each stock.
        
        Iterates through all stocks in self.stock_data and submits each metric
        to the database via query_submit(). Skips special keys 'count' and 'standing'.
        
        Uses:
            self.stock_data (dict): Stock data structure in format:
                {
                    'TICKER': {
                        'metric_name': {stat_data},
                        ...
                    },
                    'count': ...,  # skipped
                    'standing': ...  # skipped
                }

        Returns:
            int: Status code - 201 if all submissions succeeded, error code from
                handle_db_error() if any submission failed.
        
        Raises:
            Logs error via handle_db_error() when query_submit() returns status != 201,
            indicating a database submission failure.
        """

        for ticker, metrics in self.stock_data.items():
            if ticker in ["count", "standing"]:
                continue

            for metric, stats in metrics.items():
                data = {
                    metric: stats
                }

                try:
                    self.query_submit(**data)
                except Error as e:
                    return self.handle_db_error(e)

        return 201

    def __init_crypto_table(self) -> int:
        """
        Initialize the crypto database table by submitting metrics for each cryptocurrency.
        
        Iterates through all cryptocurrencies in self.crypto_data and submits each metric
        to the database via query_submit(). Skips special keys 'count' and 'standing'.
        Handles database errors by logging issues when submission fails (non-201 status).

        Returns:
            int: Status code - 201 if all submissions succeeded, error code from
                handle_db_error() if any submission failed.
        
        Raises:
            Logs error via handle_db_error() if query_submit() returns non-201 status.
        """

        for ticker, metrics in self.crypto_data.items():
            if ticker in ["count", "standing"]:
                continue

            for metric, stats in metrics.items():
                data = {
                    metric: stats
                }

                try:
                    self.query_submit(**data)
                except Error as e:
                    return self.handle_db_error(e)

        return 201

    def _init_tables(self) -> int:
        """
        Initialize and populate database tables for stocks and cryptocurrency data.
        
        This function should only be run once during initial setup. It creates
        tables for both stock and crypto datasets within the same database, then
        populates them with data from self.stock_data and self.crypto_data.
        
        Process:
            1. Checks if tables already exist using show_tables() method
            2. Creates 'stocks' and 'crypto' tables using query_create_table()
            3. Populates each table by iterating over respective data dictionaries
            4. Submits entries one by one using query_submit()
        
        Returns:
            int: Status code indicating success or failure. Returns the combined
                status from both initialization operations, or the error code
                from handle_db_error() if an exception occurs.
        
        Note:
            Should only be called once during initial database setup.
        """

        try:
            self.query_create_table("stocks")
            self.query_create_table("crypto")

            stocks = self.__init_stocks_table()
            crypto = self.__init_crypto_table()

            return stocks and crypto
        except Error as e:
            return self.handle_db_error(e)

    def enter_record(self, table: str, **kwargs: dict[str, StockAndCryptoDatabaseFilter]) -> int:
        """
        Insert a new record into the specified database table.
        
        Validates the table name before attempting insertion. Accepts arbitrary
        keyword arguments representing column names and their values.
        
        Args:
            table (str): Name of the database table to insert into.
            **kwargs: Column names and values to insert (e.g., ticker="BTC", price=50000).
        
        Returns:
            int: Status code of the operation.
        
        Raises:
            ValueError: If the table name is invalid.
        """

        if not self.__is_valid_table(table):
            raise ValueError(f"Invalid table name: '{table}'.")

        try:
            status = self.query_submit(table, **kwargs)

            return status
        except Error as e:
            return self.handle_db_error(e)

    def extract_record(self, table: str, key: StockAndCryptoDatabaseFilter) -> list | dict | int:
        """
        Extract a specific record from a database table by key.
        
        Validates the table name before attempting to retrieve the record.
        If the table is invalid, returns None without performing the query.
        
        Args:
            table (str): Name of the database table to query.
            key: Primary key or identifier for the record to extract.
        
        Returns:
            Record data returned by query_extract() if table is valid, int otherwise.
        """

        if not self.__is_valid_table(table):
            raise ValueError(f"Invalid table name: '{table}'.")

        try:
            record = self.query_extract(table, key)

            return record
        except Error as e:
            return self.handle_db_error(e)

    def delete_record(self, table: str, key: StockAndCryptoDatabaseFilter) -> int | Any:
        """
        Delete a specific record from a database table.
        
        Validates the table name before attempting deletion. Executes the delete
        operation and returns the number of affected rows.
        
        Args:
            table (str): Name of the database table to delete from.
            key (StockAndCryptoDatabaseFilter): Filter criteria identifying the record(s) to delete.
        
        Returns:
            int: Number of rows affected by the delete operation.
        
        Raises:
            ValueError: If the table name is invalid.
            Handles database errors via handle_db_error() and returns its result.
        """

        if not self.__is_valid_table(table):
            raise ValueError(f"Invalid table name: '{table}'.")

        try:
            self.query_delete_table_or_row(table, key)

            # Return the amount of rows affected.
            return self.cursor.rowcount
        except Error as e:
            return self.handle_db_error(e)

    def extract_table(self, table: str) -> dict | int:
        """
        Extract all records from the specified database table.
        
        Validates the table name before attempting to retrieve data. Returns
        all table data as a dictionary, or None if an error occurs.
        
        Args:
            table (str): Name of the database table to extract data from.
        
        Returns:
            dict[str, Any] | None: Dictionary containing all table data if successful,
                                None if a database error occurs.
        
        Raises:
            ValueError: If the table name is invalid.
        """

        if not self.__is_valid_table(table):
            raise ValueError(f"Invalid table name: '{table}'.")

        try:
            data = self.get_table_data(table)

            return data
        except Error as e:
            return self.handle_db_error(e)

    def __is_valid_table(self, table: str) -> bool:
        return table in self.tables
