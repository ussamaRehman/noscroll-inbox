from dataclasses import dataclass
import re
from typing import List, Optional

from core import replies

EMAIL_RE = re.compile(r"^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$")
URL_RE = re.compile(r"https?://\\S+")
TAG_RE = re.compile(r"(?:^|\\s)#(\\w+)")


@dataclass(frozen=True)
class ParsedMessage:
    kind: str
    start_email: Optional[str]
    urls: List[str]
    tags: List[str]
    note: Optional[str]


def parse_dm(message: str) -> ParsedMessage:
    text = message.strip()
    lower = text.lower()

    start_email = None
    if lower.startswith("start"):
        match = re.match(r"^start\\s+(\\S+)", text, flags=re.IGNORECASE)
        if match:
            start_email = match.group(1)
            kind = "start"
        else:
            kind = "unknown"
    elif lower.startswith("help"):
        kind = "help"
    elif URL_RE.search(text):
        kind = "link"
    else:
        kind = "unknown"

    urls = URL_RE.findall(text)[:5]
    tags = TAG_RE.findall(text)

    note = None
    note_index = lower.find("note:")
    if note_index != -1:
        note = text[note_index + len("note:") :].strip()

    return ParsedMessage(
        kind=kind,
        start_email=start_email,
        urls=urls,
        tags=tags,
        note=note,
    )


def is_valid_email(email: str) -> bool:
    return bool(EMAIL_RE.match(email))


def decide_reply(
    state: str,
    parsed: ParsedMessage,
    allowlisted: bool,
    start_email: Optional[str] = None,
    linked_email: Optional[str] = None,
) -> str:
    if parsed.kind == "help":
        return replies.REPLY_HELP

    if parsed.kind == "start":
        email = start_email or parsed.start_email or ""
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
