---
name: compare_sources
track: bonus
kind: local_formatter
requires_env: []
inputs: [items, question, max_sources]
outputs: [agreements, differences, source_count]
side_effect: false
---
# compare_sources

Compares two or more already-collected research items. Use when the user asks
whether sources agree, how articles differ, or what each source uniquely adds.
