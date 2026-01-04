import importlib
import os

from fastapi.testclient import TestClient


def get_client(tmp_path) -> TestClient:
    os.environ["DB_PATH"] = str(tmp_path / "test.db")
    import app.main as main_app

    importlib.reload(main_app)
    return TestClient(main_app.app)


def seed_item(client: TestClient, email: str, x_handle: str, text: str) -> None:
    client.post("/admin/allowlist/add", json={"email": email})
    client.post("/simulate_dm", json={"x_handle": x_handle, "text": f"start {email}"})
    client.post("/simulate_dm", json={"x_handle": x_handle, "text": text})


def test_email_preview_subject_and_body_pluralization(tmp_path):
    client = get_client(tmp_path)
    client.post("/admin/reset_all")
    seed_item(client, "test@example.com", "u1", "https://x.com/1 #tools")
    seed_item(client, "test@example.com", "u1", "https://x.com/2")

    response = client.get(
        "/digest/email_preview",
        params={"email": "test@example.com", "days": 365},
    )
    assert response.status_code == 200
    data = response.json()
    assert "2 saves" in data["subject"]
    assert "365 days" in data["subject"]
    assert data["body"].startswith("Daily Digest (last 365 days) — test@example.com")


def test_email_preview_single_save_single_day(tmp_path):
    client = get_client(tmp_path)
    client.post("/admin/reset_all")
    seed_item(client, "test@example.com", "u1", "https://x.com/1 #tools")

    response = client.get("/digest/email_preview", params={"email": "test@example.com", "days": 1})
    assert response.status_code == 200
    data = response.json()
    assert "1 save" in data["subject"]
    assert "1 day" in data["subject"]
    assert "#tools (1)" in data["body"]
