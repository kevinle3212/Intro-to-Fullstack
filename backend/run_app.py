import logging as log
from logging import FileHandler
from flask_cors import CORS
from flask import Flask, jsonify  

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

# _________________ Systematic Endpoint _________________ #

@app.route("/")  # ALWAYS great to have. 
def home():
    """
    HOME PAGE
    """
    return jsonify({"status": "OK"}), 200
    
@app.route("/stock/<ticker>")   
def stocks(ticker):
    """
    You can also check for the status of the database, AI client, etc...
    This just checks the status of the app as a whole.
    """
    return jsonify({"status": "OK", "Data": {"Ticker": ticker}}), 200

@app.route("/crypto/<ticker>")   
def crypto(ticker):
    """
    You can also check for the status of the database, AI client, etc...
    This just checks the status of the app as a whole.
    """
    return jsonify({"status": "OK", "Data": {"Ticker": ticker}}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4200, debug=False)
