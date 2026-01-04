import os
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from core import replies
from core.dm_parser import decide_reply, is_valid_email, parse_dm
from storage.sqlite_store import SQLiteStore

app = FastAPI()
STORE = SQLiteStore(os.getenv("DB_PATH", "noscroll.db"))
STORE.init_db()
for email in os.getenv("ALLOWLIST_EMAILS", "").split(","):
    if email.strip():
        STORE.allowlist_add(email.strip())


@app.get("/health")
def health():
    return {"status": "ok"}


class SimulateDMIn(BaseModel):
    x_handle: str
    text: str


class ParsedOut(BaseModel):
    kind: str
    email: Optional[str]
    urls: List[str]
    tags: List[str]
    note: Optional[str]


class SimulateDMOut(BaseModel):
    reply: str
    parsed: ParsedOut
    magic_link: Optional[str] = None


class InboxItem(BaseModel):
    url: str
    tags: List[str]
    note: Optional[str]
    saved_at: str


class InboxOut(BaseModel):
    email: str
    count: int
    items: List[InboxItem]


class AllowlistIn(BaseModel):
    email: str


@app.post("/simulate_dm", response_model=SimulateDMOut)
def simulate_dm(payload: SimulateDMIn) -> SimulateDMOut:
    parsed = parse_dm(payload.text)
    linked_email = STORE.link_get_email(payload.x_handle)
    state = "LINKED" if linked_email else "UNLINKED"
    magic_link = None

    if parsed.kind == "start":
        email = parsed.start_email or ""
        if not is_valid_email(email):
            reply = replies.REPLY_INVALID_EMAIL
        elif not STORE.allowlist_contains(email):
            reply = replies.REPLY_NOT_ALLOWLISTED
        else:
            result = STORE.link_set_if_unlinked(payload.x_handle, email)
            if result == "linked":
                reply = replies.REPLY_LINKED
                linked_email = email
                token = STORE.magic_create(email)
                magic_link = f"http://localhost:8000/auth/magic?token={token}"
            elif result == "resend":
                reply = replies.REPLY_RESEND
                token = STORE.magic_create(email)
                magic_link = f"http://localhost:8000/auth/magic?token={token}"
            else:
                reply = replies.REPLY_ALREADY_LINKED
    else:
        reply = decide_reply(state, parsed, allowlisted=False, linked_email=linked_email)

    if parsed.kind == "link" and linked_email:
        saved_at = datetime.now(timezone.utc).isoformat()
        STORE.inbox_add_items(linked_email, parsed.urls, parsed.tags, parsed.note, saved_at)
    return SimulateDMOut(
        reply=reply,
        parsed=ParsedOut(
            kind=parsed.kind,
            email=parsed.start_email,
            urls=parsed.urls,
            tags=parsed.tags,
            note=parsed.note,
        ),
        magic_link=magic_link,
    )


@app.get("/inbox", response_model=InboxOut)
def get_inbox(email: str) -> InboxOut:
    items = [InboxItem(**item) for item in STORE.inbox_list(email)]
    return InboxOut(email=email, count=len(items), items=items)


@app.post("/admin/allowlist/add")
def allowlist_add(payload: AllowlistIn) -> dict:
    count = STORE.allowlist_add(payload.email)
    return {"count": count}


@app.post("/admin/allowlist/clear")
def allowlist_clear() -> dict:
    count = STORE.allowlist_clear()
    return {"count": count}


@app.post("/admin/reset_all")
def reset_all() -> dict:
    STORE.allowlist_clear()
    STORE.links_clear()
    STORE.inbox_clear()
    STORE.magic_clear()
    return {"ok": True}


@app.get("/auth/magic")
def auth_magic(token: str) -> dict:
    try:
        email = STORE.magic_redeem(token)
    except ValueError as exc:
        detail = str(exc)
        if detail == "invalid":
            raise HTTPException(status_code=400, detail="invalid token")
        if detail == "used":
            raise HTTPException(status_code=400, detail="token already used")
        if detail == "expired":
            raise HTTPException(status_code=400, detail="token expired")
        raise HTTPException(status_code=400, detail="invalid token")
    return {"ok": True, "email": email}
