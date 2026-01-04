import importlib
import os

from fastapi.testclient import TestClient


def get_client(tmp_path) -> TestClient:
    os.environ["DB_PATH"] = str(tmp_path / "test.db")
    import app.main as main_app

    importlib.reload(main_app)
    return TestClient(main_app.app)


def reset(client: TestClient) -> None:
    client.post("/admin/reset_all")


def allowlist(client: TestClient, email: str) -> None:
    client.post("/admin/allowlist/add", json={"email": email})


def test_saving_flow_and_inbox(tmp_path):
    client = get_client(tmp_path)
    reset(client)
    allowlist(client, "user@example.com")
    start_payload = {"x_handle": "user", "text": "start user@example.com"}
    client.post("/simulate_dm", json=start_payload)
    payload = {
        "x_handle": "user",
        "text": "https://x.com/1 https://x.com/2 #tools note: new eval framework",
    }
    response = client.post("/simulate_dm", json=payload)
    assert response.status_code == 200

    inbox = client.get("/inbox", params={"email": "user@example.com"})
    data = inbox.json()
    assert data["count"] == 2
    assert [item["url"] for item in data["items"]] == ["https://x.com/1", "https://x.com/2"]
    assert data["items"][0]["tags"] == ["tools"]
    assert data["items"][0]["note"] == "new eval framework"
    assert data["items"][0]["saved_at"]


def test_cap_saves_at_five(tmp_path):
    client = get_client(tmp_path)
    reset(client)
    allowlist(client, "a@b.com")
    start_payload = {"x_handle": "a", "text": "start a@b.com"}
    client.post("/simulate_dm", json=start_payload)
    message = " ".join([f"https://x.com/{i}" for i in range(10)])
    payload = {"x_handle": "a", "text": message}
    response = client.post("/simulate_dm", json=payload)
    assert response.status_code == 200

    inbox = client.get("/inbox", params={"email": "a@b.com"})
    assert inbox.json()["count"] == 5


def test_isolated_inboxes(tmp_path):
    client = get_client(tmp_path)
    reset(client)
    allowlist(client, "a@example.com")
    allowlist(client, "b@example.com")
    client.post("/simulate_dm", json={"x_handle": "a", "text": "start a@example.com"})
    client.post("/simulate_dm", json={"x_handle": "b", "text": "start b@example.com"})
    client.post("/simulate_dm", json={"x_handle": "a", "text": "https://x.com/a"})
    client.post("/simulate_dm", json={"x_handle": "b", "text": "https://x.com/b"})

    inbox_a = client.get("/inbox", params={"email": "a@example.com"})
    inbox_b = client.get("/inbox", params={"email": "b@example.com"})
    assert inbox_a.json()["count"] == 1
    assert inbox_b.json()["count"] == 1
