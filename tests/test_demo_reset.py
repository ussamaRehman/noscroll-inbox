from datetime import datetime, timezone

from storage.sqlite_store import SQLiteStore


def test_demo_reset_does_not_delete_other_users(tmp_path):
    store = SQLiteStore(db_path=str(tmp_path / "test.db"))
    store.init_db()
    store.allowlist_add("other@example.com")
    store.link_set_if_unlinked("other", "other@example.com")
    now = datetime.now(timezone.utc).isoformat()
    store.inbox_add_items("other@example.com", ["https://x.com/other"], ["tools"], None, now)

    store.reset_demo("demo@example.com", "demo")
    store.seed_demo("demo@example.com", "demo")

    assert store.allowlist_contains("other@example.com") is True
    assert store.link_get_email("other") == "other@example.com"
    assert len(store.inbox_list("other@example.com")) == 1


def test_demo_seed_creates_exact_two_items_and_clears_sends(tmp_path):
    store = SQLiteStore(db_path=str(tmp_path / "test.db"))
    store.init_db()
    today = datetime.now(timezone.utc).date().isoformat()
    store.digest_send_put("demo@example.com", 1, today, 1, "subj", "body")

    store.reset_demo("demo@example.com", "demo")
    store.seed_demo("demo@example.com", "demo")

    assert store.digest_send_get("demo@example.com", 1, today) is None
    assert len(store.inbox_list("demo@example.com")) == 2
