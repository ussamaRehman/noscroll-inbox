import re
from dataclasses import dataclass
from typing import List, Optional

from core import replies

EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
URL_RE = re.compile(r"https?://\S+")
TAG_RE = re.compile(r"#([A-Za-z0-9_]+)")
NOTE_RE = re.compile(r"(?i)\bnote:\s*(.+)$")


@dataclass(frozen=True)
class ParsedMessage:
    kind: str
    start_email: Optional[str]
    urls: List[str]
    tags: List[str]
    note: Optional[str]
    raw: str


def parse_dm(message: str) -> ParsedMessage:
    raw = message.strip()
    lower = raw.lower()

    urls = URL_RE.findall(raw)[:5]
    tags = TAG_RE.findall(raw)

    note = None
    note_match = NOTE_RE.search(raw)
    if note_match:
        note = note_match.group(1).strip()

    start_email = None
    if lower.startswith("start"):
        parts = raw.split()
        start_email = parts[1] if len(parts) > 1 else None
        kind = "start"
    elif lower.startswith("help"):
        kind = "help"
    elif urls:
        kind = "link"
    else:
        kind = "unknown"

    return ParsedMessage(
        kind=kind,
        start_email=start_email,
        urls=urls,
        tags=tags,
        note=note,
        raw=raw,
    )


def is_valid_email(email: str) -> bool:
    return bool(EMAIL_RE.match(email))


def decide_reply(
    state: str,
    parsed: ParsedMessage,
    allowlisted: bool,
    linked_email: Optional[str] = None,
) -> str:
    if parsed.kind == "help":
        return replies.REPLY_HELP

    if parsed.kind == "start":
        email = parsed.start_email or ""
        if not is_valid_email(email):
            return replies.REPLY_INVALID_EMAIL

        if state == "LINKED":
            if linked_email and email.lower() == linked_email.lower():
                return replies.REPLY_RESEND
            return replies.REPLY_ALREADY_LINKED

        if allowlisted:
            return replies.REPLY_LINKED
        return replies.REPLY_NOT_ALLOWLISTED

    if parsed.kind == "link":
        if state == "LINKED":
            return replies.REPLY_SAVED
        if state == "BLOCKED":
            return replies.REPLY_NOT_APPROVED
        return replies.REPLY_LINK_FIRST

    return replies.REPLY_HELP
