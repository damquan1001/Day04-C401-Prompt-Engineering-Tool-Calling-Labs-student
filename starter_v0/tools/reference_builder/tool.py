from __future__ import annotations

import re
from typing import Any

from tools._shared import err


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    if not text:
        return []
    parts = re.split(r"\s*(?:;|,| and )\s*", text)
    return [part.strip() for part in parts if part.strip()]


def _author_display(authors: Any, style: str) -> str:
    names = _as_list(authors)
    if not names:
        return "Anonymous"
    if style == "bibtex":
        return " and ".join(names)
    if len(names) == 1:
        return names[0]
    if style == "apa":
        return ", ".join(names[:-1]) + f", & {names[-1]}"
    return ", ".join(names)


def _year(item: dict[str, Any]) -> str:
    for key in ("year", "published", "updated", "date"):
        value = str(item.get(key) or "").strip()
        if not value:
            continue
        match = re.search(r"(19|20)\d{2}", value)
        if match:
            return match.group(0)
    return "n.d."


def _title(item: dict[str, Any]) -> str:
    return str(item.get("title") or item.get("name") or "Untitled").strip()


def _source(item: dict[str, Any]) -> str:
    return str(item.get("source") or item.get("publisher") or item.get("journal") or "").strip()


def _url(item: dict[str, Any]) -> str:
    return str(item.get("url") or item.get("link") or "").strip()


def _doi(item: dict[str, Any]) -> str:
    return str(item.get("doi") or "").strip()


def _plain_reference(item: dict[str, Any], style: str) -> str:
    authors = _author_display(item.get("authors") or item.get("author"), style)
    title = _title(item)
    year = _year(item)
    source = _source(item)
    url = _url(item)
    doi = _doi(item)

    if style == "mla":
        core = f"{authors}. \"{title}.\""
        if source:
            core += f" {source},"
        core += f" {year}."
    elif style == "chicago":
        core = f"{authors}. \"{title}.\""
        if source:
            core += f" {source}"
        core += f" ({year})."
    elif style == "ieee":
        core = f"{authors}, \"{title},\""
        if source:
            core += f" {source},"
        core += f" {year}."
    elif style == "bibtex":
        key_base = re.sub(r"[^a-z0-9]+", "_", f"{authors.split()[0]}_{year}_{title.lower()}".lower()).strip("_")
        key = key_base or "ref"
        lines = [
            f"@misc{{{key},",
            f"  author = {{{authors}}},",
            f"  title = {{{title}}},",
            f"  year = {{{year}}},",
        ]
        if source:
            lines.append(f"  howpublished = {{{source}}},")
        if doi:
            lines.append(f"  doi = {{{doi}}},")
        if url:
            lines.append(f"  url = {{{url}}},")
        lines.append("}")
        return "\n".join(lines)
    else:
        core = f"{authors} ({year}). {title}."
        if source:
            core += f" {source}."

    if doi:
        core += f" DOI: {doi}."
    if url and style != "bibtex":
        core += f" {url}"
    return " ".join(core.split())


def reference_builder(
    items: list[dict[str, Any]] | None = None,
    style: str = "apa",
    include_urls: bool = True,
    title: str = "",
) -> dict[str, Any]:
    try:
        items = list(items or [])
        style = (style or "apa").strip().lower()
        allowed = {"apa", "mla", "chicago", "ieee", "bibtex", "plain"}
        if style not in allowed:
            style = "apa"

        references: list[str] = []
        metadata: list[dict[str, Any]] = []
        for index, item in enumerate(items):
            ref = _plain_reference(item, style)
            if not include_urls and style != "bibtex":
                ref = re.sub(r"\s+https?://\S+", "", ref).strip()
            references.append(ref)
            metadata.append({
                "index": index,
                "title": _title(item),
                "year": _year(item),
                "source": _source(item),
                "url": _url(item),
                "doi": _doi(item),
            })

        heading = title.strip() or "References"
        markdown_lines = [f"## {heading}", ""]
        for index, ref in enumerate(references, 1):
            markdown_lines.append(f"{index}. {ref}")
        markdown = "\n".join(markdown_lines).rstrip()

        return {
            "tool": "reference_builder",
            "style": style,
            "title": heading,
            "item_count": len(items),
            "references": references,
            "metadata": metadata,
            "markdown": markdown,
        }
    except Exception as exc:
        return err("reference_builder", exc)
