import json
import sqlite3
from typing import Dict, List, Optional


class SQLiteStore:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self) -> None:
        with self._connect() as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS allowlist (email TEXT PRIMARY KEY)")
            conn.execute(
                "CREATE TABLE IF NOT EXISTS links (x_handle TEXT PRIMARY KEY, email TEXT NOT NULL)"
            )
            conn.execute(
                "CREATE TABLE IF NOT EXISTS inbox ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "email TEXT NOT NULL, "
                "url TEXT NOT NULL, "
                "tags_json TEXT NOT NULL, "
                "note TEXT, "
                "saved_at TEXT NOT NULL)"
            )
            conn.commit()

    def allowlist_add(self, email: str) -> int:
        with self._connect() as conn:
            conn.execute("INSERT OR IGNORE INTO allowlist(email) VALUES (?)", (email,))
            count = conn.execute("SELECT COUNT(*) FROM allowlist").fetchone()[0]
            conn.commit()
            return int(count)

    def allowlist_clear(self) -> int:
        with self._connect() as conn:
            conn.execute("DELETE FROM allowlist")
            conn.commit()
            return 0

    def allowlist_contains(self, email: str) -> bool:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT 1 FROM allowlist WHERE email = ? LIMIT 1", (email,)
            ).fetchone()
            return row is not None

    def link_get_email(self, x_handle: str) -> Optional[str]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT email FROM links WHERE x_handle = ? LIMIT 1", (x_handle,)
            ).fetchone()
            return row["email"] if row else None

    def link_set_if_unlinked(self, x_handle: str, email: str) -> str:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT email FROM links WHERE x_handle = ? LIMIT 1", (x_handle,)
            ).fetchone()
            if not row:
                conn.execute("INSERT INTO links(x_handle, email) VALUES (?, ?)", (x_handle, email))
                conn.commit()
                return "linked"

            existing = row["email"]
            if existing.lower() == email.lower():
                return "resend"
            return "already_linked"

    def links_clear(self) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM links")
            conn.commit()

    def inbox_add_items(
        self,
        email: str,
        urls: List[str],
        tags: List[str],
        note: Optional[str],
        saved_at_iso: str,
    ) -> int:
        if not urls:
            return 0
        tags_json = json.dumps(tags)
        with self._connect() as conn:
            conn.executemany(
                "INSERT INTO inbox(email, url, tags_json, note, saved_at) VALUES (?, ?, ?, ?, ?)",
                [(email, url, tags_json, note, saved_at_iso) for url in urls],
            )
            conn.commit()
            return len(urls)

    def inbox_list(self, email: str) -> List[Dict[str, object]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT url, tags_json, note, saved_at FROM inbox WHERE email = ? ORDER BY id",
                (email,),
            ).fetchall()
            return [
                {
                    "url": row["url"],
                    "tags": json.loads(row["tags_json"]),
                    "note": row["note"],
                    "saved_at": row["saved_at"],
                }
                for row in rows
            ]

    def inbox_clear(self) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM inbox")
            conn.commit()
