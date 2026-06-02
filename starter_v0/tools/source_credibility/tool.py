from __future__ import annotations

from typing import Any

from tools._shared import domain, err


HIGH_TRUST_SUFFIXES = (".gov", ".edu")
HIGH_TRUST_DOMAINS = {
    "arxiv.org",
    "nature.com",
    "science.org",
    "openai.com",
    "anthropic.com",
    "deepmind.google",
    "research.google",
}
SOCIAL_OR_FORUM_DOMAINS = {
    "x.com",
    "twitter.com",
    "reddit.com",
    "tiktok.com",
    "facebook.com",
    "youtube.com",
}


def source_credibility(
    url: str = "",
    source: str = "",
    title: str = "",
    evidence_text: str = "",
) -> dict[str, Any]:
    try:
        host = (domain(url) or source or "").lower().replace("www.", "")
        score = 50
        reasons: list[str] = []

        if host.endswith(HIGH_TRUST_SUFFIXES) or host in HIGH_TRUST_DOMAINS:
            score += 30
            reasons.append("Primary, academic, official, or research-oriented domain.")
        if host in SOCIAL_OR_FORUM_DOMAINS or source.startswith("@"):
            score -= 20
            reasons.append("Social or community source; useful signal but not enough as confirmed fact.")
        if url.startswith("https://"):
            score += 5
            reasons.append("Uses HTTPS.")
        if title:
            score += 5
            reasons.append("Has a title or named source context.")
        if evidence_text and len(evidence_text.strip()) >= 200:
            score += 10
            reasons.append("Has enough excerpt text for review.")
        if not host:
            score -= 25
            reasons.append("Missing domain or source identifier.")

        score = max(0, min(score, 100))
        rating = "high" if score >= 75 else "medium" if score >= 45 else "low"
        return {
            "tool": "source_credibility",
            "url": url,
            "source": source or host,
            "rating": rating,
            "score": score,
            "reasons": reasons or ["No strong credibility signals detected."],
            "guidance": "Use high-rated sources for claims; corroborate medium/low sources before publishing.",
        }
    except Exception as exc:
        return err("source_credibility", exc)
