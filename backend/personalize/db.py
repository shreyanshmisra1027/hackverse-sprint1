import sqlite3

DB_PATH = "sessions.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            stock TEXT,
            latency_ms REAL,
            confidence REAL,
            risk_score TEXT,
            signals_used TEXT,
            degraded_mode INTEGER
        )
    """)
    conn.commit()
    conn.close()
