import sqlite3
import json
from contextlib import contextmanager
from typing import Optional, Any
from config import DATABASE_PATH

class CacheDB:
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS key_value_cache (
                    category TEXT,
                    cache_key TEXT,
                    value_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (category, cache_key)
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS bookings (
                    booking_id TEXT PRIMARY KEY,
                    plan_id TEXT,
                    item_type TEXT,
                    item_id TEXT,
                    item_name TEXT,
                    date_or_time TEXT,
                    guests INTEGER,
                    user_name TEXT,
                    amount REAL,
                    status TEXT,
                    details_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def get(self, category: str, key: str) -> Optional[Any]:
        with self._get_connection() as conn:
            cur = conn.execute(
                "SELECT value_json FROM key_value_cache WHERE category = ? AND cache_key = ?",
                (category, key)
            )
            row = cur.fetchone()
            if row:
                return json.loads(row["value_json"])
        return None

    def set(self, category: str, key: str, value: Any):
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO key_value_cache (category, cache_key, value_json)
                VALUES (?, ?, ?)
                """,
                (category, key, json.dumps(value))
            )
            conn.commit()

    def save_booking(self, booking_dict: dict):
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO bookings 
                (booking_id, plan_id, item_type, item_id, item_name, date_or_time, guests, user_name, amount, status, details_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    booking_dict["booking_id"],
                    booking_dict.get("plan_id", ""),
                    booking_dict["item_type"],
                    booking_dict["item_id"],
                    booking_dict["item_name"],
                    booking_dict["date_or_time"],
                    booking_dict.get("guests", 1),
                    booking_dict.get("user_name", "Traveler"),
                    booking_dict.get("amount", 0.0),
                    booking_dict.get("status", "CONFIRMED"),
                    json.dumps(booking_dict.get("details", {}))
                )
            )
            conn.commit()

    def get_booking(self, booking_id: str) -> Optional[dict]:
        with self._get_connection() as conn:
            cur = conn.execute("SELECT * FROM bookings WHERE booking_id = ?", (booking_id,))
            row = cur.fetchone()
            if row:
                d = dict(row)
                d["details"] = json.loads(d["details_json"]) if d.get("details_json") else {}
                return d
        return None

    def list_bookings(self, plan_id: Optional[str] = None) -> list:
        with self._get_connection() as conn:
            if plan_id:
                cur = conn.execute("SELECT * FROM bookings WHERE plan_id = ? ORDER BY created_at DESC", (plan_id,))
            else:
                cur = conn.execute("SELECT * FROM bookings ORDER BY created_at DESC")
            rows = cur.fetchall()
            results = []
            for r in rows:
                d = dict(r)
                d["details"] = json.loads(d["details_json"]) if d.get("details_json") else {}
                results.append(d)
            return results

cache_db = CacheDB()
