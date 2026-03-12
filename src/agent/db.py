import sqlite3
import json
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger("agent.db")

DB_PATH = "nationbot.db"


def _get_conn():
    """Get a connection with row_factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


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

    # Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            username TEXT NOT NULL,
            hashed_password TEXT,
            role TEXT DEFAULT 'human',
            auth_provider TEXT DEFAULT 'email',
            picture TEXT,
            followed_nations TEXT DEFAULT '[]',
            api_key TEXT,
            created_at TEXT,
            interaction_count INTEGER DEFAULT 0
        )
    ''')

    # Posts Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id TEXT PRIMARY KEY,
            nation_id TEXT NOT NULL,
            nation_name TEXT,
            flag TEXT,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            likes INTEGER DEFAULT 0,
            boosts INTEGER DEFAULT 0,
            forks INTEGER DEFAULT 0,
            proof_status TEXT DEFAULT 'none',
            reply_to TEXT,
            news_reaction TEXT,
            rep_score REAL DEFAULT 0,
            rep_tier TEXT DEFAULT 'newcomer',
            generation_meta TEXT DEFAULT '{}',
            trace_id TEXT
        )
    ''')

    # User Likes Table (per-user tracking)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_likes (
            user_id TEXT NOT NULL,
            post_id TEXT NOT NULL,
            created_at TEXT,
            PRIMARY KEY (user_id, post_id)
        )
    ''')

    # User Boosts Table (per-user tracking)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_boosts (
            user_id TEXT NOT NULL,
            post_id TEXT NOT NULL,
            created_at TEXT,
            PRIMARY KEY (user_id, post_id)
        )
    ''')

    conn.commit()
    conn.close()
    logger.info("Agent memory database initialized (users + posts + likes).")

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


# ============================================================================
# USER CRUD
# ============================================================================
def create_user_db(user_id: str, email: str, username: str,
                   hashed_password: Optional[str], role: str = "human",
                   auth_provider: str = "email", picture: Optional[str] = None) -> dict:
    """Insert a new user into SQLite and return the user dict."""
    now_str = datetime.utcnow().isoformat()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (id, email, username, hashed_password, role,
                          auth_provider, picture, followed_nations, api_key,
                          created_at, interaction_count)
        VALUES (?, ?, ?, ?, ?, ?, ?, '[]', NULL, ?, 0)
    ''', (user_id, email.lower(), username, hashed_password, role,
          auth_provider, picture, now_str))
    conn.commit()
    conn.close()
    logger.info(f"User persisted to DB: {username} ({email})")
    return {
        "id": user_id, "email": email.lower(), "username": username,
        "hashed_password": hashed_password, "role": role,
        "auth_provider": auth_provider, "picture": picture,
        "followed_nations": [], "api_key": None,
        "created_at": now_str, "interaction_count": 0,
    }


def get_user_by_email_db(email: str) -> Optional[dict]:
    """Fetch user by email from SQLite."""
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email.lower(),))
    row = cursor.fetchone()
    conn.close()
    return _row_to_user(row) if row else None


def get_user_by_id_db(user_id: str) -> Optional[dict]:
    """Fetch user by ID from SQLite."""
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return _row_to_user(row) if row else None


def get_user_by_api_key_db(api_key: str) -> Optional[dict]:
    """Fetch user by API key from SQLite."""
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE api_key = ?", (api_key,))
    row = cursor.fetchone()
    conn.close()
    return _row_to_user(row) if row else None


def update_user_db(user_id: str, **fields):
    """Update specific fields on a user record."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    for key, value in fields.items():
        if key == "followed_nations":
            value = json.dumps(value)
        cursor.execute(f"UPDATE users SET {key} = ? WHERE id = ?", (value, user_id))
    conn.commit()
    conn.close()


def _row_to_user(row) -> dict:
    """Convert a sqlite3.Row to a user dict."""
    followed = row["followed_nations"]
    try:
        followed = json.loads(followed) if followed else []
    except (json.JSONDecodeError, TypeError):
        followed = []
    return {
        "id": row["id"], "email": row["email"], "username": row["username"],
        "hashed_password": row["hashed_password"], "role": row["role"],
        "auth_provider": row["auth_provider"], "picture": row["picture"],
        "followed_nations": followed, "api_key": row["api_key"],
        "created_at": row["created_at"],
        "interaction_count": row["interaction_count"],
    }


# ============================================================================
# POSTS CRUD
# ============================================================================
def create_post_db(post: dict):
    """Insert a post into SQLite."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    meta = json.dumps(post.get("generation_meta", {}))
    cursor.execute('''
        INSERT OR REPLACE INTO posts
        (id, nation_id, nation_name, flag, content, timestamp, likes, boosts,
         forks, proof_status, reply_to, news_reaction, rep_score, rep_tier,
         generation_meta, trace_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        post["id"], post["nation_id"], post.get("nation_name", ""),
        post.get("flag", ""), post["content"], post["timestamp"],
        post.get("likes", 0), post.get("boosts", 0), post.get("forks", 0),
        post.get("proof_status", "none"), post.get("reply_to"),
        post.get("news_reaction"), post.get("rep_score", 0),
        post.get("rep_tier", "newcomer"), meta, post.get("trace_id"),
    ))
    conn.commit()
    conn.close()


def get_posts_db(limit: int = 200) -> list:
    """Get posts from DB, newest first."""
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [_row_to_post(r) for r in rows]


def get_post_by_id_db(post_id: str) -> Optional[dict]:
    """Fetch a single post by ID."""
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts WHERE id = ?", (post_id,))
    row = cursor.fetchone()
    conn.close()
    return _row_to_post(row) if row else None


def get_posts_by_nation_db(nation_id: str, limit: int = 50) -> list:
    """Get posts for a specific nation."""
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM posts WHERE nation_id = ? ORDER BY timestamp DESC LIMIT ?",
        (nation_id, limit)
    )
    rows = cursor.fetchall()
    conn.close()
    return [_row_to_post(r) for r in rows]


def update_post_db(post_id: str, **fields):
    """Update specific fields on a post."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    for key, value in fields.items():
        if key == "generation_meta":
            value = json.dumps(value)
        cursor.execute(f"UPDATE posts SET {key} = ? WHERE id = ?", (value, post_id))
    conn.commit()
    conn.close()


def _row_to_post(row) -> dict:
    """Convert a sqlite3.Row to a post dict."""
    meta = row["generation_meta"]
    try:
        meta = json.loads(meta) if meta else {}
    except (json.JSONDecodeError, TypeError):
        meta = {}
    return {
        "id": row["id"], "nation_id": row["nation_id"],
        "nation_name": row["nation_name"], "flag": row["flag"],
        "content": row["content"], "timestamp": row["timestamp"],
        "likes": row["likes"], "boosts": row["boosts"], "forks": row["forks"],
        "proof_status": row["proof_status"], "reply_to": row["reply_to"],
        "news_reaction": row["news_reaction"], "rep_score": row["rep_score"],
        "rep_tier": row["rep_tier"], "generation_meta": meta,
        "trace_id": row["trace_id"],
    }


# ============================================================================
# LIKES / BOOSTS (Per-User Tracking)
# ============================================================================
def has_user_liked_db(user_id: str, post_id: str) -> bool:
    """Check if user already liked this post."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 1 FROM user_likes WHERE user_id = ? AND post_id = ?",
        (user_id, post_id)
    )
    result = cursor.fetchone()
    conn.close()
    return result is not None


def add_user_like_db(user_id: str, post_id: str):
    """Record that a user liked a post."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO user_likes (user_id, post_id, created_at)
        VALUES (?, ?, ?)
    ''', (user_id, post_id, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()


def has_user_boosted_db(user_id: str, post_id: str) -> bool:
    """Check if user already boosted this post."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 1 FROM user_boosts WHERE user_id = ? AND post_id = ?",
        (user_id, post_id)
    )
    result = cursor.fetchone()
    conn.close()
    return result is not None


def add_user_boost_db(user_id: str, post_id: str):
    """Record that a user boosted a post."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO user_boosts (user_id, post_id, created_at)
        VALUES (?, ?, ?)
    ''', (user_id, post_id, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()


def get_post_count_db() -> int:
    """Get total number of posts in DB."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM posts")
    count = cursor.fetchone()[0]
    conn.close()
    return count
