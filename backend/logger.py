import sqlite3
from datetime import datetime, timezone
from db import DB_PATH, init_db

def log_session(stock, latency_ms, confidence, risk_score, signals_used, degraded_mode=False):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO sessions (timestamp, stock, latency_ms, confidence, risk_score, signals_used, degraded_mode) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            datetime.now(timezone.utc).isoformat(),
            stock,
            latency_ms,
            confidence,
            risk_score,
            ",".join(signals_used),
            int(degraded_mode),
        ),
    )
    conn.commit()
    conn.close()

def get_recent_sessions(n=10):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM sessions ORDER BY id DESC LIMIT ?", (n,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]
