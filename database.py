import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "trades.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            symbol TEXT NOT NULL,
            action TEXT NOT NULL,
            qty REAL,
            entry_price REAL,
            tp_price REAL,
            sl_price REAL,
            regime TEXT,
            status TEXT DEFAULT 'OPEN',
            close_price REAL,
            pnl REAL DEFAULT 0.0
        )
    """)
    conn.commit()
    conn.close()

def log_trade(symbol, action, qty, entry_price, tp_price=None, sl_price=None, regime=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO trades (symbol, action, qty, entry_price, tp_price, sl_price, regime)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (symbol, action, qty, entry_price, tp_price, sl_price, regime))
    trade_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return trade_id

def get_all_trades():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM trades ORDER BY id DESC")
    rows = cursor.fetchall()
    trades = [dict(row) for row in rows]
    conn.close()
    return trades

def get_stats():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*), SUM(pnl) FROM trades WHERE status = 'CLOSED'")
    total_closed, total_pnl = cursor.fetchone()
    total_closed = total_closed or 0
    total_pnl = total_pnl or 0.0

    cursor.execute("SELECT COUNT(*) FROM trades WHERE status = 'CLOSED' AND pnl > 0")
    wins = cursor.fetchone()[0] or 0

    win_rate = (wins / total_closed * 100) if total_closed > 0 else 0.0

    conn.close()
    return {
        "total_trades": total_closed,
        "wins": wins,
        "losses": total_closed - wins,
        "win_rate": round(win_rate, 1),
        "total_pnl": round(total_pnl, 2)
    }

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
