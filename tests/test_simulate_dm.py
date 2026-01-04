from fastapi.testclient import TestClient

from app.main import app
from core import replies


def test_simulate_unlinked_link():
    client = TestClient(app)
    payload = {"state": "UNLINKED", "text": "https://x.com/1", "allowlisted": False}
    response = client.post("/simulate_dm", json=payload)
    assert response.status_code == 200
    assert response.json()["reply"] == replies.REPLY_LINK_FIRST


def test_simulate_unlinked_start_invalid():
    client = TestClient(app)
    payload = {"state": "UNLINKED", "text": "start abc", "allowlisted": False}
    response = client.post("/simulate_dm", json=payload)
    assert response.status_code == 200
    assert response.json()["reply"] == replies.REPLY_INVALID_EMAIL


def test_simulate_unlinked_start_allowlisted():
    client = TestClient(app)
    payload = {"state": "UNLINKED", "text": "start test@example.com", "allowlisted": True}
    response = client.post("/simulate_dm", json=payload)
    assert response.status_code == 200
    assert response.json()["reply"] == replies.REPLY_LINKED


def test_simulate_linked_link():
    client = TestClient(app)
    payload = {"state": "LINKED", "text": "https://x.com/1", "allowlisted": True}
    response = client.post("/simulate_dm", json=payload)
    assert response.status_code == 200
    assert response.json()["reply"] == replies.REPLY_SAVED


def test_simulate_blocked_link():
    client = TestClient(app)
    payload = {"state": "BLOCKED", "text": "https://x.com/1", "allowlisted": False}
    response = client.post("/simulate_dm", json=payload)
    assert response.status_code == 200
    assert response.json()["reply"] == replies.REPLY_NOT_APPROVED


def test_simulate_urls_capped_at_five():
    client = TestClient(app)
    message = " ".join([f"https://x.com/{i}" for i in range(10)])
    payload = {"state": "LINKED", "text": message, "allowlisted": True}
    response = client.post("/simulate_dm", json=payload)
    assert response.status_code == 200
    parsed = response.json()["parsed"]
    assert len(parsed["urls"]) == 5
