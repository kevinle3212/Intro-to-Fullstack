"""
This module defines the StockDatabaseFilter TypedDict, which provides a
type-safe way to specify optional filtering conditions when querying
stock data from a database.

All keys in StockDatabaseFilter are optional, allowing partial filters
to be applied to stock records. Each key corresponds to a column in the
stock data table.

Example Usage:
    from filter import StockDatabaseFilter

    my_filter: StockDatabaseFilter = {
        "ticker": "AAPL",
        "metric": "close",
        "mean": 150.5
    }

Author: Kevin Le
Last Modified: November 9, 2025
"""

from typing import TypedDict

class StockAndCryptoDatabaseFilter(TypedDict, total=False):
    """
    Optional filter dictionary for querying stock data from the database.

    Each key corresponds to a column in the stock data table.
    All keys are optional, allowing partial filtering.

    Attributes:
        ticker (str, optional): Stock ticker symbol, e.g., "AAPL".
        metric (str, optional): Metric name, e.g., "close", "open".
        mean (int | float, optional): Mean value of the metric.
        median (int | float, optional): Median value of the metric.
        std (int | float, optional): Standard deviation of the metric.
        min (int | float, optional): Minimum value of the metric.
        max (int | float, optional): Maximum value of the metric.
        count (int, optional): Number of data points.
    """

    ticker: str
    metric: str
    mean: int | float
    median: int | float
    std: int | float
    min: int | float
    max: int | float
    count: int
