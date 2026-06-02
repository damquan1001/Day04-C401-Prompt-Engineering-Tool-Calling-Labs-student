---
name: extract_key_points
track: bonus
kind: local_formatter
requires_env: []
inputs: [text, items, max_points]
outputs: [key_points, source_count, chars_analyzed]
side_effect: false
---
# extract_key_points

Extracts concise key points from raw text or already-collected research items.
Use after `fetch`, `lookup`, `papers`, or `paper_text` when the user asks for
main points, takeaways, or a short summary of long material.
