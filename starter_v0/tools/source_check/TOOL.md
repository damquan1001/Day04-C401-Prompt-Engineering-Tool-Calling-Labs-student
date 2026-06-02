---
name: source_check
track: team
kind: local_formatter
requires_env: []
inputs: [items, strict]
outputs: [checked_items, missing_url_count, weak_source_count, recommendations]
side_effect: false
---
# source_check

Checks already-collected research items for source URL presence and rough source
quality. It does not fetch new data.
