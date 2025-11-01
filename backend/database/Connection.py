

# _____________________________________ Module 3 _____________________________________ #

import mysql.connector
# pip install mysql-connector-python

class Connection:
    def __init__(self) -> None:
        
        self.host = 'localhost'
        # TODO: Read module_3.md instructions to set these up according to what you put
        self.user = 'root'
        self.password = 'Shanny.139'
        self.database = 'db'
        
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
            print(f"Table {name} created successfully.")
            return 'success'
            
        except mysql.connector.Error as e:
            print(f"Failed to create table {name}: {e}")
            return 'failure'
    
    def query_submit(self, table_name: str, data: dict) -> int:
        '''
        Arguably the most important function. This could go perfect or it can cause lots of issues.
        Enters a record on a table.
        Returns a standard status code according to the operation's outcome. Example, 201 if success.
        https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status
        
        HINT:
        You don't know what type of data to expect! 
        What could you do to upload dynamic data? (e.g. **kwargs, dictionary, etc.. (?))
        '''
        if not self.conn or not self.cursor:
            print("No active connection.")
            return 400

        placeholders = ", ".join(["%s"] * len(data))
        columns = ", ".join(data.keys())
        values = tuple(data.values())

        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

        try:
            self.cursor.execute(sql, values)
            self.conn.commit()
            return 201  # Created
        except mysql.connector.Error as e:
            print(f"Error inserting record: {e}")
            return 400

    def query_extract(self, table_name: str, where: dict = None) -> dict:
        """
        Extracts records from a table, optionally filtered by a where dict.
        Returns dict-of-dicts like get_table_data.
        """
        if not self.conn or not self.cursor:
            print("No active connection.")
            return {}

        sql = f"SELECT * FROM {table_name}"
        values = ()
        if where:
            conditions = " AND ".join([f"{k}=%s" for k in where.keys()])
            sql += f" WHERE {conditions}"
            values = tuple(where.values())

        try:
            self.cursor.execute(sql, values)
            columns = [col[0] for col in self.cursor.description]
            rows = self.cursor.fetchall()
            return {row[0]: dict(zip(columns, row)) for row in rows}

        except mysql.connector.Error as e:
            print(f"Error extracting data from {table_name}: {e}")
            return {}
        
    def get_table_data(self, table_name: str) -> dict:
        """
        Returns ALL of the information contained in a table as a dict of dicts.
        Outer dict key: value of the first column (usually the primary key)
        Inner dict: column_name -> value
        """
        if not self.conn or not self.cursor:
            print("No active connection.")
            return {}

        sql = f"SELECT * FROM {table_name}"

        try:
            self.cursor.execute(sql)
            columns = [col[0] for col in self.cursor.description] 
            rows = self.cursor.fetchall()

            result = {row[0]: dict(zip(columns, row)) for row in rows} 
            return result

        except mysql.connector.Error as e:
            print(f"Error getting table data: {e}")
            return {}
        
    def show_tables(self) -> list:
        """
        Returns a list of all table names in the database.
        """
        if not self.conn or not self.cursor:
            print("No active connection.")
            return []

        try:
            self.cursor.execute("SHOW TABLES;")
            tables = self.cursor.fetchall()  # fetch all rows
            return [table[0] for table in tables]  # table[0] is the name
        except mysql.connector.Error as e:
            print(f"Error getting table data: {e}")
            return []
            
    # __________________ Custom Query __________________ #
    
    def custom_query(self, query: str):
        """
        Executes a custom SQL query.
        - Returns results for SELECT queries.
        - Commits changes for INSERT/UPDATE/DELETE queries.
        """
        if not self.conn or not self.cursor:
            print("No active connection.")
            return None

        try:
            self.cursor.execute(query)

            if query.strip().lower().startswith("select"):
                return self.cursor.fetchall()  # return rows as list of tuples
            else:
                self.conn.commit()
                print("Query executed successfully.")
                return "success"

        except mysql.connector.Error as e:
            print(f"Error executing query: {e}\nQuery: {query}")
            return "failure"
    
    # ___________________ Danger Zone ___________________ #
    
    def query_delete_table(self, table_name: str):
        '''
        Deletes a specified table. Again, allow for OPTIONAL filtering conditions. 
        '''
        user_input = input(f"Are you certain you want to delete '{table_name}'? (Y/N): ")

        if user_input.lower() == 'y':
            sql = f"DROP TABLE {table_name};"
            try:
                self.cursor.execute(sql)
                self.conn.commit()
                self.status = 'inactive'
                print(f"Table '{table_name}' deleted successfully.")
            except mysql.connector.Error as e:
                print(f"Failed to delete table '{table_name}': {e}")
        else:
            print("Table deletion cancelled.")

    def query_delete_database(self):
                
        user_input = input(f"Are you certain you want to delete '{self.database}' database? (Y/N): ")

        if user_input.lower() == 'y':
            sql = f"DROP DATABASE {self.database};"
            try:
                self.cursor.execute(sql)
                self.conn.commit()
                self.status = 'inactive'
                print(f"Database '{self.database}' deleted successfully.")
            except mysql.connector.Error as e:
                print(f"Failed to delete database '{self.database}': {e}")
        else:
            print("Database deletion cancelled.")

