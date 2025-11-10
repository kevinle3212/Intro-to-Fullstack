"""
MySQL Database Connection and Query Management Module.

This module provides a comprehensive interface for interacting with MySQL databases,
handling everything from connection initialization to complex query operations.
It supports CRUD operations, custom queries, and database/table management with
built-in error handling and validation.

Classes:
    Connection: Main database connection handler with methods for all database operations.

Key Features:
    - Secure credential management via secret storage.
    - Automatic connection and cursor initialization.
    - Table creation with predefined schema for statistical metrics.
    - Bulk data insertion with batch processing.
    - Flexible data extraction with optional filtering.
    - Custom query execution support.
    - Safe database and table deletion with user confirmation.
    - Comprehensive error handling and rollback capabilities.

Typical Usage:
    >>> from backend.database.connection import Connection
    >>> 
    >>> # Initialize connection.
    >>> db = Connection()
    >>> 
    >>> # Create a table.
    >>> db.query_create_table('stocks')
    >>> 
    >>> # Insert data.
    >>> data = {
    ...     'AAPL': {
    ...         'count': 100,
    ...         'close': {'mean': 150.5, 'median': 149.2, 'std': 5.3, 'min': 140.0, 'max': 160.0}
    ...     }
    ... }
    >>> db.query_submit('stocks', **data)
    >>> 
    >>> # Extract data with filters.
    >>> filter_obj = StockAndCryptoDatabaseFilter(ticker='AAPL', metric='close')
    >>> results = db.query_extract('stocks', f=filter_obj)
    >>> 
    >>> # Get all table data as dictionaries.
    >>> table_data = db.get_table_data('stocks')

Dependencies:
    - mysql.connector: MySQL database connector.
    - typing: Type hints for better code clarity.
    - pprint: Pretty printing for debugging.
    - backend.utils.filter: Custom filter class for query conditions.
    - backend.utils.support: Utility functions for secrets and validation.

Environment Variables (via get_secret):
    - SC_DATABASE_HOST: Database server hostname.
    - SC_DATABASE_USERNAME: Database user credentials.
    - SC_DATABASE_PASSWORD: Database password.
    - SC_DATABASE_NAME: Default database name.
    - SC_DATABASE_STATUS: Database status flag.

Security Notes:
    - Uses parameterized queries to prevent SQL injection.
    - Validates table names before executing queries.
    - Credentials stored in secure secret management system.
    - User confirmation required for destructive operations.

Error Handling:
    - Automatic transaction rollback on errors.
    - Detailed error logging with error codes.
    - Graceful degradation with empty results on query failures.

Author: Kevin Le
Last Modified: November 9, 2025
"""

from typing import Any, Optional
from pprint import pprint
from mysql.connector import connect, Error
from backend.utils.filter import StockAndCryptoDatabaseFilter
from backend.utils.support import get_secret, invalid_database_table_name

class Connection:
    """
    Initialize the database connection handler.
    
    Retrieves database credentials and configuration from secret management,
    establishes a connection to the database, and initializes a cursor for
    executing queries.

    Attributes:
        host (str): Database host address.
        user (str): Database username.
        password (str): Database password.
        database (str): Database name to connect to.
        status (str): Database connection status flag.
        conn: Active database connection object.
        cursor: Database cursor for executing SQL commands.

    Raises:
        ValueError: If any required secret is missing or empty.
        ConnectionError: If database connection cannot be established.
    """

    def __init__(self) -> None:
        self.host = get_secret("SC_DATABASE_HOST")
        self.user = get_secret("SC_DATABASE_USERNAME")
        self.password = get_secret("SC_DATABASE_PASSWORD")
        self.database = get_secret("SC_DATABASE_NAME")
        self.status = get_secret("SC_DATABASE_STATUS")

        self.conn = self._init_connection()
        self.cursor = self._init_cursor()


    def _init_connection(self):
        """
        Initialize and return a database connection.
        
        Returns:
            Connection: A database connection object.
            
        Raises:
            ConnectionError: If connection cannot be established with the provided credentials.
            ValueError: If required connection parameters are missing.
        """

        if not all([self.host, self.user, self.password, self.database]):
            raise ValueError("Missing a required database connection parameter.")

        try:
            conn = connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )

            pprint("Established a successful connection the database!")

            return conn
        except Exception as e:
            raise ConnectionError(f"Database Connection Error: {str(e)}.") from e

    def _init_cursor(self):
        """
        Initialize and return a database cursor from the connection.
        
        Returns:
            Cursor: A database cursor object for executing SQL commands.
            
        Raises:
            AttributeError: If the database connection is not established or invalid.
        """

        if not self.conn:
            raise AttributeError(
                "Connection Error: The database connection is not established.\n"
                "Ensure _init_connection() completes successfully before creating a cursor."
            )

        return self.conn.cursor()

    def handle_db_error(self, e: Error) -> int:
        """
        Handle database errors by rolling back the current transaction and returning the status code.

        Args:
            e (mysql.connector.Error): The exception object representing the database error.

        Returns:
            int: The SQLSTATE error code associated with the exception.
        """

        if self.conn:
            self.conn.rollback()

        pprint(f"{type(e)}: {e}")

        return e.errno

    def query_create_table(self, name: str) -> int | None:
        """
        Create a new table with a predefined structure for storing statistical metrics.
        
        Args:
            name (str): The name of the table to create.
        
        Returns:
            int: The HTTP-style status code indicating the result of the operation:
                - 200: Success - table created or already exists.
                - 400: Invalid table name.
                - Other codes: Database error code from handle_error().
        """

        invalid_database_table_name(name)

        try:
            query = f"""
                CREATE TABLE IF NOT EXISTS {name} (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ticker VARCHAR(5) NOT NULL,
                    metric VARCHAR(10) NOT NULL,
                    mean DOUBLE NOT NULL,
                    median DOUBLE NOT NULL,
                    std DOUBLE NOT NULL,
                    min DOUBLE NOT NULL,
                    max DOUBLE NOT NULL,
                    count INT NOT NULL
                );
            """

            self.cursor.execute(query)

            self.conn.commit()

            return 200
        except Error as e:
            return self.handle_db_error(e)

    def query_submit(self, table_name: str, **kwargs: dict[str, Any]) -> int:
        """
        Insert statistical metrics for one or more tickers into the database.
        
        Dynamically processes nested dictionary data containing statistical metrics
        (mean, median, std, min, max) for various price points (open, high, low, close)
        and inserts them as individual records. Designed to handle stock market data
        with flexible structure through **kwargs.
        
        The method expects kwargs where each key is a ticker symbol and its value
        is a dictionary containing metric data. Each metric (open, high, low, close)
        should have statistical measures, and a 'count' field indicating sample size.
        
        Args:
            table_name (str): Name of the target table for data insertion.
            **kwargs: Variable keyword arguments where each argument represents a ticker.
                Expected structure:
                {
                    'TICKER': {
                        'count': int,
                        'metric_name': {
                            'mean': float,
                            'median': float,
                            'std': float,
                            'min': float,
                            'max': float
                        },
                        ...
                    }
                }
                
                Note: 'standing' key is ignored. 'volume' and 'count' metrics are skipped
                during insertion to avoid duplication.
        
        Returns:
            int: HTTP-style status code indicating operation result:
                - 200: Success - all records inserted and committed.
                - Other codes: Database error code from handle_error().
        
        Raises:
            mysql.connector.Error: If database insertion fails, handled internally
                and returns error code via handle_error().
        
        Example:
            >>> data = {
            ...     'IBM': {
            ...         'count': 4202,
            ...         'close': {
            ...             'mean': 290.45,
            ...             'median': 287.2,
            ...             'std': 12.73,
            ...             'min': 262.2,
            ...             'max': 319.165
            ...         },
            ...         'high': {...},
            ...         'volume': {...},  # Will be skipped as it's not a necessary metric.
            ...         'standing': 'declining'  # Will be ignored.
            ...     }
            ... }
            >>> status = connect.query_submit("stocks", **data)
            >>> print(f"Status: {status}")  # Output: Status: 200
        
        Notes:
            - Uses executemany() for batch insertion efficiency.
            - Automatically commits the transaction on success.
            - Rolls back transaction on error (handled by handle_error).
            - The first key in kwargs is used as the ticker name for all records.
        """

        invalid_database_table_name(table_name)

        rows = []

        for key, val in kwargs.items():
            # Skips the 'standing' key and just allows the ticker key to pass through.
            if key == "standing":
                continue

            count = val.get("count")

            for metric, data in val.items():
                # Skip the count integer itself and non-dict values.
                if metric in ("count", "volume"):
                    continue

                # Create a tuple for SQL insertion.
                values = (
                    key,
                    metric,
                    data["mean"],
                    data["median"],
                    data["std"],
                    data["min"],
                    data["max"],
                    count
                )

                rows.append(values)

        query = f"""
            INSERT INTO {table_name} (
                ticker, metric, mean, median, std, min, max, count
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """

        try:
            self.cursor.executemany(query, rows)
            self.conn.commit()
        except Error as e:
            return self.handle_db_error(e)

        return 200

    def query_extract(self, table: str, f: Optional[StockAndCryptoDatabaseFilter] = None) -> list | dict:
        """
        Extract records from a table with optional filtering conditions.
        
        Retrieves data from the specified database table, optionally filtered by
        column values. Uses the invalid_database_table_name() function to validate
        table names before executing the query.
        
        Args:
            table (str): Name of the table to query. Validated by 
                invalid_database_table_name() to prevent SQL injection.
            f (StockDatabaseFilter, optional): Dictionary-like filter object where
                keys are column names and values are the filter criteria. All
                conditions are combined with AND logic. If None or empty, retrieves 
                all records from the table.
                
                Example: {'ticker': 'IBM', 'metric': 'close'}
                SQL: WHERE ticker=%s AND metric=%s
        
        Returns:
            list | dict: A list of tuples containing the query results. Each tuple represents
                one row from the database. Returns an empty list if:
                - No records match the filter criteria.
                - The table is empty.
                - An error occurred during query execution.
        
        Raises:
            ValueError: If table name validation fails (raised by invalid_database_table_name).
            
        Side Effects:
            - Calls handle_error() on database exceptions, which rolls back transactions.
            - Does not raise exceptions for database errors; returns empty list instead.
        
        Example:
            >>> # Get all records.
            >>> all_records = connect.query_extract("stocks")
            >>> print(f"Total records: {len(all_records)}")
            >>> 
            >>> # Get filtered records.
            >>> filter_obj = StockDatabaseFilter(ticker='IBM', metric='close')
            >>> ibm_close = connect.query_extract("stocks", f=filter_obj)
            >>> for row in ibm_close:
            ...     print(row)  # Prints tuple: (id, created_at, ticker, metric, ...)
            (1, '2024-01-15 10:30:00', 'IBM', 'close', 290.45, 287.2, ...)
        
        Notes:
            - Uses parameterized queries (%s placeholders) to prevent SQL injection on values.
            - Filter conditions use exact match (=) with AND logic between conditions.
            - Results are tuples, not dictionaries. Access by index: row[0], row[1], etc.
            - Use cursor.description to get column names if needed.
            - Silent failure: Returns empty list on errors rather than raising exceptions.
            - Column order matches the table schema definition.
        
        Warning:
            This method returns an empty list for both "no results found" and "error occurred"
            cases. Consider checking logs or modifying to return a dict with success status
            for better error handling in production code.
        """

        invalid_database_table_name(table)

        results = {}
        query = f"SELECT * FROM {table};"
        values = []

        if f:
            filter_conditions = [f"{col}=%s" for col in f]

            # List out the conditions.
            query += " WHERE " + " AND ".join(filter_conditions)

            # Get all the filter values and execute them alongside the query.
            values = list(f.values())

        try:
            self.cursor.execute(query, values)
            results = self.cursor.fetchall()
        except Error as e:
            self.handle_db_error(e)

        return results

    def get_table_data(self, table: str) -> dict:
        """
        Retrieves all data from a specified MySQL table.
    
        This method executes a SELECT * query on the given table and returns
        all rows with their corresponding column names in a structured dictionary format.
        
        Args:
            table (str): The name of the database table to query.
        
        Returns:
            dict: A dictionary containing:
                - 'rows' (list): List of dictionaries, where each dictionary represents
                                a row with column names as keys and cell values as values.
                - 'columns' (list): List of column names in the order they appear in the table.
        
        Example:
            >>> data = self.get_table_data('stocks')
            >>> print(data)
            {
                'rows': [
                    {'id': 1, 'ticker': 'AAPL', 'value': 25.5},
                    {'id': 2, 'ticker': 'GOOGL', 'value': 30.2}
                ],
                'columns': ['id', 'ticker', 'value']
            }
        
        Note:
            This method fetches ALL rows from the table. For large tables,
            consider adding pagination or limiting the result set.
        """

        query = f"SELECT * FROM {table}"
        self.cursor.execute(query)

        rows = self.cursor.fetchall()

        columns = [desc[0] for desc in self.cursor.description]

        result = []
        for row in rows:
            result.append(dict(zip(columns, row)))

        return {"rows": result, "columns": columns}

    def show_tables(self, database_name: str) -> list:
        """
        Retrieves all table names from a specified MySQL database.
    
        Args:
            database_name (str): The name of the database to query.
        
        Returns:
            list: A list of table names as strings.
        
        Example:
            >>> tables = self.show_tables('my_database')
            >>> print(tables)
            ['users', 'products', 'orders']
        """

        query = f"SHOW TABLES FROM {database_name};"

        self.cursor.execute(query)

        tables = self.cursor.fetchall()

        names = [table[0] for table in tables]

        return names

    def custom_query(self, query: str) -> dict:
        """
        Executes a custom SQL query and returns the results.
        
        This method allows for flexible query execution beyond standard operations.
        Supports SELECT queries and returns structured data similar to get_table_data().
        
        Args:
            query (str): The SQL query string to execute.
        
        Returns:
            dict: A dictionary containing:
                - 'rows' (list): List of dictionaries, where each dictionary represents
                                a row with column names as keys and cell values as values.
                - 'columns' (list): List of column names returned by the query.
                - 'rowcount' (int): Number of rows affected (useful for INSERT/UPDATE/DELETE).
        
        Example:
            >>> result = self.custom_query("SELECT * FROM stocks WHERE ticker = 'AAPL'")
            >>> print(result)
            {
                'rows': [{'id': 1, 'ticker': 'AAPL', 'value': 25.5}],
                'columns': ['id', 'ticker', 'value'],
                'rowcount': 1
            }
        
        Note:
            Be cautious with queries from untrusted sources to prevent SQL injection.
        """

        self.cursor.execute(query)

        # For SELECT (fetching) queries.
        if self.cursor.description:
            rows = self.cursor.fetchall()

            columns = [desc[0] for desc in self.cursor.description]

            result = []
            for row in rows:
                result.append(dict(zip(columns, row)))

            return {
                "rows": result,
                "columns": columns,
                "rowcount": self.cursor.rowcount
            }

        # For INSERT, UPDATE, DELETE queries (no results to fetch).
        self.conn.commit()  # Commit changes to database.
        return {
            "rows": [],
            "columns": [],
            "rowcount": self.cursor.rowcount
        }

    def query_delete_table_or_row(self, table: str, f: Optional[StockAndCryptoDatabaseFilter] = None) -> int | Any:
        """
        Deletes an entire table or specific rows based on filter conditions.
        
        If no filter is provided, drops the entire table (irreversible).
        If a filter is provided, deletes only rows matching the filter conditions.
        
        Args:
            table (str): The name of the table.
            f (StockAndCryptoDatabaseFilter, optional): Filter object containing
                column-value pairs for WHERE conditions. If None, drops the table.
        
        Returns:
            int: Number of rows affected (for DELETE) or 0 (for DROP TABLE).
        
        Example:
            >>> # Delete specific rows
            >>> filter_obj = {'ticker': 'AAPL', 'date': '2025-01-01'}
            >>> self.query_delete_table_or_row('stocks', filter_obj)
            # Deletes rows WHERE ticker='AAPL' AND date='2025-01-01'
            
            >>> # Drop entire table
            >>> self.query_delete_table_or_row('old_stocks')
            # Completely removes the 'old_stocks' table
        
        Warning:
            Dropping a table is permanent and cannot be undone!
        """

        if f:
            filter_dict = dict(f)

            filter_conditions = " AND ".join([f"{col}=%s" for col in filter_dict])

            query = f"DELETE FROM {table} WHERE {filter_conditions};"

            values = tuple(filter_dict[col] for col in filter_dict)

            self.cursor.execute(query, values)
        else:
            query = f"DROP TABLE {table};"
            self.cursor.execute(query)

        self.conn.commit()

        return self.cursor.rowcount

    def query_delete_database(self, database: Optional[str] = None) -> bool:
        """
        Deletes a specified database after user confirmation.
        
        Prompts the user for confirmation before permanently deleting the database.
        If no database is specified, uses the current database connection.
        This operation is irreversible and will remove all tables and data.
        
        Args:
            database (str, optional): Name of the database to delete. 
                                    If None, deletes the current database (self.database).
        
        Returns:
            bool: True if database was deleted, False if user cancelled.
        
        Example:
            >>> self.query_delete_database('old_db')
            Are you certain you want to delete old_db database? (Y or Press any key to exit): y
            Database 'old_db' has been deleted.
            True
            
            >>> self.query_delete_database()  # Uses self.database
            Are you certain you want to delete stocks_db database? (Y or Press any key to exit): n
            Database deletion cancelled.
            False
        
        Warning:
            This permanently deletes the ENTIRE database and all its contents!
        """

        target_database = database or self.database

        user_input = input(
            f"Are you certain you want to delete '{target_database}' database? "
            f"(Y or Press any key to exit): "
        )

        if user_input.lower() == "y":
            try:
                query = f"DROP DATABASE {target_database};"
                self.cursor.execute(query)
                self.conn.commit()

                print(f"Database '{target_database}' has been deleted successfully.")
                return True

            except Error as e:
                self.handle_db_error(e)

        print("The database deletion operation has stopped.")
        return False
