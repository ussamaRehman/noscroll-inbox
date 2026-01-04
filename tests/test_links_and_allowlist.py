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


def test_start_invalid_email(tmp_path):
    client = get_client(tmp_path)
    reset(client)
    response = client.post("/simulate_dm", json={"x_handle": "u1", "text": "start abc"})
    assert response.status_code == 200
    assert response.json()["reply"] == replies.REPLY_INVALID_EMAIL


def test_start_not_allowlisted(tmp_path):
    client = get_client(tmp_path)
    reset(client)
    response = client.post("/simulate_dm", json={"x_handle": "u1", "text": "start a@b.com"})
    assert response.status_code == 200
    assert response.json()["reply"] == replies.REPLY_NOT_ALLOWLISTED
    follow = client.post("/simulate_dm", json={"x_handle": "u1", "text": "https://x.com/1"})
    assert follow.json()["reply"] == replies.REPLY_LINK_FIRST
    inbox = client.get("/inbox", params={"email": "a@b.com"})
    assert inbox.json()["count"] == 0


def test_start_allowlisted_links_account(tmp_path):
    client = get_client(tmp_path)
    reset(client)
    allowlist(client, "user@example.com")
    response = client.post(
        "/simulate_dm",
        json={"x_handle": "u1", "text": "start user@example.com"},
    )
    assert response.status_code == 200
    assert response.json()["reply"] == replies.REPLY_LINKED
    link = client.post("/simulate_dm", json={"x_handle": "u1", "text": "https://x.com/1"})
    assert link.json()["reply"] == replies.REPLY_SAVED


def test_link_before_start(tmp_path):
    client = get_client(tmp_path)
    reset(client)
    response = client.post("/simulate_dm", json={"x_handle": "u1", "text": "https://x.com/1"})
    assert response.status_code == 200
    assert response.json()["reply"] == replies.REPLY_LINK_FIRST
    inbox = client.get("/inbox", params={"email": "user@example.com"})
    assert inbox.json()["count"] == 0


def test_start_again_same_email(tmp_path):
    client = get_client(tmp_path)
    reset(client)
    allowlist(client, "user@example.com")
    client.post("/simulate_dm", json={"x_handle": "u1", "text": "start user@example.com"})
    response = client.post(
        "/simulate_dm",
        json={"x_handle": "u1", "text": "start user@example.com"},
    )
    assert response.status_code == 200
    assert response.json()["reply"] == replies.REPLY_RESEND


def test_start_with_different_email_after_linked(tmp_path):
    client = get_client(tmp_path)
    reset(client)
    allowlist(client, "user@example.com")
    allowlist(client, "other@example.com")
    client.post("/simulate_dm", json={"x_handle": "u1", "text": "start user@example.com"})
    response = client.post(
        "/simulate_dm",
        json={"x_handle": "u1", "text": "start other@example.com"},
    )
    assert response.status_code == 200
    assert response.json()["reply"] == replies.REPLY_ALREADY_LINKED


def test_isolated_by_handle(tmp_path):
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
