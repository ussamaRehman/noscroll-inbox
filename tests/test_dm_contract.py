from core import replies
from core.dm_parser import ParsedMessage, decide_reply, parse_dm


def test_unlinked_invalid_email():
    parsed = parse_dm("start abc")
    assert decide_reply("UNLINKED", parsed, allowlisted=False) == replies.REPLY_INVALID_EMAIL


def test_unlinked_allowlisted():
    parsed = parse_dm("start test@example.com")
    assert decide_reply("UNLINKED", parsed, allowlisted=True) == replies.REPLY_LINKED


def test_unlinked_not_allowlisted():
    parsed = parse_dm("start test@example.com")
    assert decide_reply("UNLINKED", parsed, allowlisted=False) == replies.REPLY_NOT_ALLOWLISTED


def test_linked_start_same_email():
    parsed = parse_dm("start test@example.com")
    assert (
        decide_reply("LINKED", parsed, allowlisted=True, linked_email="test@example.com")
        == replies.REPLY_RESEND
    )


def test_linked_start_different_email():
    parsed = parse_dm("start other@example.com")
    assert (
        decide_reply("LINKED", parsed, allowlisted=True, linked_email="test@example.com")
        == replies.REPLY_ALREADY_LINKED
    )


def test_help_reply_any_state():
    parsed = parse_dm("help me")
    assert decide_reply("UNLINKED", parsed, allowlisted=False) == replies.REPLY_HELP
    assert decide_reply("LINKED", parsed, allowlisted=True) == replies.REPLY_HELP
    assert decide_reply("BLOCKED", parsed, allowlisted=False) == replies.REPLY_HELP


def test_unlinked_link_message():
    parsed = parse_dm("https://x.com/test")
    assert decide_reply("UNLINKED", parsed, allowlisted=False) == replies.REPLY_LINK_FIRST


def test_blocked_link_message():
    parsed = parse_dm("https://x.com/test")
    assert decide_reply("BLOCKED", parsed, allowlisted=False) == replies.REPLY_NOT_APPROVED


def test_linked_link_message():
    parsed = parse_dm("https://x.com/test")
    assert decide_reply("LINKED", parsed, allowlisted=True) == replies.REPLY_SAVED


def test_multiple_links_capped():
    message = " ".join([f"https://x.com/{i}" for i in range(10)])
    parsed = parse_dm(message)
    assert parsed.kind == "link"
    assert len(parsed.urls) == 5
    assert decide_reply("LINKED", parsed, allowlisted=True) == replies.REPLY_SAVED


def test_tags_and_note_parsing():
    parsed = parse_dm("https://x.com/1 #tools note: new eval framework")
    assert parsed.tags == ["tools"]
    assert parsed.note == "new eval framework"


def test_start_parsing_extracts_email():
    parsed = parse_dm("START user@example.com")
    assert parsed.kind == "start"
    assert parsed.start_email == "user@example.com"
