from __future__ import annotations

import re
from typing import Any

from tools._shared import err, terms


def _sentences(text: str) -> list[str]:
    cleaned = " ".join((text or "").split())
    parts = re.split(r"(?<=[.!?])\s+", cleaned)
    return [part.strip() for part in parts if len(part.strip()) >= 30]


def _item_text(items: list[dict[str, Any]] | None) -> str:
    if not items:
        return ""
    parts: list[str] = []
    for item in items:
        parts.append(str(item.get("title") or ""))
        parts.append(str(item.get("summary") or item.get("content") or ""))
    return " ".join(parts)


def extract_key_points(
    text: str = "",
    items: list[dict[str, Any]] | None = None,
    max_points: int = 5,
) -> dict[str, Any]:
    try:
        combined = " ".join([text or "", _item_text(items)]).strip()
        if not combined:
            return {"tool": "extract_key_points", "key_points": [], "source_count": len(items or [])}

        max_points = max(1, min(int(max_points or 5), 10))
        scored: list[tuple[int, int, str]] = []
        seen: set[str] = set()
        for index, sentence in enumerate(_sentences(combined)):
            folded = " ".join(sorted(terms(sentence)))
            if not folded or folded in seen:
                continue
            seen.add(folded)
            score = len(terms(sentence))
            if any(marker in sentence.lower() for marker in ("announced", "released", "published", "policy", "risk", "requires")):
                score += 3
            scored.append((score, -index, sentence))

        scored.sort(reverse=True)
        key_points = [sentence for _, _, sentence in scored[:max_points]]
        return {
            "tool": "extract_key_points",
            "key_points": key_points,
            "source_count": len(items or []),
            "chars_analyzed": len(combined),
        }
    except Exception as exc:
        return err("extract_key_points", exc)
