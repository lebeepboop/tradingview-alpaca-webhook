import os
from flask import Flask, request, jsonify, render_template
from database import init_db, log_trade, get_all_trades, get_stats
from alpaca_trader import AlpacaTrader
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
init_db()

trader = AlpacaTrader()

@app.route("/", methods=["GET"])
def dashboard():
    trades = get_all_trades()
    stats = get_stats()
    return render_template("dashboard.html", trades=trades, stats=stats)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    if not data:
        return jsonify({"status": "error", "message": "No JSON payload received"}), 400

    print(f"Received webhook: {data}")

    symbol = data.get("symbol", "QQQ")
    action = data.get("action", "buy")
    qty = data.get("qty", 1)
    entry_price = data.get("price", 0.0)
    tp_price = data.get("tp_price")
    sl_price = data.get("sl_price")
    regime = data.get("regime", "UNKNOWN")

    # Log to local DB
    trade_id = log_trade(symbol, action, qty, entry_price, tp_price, sl_price, regime)

    # Place trade on Alpaca
    alpaca_res = trader.execute_signal(symbol, action, qty, tp_price, sl_price)

    return jsonify({
        "status": "received",
        "trade_id": trade_id,
        "alpaca_response": alpaca_res
    }), 200

@app.route("/api/stats", methods=["GET"])
def api_stats():
    return jsonify(get_stats())

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
