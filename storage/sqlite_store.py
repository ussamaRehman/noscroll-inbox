import json
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone
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
            conn.execute(
                "CREATE TABLE IF NOT EXISTS magic_tokens ("
                "token TEXT PRIMARY KEY, "
                "email TEXT NOT NULL, "
                "created_at TEXT NOT NULL, "
                "expires_at TEXT NOT NULL, "
                "used_at TEXT)"
            )
            conn.execute(
                "CREATE TABLE IF NOT EXISTS digest_sends ("
                "email TEXT NOT NULL, "
                "days INTEGER NOT NULL, "
                "date_utc TEXT NOT NULL, "
                "total INTEGER NOT NULL, "
                "subject TEXT NOT NULL, "
                "body TEXT NOT NULL, "
                "sent_at TEXT NOT NULL, "
                "PRIMARY KEY (email, days, date_utc))"
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

    def list_linked_emails(self) -> List[str]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT DISTINCT email FROM ("
                "SELECT email FROM links UNION SELECT email FROM inbox"
                ") ORDER BY email"
            ).fetchall()
            return [row["email"] for row in rows]

    def link_delete(self, x_handle: str) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM links WHERE x_handle = ?", (x_handle,))
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

    def inbox_clear(self, email: Optional[str] = None) -> None:
        with self._connect() as conn:
            if email:
                conn.execute("DELETE FROM inbox WHERE email = ?", (email,))
            else:
                conn.execute("DELETE FROM inbox")
            conn.commit()

    def inbox_list_since(self, email: str, since_iso: str, limit: int) -> List[Dict[str, object]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT url, tags_json, note, saved_at FROM inbox "
                "WHERE email = ? AND saved_at >= ? "
                "ORDER BY saved_at DESC, id DESC "
                "LIMIT ?",
                (email, since_iso, limit),
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

    def magic_create(self, email: str, ttl_seconds: int = 900) -> str:
        now = datetime.now(timezone.utc)
        token = secrets.token_urlsafe(32)
        created_at = now.isoformat()
        expires_at = (now + timedelta(seconds=ttl_seconds)).isoformat()
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO magic_tokens(token, email, created_at, expires_at, used_at) "
                "VALUES (?, ?, ?, ?, NULL)",
                (token, email, created_at, expires_at),
            )
            conn.commit()
        return token

    def magic_redeem(self, token: str) -> str:
        now = datetime.now(timezone.utc)
        with self._connect() as conn:
            row = conn.execute(
                "SELECT email, expires_at, used_at FROM magic_tokens WHERE token = ?",
                (token,),
            ).fetchone()
            if not row:
                raise ValueError("invalid")
            if row["used_at"]:
                raise ValueError("used")
            expires_at = datetime.fromisoformat(row["expires_at"])
            if now > expires_at:
                raise ValueError("expired")
            conn.execute(
                "UPDATE magic_tokens SET used_at = ? WHERE token = ?",
                (now.isoformat(), token),
            )
            conn.commit()
            return row["email"]

    def magic_clear(self) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM magic_tokens")
            conn.commit()

    def digest_send_get(self, email: str, days: int, date_utc: str) -> Optional[Dict[str, object]]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT email, days, date_utc, total, subject, body, sent_at "
                "FROM digest_sends WHERE email = ? AND days = ? AND date_utc = ?",
                (email, days, date_utc),
            ).fetchone()
            if not row:
                return None
            return {
                "email": row["email"],
                "days": row["days"],
                "date_utc": row["date_utc"],
                "total": row["total"],
                "subject": row["subject"],
                "body": row["body"],
                "sent_at": row["sent_at"],
            }

    def digest_send_put(
        self,
        email: str,
        days: int,
        date_utc: str,
        total: int,
        subject: str,
        body: str,
    ) -> None:
        sent_at = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO digest_sends(email, days, date_utc, total, subject, body, sent_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (email, days, date_utc, total, subject, body, sent_at),
            )
            conn.commit()

    def digest_send_list(self, email: str, days: int) -> List[Dict[str, object]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT email, days, date_utc, total, subject, body, sent_at "
                "FROM digest_sends WHERE email = ? AND days = ? ORDER BY sent_at DESC",
                (email, days),
            ).fetchall()
            return [
                {
                    "email": row["email"],
                    "days": row["days"],
                    "date_utc": row["date_utc"],
                    "total": row["total"],
                    "subject": row["subject"],
                    "body": row["body"],
                    "sent_at": row["sent_at"],
                }
                for row in rows
            ]

    def digest_sends_clear(self) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM digest_sends")
            conn.commit()
