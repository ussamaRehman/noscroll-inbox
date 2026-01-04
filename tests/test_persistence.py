import importlib
import os

from fastapi.testclient import TestClient


def test_persistence_across_reload(tmp_path):
    db_path = tmp_path / "persist.db"
    os.environ["DB_PATH"] = str(db_path)
    import app.main as main_app

    importlib.reload(main_app)
    client = TestClient(main_app.app)
    client.post("/admin/reset_all")
    client.post("/admin/allowlist/add", json={"email": "user@example.com"})
    client.post("/simulate_dm", json={"x_handle": "u1", "text": "start user@example.com"})
    client.post("/simulate_dm", json={"x_handle": "u1", "text": "https://x.com/1"})

    importlib.reload(main_app)
    client = TestClient(main_app.app)
    inbox = client.get("/inbox", params={"email": "user@example.com"})
    assert inbox.json()["count"] == 1
