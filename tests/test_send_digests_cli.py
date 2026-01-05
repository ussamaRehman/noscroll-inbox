import importlib
import os
from datetime import datetime, timezone

from storage.sqlite_store import SQLiteStore


def test_send_digests_idempotent(tmp_path):
    os.environ["DB_PATH"] = str(tmp_path / "test.db")
    import tools.send_digests as send_digests

    importlib.reload(send_digests)
    store = SQLiteStore(os.environ["DB_PATH"])
    store.init_db()
    store.allowlist_add("test@example.com")
    store.link_set_if_unlinked("u1", "test@example.com")
    now = datetime.now(timezone.utc).isoformat()
    store.inbox_add_items("test@example.com", ["https://x.com/1"], ["tools"], None, now)

    date_utc = datetime.now(timezone.utc).date().isoformat()
    first = send_digests.run_send_digests(
        store,
        ["test@example.com"],
        days=1,
        date_utc=date_utc,
    )
    second = send_digests.run_send_digests(
        store,
        ["test@example.com"],
        days=1,
        date_utc=date_utc,
    )

    assert first["sent"] == 1
    assert second["skipped"] == 1
