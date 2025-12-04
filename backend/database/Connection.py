
# _____________________________________ Module 3 _____________________________________ #

import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
# pip install mysql-connector-python

class Connection:
    def __init__(self) -> None:
        
        self.host = 'localhost'
        # TODO: Read module_3.md instructions to set these up according to what you put
        self.user = 'root'
        self.password = os.getenv('db_password')
        if not self.password:
            raise ValueError("Database password not found in environment variables")
        self.database = 'Fullstack'
        
        self.status = 'inactive'
        self.conn = self.__init_conn()
        self.cursor = self.__init_cursor()

    # ___________________ Connection Methods ___________________ #
    
    def __init_conn(self):
        try:
            connection = mysql.connector.connect(
                host=self.host,
                user = self.user,
                password = self.password,
                database = self.database
            )
            self.status = 'active'
            return connection
        
        except mysql.connector.Error as error:
            self.status = 'inactive'
            print(f"There was an error when attempting the connection with host {self.host}\n Error: {error}")
            return None
    
    def __init_cursor(self):

        if self.conn:
            return self.conn.cursor()
        else:
            raise AttributeError("Connection Error: `self.conn` Attribute does pose a valid data type.")
    

    def close(self):
        """Closes the cursor and the database connection."""
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        if self.conn and self.conn.is_connected():
            self.conn.close()
            self.conn = None
            self.status = 'inactive'
            print("connection closed.")
    # ___________________ Queries ___________________ #
    
    def query_create_table(self, name): # Here is a demo of a query to create a table
        try:
            # Here is the pre-defined structure of a table
            # Works for both stocks and crypto with the same OHLCV structure
            query = f"""
            CREATE TABLE IF NOT EXISTS {name} (
                id INT AUTO_INCREMENT PRIMARY KEY,
                ticker VARCHAR(10),
                metric VARCHAR(20),
                mean DOUBLE,
                median DOUBLE,
                std DOUBLE,
                low DOUBLE,
                max DOUBLE,
                count INT
            )
            """
            
            self.cursor.execute(query)
            self.conn.commit()
            
            return 'success'
            
        except mysql.connector.Error as error:
            print(f"SQL Error creating table: {error}")
            return 'failure'
    
    def query_submit(self, table_name: str, **kwargs) -> int:
        '''
        Arguably the most important function. This could go perfect or it can cause lots of issues.
        Enters a record on a table.
        Returns a standard status code according to the operation's outcome. Example, 201 if success.
        https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status
        
        HINT:
        You don't know what type of data to expect! 
        What could you do to upload dynamic data? (e.g. **kwargs, dictionary, etc.. (?))
        '''
        columns = list(kwargs.keys())
        values = list(kwargs.values())

        placeholders = ', '.join(['%s'] * len(columns))
        column_string = ', '.join(columns)

        query = f"INSERT INTO {table_name} ({column_string}) VALUES ({placeholders})"

        try:
            self.cursor.execute(query, values)
            self.conn.commit()
            return 201 # Created
        except mysql.connector.Error as error:
            print(f" SQL Error inserting data: {error}")
            return 400 # Bad Request 

    def query_extract(self, table_name: str, condition: str = "", values: tuple = None) -> dict:
        '''
        Extract a record from a table. Allow for OPTIONAL filtering conditions.
        '''
        query = f"SELECT * FROM {table_name}"
        if condition:
            query += f" WHERE {condition}"

        try:
            if values:
                self.cursor.execute(query, values)
            else:
                self.cursor.execute(query)
            
            return self.cursor.fetchall()
    
        except mysql.connector.Error as error:
            print(f"SQL Error extracting data: {error}")
            return []
    
    def get_table_data(self, table_name: str) -> dict:
        '''
        Returns ALL of the information contained in a table.
        '''
        if not self.cursor or not table_name: 
            return []
        
        return self.query_extract(table_name)
    
    def show_tables(self) -> list:
        '''
        Returns a list of all table names in the data base
        '''
        if not self.cursor: 
            return []
    
        try:
            self.cursor.execute("SHOW TABLES")
            # fetchall() returns tuples, so we access the first element (index 0)
            tables = [t[0] for t in self.cursor.fetchall()]
            return tables
        except mysql.connector.Error as error:
            print(f"SQL Error showing tables: {error}")
            return []


    # __________________ Custom Query __________________ #
    
    def custom_query(self, query:str):
        '''
        Creates a custom query for potential user use.
        '''
        pass # TODO
    
    # ___________________ Danger Zone ___________________ #
    
    def query_delete_table(self, table_name: str, condition: str, values:tuple):
        '''
        Deletes a specified table. Again, allow for OPTIONAL filtering conditions. 
        '''
        if not self.cursor or not table_name:
            return 400
        
        if condition:
            query = f"DELETE FROM {table_name} WHERE {condition}"
            try:
                self.cursor.execute(query, values or [])
                self.conn.commit()
                print(f"Deleted {self.cursor.rowcount} record(s) from {table_name}.")
                return 200
            
            except mysql.connector.Error as error:
                print(f"SQL Error deleting records: {error}")
                return 400
        else:
            user_input = input(f"WARNING! Are you SURE you want to DROP the entire table '{table_name}'? (Y/N): ").upper()
            if user_input == 'Y':
                try:
                    self.cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
                    self.conn.commit()
                    print(f" Table '{table_name}' dropped.")
                    return 200
                except mysql.connector.Error as error:
                    print(f" SQL Error dropping table: {error}")
                    return 400
            return 403

    def query_delete_database(self):
        """Deletes the current database."""        
         # Logic Here #
        
        user_input = input(f"Are you certain you want to delete {self.database} database? (Y/N)") # PLACEHOLDER layer of security
        
        if user_input == 'Y':
            try:
                self.close()

                temp_conn = mysql.connector.connect(host=self.host, user=self.user, passowrd=self.password)
                temp_cursor = temp_conn.cursor()

                temp_cursor.execute(f"DROP DATABASE {self.database}")
                temp_conn.commit()

                temp_cursor.close()
                temp_conn.close()

                print(f"Database '{self.database}' has been deleted.")
                return 200
            except mysql.connector.Error as error:
                print(f"SQL Error deleting database: {error}")
                return 400
        else:
            return 403
        
    