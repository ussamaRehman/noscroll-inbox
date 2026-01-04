import importlib
import os
from urllib.parse import parse_qs, urlparse

from fastapi.testclient import TestClient

from storage.sqlite_store import SQLiteStore


def get_client(tmp_path) -> TestClient:
    os.environ["DB_PATH"] = str(tmp_path / "test.db")
    import app.main as main_app

    importlib.reload(main_app)
    return TestClient(main_app.app)


def test_magic_link_created_on_allowlisted_start(tmp_path):
    client = get_client(tmp_path)
    client.post("/admin/reset_all")
    client.post("/admin/allowlist/add", json={"email": "user@example.com"})
    response = client.post(
        "/simulate_dm",
        json={"x_handle": "u1", "text": "start user@example.com"},
    )
    data = response.json()
    assert response.status_code == 200
    assert "magic_link" in data
    assert data["magic_link"].startswith("http://localhost:8000/auth/magic?token=")


def test_magic_link_redeem_success_and_single_use(tmp_path):
    client = get_client(tmp_path)
    client.post("/admin/reset_all")
    client.post("/admin/allowlist/add", json={"email": "user@example.com"})
    response = client.post(
        "/simulate_dm",
        json={"x_handle": "u1", "text": "start user@example.com"},
    )
    token = parse_qs(urlparse(response.json()["magic_link"]).query)["token"][0]

    redeem = client.get("/auth/magic", params={"token": token})
    assert redeem.status_code == 200
    assert redeem.json()["ok"] is True

    redeem_again = client.get("/auth/magic", params={"token": token})
    assert redeem_again.status_code == 400
    assert redeem_again.json()["detail"] == "token already used"


def test_magic_link_expired(tmp_path):
    db_path = tmp_path / "test.db"
    os.environ["DB_PATH"] = str(db_path)
    import app.main as main_app

    importlib.reload(main_app)
    client = TestClient(main_app.app)
    client.post("/admin/reset_all")
    store = SQLiteStore(str(db_path))
    store.init_db()
    token = store.magic_create("user@example.com", ttl_seconds=0)
    response = client.get("/auth/magic", params={"token": token})
    assert response.status_code == 400
    assert response.json()["detail"] == "token expired"
