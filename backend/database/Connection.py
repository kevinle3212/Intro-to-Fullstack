
# _____________________________________ Module 3 _____________________________________ #
from pprint import pprint
import mysql.connector
import numpy as np
import random
# pip install mysql-connector-python

class Connection:
    def __init__(self) -> None:
        
        self.host = 'localhost'
        # TODO: Read module_3.md instructions to set these up according to what you put
        self.user = 'root'
        self.password = 'Shanny.139'
        self.database = 'IntroFullstack'
        
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
    
    # ___________________ Queries ___________________ #
    
    def query_create_table(self, name): # Here is a demo of a query to create a table
        try:
            # Here is the pre-defined structure of a table
            query = f"""
            CREATE TABLE {name} (
                id INT AUTO_INCREMENT PRIMARY KEY,
                ticker VARCHAR(5),
                metric VARCHAR(10),
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
            
        except mysql.connector.Error:
            
            return 'failure'
    
    def query_submit(self, table:str, query: dict) -> int:
        '''
        Arguably the most important function. This could go perfect or it can cause lots of issues.
        Enters a record on a table.
        Returns a standard status code according to the operation's outcome. Example, 201 if success.
        https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status
        
        HINT:
        You don't know what type of data to expect! 
        What could you do to upload dynamic data? (e.g. **kwargs, dictionary, etc.. (?))
        '''
        
        # Extract Data from dict to be used in query
        columns = ", ".join(data.keys())
        values = tuple(data.values())
        placeholders = ", ".join(["%s"] * len(values))

        try:
            query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            self.cursor.execute(query, values)

            # Auto-increment ID
            new_id = self.cursor.lastrowid

            self.conn.commit()

            return 201
        except mysql.connector.Error as e:
            return 400
    
    def query_extract(self, table:str=None, query:str=None) -> dict:
        '''
        Extract a record from a table. Allow for OPTIONAL filtering conditions.
        '''
        
        if query == None:
            query = f"Select * FROM {table}"
                
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
            
        except mysql.connector.Error:
            
            return 'failure'
    
    def get_table_data(self, name:str) -> dict[dict]:
        '''
        Returns ALL of the information contained in a table.
        '''
        try:
            query = f"DESCRIBE {name};"
             
            self.cursor.execute(query)
            data = {} 
            for row in self.cursor.fetchall():
                data[row[0]] = {
                    "type" : row[1],
                    "NULL": row[2],
                    "key": row[3],
                    "default": row[4],
                    "extra": row[5]
                    }
                
            return data
            
        except mysql.connector.Error:
            
            return 'failure'
        
    def show_tables(self) -> list:
        '''
        Returns a list of all table names in the data base
        '''
        try:
            query = f"SHOW TABLES;"
             
            self.cursor.execute(query)
            
            tables = [row[0] for row in self.cursor.fetchall()]
            return tables
            
        except mysql.connector.Error:
            
            return 'failure'
    

    
    # ___________________ Danger Zone ___________________ #
    
    def query_delete_table(self, name: str):
        '''
        Deletes a specified table. Again, allow for OPTIONAL filtering conditions. 
        '''

        try:
            query = f"DROP TABLE {name};"
            self.cursor.execute(query)
            return "sucsess"
        
        except mysql.connector.Error:
            return "Failure"
        
    def query_delete_database(self):
        """
        Deleted database
        """        
        user_input = input(f"Are you certain you want to delete {self.database} database? (Y/N)") # PLACEHOLDER layer of security
        
        if user_input.strip().lower() == "y":
            try:
                query = f"DROP DATABASE {self.database}"
                self.cursor.execute(query)
                self.conn.commit()
                return f"Deleted Data Base: {self.database}"

            except mysql.connector.Error:
                return "Failure" 
        else:
            return f"Quiting db: {self.database} Deletion.."
    
if __name__ == "__main__":
    con = Connection()
    print(f"Connection Status: {con.status}")

    print(f"Stock Table Dropped: {con.query_delete_table('Stocks')}")
    print(f"Crypto Table Dropped: {con.query_delete_table('Crypto')}")
    print("Tables Dropped")
    print(con.show_tables())
        
    print(f"Stock Table Creation: {con.query_create_table('Stocks')}")
    print(f"Crypto Table Creation: {con.query_create_table('Crypto')}")
    print("Tables Made")
    
    data = {
    "ticker": "BTC",
    "metric": "close",
    "mean": 185.2,
    "median": 184.9,
    "std": 1.1,
    "low": 182.0,
    "max": 188.5,
    "count": 30}
    
    print(f"query_submit(self, table:str, data: dict): {con.query_submit('Crypto', data)}")
   
    for i in range(250): 
        data = {
        "ticker": random.choice(["APPL", "SPY500", "AWS"]),
        "metric": random.choice(["CLOSE", "OPEN", "LOW", "HIGH "]),
        "mean": np.random.randint(0,2550),
        "median": np.random.randint(0,2550),
        "std": np.random.randint(0,2550),
        "low": np.random.randint(0,2550),
        "max": np.random.randint(0,2550),
        "count": np.random.randint(0,2550)
        }

        print(f"query_submit(self, table:str, data: dict): {con.query_submit('Stocks', data)}")
    
    for i in con.query_extract("Stocks", query="SELECT * FROM Stocks WHERE ticker like 'AWS' LIMIT 10;"):
        print(i)
    
    
    
    print(con.show_tables())
    
