import logging as log
from logging import FileHandler
from flask_cors import CORS
from flask import Flask, jsonify, request

from database.Connection import Connection

def create_app(): 
    app = Flask(__name__)
    CORS(app)
    setup_logging(app)
    return app

def setup_logging(app):
    log.basicConfig(
        level=log.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[log.StreamHandler(),
                  FileHandler("app.log")]
    )
    app.logger.info("Logging is configured.")

app = create_app()

def _fetch_last_month_data(ticker: str, limit: int = 500):
    """
    Pull the most recent month of OHLCV data for a ticker, ordered newest first.
    """
    conn = Connection()
    if conn.status != "active":
        return None, "Database connection inactive"

    try:
        query = """
            SELECT id, timestamp, symbol, open, high, low, close, volume
            FROM stocks_series
            WHERE symbol = %s AND timestamp >= NOW() - INTERVAL 1 MONTH
            ORDER BY timestamp DESC
            LIMIT %s
        """
        conn.cursor.execute(query, (ticker, limit))
        cols = [col[0] for col in conn.cursor.description]
        rows = [dict(zip(cols, row)) for row in conn.cursor.fetchall()]
        return rows, None
    except Exception as err:
        return None, str(err)
    finally:
        try:
            conn.cursor.close()
            conn.conn.close()
        except Exception:
            pass

# _________________ Systematic Endpoint _________________ #

@app.route("/")  # ALWAYS great to have. 
def home():
    """
    HOME PAGE
    """
    return jsonify({"status": "OK"}), 200
    
# @app.route("/stock/<ticker>")   
# def stocks(ticker):
#     """
#     You can also check for the status of the database, AI client, etc...
#     This just checks the status of the app as a whole.
#     """
#     return jsonify({"status": "OK", "Data": {"Ticker": ticker}}), 200

# @app.route("/crypto/<ticker>")   
# def crypto(ticker):
#     """
#     You can also check for the status of the database, AI client, etc...
#     This just checks the status of the app as a whole.
#     """
#     return jsonify({"status": "OK", "Data": {"Ticker": ticker}}), 200

@app.route("/stock/<ticker>/last-month")
def stock_last_month(ticker):
    """
    Return last month of OHLCV data for a ticker, sorted newest first, with an optional limit.
    """
    limit = request.args.get("limit", default=500, type=int)
    rows, error = _fetch_last_month_data(ticker, limit)
    if error:
        return jsonify({"status": "error", "message": error}), 500

    return jsonify({"status": "OK", "ticker": ticker, "count": len(rows), "data": rows}), 200

@app.route("/stock/<ticker>/openapi-prompt")
def stock_openapi_prompt(ticker):
    """
    Provide an OpenAPI-style prompt describing how to request last-month data for this ticker.
    """
    prompt = (
        "Create an OpenAPI 3.0 path item for GET /stock/{ticker}/last-month that "
        "accepts an optional integer query parameter 'limit' (default 500) and returns "
        "an array of OHLCV records (id, timestamp, symbol, open, high, low, close, volume) "
        "for the past month, sorted by timestamp descending."
    ).format(ticker=ticker)

    return jsonify({"status": "OK", "ticker": ticker, "prompt": prompt}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4200, debug=False)
