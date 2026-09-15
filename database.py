import sqlite3
from datetime import datetime

from config import DATABASE_PATH


def _connect():
    return sqlite3.connect(DATABASE_PATH)


def init_db():
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                product_type TEXT,
                purpose TEXT,
                image_count INTEGER
            )
        """)
        conn.commit()


def save_project(analysis, plan):
    init_db()
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO projects(created_at, product_type, purpose, image_count)
            VALUES (?, ?, ?, ?)
            """,
            (
                datetime.utcnow().isoformat(),
                analysis.product_type,
                analysis.purpose,
                len(plan.images),
            ),
        )
        conn.commit()
