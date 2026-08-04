import os
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, TakeProfitRequest, StopLossRequest
from alpaca.trading.enums import OrderSide, TimeInForce

class AlpacaTrader:
    def __init__(self, api_key=None, secret_key=None, paper=True):
        self.api_key = api_key or os.getenv("ALPACA_API_KEY")
        self.secret_key = secret_key or os.getenv("ALPACA_SECRET_KEY")
        self.paper = paper
        
        if not self.api_key or not self.secret_key:
            print("WARNING: Alpaca API keys missing! Please set ALPACA_API_KEY and ALPACA_SECRET_KEY.")
            self.client = None
        else:
            self.client = TradingClient(self.api_key, self.secret_key, paper=self.paper)

    def execute_signal(self, symbol, action, qty=1, tp_price=None, sl_price=None):
        if not self.client:
            return {"status": "error", "message": "Alpaca API keys not configured"}

        side = OrderSide.BUY if action.lower() in ["buy", "long"] else OrderSide.SELL

        try:
            take_profit = TakeProfitRequest(limit_price=round(float(tp_price), 2)) if tp_price else None
            stop_loss = StopLossRequest(stop_price=round(float(sl_price), 2)) if sl_price else None

            order_data = MarketOrderRequest(
                symbol=symbol.upper(),
                qty=qty,
                side=side,
                time_in_force=TimeInForce.GTC,
                take_profit=take_profit,
                stop_loss=stop_loss
            )

            order = self.client.submit_order(order_data)
            return {
                "status": "success",
                "order_id": str(order.id),
                "symbol": order.symbol,
                "qty": float(order.qty),
                "side": str(order.side)
            }
        except Exception as e:
            print(f"Error executing Alpaca order: {e}")
            return {"status": "error", "message": str(e)}

    def close_all_positions(self):
        if self.client:
            return self.client.close_all_positions(cancel_orders=True)
        return None
