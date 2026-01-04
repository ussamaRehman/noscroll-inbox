import os
from datetime import datetime, timezone
from typing import Dict, List, Literal, Optional, Set

from fastapi import FastAPI
from pydantic import BaseModel

from core import replies
from core.dm_parser import decide_reply, parse_dm

app = FastAPI()
ALLOWLIST: Set[str] = {
    email.strip() for email in os.getenv("ALLOWLIST_EMAILS", "").split(",") if email.strip()
}
USER_LINKS: Dict[str, str] = {}
INBOX: Dict[str, List["InboxItem"]] = {}


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
    linked_email = USER_LINKS.get(payload.x_handle)
    state: Literal["UNLINKED", "LINKED"] = "LINKED" if linked_email else "UNLINKED"

    if parsed.kind == "start":
        email = parsed.start_email or ""
        allowlisted = email in ALLOWLIST
        reply = decide_reply(
            state,
            parsed,
            allowlisted=allowlisted,
            linked_email=linked_email,
        )
        if reply == replies.REPLY_LINKED:
            USER_LINKS[payload.x_handle] = email
            linked_email = email
    else:
        reply = decide_reply(state, parsed, allowlisted=False, linked_email=linked_email)

    if parsed.kind == "link" and linked_email:
        saved_at = datetime.now(timezone.utc).isoformat()
        items = [
            InboxItem(url=url, tags=parsed.tags, note=parsed.note, saved_at=saved_at)
            for url in parsed.urls
        ]
        INBOX.setdefault(linked_email, []).extend(items)
    return SimulateDMOut(
        reply=reply,
        parsed=ParsedOut(
            kind=parsed.kind,
            email=parsed.start_email,
            urls=parsed.urls,
            tags=parsed.tags,
            note=parsed.note,
        ),
    )


@app.get("/inbox", response_model=InboxOut)
def get_inbox(email: str) -> InboxOut:
    items = INBOX.get(email, [])
    return InboxOut(email=email, count=len(items), items=items)


@app.post("/admin/allowlist/add")
def allowlist_add(payload: AllowlistIn) -> dict:
    ALLOWLIST.add(payload.email)
    return {"count": len(ALLOWLIST)}


@app.post("/admin/allowlist/clear")
def allowlist_clear() -> dict:
    ALLOWLIST.clear()
    return {"count": 0}


@app.post("/admin/reset_all")
def reset_all() -> dict:
    ALLOWLIST.clear()
    USER_LINKS.clear()
    INBOX.clear()
    return {"ok": True}
