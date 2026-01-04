import importlib
import os

from fastapi.testclient import TestClient


def get_client(tmp_path) -> TestClient:
    os.environ["DB_PATH"] = str(tmp_path / "test.db")
    import app.main as main_app

    importlib.reload(main_app)
    return TestClient(main_app.app)


def test_digest_groups_and_text(tmp_path):
    client = get_client(tmp_path)
    client.post("/admin/reset_all")
    client.post("/admin/allowlist/add", json={"email": "test@example.com"})
    client.post("/simulate_dm", json={"x_handle": "u1", "text": "start test@example.com"})
    client.post(
        "/simulate_dm",
        json={"x_handle": "u1", "text": "https://x.com/1 #tools note: persisted"},
    )
    client.post("/simulate_dm", json={"x_handle": "u1", "text": "https://x.com/2 #tools"})
    client.post("/simulate_dm", json={"x_handle": "u1", "text": "https://x.com/3"})

    response = client.get("/digest", params={"email": "test@example.com", "days": 365})
    assert response.status_code == 200
    data = response.json()
    assert "Daily Digest" in data["text"]
    assert "#tools (2)" in data["text"]
    assert "#untagged (1)" in data["text"]
    tags = {group["tag"]: group["count"] for group in data["groups"]}
    assert tags["tools"] == 2
    assert tags["untagged"] == 1


def test_digest_limit(tmp_path):
    client = get_client(tmp_path)
    client.post("/admin/reset_all")
    client.post("/admin/allowlist/add", json={"email": "test@example.com"})
    client.post("/simulate_dm", json={"x_handle": "u1", "text": "start test@example.com"})
    for i in range(60):
        client.post("/simulate_dm", json={"x_handle": "u1", "text": f"https://x.com/{i}"})

    response = client.get("/digest", params={"email": "test@example.com", "days": 365})
    assert response.status_code == 200
    total = sum(group["count"] for group in response.json()["groups"])
    assert total <= 50
