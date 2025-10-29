from dotenv import load_dotenv # pip install python-dotenv
from os import getenv

class MissingSecretError(Exception):
    pass

def get_secret(key:str):
    load_dotenv()
    value = getenv(key, None)
    
    if not value:
        raise MissingSecretError(f"Not found secrete value for key: {key} in environment.")
    return value