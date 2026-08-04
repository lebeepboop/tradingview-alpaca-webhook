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

    print(f"Received JSON webhook: {data}")

    symbol = data.get("symbol", "QQQ")
    action = data.get("action", "buy")
    qty = data.get("qty", 1)
    entry_price = data.get("price", 0.0)
    tp_price = data.get("tp_price")
    sl_price = data.get("sl_price")
    regime = data.get("regime", "UNKNOWN")

    trade_id = log_trade(symbol, action, qty, entry_price, tp_price, sl_price, regime)
    alpaca_res = trader.execute_signal(symbol, action, qty, tp_price, sl_price)

    return jsonify({"status": "received", "trade_id": trade_id, "alpaca_response": alpaca_res}), 200

@app.route("/email-webhook", methods=["POST"])
def email_webhook():
    import json, re
    form_data = request.form
    plain_text = form_data.get("plain", "") or form_data.get("html", "")
    
    print(f"Received email payload: {plain_text[:200]}...")

    # Extract JSON object from email body text
    json_match = re.search(r'\{.*\}', plain_text, re.DOTALL)
    if json_match:
        try:
            data = json.loads(json_match.group(0))
            symbol = data.get("symbol", "QQQ")
            action = data.get("action", "buy")
            qty = data.get("qty", 1)
            entry_price = data.get("price", 0.0)
            tp_price = data.get("tp_price")
            sl_price = data.get("sl_price")
            regime = data.get("regime", "UNKNOWN")

            trade_id = log_trade(symbol, action, qty, entry_price, tp_price, sl_price, regime)
            alpaca_res = trader.execute_signal(symbol, action, qty, tp_price, sl_price)

            return jsonify({"status": "success", "source": "email", "trade_id": trade_id, "alpaca": alpaca_res}), 200
        except Exception as e:
            print(f"Error parsing email JSON: {e}")
            return jsonify({"status": "error", "message": str(e)}), 400

    return jsonify({"status": "ignored", "message": "No valid JSON payload found in email body"}), 200


@app.route("/api/stats", methods=["GET"])
def api_stats():
    return jsonify(get_stats())

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
