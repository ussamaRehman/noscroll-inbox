import json
import os

import httpx

BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:8000")


def request(client: httpx.Client, method: str, path: str, **kwargs) -> httpx.Response:
    resp = client.request(method, f"{BASE_URL}{path}", **kwargs)
    resp.raise_for_status()
    return resp


def main() -> None:
    with httpx.Client(timeout=10) as client:
        request(client, "POST", "/admin/demo/reset")

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
