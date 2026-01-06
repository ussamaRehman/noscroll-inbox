import json
import os

from core.digest import build_digest, build_email_preview
from storage.sqlite_store import SQLiteStore

DEMO_EMAIL = "demo@example.com"
DEMO_HANDLE = "demo"
DEMO_DAYS = 365


def main() -> None:
    db_path = os.environ.get("DB_PATH", "noscroll.db")
    store = SQLiteStore(db_path=db_path)
    store.init_db()
    store.reset_demo(DEMO_EMAIL, DEMO_HANDLE)
    store.seed_demo(DEMO_EMAIL, DEMO_HANDLE)

    text, _groups, _total = build_digest(DEMO_EMAIL, DEMO_DAYS, store=store)
    subject, body, total = build_email_preview(DEMO_EMAIL, DEMO_DAYS, store=store)

    print("Digest")
    print(text)
    print("\nEmail Preview")
    print(
        json.dumps(
            {
                "email": DEMO_EMAIL,
                "days": DEMO_DAYS,
                "subject": subject,
                "body": body,
                "total": total,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
