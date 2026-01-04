import fastapi.testclient as testclient

import app.main as main_app


def setup_function():
    main_app.INBOX.clear()


def test_saving_flow_and_inbox():
    client = testclient.TestClient(main_app.app)
    payload = {
        "state": "LINKED",
        "text": "https://x.com/1 https://x.com/2 #tools note: new eval framework",
        "allowlisted": True,
        "linked_email": "user@example.com",
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


def test_cap_saves_at_five():
    client = testclient.TestClient(main_app.app)
    message = " ".join([f"https://x.com/{i}" for i in range(10)])
    payload = {"state": "LINKED", "text": message, "allowlisted": True, "linked_email": "a@b.com"}
    response = client.post("/simulate_dm", json=payload)
    assert response.status_code == 200

    inbox = client.get("/inbox", params={"email": "a@b.com"})
    assert inbox.json()["count"] == 5


def test_isolated_inboxes():
    client = testclient.TestClient(main_app.app)
    payload_a = {
        "state": "LINKED",
        "text": "https://x.com/a",
        "allowlisted": True,
        "linked_email": "a@example.com",
    }
    payload_b = {
        "state": "LINKED",
        "text": "https://x.com/b",
        "allowlisted": True,
        "linked_email": "b@example.com",
    }
    client.post("/simulate_dm", json=payload_a)
    client.post("/simulate_dm", json=payload_b)

    inbox_a = client.get("/inbox", params={"email": "a@example.com"})
    inbox_b = client.get("/inbox", params={"email": "b@example.com"})
    assert inbox_a.json()["count"] == 1
    assert inbox_b.json()["count"] == 1
