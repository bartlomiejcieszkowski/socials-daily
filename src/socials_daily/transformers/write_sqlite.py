"""Write SQLite output transformer."""

from __future__ import annotations

import json
import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from .base import Post, Transformer, transformer

log = logging.getLogger(__name__)


@transformer("write_sqlite")
class WriteSQLiteTransformer(Transformer):
    """Write posts to a SQLite database."""

    name = "write_sqlite"
    passthrough = True

    def __init__(self, db_path: str = "socials.db") -> None:
        """Initialize with database path.

        Args:
            db_path: Path to the SQLite database file.
        """
        self._db_path = Path(db_path)

    def transform(self, posts: list[Post]) -> list[Post]:
        """Write posts to SQLite database."""
        if not posts:
            return posts

        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self._db_path))

        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    link TEXT UNIQUE NOT NULL,
                    platform TEXT NOT NULL,
                    account TEXT NOT NULL,
                    caption TEXT,
                    date TEXT NOT NULL,
                    created_at TEXT DEFAULT (datetime('now')),
                    tags TEXT
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_posts_link ON posts(link)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_posts_platform ON posts(platform)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_posts_date ON posts(date)
            """)

            stored = 0
            for post in posts:
                tags_json = json.dumps(post.tags) if post.tags else None
                try:
                    conn.execute(
                        """
                        INSERT OR IGNORE INTO posts (link, platform, account, caption, date, tags)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            post.link,
                            post.platform,
                            post.account,
                            post.caption,
                            post.date.isoformat(),
                            tags_json,
                        ),
                    )
                    if conn.changes > 0:
                        stored += 1
                except sqlite3.IntegrityError:
                    pass  # Duplicate link, skip

            conn.commit()
            log.info("  SQLite: stored %d new posts in %s", stored, self._db_path.name)
        finally:
            conn.close()

        return posts  # Pass through unchanged
