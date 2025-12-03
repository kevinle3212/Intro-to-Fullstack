"""
Runner Code to set up db and populate db with starter stocks
"""
from database.Connection import Connection
from database.Commander import Commander


if __name__ == "__main__":
    print("Setting up db...\n")
   
    con = Connection()
    print(f"Connection Status: {con.status}")
    