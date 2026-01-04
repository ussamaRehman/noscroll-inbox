import importlib
import os

from fastapi.testclient import TestClient

from core import replies


def get_client(tmp_path) -> TestClient:
    os.environ["DB_PATH"] = str(tmp_path / "test.db")
    import app.main as main_app

    importlib.reload(main_app)
    return TestClient(main_app.app)


def reset(client: TestClient) -> None:
    client.post("/admin/reset_all")


def allowlist(client: TestClient, email: str) -> None:
    client.post("/admin/allowlist/add", json={"email": email})


def test_simulate_unlinked_link(tmp_path):
    client = get_client(tmp_path)
    reset(client)
    payload = {"x_handle": "user", "text": "https://x.com/1"}
    response = client.post("/simulate_dm", json=payload)
    assert response.status_code == 200
    assert response.json()["reply"] == replies.REPLY_LINK_FIRST


def test_simulate_unlinked_start_invalid(tmp_path):
    client = get_client(tmp_path)
    reset(client)
    payload = {"x_handle": "user", "text": "start abc"}
    response = client.post("/simulate_dm", json=payload)
    assert response.status_code == 200
    assert response.json()["reply"] == replies.REPLY_INVALID_EMAIL


def test_simulate_unlinked_start_allowlisted(tmp_path):
    client = get_client(tmp_path)
    reset(client)
    allowlist(client, "test@example.com")
    payload = {"x_handle": "user", "text": "start test@example.com"}
    response = client.post("/simulate_dm", json=payload)
    assert response.status_code == 200
    assert response.json()["reply"] == replies.REPLY_LINKED


def test_simulate_linked_link(tmp_path):
    client = get_client(tmp_path)
    reset(client)
    allowlist(client, "test@example.com")
    start_payload = {"x_handle": "user", "text": "start test@example.com"}
    client.post("/simulate_dm", json=start_payload)
    payload = {"x_handle": "user", "text": "https://x.com/1"}
    response = client.post("/simulate_dm", json=payload)
    assert response.status_code == 200
    assert response.json()["reply"] == replies.REPLY_SAVED


def test_simulate_urls_capped_at_five(tmp_path):
    client = get_client(tmp_path)
    reset(client)
    allowlist(client, "test@example.com")
    start_payload = {"x_handle": "user", "text": "start test@example.com"}
    client.post("/simulate_dm", json=start_payload)
    message = " ".join([f"https://x.com/{i}" for i in range(10)])
    payload = {"x_handle": "user", "text": message}
    response = client.post("/simulate_dm", json=payload)
    assert response.status_code == 200
    parsed = response.json()["parsed"]
    assert len(parsed["urls"]) == 5
