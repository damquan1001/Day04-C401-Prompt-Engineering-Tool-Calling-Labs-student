from __future__ import annotations

from typing import Any

from tools._shared import domain


TIER_1_DOMAINS = {
    "arxiv.org",
    "openai.com",
    "anthropic.com",
    "deepmind.google",
    "ai.google.dev",
    "microsoft.com",
    "meta.com",
    "nvidia.com",
}

WEAK_DOMAINS = {
    "x.com",
    "twitter.com",
    "reddit.com",
    "facebook.com",
    "tiktok.com",
    "instagram.com",
}


def _source_tier(item: dict[str, Any]) -> str:
    source = str(item.get("source") or domain(str(item.get("url") or ""))).lower()
    if any(source.endswith(name) for name in TIER_1_DOMAINS):
        return "tier_1"
    if any(source.endswith(name) for name in WEAK_DOMAINS):
        return "tier_3_signal"
    return "unknown"


def check_sources(items: list[dict[str, Any]] | None = None, strict: bool = False) -> dict[str, Any]:
    items = items or []
    checked_items: list[dict[str, Any]] = []
    missing_url_count = 0
    weak_source_count = 0

    for index, item in enumerate(items, start=1):
        url = str(item.get("url") or "").strip()
        source = str(item.get("source") or domain(url) or "").strip()
        tier = _source_tier(item)
        has_url = bool(url)
        has_source = bool(source)
        if not has_url:
            missing_url_count += 1
        if tier in {"tier_3_signal", "unknown"}:
            weak_source_count += 1
        checked_items.append({
            "index": index,
            "title": item.get("title") or item.get("summary", "")[:80],
            "url": url,
            "source": source,
            "has_url": has_url,
            "has_source": has_source,
            "source_tier": tier,
            "ready_for_digest": has_url and has_source and (not strict or tier == "tier_1"),
        })

    recommendations: list[str] = []
    if missing_url_count:
        recommendations.append("Add source URLs before publishing factual claims.")
    if weak_source_count:
        recommendations.append("Verify social or unknown sources with primary sources or reputable reporting.")
    if strict and any(not item["ready_for_digest"] for item in checked_items):
        recommendations.append("Strict mode requires every item to have a URL, source, and tier_1 evidence.")
    if not recommendations:
        recommendations.append("Sources look ready for a sourced research digest.")

    return {
        "tool": "check_sources",
        "checked_items": checked_items,
        "missing_url_count": missing_url_count,
        "weak_source_count": weak_source_count,
        "recommendations": recommendations,
    }
