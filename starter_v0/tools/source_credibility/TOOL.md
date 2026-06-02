---
name: source_credibility
track: bonus
kind: local_knowledge
requires_env: []
inputs: [url, source, title, evidence_text]
outputs: [rating, score, reasons, guidance]
side_effect: false
---
# source_credibility

Scores basic source credibility signals for a URL or source label. Use before
making factual claims from a social post, unknown website, or mixed-source digest.
