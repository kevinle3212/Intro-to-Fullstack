import logging as log
from logging import FileHandler
from flask_cors import CORS
from flask import Flask, jsonify, request

from database.Connection import Connection
from analysis.AI import AI

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
        rows = []
        for row in conn.cursor.fetchall():
            item = dict(zip(cols, row))
            ts = item.get("timestamp")
            if ts:
                # Ensure JSON serializable timestamp
                item["timestamp"] = ts.isoformat(sep=" ")
            rows.append(item)
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
    Use the AI client to generate an OpenAPI-style request snippet for last-month stock data.
    """
    ai_client = AI()
    prompt =    f"""
                You are an experienced equity analyst.

                Write a concise, retail-investor-friendly overview of the stock with ticker "{ticker}".

                Your response must:
                - First, briefly explain what the company does and its main business lines.
                - Then, summarize any notable recent events or themes that may affect the stock (such as earnings trends, product launches, regulatory news, or macro conditions). 
                - Give me links to articles if you find any
                - Then using data give a technical overview, like lows, highs, or any other major numbers 
                - Finally, describe the current overall market sentiment toward this stock (for example: bullish, bearish, mixed, or uncertain) and explain why in qualitative terms.
                

                Constraints:
                - Respond as a single paragraph of 6 to 7 sentences.
                - Do NOT use bullet points, headings, titles, or markdown formatting.
                - Use clear, neutral, professional language and avoid hype.
                - If you are not confident about specific recent events or sentiment, say so explicitly instead of guessing.
                - Do not make up exact prices, dates, or analyst targets.            
                """
                    


    ai_response = ai_client.request_query(prompt)
    if ai_response.get("message") != "success":
        return jsonify({
            "status": "error",
            "message": ai_response.get("message", {}),
            "details": ai_response.get("response", {})
        }), 500

    return jsonify({
        "status": "OK",
        "ticker": ticker,
        "response": ai_response.get("response")
    }), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4200, debug=False)
