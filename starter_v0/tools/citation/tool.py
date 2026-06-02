from __future__ import annotations

import re
from datetime import date
from typing import Any

from tools._shared import domain


SUPPORTED_STYLES = {"APA7", "IEEE", "Harvard", "MLA", "Chicago"}


def _first_text(item: dict[str, Any], *keys: str, default: str = "") -> str:
    for key in keys:
        value = item.get(key)
        if isinstance(value, list):
            value = ", ".join(str(part).strip() for part in value if str(part).strip())
        if value is not None and str(value).strip():
            return str(value).strip()
    return default


def _year(value: str) -> str:
    match = re.search(r"(19|20)\d{2}", value or "")
    return match.group(0) if match else "n.d."


def _fields_missing(item: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    if not _first_text(item, "author", "authors"):
        missing.append("author")
    if not _first_text(item, "published", "date", "updated"):
        missing.append("year")
    if not _first_text(item, "title", "summary"):
        missing.append("title")
    if not _first_text(item, "source") and not _first_text(item, "url"):
        missing.append("source")
    if not _first_text(item, "url"):
        missing.append("url")
    return missing


def _parts(item: dict[str, Any]) -> dict[str, str]:
    url = _first_text(item, "url")
    source = _first_text(item, "source", default=domain(url) or "Source")
    raw_date = _first_text(item, "published", "date", "updated")
    title = _first_text(item, "title", "summary", default="Untitled")
    return {
        "author": _first_text(item, "author", "authors"),
        "year": _year(raw_date),
        "title": title.rstrip("."),
        "source": source.rstrip("."),
        "url": url,
        "viewed": date.today().isoformat(),
    }


def _apa7(item: dict[str, Any]) -> str:
    parts = _parts(item)
    prefix = f"{parts['author']}. " if parts["author"] else ""
    return f"{prefix}({parts['year']}). {parts['title']}. {parts['source']}. {parts['url']}".strip()


def _ieee(index: int, item: dict[str, Any]) -> str:
    parts = _parts(item)
    author = f"{parts['author']}, " if parts["author"] else ""
    return f"[{index}] {author}\"{parts['title']},\" {parts['source']}, {parts['year']}. {parts['url']}".strip()


def _harvard(item: dict[str, Any]) -> str:
    parts = _parts(item)
    author = parts["author"] or parts["title"]
    return f"{author} {parts['year']}, {parts['title']}, {parts['source']}, viewed {parts['viewed']}, {parts['url']}".strip()


def _mla(item: dict[str, Any]) -> str:
    parts = _parts(item)
    prefix = f"{parts['author']}. " if parts["author"] else ""
    return f"{prefix}\"{parts['title']}.\" {parts['source']}, {parts['year']}, {parts['url']}.".strip()


def _chicago(item: dict[str, Any]) -> str:
    parts = _parts(item)
    prefix = f"{parts['author']}. " if parts["author"] else ""
    return f"{prefix}\"{parts['title']}.\" {parts['source']}. {parts['year']}. {parts['url']}.".strip()


def format_citations(items: list[dict[str, Any]] | None = None, style: str = "APA7") -> dict[str, Any]:
    items = items or []
    normalized_style = style if style in SUPPORTED_STYLES else "APA7"
    citations: list[str] = []
    missing_fields: list[dict[str, Any]] = []

    for index, item in enumerate(items, start=1):
        if normalized_style == "IEEE":
            citation = _ieee(index, item)
        elif normalized_style == "Harvard":
            citation = _harvard(item)
        elif normalized_style == "MLA":
            citation = _mla(item)
        elif normalized_style == "Chicago":
            citation = _chicago(item)
        else:
            citation = _apa7(item)
        citations.append(citation)
        missing = _fields_missing(item)
        if missing:
            missing_fields.append({"index": index, "missing": missing})

    markdown = "\n".join(f"- {citation}" for citation in citations)
    return {
        "tool": "format_citations",
        "style": normalized_style,
        "markdown": markdown,
        "item_count": len(items),
        "missing_fields": missing_fields,
    }
