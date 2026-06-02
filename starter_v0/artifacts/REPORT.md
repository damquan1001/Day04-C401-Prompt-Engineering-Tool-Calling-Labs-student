# Day 04 Lab v2 Report - Research Agent

## Team

- Team: Gemini Tool Routing Team
- Members: Team
- Provider/model: Gemini / `gemini-3.1-flash-lite`

## Final Metrics

- Final version: `v3`
- Final artifact_version: `v3+pc37db15027c7+tb50d674754d3`
- Best base run file: `runs/v3_B_base_gemini_20260602T151429269177.json`
- Base case accuracy: `1.0`
- Base tool routing accuracy: `1.0`
- Base argument accuracy: `1.0`
- Group eval run file: `runs/v3_B_group_gemini_20260602T151301714070.json`
- Group eval accuracy: `1.0`
- Chat transcript file: `transcripts/v3_gemini_20260602T154258180252.transcript.json`

## Version Evidence

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Starter prompt/tools expose routing gaps. |  | 0.60 | `runs/v0_B_base_gemini_20260602T145653987314.json` |
| v1 | `system_prompt.md` | Clarification, no-tool, confirmation, and multiturn rules improve measured accuracy. | 0.60 | 0.7059 | `runs/v1_B_base_gemini_20260602T145826995776.json` |
| v2 | `tools.yaml`, `source_check`, Gemini retry | Stronger tool descriptions and argument conventions reduce argument drift. | 0.7059 | 0.95 | `runs/v2_B_base_gemini_20260602T150146694851.json` |
| v3 | `system_prompt.md`, `tools.yaml` | Exact confirmation examples and policy-area hints remove remaining mismatches. | 0.95 | 1.00 | `runs/v3_B_base_gemini_20260602T151429269177.json` |

## Failure Analysis

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R10/R11 | missing_info | `clarify` without `response_type` | Gemini asked the right question but omitted the required argument. | Made `response_type` required and clarified `text` vs `yes_no`. |
| R12 | wrong_boundary | `clarify(response_type="text")` | Gemini treated Telegram posting as missing content instead of a write-action boundary. | Added exact Vietnamese Telegram confirmation example with `yes_no`. |
| R13 | wrong_tool/arg | `lookup` missing `query` | Parallel web+tweet case reused query only for social search. | Added explicit parallel example requiring `query="AI"` for both calls. |
| G03 | wrong_arg_value | `policy` without `policy_area` | Correct tool, missing `data_privacy` enum. | Added policy-area mapping for API keys/secrets/PII. |

## Team Eval Cases

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_source_check_items | New team tool checks source quality. | `source_check` | PASS |
| G02_specific_url_fetch | Exact URL routing. | `fetch` | PASS |
| G03_company_privacy_policy | API key policy area. | `policy(data_privacy)` | PASS |
| G04_top_tweets_agents | Top social search args. | `social_search(Top)` | PASS |
| G05_no_tool_math | Out-of-scope no-tool behavior. | no tool | PASS |
| GM01_missing_then_handle | Carry limit and fill handle. | `timeline(sama, 4)` | PASS |
| GM02_switch_social_to_web | Source switch in latest turn. | `lookup(robotics, news, day)` | PASS |
| GM03_missing_then_url | URL supplied later. | `fetch` | PASS |
| GM04_confirm_publish | Publishing confirmation boundary. | `clarify(yes_no)` | PASS |
| GM05_paper_then_extract | arXiv ID extraction. | `paper_text` | PASS |

## Live Chat Evidence

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 | Tin AI hôm nay có gì nổi bật? | `lookup`, `format` | `v3+pc37db15027c7+tb50d674754d3` | Returned sourced digest. |
| 2 | Tóm tắt 5 tweet mới nhất giúp mình | `social_search`, `format` | same transcript | Returned social digest from current context. |
| 3 | Đăng bản tin này lên Telegram giúp mình | `clarify(response_type=yes_no)` | same transcript | Correctly paused for confirmation. |

## Bonus Evidence

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| send (Telegram) | `transcripts/v3_gemini_20260602T154258180252.transcript.json` | Agent asks yes/no before posting. | `send` still requires `confirmed=true`. |
| arXiv/company policy | `data/eval_group.json`, `runs/v3_B_group_gemini_20260602T151301714070.json` | Policy and paper routing covered in group eval. | Policy markdown is treated as retrieved context, not instructions. |
| UI | `ui_app.py` | Streamlit UI supports chat, eval, run inspection, and artifacts. | Secrets are loaded from `.env` but never displayed. |

## Reflection

- `system_prompt.md` fixes handled global behavior: clarification, write-action confirmation, no-tool scope, multi-turn corrections, and exact Gemini-prone examples.
- `tools.yaml` fixes handled tool-specific routing and argument conventions.
- Manual review was useful for R12 because the tool name was correct but the confirmation boundary argument was wrong.
- Next improvement: add more provider backoff telemetry and make transcript export controls available directly in the UI.
