from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from storage.sqlite_store import SQLiteStore


class DigestItem:
    def __init__(self, url: str, note: Optional[str], saved_at: str) -> None:
        self.url = url
        self.note = note
        self.saved_at = saved_at


class DigestGroup:
    def __init__(self, tag: str, count: int, items: List[DigestItem]) -> None:
        self.tag = tag
        self.count = count
        self.items = items


def build_digest(
    email: str, days: int, store: SQLiteStore
) -> tuple[str, List[Dict[str, object]], int]:
    since = datetime.now(timezone.utc) - timedelta(days=days)
    items = store.inbox_list_since(email, since.isoformat(), limit=50)

    groups: Dict[str, List[DigestItem]] = {}
    for item in items:
        tags = item["tags"] or []
        target_tags = tags if tags else ["untagged"]
        for tag in target_tags:
            groups.setdefault(tag, []).append(
                DigestItem(url=item["url"], note=item["note"], saved_at=item["saved_at"])
            )

    group_list = []
    for tag, tag_items in groups.items():
        tag_items.sort(key=lambda x: x.saved_at, reverse=True)
        group_list.append(DigestGroup(tag=tag, count=len(tag_items), items=tag_items))
    group_list.sort(key=lambda g: (-g.count, g.tag))

    day_label = "day" if days == 1 else "days"
    lines = [f"Daily Digest (last {days} {day_label}) — {email}"]
    for group in group_list:
        lines.append(f"#{group.tag} ({group.count})")
        for item in group.items:
            if item.note:
                lines.append(f"- {item.url} — note: {item.note}")
            else:
                lines.append(f"- {item.url}")

    total_count = sum(group.count for group in group_list)
    groups_out = [
        {"tag": group.tag, "count": group.count, "items": group.items} for group in group_list
    ]
    return "\n".join(lines), groups_out, total_count


def build_email_preview(email: str, days: int, store: SQLiteStore) -> tuple[str, str, int]:
    text, _groups, total = build_digest(email, days, store)
    save_label = "save" if total == 1 else "saves"
    day_label = "day" if days == 1 else "days"
    subject = f"NoScroll Digest — {total} {save_label} (last {days} {day_label})"
    return subject, text, total
