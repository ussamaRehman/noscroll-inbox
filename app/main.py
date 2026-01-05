import os
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from core import replies
from core.digest import build_digest, build_email_preview
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


class DigestItem(BaseModel):
    url: str
    note: Optional[str]
    saved_at: str


class DigestGroup(BaseModel):
    tag: str
    count: int
    items: List[DigestItem]


class DigestOut(BaseModel):
    text: str
    groups: List[DigestGroup]


class DigestEmailPreviewOut(BaseModel):
    email: str
    days: int
    subject: str
    body: str


class DigestSendPreviewIn(BaseModel):
    email: str
    days: int = 1


class DigestSendPreviewOut(BaseModel):
    already_sent: bool
    email: str
    days: int
    date_utc: str
    total: int
    subject: str
    body: str


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


@app.get("/digest", response_model=DigestOut)
def get_digest(email: str, days: int = 1) -> DigestOut:
    text, groups, _total = build_digest(email, days, store=STORE)
    group_models = [
        DigestGroup(
            tag=group["tag"],
            count=group["count"],
            items=[DigestItem(**item.__dict__) for item in group["items"]],
        )
        for group in groups
    ]
    return DigestOut(text=text, groups=group_models)


@app.get("/digest/email_preview", response_model=DigestEmailPreviewOut)
def get_digest_email_preview(email: str, days: int = 1) -> DigestEmailPreviewOut:
    subject, text, _total = build_email_preview(email, days, store=STORE)
    return DigestEmailPreviewOut(email=email, days=days, subject=subject, body=text)


@app.post("/digest/send_preview", response_model=DigestSendPreviewOut)
def send_digest_preview(payload: DigestSendPreviewIn) -> DigestSendPreviewOut:
    subject, text, total = build_email_preview(payload.email, payload.days, store=STORE)
    date_utc = datetime.now(timezone.utc).date().isoformat()
    existing = STORE.digest_send_get(payload.email, payload.days, date_utc)
    if existing:
        return DigestSendPreviewOut(already_sent=True, **existing)
    STORE.digest_send_put(payload.email, payload.days, date_utc, total, subject, text)
    return DigestSendPreviewOut(
        already_sent=False,
        email=payload.email,
        days=payload.days,
        date_utc=date_utc,
        total=total,
        subject=subject,
        body=text,
    )


@app.post("/admin/allowlist/add")
def allowlist_add(payload: AllowlistIn) -> dict:
    count = STORE.allowlist_add(payload.email)
    return {"count": count}


@app.post("/admin/allowlist/clear")
def allowlist_clear() -> dict:
    count = STORE.allowlist_clear()
    return {"count": count}


@app.get("/admin/digest_sends")
def digest_sends(email: str, days: int = 1) -> dict:
    items = STORE.digest_send_list(email, days)
    return {"count": len(items), "items": items}


@app.post("/admin/demo/reset")
def demo_reset() -> dict:
    STORE.allowlist_clear()
    STORE.link_delete("demo")
    STORE.inbox_clear("demo@example.com")
    return {"ok": True}


@app.post("/admin/reset_all")
def reset_all() -> dict:
    STORE.allowlist_clear()
    STORE.links_clear()
    STORE.inbox_clear()
    STORE.magic_clear()
    STORE.digest_sends_clear()
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
