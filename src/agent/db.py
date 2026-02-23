import sqlite3
import json
import logging
from datetime import datetime

logger = logging.getLogger("agent.db")

DB_PATH = "nationbot.db"

def init_db():
    """Initialize the SQLite database and create tables if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Relationships Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS relationships (
            nation_a TEXT,
            nation_b TEXT,
            score REAL,
            updated_at TEXT,
            PRIMARY KEY (nation_a, nation_b)
        )
    ''')
    
    # History Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            event_type TEXT,
            nation_a TEXT,
            nation_b TEXT,
            delta REAL,
            detail TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("Agent memory database initialized.")

def get_all_relationships() -> dict:
    """Load all relationships from DB into a nested dictionary."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT nation_a, nation_b, score FROM relationships")
    rows = cursor.fetchall()
    conn.close()
    
    relationships = {}
    for a, b, score in rows:
        if a not in relationships:
            relationships[a] = {}
        relationships[a][b] = score
    
    return relationships

def update_relationship_db(nation_a: str, nation_b: str, score: float):
    """Upsert relationship score to DB."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now_str = datetime.utcnow().isoformat()
    cursor.execute('''
        INSERT INTO relationships (nation_a, nation_b, score, updated_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(nation_a, nation_b) DO UPDATE SET
            score=excluded.score,
            updated_at=excluded.updated_at
    ''', (nation_a, nation_b, score, now_str))
    conn.commit()
    conn.close()

def get_history(limit: int = 500) -> list:
    """Get history entries from DB, newest first."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM history ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    
    history = []
    for row in rows:
        history.append({
            "timestamp": row["timestamp"],
            "event_type": row["event_type"],
            "nation_a": row["nation_a"],
            "nation_b": row["nation_b"],
            "delta": row["delta"],
            "detail": row["detail"]
        })
    return history

def add_history_entry(event_type: str, nation_a: str, nation_b: str, delta: float, detail: str) -> dict:
    """Add a new history entry to DB and return the dictionary representation."""
    now_str = datetime.utcnow().isoformat()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO history (timestamp, event_type, nation_a, nation_b, delta, detail)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (now_str, event_type, nation_a, nation_b, delta, detail))
    conn.commit()
    conn.close()
    
    return {
        "timestamp": now_str,
        "event_type": event_type,
        "nation_a": nation_a,
        "nation_b": nation_b,
        "delta": delta,
        "detail": detail
    }
