"""
Support utilities for environment variable and secret management, and database validation.

Provides secure retrieval of configuration values from .env files and validation
utilities for database operations. Includes proper error handling for missing
credentials and invalid database identifiers.

Classes:
    MissingSecretError: Exception for missing environment variables.

Functions:
    get_secret(key): Retrieve environment variable or raise exception.
    invalid_database_table_name(name): Validate table name format and return status code.

Typical Usage Example:
    >>> from support import get_secret, invalid_database_table_name
    >>> 
    >>> # Retrieve secrets
    >>> db_host = get_secret("SC_DATABASE_HOST")
    >>> 
    >>> # Validate table name
    >>> status = invalid_database_table_name("stocks")
    >>> if status == 400:
    ...     print("Invalid table name!")

Dependencies:
    - python-dotenv: For loading environment variables from .env files

Note: Requires a .env file in the project root directory.

Author: Kevin Le
Last Modified: November 9, 2025
"""

from os import getenv
from dotenv import load_dotenv

class MissingSecretError(Exception):
    """
    Raised when a required secret/environment variable is not found.
    """


def get_secret(key: str) -> str:
    """
    Retrieve a secret value from environment variables.
    
    Loads environment variables from .env file and retrieves the value
    for the specified key. Raises an exception if the key is missing or empty.
    
    Args:
        key (str): The environment variable name to retrieve.
    
    Returns:
        str: The secret value associated with the key.
    
    Raises:
        MissingSecretError: If the key is not found or has an empty value.
    
    Example:
        >>> db_host = get_secret("SC_DATABASE_HOST")
        >>> print(db_host)
        'localhost'
    """

    load_dotenv()
    value = getenv(key, None)

    if not value:
        raise MissingSecretError(f"Not found secret value for key: {key} in environment.")

    return value

def invalid_database_table_name(name: str):
    """
    Validate a database table name for allowed characters.

    Ensures that the given table name contains only alphanumeric characters 
    and underscores. Raises a ValueError if the name includes any other 
    characters (such as spaces, symbols, or punctuation).

    Args:
        name (str): The name of the database table to validate.

    Raises:
        ValueError: If the table name contains invalid characters.

    Examples:
        >>> invalid_database_table_name("user_data")
        # Valid, no exception raised.

        >>> invalid_database_table_name("user-data!")
        Traceback (most recent call last):
            ...
        ValueError: Invalid table name. Use only alphanumeric characters and underscores.
    """

    if not name.replace("_", "").isalnum():
        raise ValueError("Invalid table name. Use only alphanumeric characters and underscores.")
