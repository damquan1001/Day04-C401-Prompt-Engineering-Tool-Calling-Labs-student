from __future__ import annotations

from typing import Any

from tools._shared import domain, err, terms


def _label(item: dict[str, Any], index: int) -> str:
    return str(item.get("source") or domain(str(item.get("url") or "")) or item.get("title") or f"source_{index + 1}")


def compare_sources(
    items: list[dict[str, Any]] | None = None,
    question: str = "",
    max_sources: int = 4,
) -> dict[str, Any]:
    try:
        selected = list(items or [])[: max(2, min(int(max_sources or 4), 8))]
        profiles: list[dict[str, Any]] = []
        for index, item in enumerate(selected):
            text = " ".join([
                str(item.get("title") or ""),
                str(item.get("summary") or item.get("content") or ""),
            ])
            profiles.append({
                "label": _label(item, index),
                "url": item.get("url"),
                "terms": terms(text),
                "title": item.get("title"),
            })

        if len(profiles) < 2:
            return {
                "tool": "compare_sources",
                "question": question,
                "source_count": len(profiles),
                "agreements": [],
                "differences": [],
                "note": "Need at least two sources to compare.",
            }

        common = set.intersection(*(profile["terms"] for profile in profiles)) if profiles else set()
        agreements = sorted(common)[:12]
        differences: list[dict[str, Any]] = []
        for profile in profiles:
            other_terms = set.union(*(p["terms"] for p in profiles if p is not profile))
            unique_terms = sorted(profile["terms"] - other_terms)[:10]
            differences.append({
                "source": profile["label"],
                "url": profile["url"],
                "distinct_terms": unique_terms,
            })

        return {
            "tool": "compare_sources",
            "question": question,
            "source_count": len(profiles),
            "agreements": agreements,
            "differences": differences,
            "comparison_note": "This is a lexical comparison for research triage; verify claims before publication.",
        }
    except Exception as exc:
        return err("compare_sources", exc)
