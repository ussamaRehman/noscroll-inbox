from typing import List, Literal, Optional

from fastapi import FastAPI
from pydantic import BaseModel

from core.dm_parser import decide_reply, parse_dm

app = FastAPI()


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


@app.post("/simulate_dm", response_model=SimulateDMOut)
def simulate_dm(payload: SimulateDMIn) -> SimulateDMOut:
    parsed = parse_dm(payload.text)
    reply = decide_reply(
        payload.state,
        parsed,
        allowlisted=payload.allowlisted,
        linked_email=payload.linked_email,
    )
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
