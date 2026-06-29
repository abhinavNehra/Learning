# monitoring.py — log everything, alert on drift

import sqlite3
from datetime import datetime, timedelta

db = sqlite3.connect("prompt_logs.db")
db.execute("""
    CREATE TABLE IF NOT EXISTS interactions (
        id           INTEGER PRIMARY KEY,
        timestamp    TEXT,
        prompt_ver   TEXT,
        user_input   TEXT,
        output       TEXT,
        input_tokens  INTEGER,
        output_tokens INTEGER,
        latency_ms    INTEGER,
        user_rating   INTEGER,    -- -1 (thumbs down) | 0 (no rating) | 1 (thumbs up)
        flagged       BOOLEAN
    )
""")

def log_interaction(data: dict):
    db.execute("""
        INSERT INTO interactions
        (timestamp, prompt_ver, user_input, output, input_tokens,
         output_tokens, latency_ms, user_rating, flagged)
        VALUES (?,?,?,?,?,?,?,?,?)
    """, (
        datetime.now().isoformat(),
        data["prompt_ver"],
        data["user_input"][:500],   # truncate for storage
        data["output"][:1000],
        data["input_tokens"],
        data["output_tokens"],
        data["latency_ms"],
        data.get("user_rating", 0),
        data.get("flagged", False)
    ))
    db.commit()

def daily_health_check():
    """Run every morning. Alert if metrics drift from baseline."""
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    stats = db.execute("""
        SELECT
            COUNT(*)                                    as total,
            AVG(latency_ms)                             as avg_latency,
            AVG(CASE WHEN user_rating = -1 THEN 1.0 ELSE 0.0 END) as thumbs_down_rate,
            AVG(output_tokens)                          as avg_output_tokens,
            SUM(CASE WHEN flagged THEN 1 ELSE 0 END)   as flagged_count
        FROM interactions
        WHERE timestamp LIKE ?
    """, (f"{yesterday}%",)).fetchone()

    total, avg_latency, thumbs_down_rate, avg_tokens, flagged = stats

    alerts = []
    if thumbs_down_rate  > 0.15:  alerts.append(f"⚠️ High thumbs-down rate: {thumbs_down_rate:.0%}")
    if avg_latency       > 3000:  alerts.append(f"⚠️ High latency: {avg_latency:.0f}ms avg")
    if avg_tokens        > 600:   alerts.append(f"⚠️ Verbose outputs: {avg_tokens:.0f} tokens avg")
    if flagged           > 10:    alerts.append(f"⚠️ Injection attempts: {flagged}")

    if alerts:
        print('--------------------------ALERTS--------------------------')
        print("\n".join(alerts))
        print('--------------------------------------------------------')
    else:
        print(f"✅ Health check passed — {total} interactions, "
              f"{thumbs_down_rate:.0%} negative feedback")