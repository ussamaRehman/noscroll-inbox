from core.digest import build_digest
from storage.sqlite_store import SQLiteStore


def test_demo_seed_and_digest_text(tmp_path):
    store = SQLiteStore(db_path=str(tmp_path / "test.db"))
    store.init_db()
    store.reset_demo("demo@example.com", "demo")
    store.seed_demo("demo@example.com", "demo")

    text, _groups, total = build_digest("demo@example.com", 365, store=store)
    assert total == 2
    assert "Daily Digest" in text
    assert "#tools (1)" in text
    assert "#untagged (1)" in text
