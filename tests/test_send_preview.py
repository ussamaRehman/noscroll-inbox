import importlib
import os

from fastapi.testclient import TestClient


def get_client(tmp_path) -> TestClient:
    os.environ["DB_PATH"] = str(tmp_path / "test.db")
    import app.main as main_app

    importlib.reload(main_app)
    return TestClient(main_app.app)


def seed_two_saves(client: TestClient) -> None:
    client.post("/admin/reset_all")
    client.post("/admin/allowlist/add", json={"email": "test@example.com"})
    client.post("/simulate_dm", json={"x_handle": "u1", "text": "start test@example.com"})
    client.post("/simulate_dm", json={"x_handle": "u1", "text": "https://x.com/1 #tools"})
    client.post("/simulate_dm", json={"x_handle": "u1", "text": "https://x.com/2"})


def test_send_preview_idempotent_same_day(tmp_path):
    client = get_client(tmp_path)
    seed_two_saves(client)

    first = client.post("/digest/send_preview", json={"email": "test@example.com", "days": 365})
    assert first.status_code == 200
    first_data = first.json()
    assert first_data["already_sent"] is False

    second = client.post("/digest/send_preview", json={"email": "test@example.com", "days": 365})
    assert second.status_code == 200
    second_data = second.json()
    assert second_data["already_sent"] is True
    assert second_data["subject"] == first_data["subject"]
    assert second_data["body"] == first_data["body"]


def test_send_preview_total_matches_digest(tmp_path):
    client = get_client(tmp_path)
    seed_two_saves(client)

    digest = client.get("/digest", params={"email": "test@example.com", "days": 365})
    groups = digest.json()["groups"]
    total = sum(group["count"] for group in groups)

    preview = client.post("/digest/send_preview", json={"email": "test@example.com", "days": 365})
    assert preview.status_code == 200
    assert preview.json()["total"] == total
