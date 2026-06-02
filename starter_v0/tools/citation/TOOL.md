---
name: citation
track: team
kind: local_formatter
requires_env: []
inputs: [items, style]
outputs: [markdown, style, item_count, missing_fields]
side_effect: false
---
# citation

Formats already-collected source items into reference lists. Defaults to APA7
when the user asks for references or citations but does not name a style.
