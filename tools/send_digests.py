import os
from datetime import datetime, timezone
from typing import List

from core.digest import build_email_preview
from storage.sqlite_store import SQLiteStore


def run_send_digests(
    store: SQLiteStore,
    emails: List[str],
    days: int,
    date_utc: str,
) -> dict:
    sent_count = 0
    skip_count = 0
    lines: List[str] = []
    for email in emails:
        existing = store.digest_send_get(email, days, date_utc)
        if existing:
            lines.append(f"SKIP {email} (already sent)")
            skip_count += 1
            continue
        subject, body, total = build_email_preview(email, days, store=store)
        store.digest_send_put(email, days, date_utc, total, subject, body)
        lines.append(f"SENT {email} total={total}")
        sent_count += 1
    return {"sent": sent_count, "skipped": skip_count, "lines": lines}


def main() -> None:
    db_path = os.environ.get("DB_PATH", "noscroll.db")
    store = SQLiteStore(db_path=db_path)
    store.init_db()

    email = os.getenv("EMAIL")
    days = int(os.getenv("DAYS", "1"))
    date_utc = datetime.now(timezone.utc).date().isoformat()

    if email:
        emails = [email]
    else:
        emails = store.list_linked_emails()

    result = run_send_digests(store, emails, days, date_utc)
    for line in result["lines"]:
        print(line)
    print(f"Summary: sent={result['sent']} skipped={result['skipped']} total={len(emails)}")


if __name__ == "__main__":
    main()
