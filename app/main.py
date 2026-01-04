from datetime import datetime, timezone
from typing import Dict, List, Literal, Optional

from fastapi import FastAPI
from pydantic import BaseModel

from core.dm_parser import decide_reply, parse_dm

app = FastAPI()
INBOX: Dict[str, List["InboxItem"]] = {}


@app.get("/health")
def health():
    return {"status": "ok"}


class SimulateDMIn(BaseModel):
    state: Literal["UNLINKED", "LINKED", "BLOCKED"]
    text: str
    allowlisted: bool = False
    linked_email: Optional[str] = None


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


@app.post("/simulate_dm", response_model=SimulateDMOut)
def simulate_dm(payload: SimulateDMIn) -> SimulateDMOut:
    parsed = parse_dm(payload.text)
    reply = decide_reply(
        payload.state,
        parsed,
        allowlisted=payload.allowlisted,
        linked_email=payload.linked_email,
    )
    if payload.state == "LINKED" and parsed.kind == "link" and payload.linked_email:
        saved_at = datetime.now(timezone.utc).isoformat()
        items = [
            InboxItem(url=url, tags=parsed.tags, note=parsed.note, saved_at=saved_at)
            for url in parsed.urls
        ]
        INBOX.setdefault(payload.linked_email, []).extend(items)
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
