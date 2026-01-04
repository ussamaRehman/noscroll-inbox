import json

import httpx

BASE_URL = "http://localhost:8000"


def request(client: httpx.Client, method: str, path: str, **kwargs) -> httpx.Response:
    resp = client.request(method, f"{BASE_URL}{path}", **kwargs)
    resp.raise_for_status()
    return resp


def main() -> None:
    with httpx.Client(timeout=10) as client:
        request(client, "POST", "/admin/demo/reset")
        request(client, "POST", "/admin/allowlist/add", json={"email": "demo@example.com"})
        request(
            client,
            "POST",
            "/simulate_dm",
            json={"x_handle": "demo", "text": "start demo@example.com"},
        )
        request(
            client,
            "POST",
            "/simulate_dm",
            json={"x_handle": "demo", "text": "https://x.com/1 #tools note: demo"},
        )
        request(
            client, "POST", "/simulate_dm", json={"x_handle": "demo", "text": "https://x.com/2"}
        )

        digest = request(
            client,
            "GET",
            "/digest",
            params={"email": "demo@example.com", "days": 365},
        )
        preview = request(
            client,
            "GET",
            "/digest/email_preview",
            params={"email": "demo@example.com", "days": 365},
        )

    print("Digest")
    print(digest.json()["text"])
    print("\nEmail Preview")
    print(json.dumps(preview.json(), indent=2))


if __name__ == "__main__":
    main()
